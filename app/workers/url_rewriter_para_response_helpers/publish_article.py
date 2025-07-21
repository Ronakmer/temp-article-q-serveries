import requests
import os
import json
import time
import logging
from app.workers.core.article_innovator_api_call.api_client.api_client import APIClient
# from app.workers.core.article_innovator_api_call.wordpress.add_category.add_category import AddCategory
from typing import Dict, List, Any


class PublishArticle:
    def __init__(self):
        self.headers = {
            "Content-Type": "application/json"
        }
        
        self.api_client = APIClient()
        # self.add_category_service = AddCategory()
        

    # def publish_article(self, final_formatted_article_content_data, all_stored_wp_message_data, temp_article_id):
    #     try:
            
    #         all_stored_wp_message_datas = all_stored_wp_message_data["data"]
            
    #         generated_article_title = final_formatted_article_content_data['generated_title']
    #         generated_article_content= final_formatted_article_content_data['generated_content']

    #         wp_excerpt = generated_article_title    
    #         wp_slug = generated_article_title    

    #         wp_datas = None
    #         try:
    #             wp_datas = self.get_slug_ids_by_type(all_stored_wp_message_datas)
    #             # print(wp_datas, '----------------------wp_datas----------------------')
                
    #         except Exception as e:
    #             print({"status": "error", "step": "get_slug_ids_by_type", "message": str(e)})
                
    #         author_slug_ids = wp_datas.get('author', [])
    #         tag_slug_ids = wp_datas.get('tag', [])
    #         category_slug_ids = wp_datas.get('category', [])  # support both keys


                
    #         try:
    #             from app.workers.url_rewriter_para_response_helpers.get_input_json_data import GetInputJson
    #             self.get_input_json_service = GetInputJson()
                                
                                        
    #             # get_input_json_datas = self.get_input_json_service.get_input_json_data_to_article_innovator(data)
    #             get_input_json_datas = self.get_input_json_service.get_input_json_data_for_wp(temp_article_id)
    #             # print(get_input_json_datas, '----------------------get_input_json_datas----------------------')
    #         except Exception as e:
    #             print({"status": "error", "step": "get_input_json_datas", "message": str(e)})


    #         # input_data = get_input_json_datas.get("data", [])[0].get("input_json_data", {}).get("message", {})
    #         data_list = get_input_json_datas.get("data", [])

    #         if not data_list:
    #             return {"success": False, "error": "No input_json_data found for article"}

    #         input_data = data_list[0].get("input_json_data", {}).get("message", {})

    #         domain_slug_id = input_data.get("domain", {}).get("slug_id", {})
    #         workspace_slug_id = input_data.get("workspace", {}).get("slug_id", {})
    #         article_type_slug_id = input_data.get("prompt", {}).get("article_type", {}).get("slug_id", "")
    #         article_status = input_data.get("article_status")
    #         wp_status = input_data.get("wp_status")
    #         article_slug_id = input_data.get("article_slug_id")
            
    #         # Prepare request payload (omit ai_request)
    #         request_data = {
    #             "article_slug_id":article_slug_id,
    #             "article_type_slug_id": article_type_slug_id,
    #             "author_slug_id": author_slug_ids,
    #             "domain_slug_id": domain_slug_id,
    #             "category_slug_id": category_slug_ids,
    #             "tag_slug_id": tag_slug_ids,
    #             "workspace_slug_id": workspace_slug_id,
    #             "wp_title": generated_article_title,
    #             "wp_content": generated_article_content,
    #             "article_status": article_status,
    #             "wp_excerpt": wp_excerpt,
    #             "wp_status": wp_status,
    #             "wp_slug": wp_slug,
    #         }


    #         # Combine article_id and message_id as item_id
    #         request_item_id = f"{article_slug_id}"
            
            
    #         max_retries = 3
    #         for attempt in range(1, max_retries + 1):
    #             stored_message = self.api_client.crud(
    #                 'article',
    #                 'update',
    #                 data=request_data,
    #                 item_id=request_item_id 
    #             )
    #             print(stored_message, f'stored_message [debug] attempt {attempt}')

    #             if stored_message.get('status_code') == 200:
    #                 return stored_message
    #             else:
    #                 print(f"Attempt {attempt} failed with status_code {stored_message.get('status_code')}. Retrying...")

    #         # If we exit the loop, all attempts failed
    #         return {
    #             "success": False,
    #             "error": f"Failed to update after {max_retries} attempts",
    #             "last_response": stored_message,
    #         }

            

    #     except Exception as e:
    #         print(f"[store_ai_message] Exception: {e}")
    #         return {"success": False, "error": f"Unexpected error: {str(e)}"}





    def publish_article(self, final_formatted_article_content_data, all_stored_wp_message_data, temp_article_id):
        try:
            
            generated_article_title = final_formatted_article_content_data['generated_title']
            generated_article_content = final_formatted_article_content_data['generated_content']

            wp_excerpt = generated_article_title
            wp_slug = generated_article_title
            if all_stored_wp_message_data is not None and "data" in all_stored_wp_message_data:
                all_stored_wp_message_datas = all_stored_wp_message_data["data"]

                wp_datas = None
                try:
                    wp_datas = self.get_slug_ids_by_type(all_stored_wp_message_datas)
                except Exception as e:
                    print({"status": "error", "step": "get_slug_ids_by_type", "message": str(e)})

            try:
                from app.workers.url_rewriter_para_response_helpers.get_input_json_data import GetInputJson
                self.get_input_json_service = GetInputJson()

                get_input_json_datas = self.get_input_json_service.get_input_json_data_for_wp(temp_article_id)
            except Exception as e:
                print({"status": "error", "step": "get_input_json_datas", "message": str(e)})

            data_list = get_input_json_datas.get("data", [])
            if not data_list:
                return {"success": False, "error": "No input_json_data found for article"}

            input_data = data_list[0].get("input_json_data", {}).get("message", {})

            domain_slug_id = input_data.get("domain", {}).get("slug_id", {})
            workspace_slug_id = input_data.get("workspace", {}).get("slug_id", {})
            article_type_slug_id = input_data.get("prompt", {}).get("article_type", {}).get("slug_id", "")
            article_status = input_data.get("article_status")
            wp_status = input_data.get("wp_status")
            article_slug_id = input_data.get("article_slug_id")

            # # Default fallback values from AI response
            # default_author_slug_ids = wp_datas.get('author', []) if wp_datas else []
            # default_tag_slug_ids = wp_datas.get('tag', []) if wp_datas else []
            # default_category_slug_ids = wp_datas.get('category', []) if wp_datas else []

            # Input JSON values
            wp_author = input_data.get("wp_author")
            wp_category = input_data.get("wp_category")
            wp_tag = input_data.get("wp_tag")

            # Ensure all values are lists
            def ensure_list(value):
                if value is None:
                    return []
                return value if isinstance(value, list) else [value]

            # Use input if available, else fallback to AI-generated
            # author_slug_ids = ensure_list(wp_author) or default_author_slug_ids
            # author_slug_ids = ensure_list(wp_author)
            # if not author_slug_ids:
            #     author_slug_ids = ensure_list(default_author_slug_ids)

            # category_slug_ids = ensure_list(wp_category) or default_category_slug_ids
            # tag_slug_ids = ensure_list(wp_tag) or default_tag_slug_ids

            # Prepare request payload
            request_data = {
                "article_slug_id": article_slug_id,
                "article_type_slug_id": article_type_slug_id,
                # "author_slug_id": '',
                "domain_slug_id": domain_slug_id,
                # "category_slug_id": '',
                # "tag_slug_id": '',
                "workspace_slug_id": workspace_slug_id,
                "wp_title": generated_article_title,
                "wp_content": generated_article_content,
                "article_status": article_status,
                "wp_excerpt": wp_excerpt,
                "wp_status": wp_status,
                "wp_slug": wp_slug,
            }

            request_item_id = f"{article_slug_id}"
            max_retries = 3
            for attempt in range(1, max_retries + 1):
                stored_message = self.api_client.crud(
                    'article',
                    'update',
                    data=request_data,
                    item_id=request_item_id
                )
                print(stored_message, f'stored_message [debug] attempt {attempt}')

                if stored_message.get('status_code') == 200:
                    return stored_message
                else:
                    print(f"Attempt {attempt} failed with status_code {stored_message.get('status_code')}. Retrying...")

            return {
                "success": False,
                "error": f"Failed to update after {max_retries} attempts",
                "last_response": stored_message,
            }

        except Exception as e:
            print(f"[publish_article] Exception: {e}")
            return {"success": False, "error": f"Unexpected error: {str(e)}"}








    # def get_slug_ids_by_type(self, input_data):
    #     # Save original input
    #     with open('demo_json/raw_input.json', 'w', encoding='utf-8') as f:
    #         json.dump(input_data, f, ensure_ascii=False, indent=4)

    #     # Initialize result
    #     result = {'author': [], 'tag': [], 'cat': []}

    #     try:
    #         all_data = input_data.get('data', [])  # <-- Fix for input format

    #         for item in all_data:
    #             if item.get('ai_response_status') != 'success':
    #                 continue

    #             field = item.get('message_field_type')
    #             if field == 'category':
    #                 field = 'cat'  # Normalize to 'cat' key in result

    #             if field not in result:
    #                 continue

    #             try:
    #                 ai_response_str = item.get('ai_response', '{}')
    #                 ai_response = json.loads(ai_response_str)
    #                 processed_text = ai_response['result']['processed_text']

    #                 # Extract embedded JSON from processed_text
    #                 if '```json' in processed_text:
    #                     embedded_json_str = processed_text.split('```json')[1].split('```')[0].strip()
    #                     parsed_obj = json.loads(embedded_json_str)

    #                     # Parse based on field type
    #                     if field == 'author':
    #                         result['author'].append(parsed_obj['output'].get('slug_id'))
    #                     elif field == 'tag':
    #                         result['tag'].extend(tag.get('slug_id') for tag in parsed_obj if tag.get('slug_id'))
    #                     elif field == 'cat':
    #                         cat_value = parsed_obj.get('category')
    #                         if cat_value:
    #                             result['category'].append(cat_value)

    #             except Exception as e:
    #                 print(f"Error processing item ID {item.get('id')}: {e}")

    #     except Exception as e:
    #         return {'status': 'error', 'step': 'get_slug_ids_by_type', 'message': str(e)}

    #     # Save final result
    #     with open('demo_json/final_wp_data.json', 'w', encoding='utf-8') as f:
    #         json.dump(result, f, ensure_ascii=False, indent=4)

    #     return result

    
    
    
    def get_slug_ids_by_type(self, input_list):
        # Save original input
        with open('demo_json/raw_input.json', 'w', encoding='utf-8') as f:
            json.dump(input_list, f, ensure_ascii=False, indent=4)

        # Initialize result
        result = {'author': [], 'tag': [], 'category': []}

        try:
            for item in input_list:
                if item.get('ai_response_status') != 'success':
                    continue

                field = item.get('message_field_type')
                if field == 'category':
                    field = 'category'  # Normalize key

                if field not in result:
                    continue

                try:
                    ai_response_str = item.get('ai_response', '{}')
                    ai_response = json.loads(ai_response_str)
                    processed_text = ai_response['result']['processed_text']

                    # Extract embedded JSON from processed_text
                    if '```json' in processed_text:
                        embedded_json_str = processed_text.split('```json')[1].split('```')[0].strip()
                        parsed_obj = json.loads(embedded_json_str)

                        if field == 'author':
                            # Case: single author object
                            slug_id = parsed_obj.get("slug_id") or parsed_obj.get("output", {}).get("slug_id")
                            # if slug_id:
                            #     result['author'].append(slug_id)
                            if slug_id:
                                if isinstance(slug_id, list):
                                    result['author'].extend(slug_id)
                                else:
                                    result['author'].append(slug_id)

                        elif field == 'tag':
                            # Case: list of tag objects
                            for tag in parsed_obj:
                                if isinstance(tag, dict):
                                    slug_id = tag.get("slug_id")
                                    if slug_id:
                                        result['tag'].append(slug_id)
                        elif field == 'category':
                            # Case: single category object
                            slug_id = parsed_obj.get("slug_id")
                            if slug_id:
                                result['category'].append(slug_id)

                except Exception as e:
                    print(f"Error processing item ID {item.get('id')}: {e}")

        except Exception as e:
            return {'status': 'error', 'step': 'get_slug_ids_by_type', 'message': str(e)}

        # Save final result
        with open('demo_json/final_wp_data.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=4)

        return result
