from .base import BaseWorker
from app.config.logger import LoggerSetup
import os
import json
from app.workers.url_rewriter_para_response_helpers.ai_message_response_store import AIMessageResponseStore 
from app.workers.url_rewriter_para_response_helpers.get_all_stored_message import StoredMessageFetcher 
from app.workers.url_rewriter_para_response_helpers.format_article_content import ArticleContentFormatter 
from app.workers.url_rewriter_para_response_helpers.get_input_json_data import GetInputJson
# from app.workers.core.article_innovator_api_call.wordpress.fetch_category.fetch_category import FetchCategory
from app.workers.core.article_innovator_api_call.wordpress.add_category.add_category import AddCategory
from app.workers.core.article_innovator_api_call.fetch_supportive_prompt.fetch_supportive_prompt import FetchSupportivePrompt
from app.workers.url_rewriter_para_response_helpers.create_wp_base_prompt import CreateWpBasePrompt
from app.workers.url_rewriter_para_request_helpers.send_single_ai_request import SendSingleAiRequest
from app.workers.url_rewriter_para_request_helpers.ai_message_request_store import AIMessageRequestStore
from app.workers.url_rewriter_para_response_helpers.publish_article import PublishArticle


class UrlRewriterParallelWorker(BaseWorker):
    def __init__(self, channel, queue_name):
        # Set worker name first
        self.worker_name = 'url_rewriter_para_response_worker'
        
        # Call the parent class's __init__ after setting worker_name
        super().__init__(channel, queue_name)
        
        # Set up logger for url_rewriter_para_response_worker
        logger_setup = LoggerSetup()
        self.logger = logger_setup.setup_worker_logger(self.pid)
        self.logger = self.logger.bind(worker_name=self.worker_name, worker_type="url_rewriter_para_response_worker")
        self.logger.info("url_rewriter_para_response_worker initialized and ready to process messages")
        self.ai_message_response_store_service = AIMessageResponseStore()
        self.get_all_stored_message_service = StoredMessageFetcher()
        self.article_content_formatter_service = ArticleContentFormatter()
        self.fetch_supportive_prompt_service = FetchSupportivePrompt()
        
        self.send_single_ai_request_service = SendSingleAiRequest()
        self.ai_message_request_store_service = AIMessageRequestStore()
        
        self.get_input_json_service = GetInputJson()
        # self.fetch_category_service = FetchCategory()
        self.add_category_service = AddCategory()
        self.create_wp_base_prompt_service = CreateWpBasePrompt()
        self.publish_article_service = PublishArticle()
        


    def str_to_bool(value):
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.strip().lower() in ['true', '1', 'yes']
        return bool(value)
    
            
    def process_message(self, ch, method, properties, body):
        try:
            data = json.loads(body)
            self.logger.info(f"Processing message: {data}")

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


            # Step 2: Store AI message response
            try:
                stored_message_data = self.ai_message_response_store_service.store_ai_message_response(data)
                # print(stored_message_data, '----------------------stored_message_data----------------------')
            except Exception as e:
                print({"status": "error", "step": "store_ai_message_response", "message": str(e)})

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
            except Exception as e:
                print({"status": "error", "step": "stored_message_data not found", "message": str(e)})

            print(article_message_total_count,'article_message_total_count')
            print(article_message_count,'article_message_count')


            # ✅ Only proceed if both are set and equal
            if (
                article_message_count is not None and
                article_message_total_count is not None and
                article_message_count == article_message_total_count and
                message_field_type == "content_message"
            ):
                
                
                print('************************ this is 20 == 20 ******************************')
                print('✔️ Article message count matches total count.')

                try:
                    all_stored_message_data = self.get_all_stored_message_service.get_all_stored_message(
                        article_id, message_field_type)
                except Exception as e:
                    print({"status": "error", "step": "get_all_stored_message", "message": str(e)})

                if all_stored_message_data:
                    try:
                        formatted_article_content_data = self.article_content_formatter_service.format_article_content(
                            all_stored_message_data)
                        # print(formatted_article_content_data, '----------------------formatted_article_content_data----------------------')
                    except Exception as e:
                        print({"status": "error", "step": "format_article_content", "message": str(e)})

                if formatted_article_content_data:
                    try:
                        # get_input_json_data = self.get_input_json_service.get_input_json_data(data)
                        get_input_json_data = self.get_input_json_service.get_input_json_data_to_article_innovator(data)
                        # print(get_input_json_data, '----------------------get_input_json_data----------------------')
                    except Exception as e:
                        print({"status": "error", "step": "get_input_json_data", "message": str(e)})

                    input_data = get_input_json_data.get("data", [])[0].get("input_json_data", {}).get("message", {})
                    ai_flags = input_data.get("ai_content_flags", {})
                    support_ids = input_data.get("prompt", {}).get("supportive_prompt_json_data", {})
                    domain_slug_id = input_data.get("domain", {}).get("slug_id", {})
                    workspace_slug_id = input_data.get("workspace", {}).get("slug_id", {})


                    # ✅ Process WP category (Selected by AI)
                    if ai_flags.get("is_wp_categories_selected_by_ai", False):
                        try:
                            category_id = support_ids.get("supportive_prompt_wp_categories_selected_by_ai_id")
                            category_max_retries = 3

                            for attempt in range(1, category_max_retries + 1):
                                try:
                                    category_supportive_prompt_data = self.fetch_supportive_prompt_service.fetch_supportive_prompt(
                                        supportive_prompts_slug_id=category_id,
                                        domain_slug_id=domain_slug_id
                                    )
                                    # print(category_supportive_prompt_data, '----------------------category_supportive_prompt_data----------------------')

                                    failed_prompts = [
                                        item for item in category_supportive_prompt_data.get('supportive_prompts', [])
                                        if not item.get('success')
                                    ]

                                    if not failed_prompts:
                                        break

                                    print(f"[Attempt {attempt}] Some prompts failed, retrying...")

                                except Exception as retry_exception:
                                    print(f"[Attempt {attempt}] Retry error: {retry_exception}")

                        except Exception as e:
                            print({"status": "error", "step": "fetch_wp_categories", "message": str(e)})

                        try:
                            wp_category_base_prompt = self.create_wp_base_prompt_service.create_wp_base_prompt(
                                category_supportive_prompt_data,
                                formatted_article_content_data,
                                get_input_json_data,
                                'category'
                            )
                            # print(wp_category_base_prompt, '----------------------wp_category_base_prompt----------------------')
                        except Exception as e:
                            print({"status": "error", "step": "create_wp_base_prompt", "message": str(e)})

                        if wp_category_base_prompt is not None:
                            try:
                                # store_ai_message_request_data = self.ai_message_request_store_service.store_ai_message_request(
                                #     wp_category_base_prompt
                                # )
                                # print(store_ai_message_request_data, '----------------------store_ai_message_request_data----------------------')

                                send_single_ai_request_data = self.send_single_ai_request_service.send_single_ai_request(
                                    wp_category_base_prompt, workspace_slug_id
                                )
                                print(send_single_ai_request_data, '----------------------send_single_ai_request_data----------------------')
                                
                            except Exception as e:
                                print({"status": "error", "step": "store_or_send_prompt", "message": str(e)})


                    # ✅ Process WP Categories (Generated by AI)
                    if ai_flags.get("is_wp_categories_generated_by_ai", False):

                        try:
                            generated_category_id = support_ids.get("supportive_prompt_wp_categories_generated_by_ai_id")
                            generated_category_max_retries = 3

                            for attempt in range(1, generated_category_max_retries + 1):
                                try:
                                    generated_category_supportive_prompt_data = self.fetch_supportive_prompt_service.fetch_supportive_prompt(
                                        supportive_prompts_slug_id=generated_category_id,
                                        domain_slug_id=domain_slug_id
                                    )

                                    failed_prompts = [
                                        item for item in generated_category_supportive_prompt_data.get('supportive_prompts', [])
                                        if not item.get('success')
                                    ]

                                    if not failed_prompts:
                                        break

                                    print(f"[Attempt {attempt}] Some prompts failed, retrying...")

                                except Exception as retry_exception:
                                    print(f"[Attempt {attempt}] Retry error: {retry_exception}")

                        except Exception as e:
                            print({"status": "error", "step": "fetch_wp_categories_generated", "message": str(e)})

                        try:
                            wp_category_generat_base_prompt = self.create_wp_base_prompt_service.create_wp_base_prompt(
                                generated_category_supportive_prompt_data,
                                formatted_article_content_data,
                                get_input_json_data,
                                'category'
                            )
                        except Exception as e:
                            print({"status": "error", "step": "create_wp_base_prompt_generated", "message": str(e)})

                        if wp_category_generat_base_prompt is not None:
                            try:
                                # store_ai_message_request_data = self.ai_message_request_store_service.store_ai_message_request(
                                #     wp_category_generat_base_prompt
                                # )
                                # print(store_ai_message_request_data, '----------------------store_ai_message_request_data----------------------')

                                send_single_ai_request_data = self.send_single_ai_request_service.send_single_ai_request(
                                    wp_category_generat_base_prompt, workspace_slug_id
                                )
                                # print(send_single_ai_request_data, '----------------------send_single_ai_request_data----------------------')

                            except Exception as e:
                                print({"status": "error", "step": "store_or_send_prompt_generated", "message": str(e)})



                    # ✅ Process WP Tags (Selected by AI)
                    if ai_flags.get("is_wp_tags_selected_by_ai", False):
                        try:
                            tag_id = support_ids.get("supportive_prompt_wp_tags_selected_by_ai_id")
                            tag_max_retries = 3

                            for attempt in range(1, tag_max_retries + 1):
                                try:
                                    tag_supportive_prompt_data = self.fetch_supportive_prompt_service.fetch_supportive_prompt(
                                        supportive_prompts_slug_id=tag_id,
                                        domain_slug_id=domain_slug_id
                                    )

                                    failed_prompts = [
                                        item for item in tag_supportive_prompt_data.get('supportive_prompts', [])
                                        if not item.get('success')
                                    ]

                                    if not failed_prompts:
                                        break

                                    print(f"[Attempt {attempt}] Some tag prompts failed, retrying...")

                                except Exception as retry_exception:
                                    print(f"[Attempt {attempt}] Retry error (tags): {retry_exception}")

                        except Exception as e:
                            print({"status": "error", "step": "fetch_wp_tags", "message": str(e)})

                        try:
                            wp_tag_base_prompt = self.create_wp_base_prompt_service.create_wp_base_prompt(
                                tag_supportive_prompt_data,
                                formatted_article_content_data,
                                get_input_json_data,
                                'tag'
                            )
                        except Exception as e:
                            print({"status": "error", "step": "create_wp_tag_base_prompt", "message": str(e)})

                        if wp_tag_base_prompt is not None:
                            try:
                                # store_ai_message_request_data = self.ai_message_request_store_service.store_ai_message_request(
                                #     wp_tag_base_prompt
                                # )
                                # print(store_ai_message_request_data, '----------------------store_ai_message_request_data (tags)----------------------')

                                send_single_ai_request_data = self.send_single_ai_request_service.send_single_ai_request(
                                    wp_tag_base_prompt, workspace_slug_id
                                )
                                print(send_single_ai_request_data, '----------------------send_single_ai_request_data (tags)----------------------')

                            except Exception as e:
                                print({"status": "error", "step": "store_or_send_prompt_tag", "message": str(e)})





                    # ✅ Process WP tags (Generated by AI)
                    if ai_flags.get("is_wp_tags_generated_by_ai", False):

                        try:
                            generated_tag_id = support_ids.get("supportive_prompt_wp_tags_generated_by_ai_id")
                            generated_tag_max_retries = 3

                            for attempt in range(1, generated_tag_max_retries + 1):
                                try:
                                    generated_tag_supportive_prompt_data = self.fetch_supportive_prompt_service.fetch_supportive_prompt(
                                        supportive_prompts_slug_id=generated_tag_id,
                                        domain_slug_id=domain_slug_id
                                    )

                                    failed_prompts = [
                                        item for item in generated_tag_supportive_prompt_data.get('supportive_prompts', [])
                                        if not item.get('success')
                                    ]

                                    if not failed_prompts:
                                        break

                                    print(f"[Attempt {attempt}] Some prompts failed, retrying...")

                                except Exception as retry_exception:
                                    print(f"[Attempt {attempt}] Retry error (generated tags): {retry_exception}")

                        except Exception as e:
                            print({"status": "error", "step": "fetch_wp_tags_generated", "message": str(e)})

                        try:
                            wp_tag_generat_base_prompt = self.create_wp_base_prompt_service.create_wp_base_prompt(
                                generated_tag_supportive_prompt_data,
                                formatted_article_content_data,
                                get_input_json_data,
                                'tag'
                            )
                        except Exception as e:
                            print({"status": "error", "step": "create_wp_tag_base_prompt_generated", "message": str(e)})

                        if wp_tag_generat_base_prompt is not None:
                            try:
                                # store_ai_message_request_data = self.ai_message_request_store_service.store_ai_message_request(
                                #     wp_tag_generat_base_prompt
                                # )
                                # print(store_ai_message_request_data, '----------------------store_ai_message_request_data (generated tags)----------------------')

                                send_single_ai_request_data = self.send_single_ai_request_service.send_single_ai_request(
                                    wp_tag_generat_base_prompt, workspace_slug_id
                                )
                                print(send_single_ai_request_data, '----------------------send_single_ai_request_data (generated tags)----------------------')

                            except Exception as e:
                                print({"status": "error", "step": "store_or_send_prompt_generated_tags", "message": str(e)})



                    # ✅ Process WP authors (Selected by AI)
                    if ai_flags.get("is_wp_authors_selected_by_ai", False):
                        try:
                            author_id = support_ids.get("supportive_prompt_wp_authors_selected_by_ai_id")
                            author_max_retries = 3

                            for attempt in range(1, author_max_retries + 1):
                                try:
                                    author_supportive_prompt_data = self.fetch_supportive_prompt_service.fetch_supportive_prompt(
                                        supportive_prompts_slug_id=author_id,
                                        domain_slug_id=domain_slug_id
                                    )

                                    failed_prompts = [
                                        item for item in author_supportive_prompt_data.get('supportive_prompts', [])
                                        if not item.get('success')
                                    ]

                                    if not failed_prompts:
                                        break

                                    print(f"[Attempt {attempt}] Some author prompts failed, retrying...")

                                except Exception as retry_exception:
                                    print(f"[Attempt {attempt}] Retry error (authors): {retry_exception}")

                        except Exception as e:
                            print({"status": "error", "step": "fetch_wp_authors", "message": str(e)})

                        try:
                            wp_author_base_prompt = self.create_wp_base_prompt_service.create_wp_base_prompt(
                                author_supportive_prompt_data,
                                formatted_article_content_data,
                                get_input_json_data,
                                'author'
                            )
                        except Exception as e:
                            print({"status": "error", "step": "create_wp_author_base_prompt", "message": str(e)})

                        if wp_author_base_prompt is not None:
                            try:
                                # store_ai_message_request_data = self.ai_message_request_store_service.store_ai_message_request(
                                #     wp_author_base_prompt
                                # )
                                # print(store_ai_message_request_data, '----------------------store_ai_message_request_data (authors)----------------------')

                                send_single_ai_request_data = self.send_single_ai_request_service.send_single_ai_request(
                                    wp_author_base_prompt, workspace_slug_id
                                )
                                print(send_single_ai_request_data, '----------------------send_single_ai_request_data (authors)----------------------')

                            except Exception as e:
                                print({"status": "error", "step": "store_or_send_prompt_author", "message": str(e)})




                    # ✅ Process WP authors (Generated by AI)
                    if ai_flags.get("is_wp_authors_generated_by_ai", False):

                        try:
                            generated_author_id = support_ids.get("supportive_prompt_wp_authors_generated_by_ai_id")
                            generated_author_max_retries = 3

                            for attempt in range(1, generated_author_max_retries + 1):
                                try:
                                    generated_author_supportive_prompt_data = self.fetch_supportive_prompt_service.fetch_supportive_prompt(
                                        supportive_prompts_slug_id=generated_author_id,
                                        domain_slug_id=domain_slug_id
                                    )

                                    failed_prompts = [
                                        item for item in generated_author_supportive_prompt_data.get('supportive_prompts', [])
                                        if not item.get('success')
                                    ]

                                    if not failed_prompts:
                                        break

                                    print(f"[Attempt {attempt}] Some prompts failed, retrying...")

                                except Exception as retry_exception:
                                    print(f"[Attempt {attempt}] Retry error (generated authors): {retry_exception}")

                        except Exception as e:
                            print({"status": "error", "step": "fetch_wp_authors_generated", "message": str(e)})

                        try:
                            wp_author_generat_base_prompt = self.create_wp_base_prompt_service.create_wp_base_prompt(
                                generated_author_supportive_prompt_data,
                                formatted_article_content_data,
                                get_input_json_data,
                                'author'
                            )
                        except Exception as e:
                            print({"status": "error", "step": "create_wp_author_base_prompt_generated", "message": str(e)})

                        if wp_author_generat_base_prompt is not None:
                            try:
                                # store_ai_message_request_data = self.ai_message_request_store_service.store_ai_message_request(
                                #     wp_author_generat_base_prompt
                                # )
                                # print(store_ai_message_request_data, '----------------------store_ai_message_request_data (generated authors)----------------------')

                                send_single_ai_request_data = self.send_single_ai_request_service.send_single_ai_request(
                                    wp_author_generat_base_prompt, workspace_slug_id
                                )
                                print(send_single_ai_request_data, '----------------------send_single_ai_request_data (generated authors)----------------------')

                            except Exception as e:
                                print({"status": "error", "step": "store_or_send_prompt_generated_authors", "message": str(e)})



            if message_field_type != "content_message" and message_field_type != "primary_keyword_generated_by_ai":
                # get all message using artical id [content_message, primary_keyword_generated_by_ai ] ---->> aa bane nay leva nu 
                all_stored_wp_message_data = None
                try:
                    all_stored_wp_message_data = self.get_all_stored_message_service.get_all_stored_wp_message(
                        article_id)
                    print(all_stored_wp_message_data, '----------------------all_stored_wp_message_data----------------------')

                except Exception as e:
                    print({"status": "error", "step": "get_all_stored_wp_message", "message": str(e)})


                try:
                    final_all_stored_message_data = self.get_all_stored_message_service.get_all_stored_message(
                        article_id, 'content_message')
                except Exception as e:
                    print({"status": "error", "step": "get_all_stored_message", "message": str(e)})


                if final_all_stored_message_data:
                    try:
                        final_formatted_article_content_data = self.article_content_formatter_service.format_article_content(
                            final_all_stored_message_data)
                        print(final_formatted_article_content_data, '----------------------final_formatted_article_content_data----------------------')
                    except Exception as e:
                        print({"status": "error", "step": "format_article_content", "message": str(e)})
                # print(all_stored_wp_message_data['total_messages'], 'all_stored_wp_message_data')
                # print(all_stored_wp_message_data['total_successful_messages'],'total_successful_messages')

                # if all_stored_wp_message_data['total_messages'] == all_stored_wp_message_data['total_successful_messages']:
                try:
                    publish_article_datas = self.publish_article_service.publish_article(
                        final_formatted_article_content_data, all_stored_wp_message_data, article_id)
                    print(publish_article_datas, '----------------------publish_article_service----------------------')
                except Exception as e:
                    print({"status": "error", "step": "format_article_content", "message": str(e)})
        
            
                    
            
            
            
            # add if all message are success so call articel update

            # self.logger.info(f"✔️ url_rewriter_para_response_worker processing complete.")
            self.logger.info(f"xxxxxxxxxxxxxxxxxxxxxxxxx url_rewriter_para_response_worker xxxxxxxxxxxxxxxxxxxxxxxxx")

            ch.basic_ack(delivery_tag=method.delivery_tag)
            return True

        except Exception as e:
            self.logger.error(f"❌ Message processing failed for data: {body}. Error: {str(e)}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
            return False
