import requests
import os
import time
import json
import uuid
from app.workers.core.article_innovator_api_call.api_client.api_client import APIClient
from app.workers.core.calculate_priority.calculate_priority import CalculatePriority
from app.workers.url_rewriter_para_request_helpers.content_processor import ContentProcessor
from app.workers.url_rewriter_para_response_helpers.get_all_stored_message import StoredMessageFetcher 


class CreateSingleAiRequest:
    def __init__(self):
        self.api_client = APIClient()
        self.calculate_priority_service = CalculatePriority()
        self.content_processor = ContentProcessor()
        self.get_stored_message_service = StoredMessageFetcher()
        

       
    # def create_single_ai_request(self, input_json_data, request_data, message_type,scraped_data):
    #     try:
            
    #         # data_list = [item['data'] for item in request_data.get('supportive_prompts', []) if 'data' in item]

    #         data_list = [
    #             item['data']['updated_text']
    #             for item in request_data.get('supportive_prompts', [])
    #             if 'data' in item and 'updated_text' in item['data']
    #         ]
    #         print(data_list,'data_listxxxxxxxxxx')

    #         prompt_data = self.primary_keyword_mapping(data_list, scraped_data)

    #         article_priority = input_json_data.get("message", {}).get("article_priority", 100)
    #         priority = self.calculate_priority_service.calculate_priority(article_priority, 'primary_keyword')
            
    #         workspace_obj = input_json_data.get("message", {}).get("workspace", {})
    #         workspace_slug_id = workspace_obj.get("slug_id", {})
    #         prompt_obj = input_json_data.get("message", {}).get("prompt", {})
    #         ai_model = prompt_obj.get("ai_rate_model", 'deepseek/deepseek_v3')

    #         article_id = input_json_data.get("message", {}).get("article_slug_id")

    #         try:
    #             get_message_data = self.get_stored_message_service.get_stored_message(article_id, message_type)
    #         except Exception as e:
    #             print({"status": "error", "step": "get_stored_message", "message": str(e)})


    #         single_ai_request={
    #             "article_id": input_json_data.get("message", {}).get("article_slug_id"),
    #             "model": ai_model,
    #             "system_prompt": "You are a helpful assistant.",
    #             "sequence_index": 1,
    #             "html_tag": "",
    #             "response_format":"json",
    #             "message_id": str(uuid.uuid4()),
    #             "article_message_total_count": 1,
    #             "prompt": prompt_data,
    #             "ai_request_status": 'sent',
    #             "message_field_type": message_type,
    #             "message_priority": priority, 
    #             "content":"",
    #             "workspace_id":workspace_slug_id,
    #             # "article_message_count":1,
    #         }
    #         # print(single_ai_request)
            
    #         return single_ai_request

    #     except requests.RequestException as e:
    #         return f"Request to ai lambda failed: {e}"
    #     except Exception as e:
    #         return f"An unexpected error occurred: {e}"
        
        
        
    def create_single_ai_request(self, input_json_data, request_data, message_type, scraped_data):
        try:
            # Extract updated_text from supportive prompts
            data_list = [
                item['data']['updated_text']
                for item in request_data.get('supportive_prompts', [])
                if 'data' in item and 'updated_text' in item['data']
            ]
            print(data_list, 'data_listxxxxxxxxxx')

            # Create prompt
            prompt_data = self.primary_keyword_mapping(data_list, scraped_data)
            print(prompt_data, 'prompt_dataxxxxxxxxxx')
            # Set priority
            article_priority = input_json_data.get("message", {}).get("article_priority", 100)
            priority = self.calculate_priority_service.calculate_priority(article_priority, 'primary_keyword')

            # Metadata
            workspace_obj = input_json_data.get("message", {}).get("workspace", {})
            workspace_slug_id = workspace_obj.get("slug_id", {})
            prompt_obj = input_json_data.get("message", {}).get("prompt", {})
            ai_model = prompt_obj.get("ai_rate_model", 'deepseek/deepseek_v3')
            article_id = input_json_data.get("message", {}).get("article_slug_id")

            # Try to get existing message data
            message_id = str(uuid.uuid4())  # default new UUID

            try:
                stored_data = self.get_stored_message_service.get_stored_message(article_id, message_type)
                print(stored_data, 'stored_dataxxxxxxxxxx')
                if stored_data.get("success") and stored_data.get("data"):
                    # Use the existing message_id
                    message_id = stored_data["data"][0].get("message_id", message_id)
                    print(message_id, 'message_idxxxxxxxxxx')
            except Exception as e:
                print({"status": "error", "step": "get_stored_message", "message": str(e)})

            # Build AI request
            single_ai_request = {
                "article_id": article_id,
                "model": ai_model,
                "system_prompt": "You are a helpful assistant.",
                "sequence_index": 1,
                "html_tag": "",
                "response_format": "json",
                "message_id": message_id,
                "article_message_total_count": 1,
                "prompt": prompt_data,
                "ai_request_status": 'sent',
                "message_field_type": message_type,
                "message_priority": priority,
                "content": "",
                "workspace_id": workspace_slug_id,
            }
            print(single_ai_request, 'single_ai_requestxxxxxxxxxx')

            return single_ai_request

        except requests.RequestException as e:
            return f"Request to ai lambda failed: {e}"
        except Exception as e:
            return f"An unexpected error occurred: {e}"

        
        
    
    def primary_keyword_mapping(self, prompt_data, scraped_data):
        try:
            # print('this is ronak sdf')
            fetch_content_data = self.content_processor.fetch_content(scraped_data)
            print(fetch_content_data,'fetch_content_dataxxxxxxxxxx')

            # Save the file directly to the existing 'demo_json' folder
            with open('demo_json/fetch_content_data.json', 'w', encoding='utf-8') as f:
                json.dump(fetch_content_data, f, ensure_ascii=False, indent=4)


            # Create a map from selectors_output: { "source_title": "value", ... }
            selector_map = {
                item['name']: item['value']
                for item in fetch_content_data.get("selectors_output", [])
            }
            print(selector_map, 'selector_mapxxxxxxxxxx')

            # Replace placeholders in prompt_data
            processed_prompts = []
            for prompt in prompt_data:
                for key, value in selector_map.items():
                    placeholder = f"[[{key}]]"
                    if placeholder in prompt:
                        prompt = prompt.replace(placeholder, str(value))
                processed_prompts.append(prompt)

            # print(processed_prompts,'processed_promptsxxxxxxxxxx')
            # Save the file directly to the existing 'demo_json' folder
            with open('demo_json/processed_prompts.json', 'w', encoding='utf-8') as f:
                json.dump(processed_prompts, f, ensure_ascii=False, indent=4)


            return processed_prompts
        except Exception as e:
            print(f"Error in primary_keyword_mapping: {e}")
            return f"An unexpected error occurred: {e}"