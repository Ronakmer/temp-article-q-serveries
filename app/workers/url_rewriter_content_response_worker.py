from .base import BaseWorker
from app.config.logger import LoggerSetup
import os
import json
# from app.workers.url_rewriter_para_response_helpers.ai_message_response_store import AIMessageResponseStore 
# from app.workers.url_rewriter_para_response_helpers.get_all_stored_message import StoredMessageFetcher 
# from app.workers.url_rewriter_para_response_helpers.format_article_content import ArticleContentFormatter 
# from app.workers.url_rewriter_para_response_helpers.get_input_json_data import GetInputJson
# from app.workers.core.article_innovator_api_call.wordpress.fetch_category.fetch_category import FetchCategory
# from app.workers.core.article_innovator_api_call.wordpress.add_category.add_category import AddCategory
# from app.workers.core.article_innovator_api_call.fetch_supportive_prompt.fetch_supportive_prompt import FetchSupportivePrompt
# from app.workers.url_rewriter_para_response_helpers.create_wp_base_prompt import CreateWpBasePrompt
# from app.workers.url_rewriter_para_request_helpers.send_single_ai_request import SendSingleAiRequest
# from app.workers.url_rewriter_para_request_helpers.ai_message_request_store import AIMessageRequestStore
# from app.workers.url_rewriter_para_response_helpers.publish_article import PublishArticle

from app.workers.core.article_innovator_api_call.ai_message.ai_message import AIMessage
from app.workers.core.ai_rate_limiter.ai_rate_limiter import AIRateLimiter
from app.workers.url_rewriter_content_helpers.publish_article import PublishArticle
from app.workers.core.article_innovator_api_call.fetch_supportive_prompt.fetch_supportive_prompt import FetchSupportivePrompt
from app.workers.url_rewriter_content_helpers.ai_rate_limiter_request import AIRateLimiterService
from app.config.config import AI_RATE_LIMITER_URL

