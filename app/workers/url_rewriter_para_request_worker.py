from .base import BaseWorker
from app.config.logger import LoggerSetup
import os
import json
from app.workers.url_rewriter_para_request_helpers.ai_message_request_send import AIRateLimiterService
from app.workers.core.selector_lambda.selector_lambda import ArticleSelectorService
# from app.workers.core.article_innovator_api_call.wordpress.fetch_category.fetch_category import FetchCategory
from app.workers.core.article_innovator_api_call.fetch_supportive_prompt.fetch_supportive_prompt import FetchSupportivePrompt
from app.workers.core.scraper_lmabda.scraper_lmabda import ArticleScraperService  # ensure it's the class version
from app.workers.core.article_innovator_api_call.fetch_base_prompt_data.fetch_base_prompt_data import FetchBasePromptData
from app.workers.url_rewriter_para_request_helpers.send_single_ai_request import SendSingleAiRequest
from app.workers.url_rewriter_para_request_helpers.ai_message_request_store import AIMessageRequestStore
from app.workers.url_rewriter_para_request_helpers.create_single_ai_request import CreateSingleAiRequest
from app.workers.url_rewriter_para_request_helpers.get_single_ai_response import GetSingleAiResponse
from app.workers.url_rewriter_para_response_helpers.ai_message_response_store import AIMessageResponseStore
from app.workers.url_rewriter_para_request_helpers.final_prompt_creator import FinalPromptCreator


