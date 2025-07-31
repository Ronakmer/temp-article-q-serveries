from .base import BaseWorker
from app.config.logger import LoggerSetup
import os
import json
from app.workers.core.selector_lambda.selector_lambda import ArticleSelectorService
# from app.workers.core.article_innovator_api_call.wordpress.fetch_category.fetch_category import FetchCategory
from app.workers.core.article_innovator_api_call.fetch_supportive_prompt.fetch_supportive_prompt import FetchSupportivePrompt
from app.workers.core.article_innovator_api_call.fetch_base_prompt_data.fetch_base_prompt_data import FetchBasePromptData
from app.workers.core.scraper_lmabda.scraper_lmabda import ArticleScraperService  # ensure it's the class version
from app.workers.url_rewriter_para_request_helpers.send_single_ai_request import SendSingleAiRequest
from app.workers.url_rewriter_para_request_helpers.ai_message_request_store import AIMessageRequestStore
from app.workers.url_rewriter_para_request_helpers.create_single_ai_request import CreateSingleAiRequest
from app.workers.url_rewriter_para_request_helpers.get_single_ai_response import GetSingleAiResponse
from app.workers.url_rewriter_para_response_helpers.ai_message_response_store import AIMessageResponseStore

from app.workers.url_rewriter_content_helpers.prompt_merge import FinalPromptCreator
from app.workers.url_rewriter_content_helpers.content_processor import ContentProcessor
from app.workers.url_rewriter_content_helpers.ai_rate_limiter_request import AIRateLimiterService
from app.workers.core.article_innovator_api_call.ai_message.ai_message import AIMessage