class UrlRewriterParallelWorker(BaseWorker):
    def __init__(self, channel, queue_name):
        # Set worker name first
        self.worker_name = 'url_rewriter_content_response_worker'
        
        # Call the parent class's __init__ after setting worker_name
        super().__init__(channel, queue_name)
        
        # Set up logger for url_rewriter_content_response_worker
        logger_setup = LoggerSetup()
        self.logger = logger_setup.setup_worker_logger(self.pid)
        self.logger = self.logger.bind(worker_name=self.worker_name, worker_type="url_rewriter_content_response_worker")
        print("url_rewriter_content_response_worker initialized and ready to process messages")
        # self.ai_message_response_store_service = AIMessageResponseStore()
        # self.get_all_stored_message_service = StoredMessageFetcher()
        # self.article_content_formatter_service = ArticleContentFormatter()
        # self.fetch_supportive_prompt_service = FetchSupportivePrompt()
        
        # self.send_single_ai_request_service = SendSingleAiRequest()
        # self.ai_message_request_store_service = AIMessageRequestStore()
        
        # self.get_input_json_service = GetInputJson()
        # self.fetch_category_service = FetchCategory()
        # self.add_category_service = AddCategory()
        # self.create_wp_base_prompt_service = CreateWpBasePrompt()
        self.publish_article_service = PublishArticle()
        self.fetch_supportive_prompt_service = FetchSupportivePrompt()
        self.ai_rate_limiter_service = AIRateLimiterService()
        
        self.ai_message_service = AIMessage()
        


    def str_to_bool(value):
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.strip().lower() in ['true', '1', 'yes']
        return bool(value)
    
    
    def supportive_prompt_funcs(self, prompt_id, prompt_type, input_data, domain_slug_id, all_stored_message_data, workspace_slug_id):
        """
        Handles supportive prompt logic (fetch, prepare prompt, send AI request).
        `prompt_type` can be: 'category', 'tag', 'author', etc.
        """
        try:
            if not prompt_id:
                self.logger.warning(f"❗ No supportive prompt ID found for type: {prompt_type}")
                return

            supportive_prompt_data = self.fetch_supportive_prompt_service.fetch_supportive_prompt(
                supportive_prompts_slug_id=prompt_id,
                domain_slug_id=domain_slug_id
            )
            print(f"Supportive prompt data for {prompt_type}: {supportive_prompt_data}")

            wp_base_prompt = self.ai_rate_limiter_service.create_single_wp_ai_request(
                input_data, supportive_prompt_data, all_stored_message_data, prompt_type
            )

            send_ai_result = self.ai_rate_limiter_service.send_ai_request(
                wp_base_prompt, workspace_slug_id
            )
            print(f"AI request sent for {prompt_type}: {send_ai_result}")

        except Exception as e:
            self.logger.error({
                "status": "error",
                "step": f"supportive_prompt_funcs - {prompt_type}",
                "message": str(e)
            })
            
            
        
            
    def process_message(self, ch, method, properties, body):
        try:
            data = json.loads(body)
            print(f"Processing message: {data}")

            message = data.get("message", {})
            all_stored_message_data = None
            formatted_article_content_data = None
            category_supportive_prompt_data = {}
            get_input_json_data = None
            wp_category_base_prompt = None
            article_message_count = None
            article_message_total_count = None
            article_id = None
            message_field_type = None

            # Generated category prompt variables
            generated_category_supportive_prompt_data = {}
            wp_category_generat_base_prompt = None


            # selection tag prompt variables
            tag_supportive_prompt_data = {}  # ← added
            wp_tag_base_prompt = None        # ← added

            # Generated tag prompt variables
            generated_tag_supportive_prompt_data = {}   # ← Added
            wp_tag_generat_base_prompt = None           # ← Added


            # Author prompt variables
            author_supportive_prompt_data = {}   # ← NEW
            wp_author_base_prompt = None         # ← NEW


            # Generated author prompt variables
            generated_author_supportive_prompt_data = {}   # ← NEW
            wp_author_generat_base_prompt = None           # ← NEW

            final_all_stored_message_data = None
            
            
            # message_retry_count = data.get("message_retry_count", 0)
            message_retry_count = 3


            # Step 1: Store AI message response
            try:
                stored_message_data = self.ai_message_service.store_ai_message_response(data, message_retry_count)
                # print(stored_message_data, '----------------------stored_message_data----------------------')
            except Exception as e:
                self.logger.error({"status": "error", "step": "store_ai_message_response", "message": str(e)})
                return {"status": "error", "step": "url_rewriter_content_response_worker in store_ai_message_response", "message": str(e)}


            # Step 3: Get stored message data
            try:
                if (
                    stored_message_data and
                    stored_message_data.get("status_code") == 200 and
                    stored_message_data.get("data", {}).get("success") is True
                ):
                    message_data = stored_message_data.get("data", {}).get("data", {})
                    article_message_count = message_data.get("article_message_count")
                    article_message_total_count = message_data.get("article_message_total_count")
                    article_id = message_data.get("article_id")
                    message_field_type = message_data.get("message_field_type")
                    ai_response = message_data.get("ai_response")
                    
            except Exception as e:
                print({"status": "error", "step": "stored_message_data not found", "message": str(e)})
                return {"status": "error", "step": "url_rewriter_content_response_worker in stored_message_data not found", "message": str(e)}


            print(article_message_total_count,'article_message_total_count')
            print(article_message_count,'article_message_count')



            try:
                get_input_json_data = self.ai_message_service.get_input_json_data_to_article_innovator(data)
                # print(get_input_json_data, '----------------------get_input_json_data----------------------')
            except Exception as e:
                self.logger.error({"status": "error", "step": "get_input_json_data", "message": str(e)})
                return {"status": "error", "step": "url_rewriter_content_response_worker in get_input_json_data", "message": str(e)}


            input_data = get_input_json_data.get("data", [])[0].get("input_json_data", {}).get("message", {})
            ai_flags = input_data.get("ai_content_flags", {})
            support_ids = input_data.get("prompt", {}).get("supportive_prompt_json_data", {})
            domain_slug_id = input_data.get("domain", {}).get("slug_id", {})
            workspace_slug_id = input_data.get("workspace", {}).get("slug_id", {})


            # # ✅ Only proceed if both are set and equal
            if (
                article_message_count is not None and
                article_message_total_count is not None and
                article_message_count == article_message_total_count and
                message_field_type == "content_message"
            ):
                
                
                print('************************ this is 20 == 20 ******************************')
                print('✔️ Article message count matches total count.')

                try:
                    all_stored_message_data = self.ai_message_service.get_all_stored_content_message(
                        article_id, message_field_type)
                except Exception as e:
                    self.logger.error({"status": "error", "step": "get_all_stored_content_message", "message": str(e)})
                    return {"status": "error", "step": "url_rewriter_content_response_worker in get_all_stored_content_message", "message": str(e)}



                # permissions = {
                #     'supportive_prompt_wp_categories_selected_by_ai_id': 'category',
                #     'supportive_prompt_wp_tags_selected_by_ai_id': 'tag',
                #     'supportive_prompt_wp_authors_selected_by_ai_id': 'author',
                #     'supportive_prompt_wp_keys_selected_by_ai_id': 'key',
                #     # Add more if needed
                # }

                # for support_id_key, prompt_type in permissions.items():
                #     prompt_id = support_ids.get(support_id_key)
                #     if prompt_id:
                #         self.supportive_prompt_funcs(
                #             prompt_id=prompt_id,
                #             prompt_type=prompt_type,
                #             input_data=input_data,
                #             domain_slug_id=domain_slug_id,
                #             all_stored_message_data=all_stored_message_data,
                #             workspace_slug_id=workspace_slug_id
                #         )



                permissions = {
                    'supportive_prompt_wp_categories_selected_by_ai_id': 'category',
                    'supportive_prompt_wp_categories_generated_by_ai_id': 'category',
                    'supportive_prompt_wp_tags_selected_by_ai_id': 'tag',
                    'supportive_prompt_wp_tags_generated_by_ai_id': 'tag',
                    'supportive_prompt_wp_authors_selected_by_ai_id': 'author',
                    'supportive_prompt_wp_authors_generated_by_ai_id': 'author',
                }

                for support_id_key, prompt_type in permissions.items():
                    prompt_id = support_ids.get(support_id_key)
                    
                    # Convert key like 'supportive_prompt_wp_categories_generated_by_ai_id' 
                    # to flag like 'is_wp_categories_generated_by_ai'
                    ai_flag = support_id_key.replace("supportive_prompt_", "").replace("_id", "")
                    ai_flag = f"is_{ai_flag}"

                    if ai_flags.get(ai_flag, False) and prompt_id:
                        self.supportive_prompt_funcs(
                            prompt_id=prompt_id,
                            prompt_type=prompt_type,
                            input_data=input_data,
                            domain_slug_id=domain_slug_id,
                            all_stored_message_data=all_stored_message_data,
                            workspace_slug_id=workspace_slug_id
                        )




                # if ai_flags.get("is_wp_categories_selected_by_ai", False):
                #     supportive_prompt_data = {}     
                #     create_single_ai_request_data = None   
                #     ai_response_json = None   
                #     try:
                #         # Step 4: get supportive_prompt data from Article Innovator                    
                #         category_id = support_ids.get("supportive_prompt_wp_categories_selected_by_ai_id")
                #         supportive_prompt_data = self.fetch_supportive_prompt_service.fetch_supportive_prompt(supportive_prompts_slug_id=category_id,domain_slug_id=domain_slug_id)
                #         print(supportive_prompt_data, '----------------------supportive_prompt_data----------------------')
                #     except Exception as e:
                #         print({"status": "error", "step": "fetch_supportive_prompt", "message": str(e)})
                #         # return {"status": "error", "step": "fetch_supportive_prompt", "message": str(e)}


                #     try:
                #         wp_category_base_prompt = self.ai_rate_limiter_service.create_single_wp_ai_request(input_data, supportive_prompt_data, all_stored_message_data, 'category')
                #         print(wp_category_base_prompt, '----------------------wp_category_base_prompt----------------------')
                #     except Exception as e:
                #         print({"status": "error", "step": "create_wp_base_prompt", "message": str(e)})


                #     try:
                #         send_single_ai_request_data = self.ai_rate_limiter_service.send_ai_request(wp_category_base_prompt, workspace_slug_id)
                #         print(send_single_ai_request_data, '----------------------send_single_ai_request_data----------------------')
                #     except Exception as e:
                #         print({"status": "error", "step": "store_or_send_prompt", "message": str(e)})
                        
                        
                        
                # if ai_flags.get("is_wp_categories_generated_by_ai", False):
                #     supportive_prompt_data = {}     
                #     create_single_ai_request_data = None   
                #     ai_response_json = None   
                #     try:
                #         # Step 4: get supportive_prompt data from Article Innovator                    
                #         category_id = support_ids.get("supportive_prompt_wp_categories_generated_by_ai_id")
                #         supportive_prompt_data = self.fetch_supportive_prompt_service.fetch_supportive_prompt(supportive_prompts_slug_id=category_id,domain_slug_id=domain_slug_id)
                #         print(supportive_prompt_data, '----------------------supportive_prompt_data----------------------')
                #     except Exception as e:
                #         print({"status": "error", "step": "fetch_supportive_prompt", "message": str(e)})
                #         # return {"status": "error", "step": "fetch_supportive_prompt", "message": str(e)}


                #     try:
                #         wp_category_base_prompt = self.ai_rate_limiter_service.create_single_wp_ai_request(input_data, supportive_prompt_data, all_stored_message_data, 'category')
                #         print(wp_category_base_prompt, '----------------------wp_category_base_prompt----------------------')
                #     except Exception as e:
                #         print({"status": "error", "step": "create_wp_base_prompt", "message": str(e)})


                #     try:
                #         send_single_ai_request_data = self.ai_rate_limiter_service.send_ai_request(wp_category_base_prompt, workspace_slug_id)
                #         print(send_single_ai_request_data, '----------------------send_single_ai_request_data----------------------')
                #     except Exception as e:
                #         print({"status": "error", "step": "store_or_send_prompt", "message": str(e)})
    

            all_stored_message_data = None
            try:
                all_stored_message_data = self.ai_message_service.get_all_stored_message(article_id)
            except Exception as e:
                self.logger.error({"status": "error", "step": "all_stored_message_data", "message": str(e)})
                return {"status": "error", "step": "url_rewriter_content_response_worker in all_stored_message_data", "message": str(e)}



            print(all_stored_message_data, '----------------------all_stored_message_data----------------------')

            if all_stored_message_data and all_stored_message_data.get("all_success"):
                print("----------------------All messages are successful!----------------------")



            # if message_field_type != "content_message" and message_field_type != "primary_keyword":
            # if (any(ai_flags.values()) and message_field_type not in ("content_message", "primary_keyword")):

                all_stored_wp_message_data = None
                
                try:
                    all_stored_wp_message_data = self.ai_message_service.get_all_stored_wp_message(article_id)
                    print(all_stored_wp_message_data, '----------------------all_stored_wp_message_data----------------------')
                except Exception as e:
                    self.logger.error({"status": "error", "step": "get_all_stored_wp_message", "message": str(e)})
                    return {"status": "error", "step": "url_rewriter_content_response_worker in get_all_stored_wp_message", "message": str(e)}




                # if all_stored_wp_message_data['total_messages'] == all_stored_wp_message_data['total_successful_messages']:
                
                # print("----------------------All messages are successful!----------------------")
                all_stored_content_message_data= None

                try:
                    all_stored_content_message_data = self.ai_message_service.get_all_stored_content_message(article_id, 'content_message')
                except Exception as e:
                    self.logger.error({"status": "error", "step": "get_all_stored_content_message", "message": str(e)})
                    return {"status": "error", "step": "url_rewriter_content_response_worker in get_all_stored_content_message", "message": str(e)}




                try:
                    publish_article_datas = self.publish_article_service.publish_article(all_stored_content_message_data, all_stored_wp_message_data, article_id)
                    print(publish_article_datas, '----------------------publish_article_service----------------------')
                except Exception as e:
                    self.logger.error({"status": "error", "step": "publish_article", "message": str(e)})
                    return {"status": "error", "step": "url_rewriter_content_response_worker in publish_article", "message": str(e)}








            #     try:
            #         final_all_stored_message_data = self.get_all_stored_message_service.get_all_stored_message(
            #             article_id, 'content_message')
            #     except Exception as e:
            #         print({"status": "error", "step": "get_all_stored_message", "message": str(e)})


            #     if final_all_stored_message_data:
            #         try:
            #             final_formatted_article_content_data = self.article_content_formatter_service.format_article_content(
            #                 final_all_stored_message_data)
            #             print(final_formatted_article_content_data, '----------------------final_formatted_article_content_data----------------------')
            #         except Exception as e:
            #             print({"status": "error", "step": "format_article_content", "message": str(e)})
            #     # print(all_stored_wp_message_data['total_messages'], 'all_stored_wp_message_data')
            #     # print(all_stored_wp_message_data['total_successful_messages'],'total_successful_messages')

            #     # if all_stored_wp_message_data['total_messages'] == all_stored_wp_message_data['total_successful_messages']:
            #     try:
            #         publish_article_datas = self.publish_article_service.publish_article(
            #             final_formatted_article_content_data, all_stored_wp_message_data, article_id)
            #         print(publish_article_datas, '----------------------publish_article_service----------------------')
            #     except Exception as e:
            #         print({"status": "error", "step": "format_article_content", "message": str(e)})
        
            
                    
            
            
            
            # add if all message are success so call articel update

            # print(f"✔️ url_rewriter_content_response_worker processing complete.")
            print(f"xxxxxxxxxxxxxxxxxxxxxxxxx url_rewriter_content_response_worker xxxxxxxxxxxxxxxxxxxxxxxxx")

            ch.basic_ack(delivery_tag=method.delivery_tag)
            return True

        except Exception as e:
            self.logger.error(f"❌ Message processing failed for data: {body}. Error: {str(e)}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
            return False