class UrlRewriterParallelWorker(BaseWorker):
    def __init__(self, channel, queue_name):
        # Set worker name first
        self.worker_name = 'url_rewriter_para_request_worker'
        
        # Call the parent class's __init__ after setting worker_name
        super().__init__(channel, queue_name)
        
        # Set up logger for url_rewriter_para_request_worker
        logger_setup = LoggerSetup()
        self.logger = logger_setup.setup_worker_logger(self.pid)
        self.logger = self.logger.bind(worker_name=self.worker_name, worker_type="url_rewriter_para_request_worker")
        self.logger.info("url_rewriter_para_request_worker initialized and ready to process messages")
        self.selector_service = ArticleSelectorService()
        self.scraper_service = ArticleScraperService()
        self.ai_rate_limiter_service = AIRateLimiterService()
        # self.fetch_category_service = FetchCategory()
        self.fetch_supportive_prompt_service = FetchSupportivePrompt()
        self.fetch_base_prompt_data_service = FetchBasePromptData()
        self.send_single_ai_request_service = SendSingleAiRequest()
        self.ai_message_request_store_service = AIMessageRequestStore()
        self.create_single_ai_request_service = CreateSingleAiRequest()
        self.get_single_ai_response_service = GetSingleAiResponse()
        self.ai_message_response_store_service = AIMessageResponseStore()
        self.final_prompt_creator_service = FinalPromptCreator()
        
        
    
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
            # self.logger.info(f"Processing message: {data}")
            
        
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

            get_single_ai_response_data=None
            final_prompt_data=None
            
            # TODO 
            # # Your processing logic here
            try:
                # Step 1: Get selectors
                selector_data = self.selector_service.get_selectors(data)
                # print(selector_data,'----------------------selector_data----------------------')
            except Exception as e:
                print({"status": "error", "step": "get_selectors", "message": str(e)})
                # return {"status": "error", "step": "get_selectors", "message": str(e)}
   
            try:
                # Step 2: Scrape article data
                scraped_data = self.scraper_service.get_scraped_article_data(selector_data, data)
                # print(scraped_data,'----------------------scraped_data----------------------')
            except Exception as e:
                print({"status": "error", "step": "get_scraped_article_data", "message": str(e)})
                # return {"status": "error", "step": "get_scraped_article_data", "message": str(e)}
                
            try:
                # Step 3: Fetch base prompt data
                
                # Check if any prompt value contains [[...]]
                contains_placeholder = any(
                    isinstance(v, str) and '[[' in v and ']]' in v
                    for v in prompt_data.values()
                )
                # print(contains_placeholder, '----------------------contains_placeholder----------------------')
                # Call fetch_base_prompt_data if needed
                if contains_placeholder:
                    base_prompt_data = self.fetch_base_prompt_data_service.fetch_base_prompt_data(prompt_slug_id, domain_slug_id)
                    print(base_prompt_data, '----------------------base_prompt_data----------------------')
            except Exception as e:
                print({"status": "error", "step": "fetch_base_prompt_data", "message": str(e)})
                # return {"status": "error", "step": "fetch_base_prompt_data", "message": str(e)}
            
            print(ai_flags, '----------------------ai_flags----------------------')
            if ai_flags.get("is_primary_keyword_generated_by_ai", False):
                supportive_prompt_data = {}                
                try:
                    # Step 4: get supportive_prompt data from Article Innovator
                    
                    primery_keywords_id = support_ids.get("supportive_prompt_primary_keyword_generated_by_ai_id")

                    primery_keywords_max_retries = 3  # You can configure this dynamically if needed

                    for attempt in range(1, primery_keywords_max_retries + 1):
                        try:
                            supportive_prompt_data = self.fetch_supportive_prompt_service.fetch_supportive_prompt(primery_keywords_id, '')
                            print(supportive_prompt_data, '----------------------supportive_prompt_data----------------------')

                            failed_prompts = [
                                item for item in supportive_prompt_data.get('supportive_prompts', [])
                                if not item.get('success')
                            ]

                            if not failed_prompts:
                                break  # All prompts succeeded

                            print(f"[Attempt {attempt}] Some prompts failed, retrying...")

                        except Exception as retry_exception:
                            print(f"[Attempt {attempt}] Retry error: {retry_exception}")                            
                except Exception as e:
                    print({"status": "error", "step": "fetch_supportive_prompt", "message": str(e)})
                    # return {"status": "error", "step": "fetch_supportive_prompt", "message": str(e)}
                    
                    
                if supportive_prompt_data:
                    
                    try:
                        # Step 4.1: Create single ai request
                        single_ai_request_data = self.create_single_ai_request_service.create_single_ai_request(data, supportive_prompt_data, 'primary_keyword_generated_by_ai', scraped_data)
                        # print(single_ai_request_data, '----------------------single_ai_request_data----------------------')
                    except Exception as e:
                        print({"status": "error", "step": "create_single_ai_request", "message": str(e)})
                        # return {"status": "error", "step": "create_single_ai_request", "message": str(e)}
                    
                    # try:
                    #     # Step 4.2: Store ai message request
                    #     store_ai_message_request_data = self.ai_message_request_store_service.store_ai_message_request(single_ai_request_data)
                    #     # print(store_ai_message_request_data, '----------------------store_ai_message_request_data----------------------')
                    # except Exception as e:
                    #     print({"status": "error", "step": "store_ai_message_request", "message": str(e)})
                    #     # return {"status": "error", "step": "store_ai_message_request", "message": str(e)}
                      
                    try:
                        # Step 4.3: Send single ai request
                        send_single_ai_request_data = self.send_single_ai_request_service.send_single_ai_request(single_ai_request_data, workspace_slug_id)
                        # print(send_single_ai_request_data, '----------------------send_single_ai_request_data----------------------')
                        

                        # Check if the request was successful
                        if not send_single_ai_request_data or not send_single_ai_request_data.get("success", True):
                            print({
                                "status": "error",
                                "step": "send_single_ai_request",
                                "message": send_single_ai_request_data.get("error", "Unknown error")
                            })


                    except Exception as e:
                        print({"status": "error", "step": "send_single_ai_request", "message": str(e)})
                        # return {"status": "error", "step": "send_single_ai_request", "message": str(e)}
                    
                    try:
                        # Step 4.4: get single ai response
                        message_id = send_single_ai_request_data.get("message_id")

                        # # Step 4.4: Get single AI response
                        # message_id = send_single_ai_request_data.get("message_id") or single_ai_request_data.get("message_id")
                        # if not message_id:
                        #     raise ValueError("Missing message_id for response retrieval")


                        get_single_ai_response_data = self.get_single_ai_response_service.get_single_ai_response(message_id)
                        # print(get_single_ai_response_data, '----------------------get_single_ai_response_data----------------------')
                    except Exception as e:
                        print({"status": "error", "step": "get_single_ai_response", "message": str(e)})
                        # return {"status": "error", "step": "get_single_ai_response", "message": str(e)}
                    
                    try:
                        # Step 4.5: Store single ai response
                        store_ai_response_data = self.ai_message_response_store_service.store_ai_message_response(get_single_ai_response_data)
                        # print(store_ai_response_data, '----------------------store_ai_response_data----------------------')
                    except Exception as e:
                        print({"status": "error", "step": "store_ai_message_response", "message": str(e)})
                        # return {"status": "error", "step": "store_ai_message_response", "message": str(e)}
                    
            try:
                # Step 5: final prompt
                final_prompt_data = self.final_prompt_creator_service.final_prompt_creator(base_prompt_data, get_single_ai_response_data, scraped_data)
                # print(final_prompt_data,'----------------------final_prompt_data----------------------')
            except Exception as e:
                print({"status": "error", "step": "final_prompt_creator", "message": str(e)})
                # return {"status": "error", "step": "final_prompt_creator", "message": str(e)}
            

            try:
                # Step 6: Prepare content for AI
                process_content_data = self.ai_rate_limiter_service.fetch_and_process_content(scraped_data, data, final_prompt_data)
                # print(process_content_data,'----------------------process_content_data----------------------')
            except Exception as e:
                print({"status": "error", "step": "fetch_and_process_content", "message": str(e)})
                # return {"status": "error", "step": "fetch_and_process_content", "message": str(e)}

            try:
                # Step 4: Get AI response
                ai_response_json = self.ai_rate_limiter_service.send_ai_requests(process_content_data, article_priority)
                # print(ai_response_json,'----------------------ai_response_json----------------------')
            except Exception as e:
                print({"status": "error", "step": "send_ai_request", "message": str(e)})
                # return {"status": "error", "step": "send_ai_request", "message": str(e)}










            # try:
            #     # Step 5: Final formatting
            #     final_article_content_response = self.ai_rate_limiter_service.merge_and_sequence_ai_response(ai_response_json, process_content_data)
            # except Exception as e:
            #     return {"status": "error", "step": "merge_and_sequence_ai_response", "message": str(e)}
            
            
            # try:
            #     # Step 5: Find category 
            #     print(is_category_selected_by_ai,'is_category_selected_by_aizzzz')
            #     if is_category_selected_by_ai == True:
            #         fetch_all_categories = self.fetch_category_service.fetch_category(data)
                
            # except Exception as e:
            #     return {"status": "error", "step": "fetch_category", "message": str(e)}
            
            
            
            
            
            
            # self.logger.info(f"final_article_content_response: {final_article_content_response}")
            
            # Log successful completion
            # self.logger.info(f"Message processing completed successfully for data: {data}")
            self.logger.info(f"xxxxxxxxxxxxxxxxxxxxxxxxx url_rewriter_para_request_worker xxxxxxxxxxxxxxxxxxxxxxxxx")
            
            # Explicitly acknowledge the message
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return True
        except Exception as e:
            self.logger.error(f"Message processing failed for data:. Error: {str(e)}")
            # Negative acknowledge the message and requeue it
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
            return False