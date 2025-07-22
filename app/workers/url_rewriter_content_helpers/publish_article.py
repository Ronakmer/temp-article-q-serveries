import requests
import os
import json
import time
import logging
from app.workers.core.article_innovator_api_call.api_client.api_client import APIClient
# from app.workers.core.article_innovator_api_call.wordpress.add_category.add_category import AddCategory
from typing import Dict, List, Any
import re


class PublishArticle:
    def __init__(self):
        self.headers = {
            "Content-Type": "application/json"
        }
        
        self.api_client = APIClient()
        # self.add_category_service = AddCategory()

    # def publish_article(self, all_stored_content_message_data, all_stored_wp_message_data, temp_article_id):
    #     try:
            
    #         get_input_json_datas = None
            
    #         print(type(all_stored_content_message_data), '555666666633')

    #         if not all_stored_content_message_data:
    #             return {'success': False, 'error': 'Message data is empty'}

    #         # Normalize input to list
    #         if isinstance(all_stored_content_message_data, dict):
    #             all_stored_content_message_data = [all_stored_content_message_data]
    #         elif not isinstance(all_stored_content_message_data, list):
    #             return {'success': False, 'error': 'Invalid message data format'}


    #         # ✅ FIX: Navigate into 'data' list first if present
    #         first_item = all_stored_content_message_data[0]
    #         if "data" in first_item and isinstance(first_item["data"], list) and first_item["data"]:
    #             first_item = first_item["data"][0]

    #         # Step 1: Extract ai_response safely
    #         ai_response_raw = first_item.get("ai_response", "")
    #         if not ai_response_raw:
    #             return {'success': False, 'error': 'AI response missing'}

    #         ai_response_dict = json.loads(ai_response_raw)

    #         # Step 2: Extract processed_text
    #         processed_text = ai_response_dict.get("result", {}).get("processed_text", "")
    #         if not processed_text:
    #             return {'success': False, 'error': 'Processed text missing'}


    #         # Step 3: Extract JSON from triple backticks if present
    #         json_match = re.search(r'```json\s*(\{.*?\})\s*```', processed_text, re.DOTALL)
    #         if json_match:
    #             json_string = json_match.group(1)
    #         else:
    #             # If no triple backticks, assume processed_text is already JSON
    #             json_string = processed_text.strip()

    #         # Step 4: Parse JSON content
    #         content_data = json.loads(json_string)
    #         title = content_data.get("title", "")
    #         content = content_data.get("content", "")

    #         # print("Title:", title)
    #         # print("Content:", content[:200])


    #         generated_article_title = title
    #         generated_article_content = content

    #         try:
    #             from app.workers.url_rewriter_para_response_helpers.get_input_json_data import GetInputJson
    #             self.get_input_json_service = GetInputJson()

    #             get_input_json_datas = self.get_input_json_service.get_input_json_data_for_wp(temp_article_id)
    #         except Exception as e:
    #             print({"status": "error", "step": "get_input_json_datas", "message": str(e)})

    #         print(get_input_json_datas,'get_input_json_datassdfsdfsdfsdf')

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



    #         # wp_tag and wp_category are lists; normalize to list-of-strings
    #         raw_wp_tags = input_data.get("wp_tag", []) or []
    #         wp_tag_slug_ids = [str(t).strip() for t in raw_wp_tags if t]

    #         raw_wp_categories = input_data.get("wp_category", []) or []
    #         wp_category_slug_ids = [str(c).strip() for c in raw_wp_categories if c]

    #         # wp_author is a single value
    #         wp_author_slug_id = str(input_data.get("wp_author") or "").strip()


    #         # Prepare request payload
    #         request_data = {
    #             "article_slug_id": article_slug_id,
    #             "article_type_slug_id": article_type_slug_id,
    #             "author_slug_id": wp_author_slug_id,
    #             "domain_slug_id": domain_slug_id,
    #             "category_slug_id": wp_category_slug_ids,
    #             "tag_slug_id": wp_tag_slug_ids,
    #             "workspace_slug_id": workspace_slug_id,
    #             "wp_title": generated_article_title,
    #             "wp_content": generated_article_content,
    #             "article_status": article_status,
    #             # "wp_excerpt": wp_excerpt,
    #             "wp_status": wp_status,
    #             # "wp_slug": wp_slug,
    #         }

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

    #         return {
    #             "success": False,
    #             "error": f"Failed to update after {max_retries} attempts",
    #             "last_response": stored_message,
    #         }

    #     except Exception as e:
    #         print(f"[publish_article] Exception: {e}")
    #         return {"success": False, "error": f"Unexpected error: {str(e)}"}



    def publish_article(self, all_stored_content_message_data, all_stored_wp_message_data, temp_article_id):
        try:
            get_input_json_datas = None

            if not all_stored_content_message_data:
                return {'success': False, 'error': 'Message data is empty'}

            # Normalize input
            if isinstance(all_stored_content_message_data, dict):
                all_stored_content_message_data = [all_stored_content_message_data]
            elif not isinstance(all_stored_content_message_data, list):
                return {'success': False, 'error': 'Invalid message data format'}

            # Extract ai_response
            first_item = all_stored_content_message_data[0]
            if "data" in first_item and isinstance(first_item["data"], list) and first_item["data"]:
                first_item = first_item["data"][0]

            ai_response_raw = first_item.get("ai_response", "")
            if not ai_response_raw:
                return {'success': False, 'error': 'AI response missing'}

            ai_response_dict = json.loads(ai_response_raw)
            processed_text = ai_response_dict.get("result", {}).get("processed_text", "")
            if not processed_text:
                return {'success': False, 'error': 'Processed text missing'}

            # Extract JSON content
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', processed_text, re.DOTALL)
            json_string = json_match.group(1) if json_match else processed_text.strip()
            content_data = json.loads(json_string)

            generated_article_title = content_data.get("title", "")
            generated_article_content = content_data.get("content", "")


            # Fetch input_json_data
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

            # Extract flags
            ai_flags = input_data.get("ai_content_flags", {})

            # Default values from input_data
            wp_category_slug_ids = input_data.get("wp_category", [])
            wp_tag_slug_ids = input_data.get("wp_tag", [])
            wp_author_slug_id = str(input_data.get("wp_author") or "").strip()

            # If AI-selected categories/tags/authors are enabled, extract them from wp_data_list
            if ai_flags.get("is_wp_categories_selected_by_ai") or \
            ai_flags.get("is_wp_tags_selected_by_ai") or \
            ai_flags.get("is_wp_authors_selected_by_ai"):
                wp_processed = self.process_wp_data(all_stored_wp_message_data)
                
                if ai_flags.get("is_wp_categories_selected_by_ai"):
                    wp_category_slug_ids = wp_processed.get("categories", []) or wp_category_slug_ids
                if ai_flags.get("is_wp_tags_selected_by_ai"):
                    wp_tag_slug_ids = wp_processed.get("tags", []) or wp_tag_slug_ids
                if ai_flags.get("is_wp_authors_selected_by_ai") and wp_processed.get("author"):
                    wp_author_slug_id = wp_processed["author"]

            # Prepare request payload
            request_data = {
                "article_slug_id": input_data.get("article_slug_id"),
                "article_type_slug_id": input_data.get("prompt", {}).get("article_type", {}).get("slug_id", ""),
                "author_slug_id": wp_author_slug_id,
                "domain_slug_id": input_data.get("domain", {}).get("slug_id", ""),
                "category_slug_id": wp_category_slug_ids,
                "tag_slug_id": wp_tag_slug_ids,
                "workspace_slug_id": input_data.get("workspace", {}).get("slug_id", ""),
                "wp_title": generated_article_title,
                "wp_content": generated_article_content,
                "article_status": input_data.get("article_status"),
                "wp_status": input_data.get("wp_status"),
            }

            # Retry logic
            request_item_id = f"{input_data.get('article_slug_id')}"
            max_retries = 3
            for attempt in range(1, max_retries + 1):
                stored_message = self.api_client.crud(
                    'article', 'update', data=request_data, item_id=request_item_id
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

    
    
    
    def process_wp_data(self, wp_data_list):
        categories = []
        tags = []
        author = None

        for item in wp_data_list.get("data", []):
            try:
                # Extract ai_response JSON
                ai_response = json.loads(item.get("ai_response", "{}"))
                processed_text = ai_response.get("result", {}).get("processed_text", "")
                
                # Extract the JSON from the processed_text (look for { ... } block)
                start = processed_text.find("{")
                end = processed_text.rfind("}")
                if start != -1 and end != -1:
                    data_json = json.loads(processed_text[start:end+1])
                    slug_id = data_json.get("slug_id")
                else:
                    slug_id = None

                field_type = item.get("message_field_type", "")
                if slug_id:
                    if field_type == "categories_selected_by":
                        categories.append(slug_id)
                    elif field_type == "tag_selected_by":
                        tags.append(slug_id)
                    elif field_type == "author_selected_by":
                        author = slug_id  # Only one author needed
            except Exception as e:
                print(f"Error processing item {item.get('id')}: {e}")

        return {
            "categories": categories,
            "tags": tags,
            "author": author
        }
