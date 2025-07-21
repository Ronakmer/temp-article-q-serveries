import requests
import os
import time
import json
import uuid
from app.workers.core.article_innovator_api_call.api_client.api_client import APIClient
from app.config.logger import LoggerSetup
from app.config.config import AI_RATE_LIMITER_URL
from app.workers.url_rewriter_para_request_helpers.ai_rate_limiter_scale_worker import AIRateLimiterScaleWorker
from app.workers.url_rewriter_para_request_helpers.ai_message_request_store import AIMessageRequestStore

class SendSingleAiRequest:
    def __init__(self):
        self.api_client = APIClient()

        # logger_setup = LoggerSetup()
        self.ai_rate_limiter_scale_worker = AIRateLimiterScaleWorker()
        self.ai_message_request_store_service = AIMessageRequestStore()
        
        # self.logger = logger_setup.setup_worker_logger(self.pid)
        self.ai_rate_limiter_url = AI_RATE_LIMITER_URL
        self.headers = {
            "Content-Type": "application/json"
        }

       
    # def send_single_ai_request(self, single_request_data, workspace_slug_id):
    #     try:
            
    #         # print(single_request_data,'akajsisndf')
            
    #         try:
    #             # Step 4.2: Store ai message request
    #             store_ai_message_request_data = self.ai_message_request_store_service.store_ai_message_request(single_request_data)
    #             # print(store_ai_message_request_data, '----------------------store_ai_message_request_data----------------------')
    #         except Exception as e:
    #             print({"status": "error", "step": "store_ai_message_request", "message": str(e)})
    #             # return {"status": "error", "step": "store_ai_message_request", "message": str(e)}
                





    #         url = f'{self.ai_rate_limiter_url}/message/publish'

    #         single_ai_response = requests.post(url, json=single_request_data, headers=self.headers)

    #         # print("send_ai_request single_ai_Response Body:", single_ai_response.json())


    #         if single_ai_response.status_code not in [200, 201]:
    #             try:
    #                 error_data = single_ai_response.json() if single_ai_response.text else {}
    #             except ValueError:
    #                 error_data = {}

    #             # Fix: Check for "worker_required" field or message string directly
    #             no_worker_error = (
    #                 isinstance(error_data, dict) and (
    #                     error_data.get("worker_required") is True or 
    #                     "no worker available" in str(error_data.get("message", "")).lower()
    #                 )
    #             )

    #             if no_worker_error:
    #                 print("No worker available, attempting to scale up...")

    #                 scaled = self.ai_rate_limiter_scale_worker.scale_worker(str(workspace_slug_id))

    #                 if scaled:
    #                     print("Successfully initiated worker scale up")
    #                     single_ai_response = requests.post(
    #                         url,
    #                         json=single_request_data,
    #                         headers=self.headers,
    #                         timeout=30
    #                     )

    #         return single_ai_response.json()

    #     except requests.RequestException as e:
    #         return f"Request to ai lambda failed: {e}"
    #     except Exception as e:
    #         return f"An unexpected error occurred: {e}"
    
    
    
    
    
    
    
    
    
    # def send_single_ai_request(self, single_request_data, workspace_slug_id):
    #     try:
    #         # Step 4.2: Store ai message request
    #         try:
    #             self.ai_message_request_store_service.store_ai_message_request(single_request_data)
    #         except Exception as e:
    #             print({"status": "error", "step": "store_ai_message_request", "message": str(e)})

    #         url = f'{self.ai_rate_limiter_url}/message/publish'
    #         max_retries = 1
    #         response = None

    #         for attempt in range(1, max_retries + 1):
    #             try:
    #                 print(f"[Attempt {attempt}] Sending AI request...")
    #                 response = requests.post(url, json=single_request_data, headers=self.headers, timeout=30)

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
    #                     scaled = self.ai_rate_limiter_scale_worker.scale_worker(str(workspace_slug_id))
    #                     if scaled:
    #                         print("Successfully initiated worker scale up")

    #             except requests.RequestException as e:
    #                 print(f"[Attempt {attempt}] RequestException: {e}")

    #             except Exception as e:
    #                 print(f"[Attempt {attempt}] General Exception: {e}")

    #         return {
    #             "success": False,
    #             "error": f"Failed after {max_retries} attempts",
    #             "message_id": single_request_data.get("message_id")
    #         }

    #     except Exception as e:
    #         return {"success": False, "error": f"Unexpected error: {e}"}














    def send_single_ai_request(self, single_request_data, workspace_slug_id):
        try:
            

            # Step 4.2: Store AI message request
            try:
                self.ai_message_request_store_service.store_ai_message_request(single_request_data)
            except Exception as e:
                error_msg = f"Error storing AI message request: {str(e)}"
                print({"status": "error", "step": "store_ai_message_request", "message": error_msg})
                return {
                    "success": False,
                    "error": error_msg,
                    "message_id": single_request_data.get("message_id")
                }

            url = f'{self.ai_rate_limiter_url}/message/publish'
            max_retries = 2
            response = None

            for attempt in range(1, max_retries + 1):
                try:
                    print(f"[Attempt {attempt}] Sending AI request...")
                    response = requests.post(url, json=single_request_data, headers=self.headers, timeout=30)

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
                        scaled = self.ai_rate_limiter_scale_worker.scale_worker(str(workspace_slug_id))
                        if scaled:
                            print("Successfully initiated worker scale up")

                except requests.RequestException as e:
                    print(f"[Attempt {attempt}] RequestException: {e}")
                    if attempt == max_retries:
                        return {
                            "success": False,
                            "error": f"RequestException after {max_retries} attempts: {e}",
                            "message_id": single_request_data.get("message_id")
                        }

                except Exception as e:
                    print(f"[Attempt {attempt}] General Exception: {e}")
                    if attempt == max_retries:
                        return {
                            "success": False,
                            "error": f"Exception after {max_retries} attempts: {e}",
                            "message_id": single_request_data.get("message_id")
                        }

            return {
                "success": False,
                "error": f"Failed after {max_retries} attempts, status: {response.status_code if response else 'No Response'}",
                "message_id": single_request_data.get("message_id")
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected outer error: {e}",
                "message_id": single_request_data.get("message_id")
            }






