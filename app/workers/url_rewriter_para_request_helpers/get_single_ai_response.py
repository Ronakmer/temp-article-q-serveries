import requests
import os
import time
import json
import uuid
from app.workers.core.article_innovator_api_call.api_client.api_client import APIClient
from app.config.logger import LoggerSetup
from app.config.config import AI_RATE_LIMITER_URL
from app.workers.url_rewriter_para_request_helpers.ai_rate_limiter_scale_worker import AIRateLimiterScaleWorker

class GetSingleAiResponse:
    def __init__(self):
        self.api_client = APIClient()

        # logger_setup = LoggerSetup()
        self.ai_rate_limiter_scale_worker = AIRateLimiterScaleWorker()
        # self.logger = logger_setup.setup_worker_logger(self.pid)
        self.ai_rate_limiter_url = AI_RATE_LIMITER_URL
        self.headers = {
            "Content-Type": "application/json"
        }

       
    # def get_single_ai_response(self, message_id):
    #     try:
            
    #         max_retries = 5
    #         delay_seconds = 90
            

    #         for attempt in range(1, max_retries + 1):
    #             try:
    #                 url = f'{self.ai_rate_limiter_url}/message/{message_id}'
    #                 response = requests.get(url, headers=self.headers)

    #                 if response.status_code in [200, 201]:
    #                     response_data = response.json()
    #                     print(response_data, 'single_ai_responsexxxxxxxxxx')
    #                     data_obj = {}
                        
    #                     # Check if status is 'pending'
    #                     if response_data.get("ai_response_status") == "pending":
    #                         print(f"Attempt {attempt}: Response pending. Retrying after {delay_seconds} seconds...")
    #                         if attempt < max_retries:
    #                             time.sleep(delay_seconds)
    #                             continue
                            
    #                         data_obj = {
    #                             "message": response_data,
    #                         }
    #                     return data_obj  # Success or final attempt

    #                 else:
    #                     print(f"Attempt {attempt}: Unexpected status code {response.status_code}")
    #                     return response.json()

    #             except requests.RequestException as e:
    #                 print(f"Attempt {attempt}: Request to AI lambda failed: {e}")
    #                 if attempt < max_retries:
    #                     time.sleep(delay_seconds)
    #             except Exception as e:
    #                 print(f"Attempt {attempt}: Unexpected error: {e}")
    #                 if attempt < max_retries:
    #                     time.sleep(delay_seconds)

    #         return {"error": "Max retries exceeded or failed to get a valid response"}

    #     except Exception as e:
    #         return f"An unexpected error occurred: {e}"
    
    
    
    

    # def get_single_ai_response(self, message_id):
    #     try:
    #         max_retries = 2
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

    #                     # Ensure response_data is a dict
    #                     if isinstance(response_data, dict):
    #                         data_obj = {
    #                             "message": response_data
    #                         }

    #                         if response_data.get("ai_response_status") == "pending":
    #                             print(f"Attempt {attempt}: Response pending. Retrying after {delay_seconds} seconds...")
    #                             if attempt < max_retries:
    #                                 time.sleep(delay_seconds)
    #                                 continue

    #                         return data_obj  # final return

    #                     else:
    #                         return {"message": {"error": "Response is not a valid JSON object"}}

    #                 else:
    #                     print(f"Attempt {attempt}: Unexpected status code {response.status_code}")
    #                     return {"message": {"error": f"Status code {response.status_code}"}}  # wrapped

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
            max_retries = 3
            delay_seconds = 30

            for attempt in range(1, max_retries + 1):
                try:
                    url = f'{self.ai_rate_limiter_url}/message/{message_id}'
                    response = requests.get(url, headers=self.headers)

                    if response.status_code in [200, 201]:
                        try:
                            response_data = response.json()
                        except ValueError:
                            return {"message": {"error": "Invalid JSON response"}}

                        if isinstance(response_data, dict):
                            data_obj = {
                                "message": response_data
                            }

                            status = response_data.get("ai_response_status")
                            if status in ["pending", "processing"]:
                                print(f"Attempt {attempt}: Response status '{status}'. Retrying after {delay_seconds} seconds...")
                                if attempt < max_retries:
                                    time.sleep(delay_seconds)
                                    continue

                            return data_obj

                        else:
                            return {"message": {"error": "Response is not a valid JSON object"}}

                    else:
                        print(f"Attempt {attempt}: Unexpected status code {response.status_code}")
                        return {"message": {"error": f"Status code {response.status_code}"}}  

                except requests.RequestException as e:
                    print(f"Attempt {attempt}: Request failed: {e}")
                    if attempt < max_retries:
                        time.sleep(delay_seconds)

                except Exception as e:
                    print(f"Attempt {attempt}: Unexpected error: {e}")
                    if attempt < max_retries:
                        time.sleep(delay_seconds)

            return {"message": {"error": "Max retries exceeded"}}

        except Exception as e:
            return {"message": {"error": f"Unexpected error: {str(e)}"}}