class UrlRewriterParallelWorker(BaseWorker):
    def __init__(self, channel, queue_name):
        # Set worker name first
        self.worker_name = 'url_rewriter_content_request_worker'
        
        # Call the parent class's __init__ after setting worker_name
        super().__init__(channel, queue_name)
        
        # Set up logger for url_rewriter_content_request_worker
        logger_setup = LoggerSetup()
        self.logger = logger_setup.setup_worker_logger(self.pid)
        self.logger = self.logger.bind(worker_name=self.worker_name, worker_type="url_rewriter_content_request_worker")
        print("url_rewriter_content_request_worker initialized and ready to process messages")
        self.ai_rate_limiter_service = AIRateLimiterService()
        # self.fetch_category_service = FetchCategory()
        self.fetch_supportive_prompt_service = FetchSupportivePrompt()
        self.fetch_base_prompt_data_service = FetchBasePromptData()
        self.send_single_ai_request_service = SendSingleAiRequest()
        self.ai_message_request_store_service = AIMessageRequestStore()
        self.create_single_ai_request_service = CreateSingleAiRequest()
        self.get_single_ai_response_service = GetSingleAiResponse()
        self.ai_message_response_store_service = AIMessageResponseStore()
        
        self.selector_service = ArticleSelectorService()
        self.scraper_service = ArticleScraperService()

        self.final_prompt_creator_service = FinalPromptCreator()
        self.content_processor_service = ContentProcessor()
        
        self.ai_message_service = AIMessage()

        
    
    def str_to_bool(value):
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.strip().lower() in ['true', '1', 'yes']
        return bool(value)
            


    def process_message(self, ch, method, properties, body):
        try:
            # Process the message
            data = json.loads(body)  # Parse the JSON body
            # print(f"Processing message: {data}")
            
        
            message = data.get("message", {})
            # target_category_ids = message.get("wp_category_id", [])

            is_category_selected_by_ai = message.get("is_category_selected_by_ai")
            ai_flags = message.get("ai_content_flags", {})
            article_priority = message.get("article_priority", 100)
            domain_obj = message.get("domain", {})
            domain_slug_id = domain_obj.get("slug_id", {})
            workspace_obj = message.get("workspace", {})
            workspace_slug_id = workspace_obj.get("slug_id", {})
            prompt_obj = message.get("prompt", {})
            support_ids = prompt_obj.get("supportive_prompt_json_data", {})
            prompt_data = prompt_obj.get("prompt_data", {})
            prompt_slug_id = prompt_obj.get("slug_id", {})



            selector_data=None
            scraped_data=None
            base_prompt_data=None
            final_prompt_data=None
            fetch_content_data=None
            processed_data=None
            get_single_ai_response_data = None     

            message_retry_count = 3

            
            try:
                # Step 1: Get selectors
                selector_data = self.selector_service.get_selectors(data)
                
            except Exception as e:
                self.logger.error({"status": "error", "step": "get_selectors", "message": str(e)})
                return {"status": "error", "step": "url_rewriter_content_request_worker in get_selectors", "message": str(e)}
   
            try:
                # Step 2: Scrape article data
                scraped_data = self.scraper_service.get_scraped_article_data(selector_data, data)
            except Exception as e:
                self.logger.error({"status": "error", "step": "get_scraped_article_data", "message": str(e)})
                return {"status": "error", "step": "url_rewriter_content_request_worker in get_scraped_article_data", "message": str(e)}


            try:
                # Step 3: Fetch base prompt data
                
                # Check if any prompt value contains [[...]]
                contains_placeholder = any(
                    isinstance(v, str) and '[[' in v and ']]' in v
                    for v in prompt_data.values()
                )
                # Call fetch_base_prompt_data if needed
                if contains_placeholder:
                    base_prompt_data = self.fetch_base_prompt_data_service.fetch_base_prompt_data(prompt_slug_id, domain_slug_id)
                else:
                    base_prompt_data = prompt_data
                    
            except Exception as e:
                self.logger.error({"status": "error", "step": "fetch_base_prompt_data", "message": str(e)})
                return {"status": "error", "step": "url_rewriter_content_request_worker in fetch_base_prompt_data", "message": str(e)}


            try:
                # Step 4: fetch content
                fetch_content_data = self.content_processor_service.fetch_content(scraped_data)
            except Exception as e:
                self.logger.error({"status": "error", "step": "fetch_content", "message": str(e)})
                return {"status": "error", "step": "url_rewriter_content_request_worker in fetch_content", "message": str(e)}

            try:
                # Step 5: process content
                processed_data = self.content_processor_service.process_content(fetch_content_data)
            except Exception as e:
                self.logger.error({"status": "error", "step": "process_content", "message": str(e)})
                return {"status": "error", "step": "url_rewriter_content_request_worker in process_content", "message": str(e)}



            # Step 5: primary keyword
            print(ai_flags, '----------------------ai_flags----------------------')
            if ai_flags.get("is_primary_keyword_generated_by_ai", False):
                supportive_prompt_data = {}     
                create_single_ai_request_data = None   
                ai_response_json = None   
                try:
                    # Step 5.1: fetch supportive prompt                    
                    primery_keywords_id = support_ids.get("supportive_prompt_primary_keyword_generated_by_ai_id")
                    supportive_prompt_data = self.fetch_supportive_prompt_service.fetch_supportive_prompt(primery_keywords_id, '')
                except Exception as e:
                    self.logger.error({"status": "error", "step": "fetch_supportive_prompt", "message": str(e)})
                    return {"status": "error", "step": "url_rewriter_content_request_worker in fetch_supportive_prompt", "message": str(e)}
                    

                try:
                    # Step 5.2: create single primary keyword request
                    create_single_ai_request_data = self.ai_rate_limiter_service.create_single_primary_keyword_ai_request(data, supportive_prompt_data, processed_data)
                except Exception as e:
                    self.logger.error({"status": "error", "step": "create_single_primary_keyword_ai_request", "message": str(e)})
                    return {"status": "error", "step": "url_rewriter_content_request_worker in create_single_primary_keyword_ai_request", "message": str(e)}


                try:
                    # Step 5.3: send ai request
                    ai_response_json = self.ai_rate_limiter_service.send_ai_request(create_single_ai_request_data, workspace_slug_id)
                except Exception as e:
                    self.logger.error({"status": "error", "step": "send_ai_request", "message": str(e)})
                    return {"status": "error", "step": "url_rewriter_content_request_worker in send_ai_request", "message": str(e)}

                try:
                    # Step 5.4: get single ai response
                    message_id = ai_response_json.get("message_id")

                    get_single_ai_response_data = self.ai_rate_limiter_service.get_single_ai_response(message_id)
                except Exception as e:
                    self.logger.error({"status": "error", "step": "get_single_ai_response", "message": str(e)})
                    return {"status": "error", "step": "url_rewriter_content_request_worker in get_single_ai_response", "message": str(e)}


                # Step 5.5: Store AI message response
                try:
                    stored_message_data = self.ai_message_service.store_ai_message_response(get_single_ai_response_data, message_retry_count)
                except Exception as e:
                    self.logger.error({"status": "error", "step": "store_ai_message_response", "message": str(e)})
                    return {"status": "error", "step": "url_rewriter_content_request_worker in store_ai_message_response", "message": str(e)}


            
            try:
                # Step 6: merge prompt data
                final_prompt_data = self.final_prompt_creator_service.merge_prompt_data(base_prompt_data, processed_data, fetch_content_data, get_single_ai_response_data)
            except Exception as e:
                self.logger.error({"status": "error", "step": "final_prompt_creator", "message": str(e)})
                return {"status": "error", "step": "url_rewriter_content_request_worker in final_prompt_creator", "message": str(e)}
            


            try:
                # Step 7: create content ai request
                created_ai_request_data = self.ai_rate_limiter_service.create_content_ai_request(data, final_prompt_data)
            except Exception as e:
                self.logger.error({"status": "error", "step": "send_ai_request", "message": str(e)})
                return {"status": "error", "step": "url_rewriter_content_request_worker in create_content_ai_request", "message": str(e)}


            try:
                # Step 8: send ai request
                ai_response_json = self.ai_rate_limiter_service.send_ai_request(created_ai_request_data, workspace_slug_id)
            except Exception as e:
                self.logger.error({"status": "error", "step": "send_ai_request", "message": str(e)})
                return {"status": "error", "step": "url_rewriter_content_request_worker in send_ai_request", "message": str(e)}
            
                        
            # Log successful completion
            # print(f"Message processing completed successfully for data: {data}")
            print(f"xxxxxxxxxxxxxxxxxxxxxxxxx url_rewriter_content_request_worker xxxxxxxxxxxxxxxxxxxxxxxxx")
            
            # Explicitly acknowledge the message
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return True
        except Exception as e:
            self.logger.error(f"Message processing failed for data:. Error: {str(e)}")
            # Negative acknowledge the message and requeue it
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
            return False