import requests
import os
import uuid
import logging
import json
import time
from app.workers.url_rewriter_para_request_helpers.content_processor import ContentProcessor
from app.workers.core.calculate_priority.calculate_priority import CalculatePriority
from app.workers.url_rewriter_para_request_helpers.ai_message_request_store import AIMessageRequestStore
from app.config.config import AI_RATE_LIMITER_URL


class AIRateLimiterService:
    def __init__(self):
        self.ai_rate_limiter_url = AI_RATE_LIMITER_URL
        self.headers = {
            "Content-Type": "application/json"
        }
        
        self.content_handler = ContentProcessor()
        self.calculate_priority_service = CalculatePriority()
        self.ai_message_request_store_service = AIMessageRequestStore()
        

    def fetch_and_process_content(self, scraped_content, input_json_data, final_prompt_data):
        try:
            print('2222222222222222222222222222222222')
            # Fetch content
            content_data = self.content_handler.fetch_content(scraped_content)
            if not content_data:
                return None, False
                    
            if isinstance(content_data, dict):
                request_data = self.content_handler.process_content(content_data, input_json_data, final_prompt_data)

            # for tesing  
            with open('demo_json/process_content_data.json', 'w', encoding='utf-8') as f:
                json.dump(request_data, f, ensure_ascii=False, indent=4)
                    
            return request_data

            # return request_data
            # return_data = self.send_ai_request(request_data)

        except Exception as e:
            return f"An unexpected error occurred: {e}"
        
        
    # def send_ai_requests(self, request_json_data, article_priority):
    #     try:
    #         submit_data_responses = []

    #         input_article_id = request_json_data.get("article_id")
    #         workspace_slug_id = request_json_data.get("workspace_id")
    #         message_total_count = len(request_json_data.get("ai_requests", []))

    #         for index, single_request_data in enumerate(request_json_data.get("ai_requests", [])):
    #             try:
    #                 ai_model = single_request_data.get("model", "default-model")
    #                 prompt_data = single_request_data.get("prompt", "")
    #                 message_type = single_request_data.get("html_tag", "")
    #                 sequence_index = single_request_data.get("sequence_index", "")
                    
    #                 # Calculate priority using the service
    #                 priority = self.calculate_priority_service.calculate_priority(article_priority, 'content_message')
    #                 article_message_total_count = len(request_json_data.get("ai_requests", []))

    #                 # sequence_index = index + 1

    #                 payload = {
    #                     "article_id": input_article_id,
    #                     "message_id": str(uuid.uuid4()),
    #                     "model": ai_model,
    #                     "system_prompt": single_request_data.get("system_prompt", "You are a helpful assistant."),
    #                     "sequence_index": int(sequence_index),
    #                     "html_tag": message_type,
    #                     "response_format": "json",
    #                     "prompt": prompt_data,
    #                     "ai_request_status": "sent",
    #                     "message_field_type": 'content_message',
    #                     "message_priority": priority,
    #                     "content": single_request_data.get("content", ""),
    #                     "workspace_id": workspace_slug_id,
    #                     "article_message_total_count": article_message_total_count,
    #                     # "article_message_count":sequence_index,        # same like sequence_index number 
    #                 }
                    
    #                 store_ai_message_request_data = self.ai_message_request_store_service.store_ai_message_request(payload)
    #                 # print(store_ai_message_request_data,'=============store_ai_message_request_data=================')
                    
                    
    #                 # Extract the status_code from the response
    #                 status_code = store_ai_message_request_data.get("status_code")

    #                 # If status_code is NOT 200 or 201, return early
    #                 if status_code not in [200, 201]:
    #                     print(f"Aborting: status code is {status_code}, not proceeding with POST request.")
    #                     # return store_ai_message_request_data  # or just `return` if no value is needed


    #                 url = f'{self.ai_rate_limiter_url}/message/publish'
    #                 response = requests.post(url, json=payload, headers=self.headers)

    #                 if response.status_code not in [200, 201]:
    #                     return f"AI request error: {response.status_code} - {response.text}"

    #                 request_and_response_merged_entry = {
    #                     "ai_request": payload,
    #                     "ai_response": response.json()
    #                 }
    #                 submit_data_responses.append(request_and_response_merged_entry)


    #             except requests.RequestException as e:
    #                 return f"Request failed: {e}"
    #             except Exception as e:
    #                 return f"Error during processing: {e}"

    #         with open('demo_json/send_ai_requests_data.json', 'w', encoding='utf-8') as f:
    #             json.dump(submit_data_responses, f, ensure_ascii=False, indent=4)

    #         return submit_data_responses

    #     except Exception as e:
    #         return f"Unexpected error: {e}"



    def send_ai_requests(self, request_json_data, article_priority):
        try:
            submit_data_responses = []

            input_article_id = request_json_data.get("article_id")
            workspace_slug_id = request_json_data.get("workspace_id")
            message_total_count = len(request_json_data.get("ai_requests", []))

            for index, single_request_data in enumerate(request_json_data.get("ai_requests", [])):
                try:
                    ai_model = single_request_data.get("model", "default-model")
                    prompt_data = single_request_data.get("prompt", "")
                    message_type = single_request_data.get("html_tag", "")
                    sequence_index = single_request_data.get("sequence_index", "")
                    existing_message_id = single_request_data.get("message_id")

                    if not existing_message_id:
                        print(f"[Warning] message_id missing for index {index}, generating new one.")
                        existing_message_id = str(uuid.uuid4())

                    # Calculate priority
                    priority = self.calculate_priority_service.calculate_priority(article_priority, 'content_message')
                    article_message_total_count = message_total_count

                    payload = {
                        "article_id": input_article_id,
                        "message_id": existing_message_id,
                        "model": ai_model,
                        "system_prompt": single_request_data.get("system_prompt", "You are a helpful assistant."),
                        "sequence_index": int(sequence_index),
                        "html_tag": message_type,
                        "response_format": "json",
                        "prompt": prompt_data,
                        "ai_request_status": "sent",
                        "message_field_type": "content_message",
                        "message_priority": priority,
                        "content": single_request_data.get("content", ""),
                        "workspace_id": workspace_slug_id,
                        "article_message_total_count": article_message_total_count,
                    }

                    # Step 1: Store the request
                    store_response = self.ai_message_request_store_service.store_ai_message_request(payload)

                    if store_response.get("status_code") not in [200, 201]:
                        print(f"Store failed with status {store_response.get('status_code')}. Skipping send.")
                        continue

                    # Step 2: Send the request with retry logic
                    url = f'{self.ai_rate_limiter_url}/message/publish'
                    max_retries = 3
                    retry_delay = 5  # seconds

                    for attempt in range(1, max_retries + 1):
                        try:
                            response = requests.post(url, json=payload, headers=self.headers, timeout=30)
                            if response.status_code in [200, 201]:
                                break
                            print(f"[Attempt {attempt}] Failed with {response.status_code}, retrying...")
                            time.sleep(retry_delay)
                        except requests.RequestException as e:
                            print(f"[Attempt {attempt}] RequestException: {e}")
                            time.sleep(retry_delay)
                            if attempt == max_retries:
                                raise

                    request_and_response_merged_entry = {
                        "ai_request": payload,
                        "ai_response": response.json()
                    }
                    submit_data_responses.append(request_and_response_merged_entry)

                except Exception as e:
                    print(f"Error during processing index {index}: {e}")
                    continue  # Skip to next instead of failing whole batch

            # Save to file (optional)
            with open('demo_json/send_ai_requests_data.json', 'w', encoding='utf-8') as f:
                json.dump(submit_data_responses, f, ensure_ascii=False, indent=4)

            return submit_data_responses

        except Exception as e:
            return f"Unexpected error: {e}"
