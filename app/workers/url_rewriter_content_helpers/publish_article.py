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

    def publish_article(self, all_stored_message_data, temp_article_id):
        try:
            
            get_input_json_datas = None
            
            print(type(all_stored_message_data), '555666666633')

            if not all_stored_message_data:
                return {'success': False, 'error': 'Message data is empty'}

            # Normalize input to list
            if isinstance(all_stored_message_data, dict):
                all_stored_message_data = [all_stored_message_data]
            elif not isinstance(all_stored_message_data, list):
                return {'success': False, 'error': 'Invalid message data format'}

            print(all_stored_message_data, 'all_stored_message_datasdfsfzxczczxczxczczcxzxxxxxxxxxxxxx')

            # ✅ FIX: Navigate into 'data' list first if present
            first_item = all_stored_message_data[0]
            if "data" in first_item and isinstance(first_item["data"], list) and first_item["data"]:
                first_item = first_item["data"][0]

            # Step 1: Extract ai_response safely
            ai_response_raw = first_item.get("ai_response", "")
            if not ai_response_raw:
                return {'success': False, 'error': 'AI response missing'}

            ai_response_dict = json.loads(ai_response_raw)

            # Step 2: Extract processed_text
            processed_text = ai_response_dict.get("result", {}).get("processed_text", "")
            if not processed_text:
                return {'success': False, 'error': 'Processed text missing'}


            # Step 3: Extract JSON from triple backticks if present
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', processed_text, re.DOTALL)
            if json_match:
                json_string = json_match.group(1)
            else:
                # If no triple backticks, assume processed_text is already JSON
                json_string = processed_text.strip()

            # Step 4: Parse JSON content
            content_data = json.loads(json_string)
            title = content_data.get("title", "")
            content = content_data.get("content", "")

            # print("Title:", title)
            # print("Content:", content[:200])


            generated_article_title = title
            generated_article_content = content

            try:
                from app.workers.url_rewriter_para_response_helpers.get_input_json_data import GetInputJson
                self.get_input_json_service = GetInputJson()

                get_input_json_datas = self.get_input_json_service.get_input_json_data_for_wp(temp_article_id)
            except Exception as e:
                print({"status": "error", "step": "get_input_json_datas", "message": str(e)})

            print(get_input_json_datas,'get_input_json_datassdfsdfsdfsdf')

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


            # wp_tag and wp_category are lists; normalize to list-of-strings
            raw_wp_tags = input_data.get("wp_tag", []) or []
            wp_tag_slug_ids = [str(t).strip() for t in raw_wp_tags if t]

            raw_wp_categories = input_data.get("wp_category", []) or []
            wp_category_slug_ids = [str(c).strip() for c in raw_wp_categories if c]

            # wp_author is a single value
            wp_author_slug_id = str(input_data.get("wp_author") or "").strip()


            # Prepare request payload
            request_data = {
                "article_slug_id": article_slug_id,
                "article_type_slug_id": article_type_slug_id,
                "author_slug_id": wp_author_slug_id,
                "domain_slug_id": domain_slug_id,
                "category_slug_id": wp_category_slug_ids,
                "tag_slug_id": wp_tag_slug_ids,
                "workspace_slug_id": workspace_slug_id,
                "wp_title": generated_article_title,
                "wp_content": generated_article_content,
                "article_status": article_status,
                # "wp_excerpt": wp_excerpt,
                "wp_status": wp_status,
                # "wp_slug": wp_slug,
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
