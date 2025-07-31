import requests
import os
import uuid
import logging
import json
import time
from app.workers.core.calculate_priority.calculate_priority import CalculatePriority
from app.workers.core.article_innovator_api_call.ai_message.ai_message import AIMessage
from app.workers.core.ai_rate_limiter.ai_rate_limiter import AIRateLimiter
from app.workers.core.primary_keyword_mapping.primary_keyword_mapping import PrimaryKeywordMapping
from app.workers.core.wp_data_mapping.wp_data_mapping import WPDataMapping
from app.config.config import AI_RATE_LIMITER_URL


class AIRateLimiterService:
    def __init__(self):
        self.ai_rate_limiter_url = AI_RATE_LIMITER_URL
        self.headers = {
            "Content-Type": "application/json"
        }
        
        self.calculate_priority_service = CalculatePriority()
        self.ai_rate_limiter_service = AIRateLimiter()
        self.ai_message_service = AIMessage()
        self.primary_keyword_mapping_service = PrimaryKeywordMapping()
        self.wp_data_mapping_service = WPDataMapping()


    
        
    def create_content_ai_request(self, input_json_data, final_prompt_data):
        try:

            # Set priority
            article_priority = input_json_data.get("message", {}).get("article_priority", 100)
            priority = self.calculate_priority_service.calculate_priority(article_priority, 'content_message')

            # Metadata
            workspace_obj = input_json_data.get("message", {}).get("workspace", {})
            workspace_slug_id = workspace_obj.get("slug_id", {})
            prompt_obj = input_json_data.get("message", {}).get("prompt", {})
            ai_model = prompt_obj.get("ai_rate_model", 'deepseek/deepseek_v3')
            article_id = input_json_data.get("message", {}).get("article_slug_id")

            # Try to get existing message data
            message_id = str(uuid.uuid4())  # default new UUID

            try:
                stored_message_data = self.ai_message_service.check_if_prompt_already_stored(article_id, 'content_message')
                # print(stored_message_data, 'stored_message_dataxxxxxxxxxx')
                if stored_message_data.get("success") and stored_message_data.get("data"):
                    # Use the existing message_id
                    message_id = stored_message_data["data"][0].get("message_id", message_id)
                    print(message_id, 'message_idxxxxxxxxxx')
            except Exception as e:
                # print({"status": "error", "step": "get_stored_message", "message": str(e)})
                raise ValueError({"status": "error", "step": "get_stored_message", "message": str(e)})

            print(final_prompt_data,'final_prompt_data')
            # combined_text = (
            #     final_prompt_data['instruction'].strip() + "\n\n" +
            #     final_prompt_data['title'].strip() + "\n\n" +
            #     final_prompt_data['content'].strip()
            # )

            
            
            
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
                "prompt": final_prompt_data,
                "ai_request_status": 'sent',
                "message_field_type": 'content_message',
                "message_priority": priority,
                "content": "",
                "workspace_id": workspace_slug_id,
            }
            print(single_ai_request, 'single_ai_requestxxxxxxxxxx')


            # Step 4.2: Store AI message request
            try:
                self.ai_message_service.store_ai_message_request(single_ai_request)
            except Exception as e:
                error_msg = f"Error storing AI message request: {str(e)}"
                print({"status": "error", "step": "store_ai_message_request", "message": error_msg})
                return {
                    "success": False,
                    "error": error_msg,
                    "message_id": single_ai_request.get("message_id")
                }

            return single_ai_request

        except requests.RequestException as e:
            # return f"Request to ai lambda failed: {e}"
            raise ValueError(f"error in create_content_ai_request: {e}")
        except Exception as e:
            # return f"An unexpected error occurred: {e}"
            raise ValueError(f"An unexpected error occurred: {e}")

        
   
    def create_single_primary_keyword_ai_request(self, input_json_data, request_data, processed_data):     
        
        try:
            # Extract updated_text from supportive prompts
            data_list = [
                item['data']['updated_text']
                for item in request_data.get('supportive_prompts', [])
                if 'data' in item and 'updated_text' in item['data']
            ]
            # print(data_list, 'data_listxxxxxxxxxx')

            # Create prompt
            prompt_data = self.primary_keyword_mapping_service.primary_keyword_mapping(data_list, processed_data)
            # print(prompt_data, 'prompt_dataxxxxxxxxxx')
            # Set priority
            article_priority = input_json_data.get("message", {}).get("article_priority", 100)
            priority = self.calculate_priority_service.calculate_priority(article_priority, 'primary_keyword')
            # print(priority, 'priorityxxxxxxxxxx')

            # Metadata
            workspace_obj = input_json_data.get("message", {}).get("workspace", {})
            workspace_slug_id = workspace_obj.get("slug_id", {})
            prompt_obj = input_json_data.get("message", {}).get("prompt", {})
            ai_model = prompt_obj.get("ai_rate_model", 'deepseek/deepseek_v3')
            article_id = input_json_data.get("message", {}).get("article_slug_id")

            # Try to get existing message data
            message_id = str(uuid.uuid4())  # default new UUID

            try:
                stored_message_data = self.ai_message_service.check_if_prompt_already_stored(article_id, 'primary_keyword')
                # print(stored_message_data, 'stored_message_dataxxxxxxxxxx')
                if stored_message_data.get("success") and stored_message_data.get("data"):
                    # Use the existing message_id
                    message_id = stored_message_data["data"][0].get("message_id", message_id)
                    print(message_id, 'message_idxxxxxxxxxx')
            except Exception as e:
                # print({"status": "error", "step": "get_stored_message", "message": str(e)})
                raise ValueError({"status": "error", "step": "get_stored_message", "message": str(e)})

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
                "message_field_type": 'primary_keyword',
                "message_priority": priority,
                "content": "",
                "workspace_id": workspace_slug_id,
            }
            print(single_ai_request, 'single_ai_requestxxxxxxxxxx')

            # Step 4.2: Store AI message request
            try:
                self.ai_message_service.store_ai_message_request(single_ai_request)
            except Exception as e:
                error_msg = f"Error storing AI message request: {str(e)}"
                print({"status": "error", "step": "store_ai_message_request", "message": error_msg})
                return {
                    "success": False,
                    "error": error_msg,
                    "message_id": single_ai_request.get("message_id")
                }
            return single_ai_request

        except requests.RequestException as e:
            # return f"Request to create_single_primary_keyword_ai_request failed: {e}"
            raise ValueError(f"Request to create_single_primary_keyword_ai_request failed: {e}")
        except Exception as e:
            raise ValueError(f"An unexpected error occurred: {e}")
        
        
        
    def create_single_wp_ai_request(self, input_json_data, request_data, all_stored_message, message_type):     
        try:
            # Extract updated_text from supportive prompts
            data_list = [
                item['data']['updated_text']
                for item in request_data.get('supportive_prompts', [])
                if 'data' in item and 'updated_text' in item['data']
            ]
            # print(data_list, 'data_listxxxxxxxxxx')

            # Create prompt
            prompt_data = self.wp_data_mapping_service.wp_data_mapping(data_list, all_stored_message)
            print(prompt_data, 'prompt_dataxxxxxxxxxx')
            # Set priority
            article_priority = input_json_data.get("article_priority", 100)
            priority = self.calculate_priority_service.calculate_priority(article_priority, message_type)
            print(priority, 'priorityxxxxxxxxxx')

            print(input_json_data, 'input_json_datasssssssssssssssseeeeeeeeeeeeeeee')
            # Metadata
            workspace_obj = input_json_data.get("workspace", {})
            workspace_slug_id = workspace_obj.get("slug_id", "")
            print(workspace_slug_id,'workspace_slug_idxxxxxxxxxx')
            
            prompt_obj = input_json_data.get("prompt", {})
            ai_model = prompt_obj.get("ai_rate_model", 'deepseek/deepseek_v3')
            article_id = input_json_data.get("article_slug_id")

            # Try to get existing message data
            message_id = str(uuid.uuid4())  # default new UUID

            try:
                stored_message_data = self.ai_message_service.check_if_prompt_already_stored(article_id, message_type)
                # print(stored_message_data, 'stored_message_dataxxxxxxxxxx')
                if stored_message_data.get("success") and stored_message_data.get("data"):
                    # Use the existing message_id
                    message_id = stored_message_data["data"][0].get("message_id", message_id)
                    print(message_id, 'message_idxxxxxxxxxx')
            except Exception as e:
                # print({"status": "error", "step": "get_stored_message", "message": str(e)})
                raise ValueError({"status": "error", "step": "get_stored_message", "message": str(e)})

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
            print(single_ai_request, 'single_ai_requestxxxxxxxsdfsdfsdfsdfsdfxxx')

            # Step 4.2: Store AI message request
            try:
                self.ai_message_service.store_ai_message_request(single_ai_request)
            except Exception as e:
                error_msg = f"Error storing AI message request: {str(e)}"
                print({"status": "error", "step": "store_ai_message_request", "message": error_msg})
                return {
                    "success": False,
                    "error": error_msg,
                    "message_id": single_ai_request.get("message_id")
                }
            return single_ai_request

        except requests.RequestException as e:
            # return f"Request to ai lambda failed: {e}"
            raise ValueError(f"error in create_single_wp_ai_request: {e}")
        except Exception as e:
            # return f"An unexpected error occurred: {e}"
            raise ValueError(f"An unexpected error occurred: {e}")
        
        
        

    # def send_ai_request(self, request_data, workspace_slug_id):
    #     try:
    #         url = f'{self.ai_rate_limiter_url}/message/publish'
    #         max_retries = 4
    #         base_timeout = 30  # Initial timeout in seconds
    #         response = None

    #         for attempt in range(1, max_retries + 1):
    #             try:
    #                 timeout = base_timeout * (2 ** (attempt - 1))  # Exponential timeout
    #                 print(f"[Attempt {attempt}] Sending AI request with timeout {timeout}s...")

    #                 response = requests.post(url, json=request_data, headers=self.headers, timeout=timeout)

    #                 if response.status_code in [200, 201]:
    #                     return response.json()

    #                 # Handle specific "no worker" error
    #                 error_data = {}
    #                 try:
    #                     error_data = response.json() if response.text else {}
    #                 except ValueError:
    #                     pass

    #                 no_worker_error = (
    #                     isinstance(error_data, dict) and (
    #                         error_data.get("worker_required") is True or 
    #                         "no worker available" in str(error_data.get("message", "")).lower()
    #                     )
    #                 )

    #                 if no_worker_error and attempt == 1:
    #                     print("No worker available, attempting to scale up...")
    #                     scaled = self.ai_rate_limiter_service.scale_worker(str(workspace_slug_id))
    #                     if scaled:
    #                         print("Successfully initiated worker scale up")

    #             except requests.RequestException as e:
    #                 print(f"[Attempt {attempt}] RequestException: {e}")
    #                 if attempt == max_retries:
    #                     return {
    #                         "success": False,
    #                         "error": f"RequestException after {max_retries} attempts: {e}",
    #                         "message_id": request_data.get("message_id")
    #                     }

    #             except Exception as e:
    #                 print(f"[Attempt {attempt}] General Exception: {e}")
    #                 if attempt == max_retries:
    #                     return {
    #                         "success": False,
    #                         "error": f"Exception after {max_retries} attempts: {e}",
    #                         "message_id": request_data.get("message_id")
    #                     }

    #             # Sleep before next retry (exponential delay)
    #             sleep_time = 10 * attempt  # e.g., 10s, 20s, 30s, 40s
    #             print(f"[Attempt {attempt}] Waiting {sleep_time}s before retry...")
    #             time.sleep(sleep_time)

    #         return {
    #             "success": False,
    #             "error": f"Failed after {max_retries} attempts, status: {response.status_code if response else 'No Response'}",
    #             "message_id": request_data.get("message_id")
    #         }

    #     except Exception as e:
    #         return {
    #             "success": False,
    #             "error": f"Unexpected outer error: {e}",
    #             "message_id": request_data.get("message_id")
    #         }



    def send_ai_request(self, request_data, workspace_slug_id):
        try:
            url = f'{self.ai_rate_limiter_url}/message/publish'
            max_retries = 4
            base_timeout = 30  # Initial timeout in seconds
            response = None

            for attempt in range(1, max_retries + 1):
                try:
                    timeout = base_timeout * (2 ** (attempt - 1))  # Exponential timeout
                    print(f"[Attempt {attempt}] Sending AI request with timeout {timeout}s...")

                    response = requests.post(url, json=request_data, headers=self.headers, timeout=timeout)

                    if response.status_code in [200, 201]:
                        return response.json()

                    # Handle specific "no worker" error
                    error_data = {}
                    try:
                        error_data = response.json() if response.text else {}
                    except ValueError:
                        pass

                    no_worker_error = (
                        isinstance(error_data, dict) and (
                            error_data.get("worker_required") is True or 
                            "no worker available" in str(error_data.get("message", "")).lower()
                        )
                    )

                    if no_worker_error and attempt == 1:
                        print("No worker available, attempting to scale up...")
                        scaled = self.ai_rate_limiter_service.scale_worker(str(workspace_slug_id))
                        if scaled:
                            print("Successfully initiated worker scale up")

                except requests.RequestException as e:
                    print(f"[Attempt {attempt}] RequestException: {e}")
                    if attempt == max_retries:
                        raise RuntimeError(f"RequestException after {max_retries} attempts: {e}")

                except Exception as e:
                    print(f"[Attempt {attempt}] General Exception: {e}")
                    if attempt == max_retries:
                        raise RuntimeError(f"Exception after {max_retries} attempts: {e}")

                # Sleep before next retry (exponential delay)
                sleep_time = 10 * attempt  # e.g., 10s, 20s, 30s, 40s
                print(f"[Attempt {attempt}] Waiting {sleep_time}s before retry...")
                time.sleep(sleep_time)

            raise RuntimeError(
                f"Failed after {max_retries} attempts, status: {response.status_code if response else 'No Response'}"
            )

        except Exception as e:
            raise RuntimeError(
                f"Unexpected outer error: {e}"
            )




    def retry_failed_messages(self, resp_retry):

        try:
            # print(resp_retry, 'resp_retryssdfsasq')

            # ✅ Step 1: Extract ai_request string from the nested response
            ai_request_str = resp_retry.get("data", {}).get("data", {}).get("ai_request", "")

            # ✅ Step 2: Convert JSON string to Python dictionary
            ai_request = json.loads(ai_request_str) if ai_request_str else {}

            # print(ai_request, 'ai_requestxxxxxxxxx')

            # ✅ Step 3: Build retry payload using the same message_id
            retry_payload = {
                "article_id": ai_request.get("article_id", ""),
                "model": ai_request.get("model", ""),
                "system_prompt": ai_request.get("system_prompt", ""),
                "sequence_index": ai_request.get("sequence_index", 1),
                "html_tag": ai_request.get("html_tag", ""),
                "response_format": ai_request.get("response_format", "json"),
                "message_id": ai_request.get("message_id", ""),  # ✅ Keep original message_id
                "article_message_total_count": ai_request.get("article_message_total_count", 1),
                "prompt": ai_request.get("prompt", ""),
                "ai_request_status": "retry",  # ✅ Change status
                "message_field_type": ai_request.get("message_field_type", ""),
                "message_priority": 202,  # ✅ Retry priority
                "content": "",
                "workspace_id": ai_request.get("workspace_id", "")
            }

            # print(retry_payload, '✅ Final Retry Payload')
        
            retry_message_response = self.send_ai_request(retry_payload, ai_request.get("workspace_id", ""))
            print(retry_message_response, 'retry_message_responsesdfsdfsdfxczzxc')

        except Exception as e:
            print(f"[retry_failed_messages] Exception: {e}")
            # return {"success": False, "error": f"Unexpected error: {str(e)}"}
            raise ValueError({"success": False, "error": f"Unexpected error: {str(e)}"})



    # def get_single_ai_response(self, message_id):
    #     try:
    #         max_retries = 3
    #         delay_seconds = 30

    #         for attempt in range(1, max_retries + 1):
    #             try:
    #                 url = f'{self.ai_rate_limiter_url}/message/{message_id}'
    #                 response = requests.get(url, headers=self.headers)

    #                 if response.status_code in [200, 201]:
    #                     try:
    #                         response_data = response.json()
    #                     except ValueError:
    #                         return {"message": {"error": "Invalid JSON response"}}

    #                     if isinstance(response_data, dict):
    #                         data_obj = {
    #                             "message": response_data
    #                         }

    #                         status = response_data.get("ai_response_status")
    #                         if status in ["pending", "processing"]:
    #                             print(f"Attempt {attempt}: Response status '{status}'. Retrying after {delay_seconds} seconds...")
    #                             if attempt < max_retries:
    #                                 time.sleep(delay_seconds)
    #                                 continue

    #                         return data_obj

    #                     else:
    #                         return {"message": {"error": "Response is not a valid JSON object"}}

    #                 else:
    #                     print(f"Attempt {attempt}: Unexpected status code {response.status_code}")
    #                     return {"message": {"error": f"Status code {response.status_code}"}}  

    #             except requests.RequestException as e:
    #                 print(f"Attempt {attempt}: Request failed: {e}")
    #                 if attempt < max_retries:
    #                     time.sleep(delay_seconds)

    #             except Exception as e:
    #                 print(f"Attempt {attempt}: Unexpected error: {e}")
    #                 if attempt < max_retries:
    #                     time.sleep(delay_seconds)

    #         return {"message": {"error": "Max retries exceeded"}}

    #     except Exception as e:
    #         return {"message": {"error": f"Unexpected error: {str(e)}"}}
    
    
    def get_single_ai_response(self, message_id):
        try:
            max_retries = 4
            base_delay = 30  # Base delay in seconds

            for attempt in range(1, max_retries + 1):
                try:
                    url = f'{self.ai_rate_limiter_url}/message/{message_id}'
                    response = requests.get(url, headers=self.headers)

                    if response.status_code in [200, 201]:
                        try:
                            response_data = response.json()
                        except ValueError:
                            # return {"message": {"error": "Invalid JSON response"}}
                            raise ValueError({"message": {"error": "Invalid JSON response"}})

                        if isinstance(response_data, dict):
                            data_obj = {"message": response_data}
                            status = response_data.get("ai_response_status")

                            if status in ["pending", "processing"]:
                                print(f"Attempt {attempt}: Response status '{status}'. Retrying after {base_delay * attempt} seconds...")
                                if attempt < max_retries:
                                    time.sleep(base_delay * attempt)  # Increase delay per attempt
                                    continue

                            return data_obj
                        else:
                            # return {"message": {"error": "Response is not a valid JSON object"}}
                            raise ValueError({"message": {"error": "Response is not a valid JSON object"}})

                    else:
                        print(f"Attempt {attempt}: Unexpected status code {response.status_code}")
                        # return {"message": {"error": f"Status code {response.status_code}"}}  
                        raise ValueError({"message": {"error": f"Status code {response.status_code}"}})

                except requests.RequestException as e:
                    print(f"Attempt {attempt}: Request failed: {e}")
                    if attempt < max_retries:
                        time.sleep(base_delay * attempt)

                except Exception as e:
                    print(f"Attempt {attempt}: Unexpected error: {e}")
                    if attempt < max_retries:
                        time.sleep(base_delay * attempt)

            return {"message": {"error": "Max retries exceeded"}}

        except Exception as e:
            # return {"message": {"error": f"Unexpected error: {str(e)}"}}
            raise ValueError({"message": {"error": f"Unexpected error: {str(e)}"}})
