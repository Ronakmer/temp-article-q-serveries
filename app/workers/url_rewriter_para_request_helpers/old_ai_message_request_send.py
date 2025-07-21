import requests
import os
from app.workers.url_rewriter_para_request_helpers.content_processor import ContentProcessor
import time
import json
import uuid
from app.config.config import AI_RATE_LIMITER_URL



import logging
import json
import time

class AIRateLimiterService:
    def __init__(self):
        self.ai_rate_limiter_url = AI_RATE_LIMITER_URL
        self.headers = {
            "Content-Type": "application/json"
        }
        
        self.content_handler = ContentProcessor()
        

    def fetch_and_process_content(self, scraped_content, input_json_data):
        try:
            print('2222222222222222222222222222222222')
            # Fetch content
            content_data = self.content_handler.fetch_content(scraped_content)
            if not content_data:
                return None, False
                    
            if isinstance(content_data, dict):
                request_data = self.content_handler.process_content(content_data, input_json_data)

            # for tesing  
            with open('result_data.json', 'w', encoding='utf-8') as f:
                json.dump(request_data, f, ensure_ascii=False, indent=4)
                    
            return request_data

            # return request_data
            # return_data = self.send_ai_request(request_data)

        except Exception as e:
            return f"An unexpected error occurred: {e}"


    # def scale_worker(self, worker_id, count=1):
    #     scale_url = f"{self.ai_rate_limiter_url}/workers/scale/{worker_id}"        
    #     scale_data = {"count": count}
    #     headers = {'Content-Type': 'application/json'}

    #     try:
    #         response = requests.post(scale_url, json=scale_data, headers=headers)
    #         if response.status_code in [200, 201]:
    #             print(f"Successfully scaled worker {worker_id} with count {count}")
    #             return True
    #         else:
    #             print(f"Failed to scale worker: {response.status_code} - {response.text}")
    #             return False
    #     except requests.RequestException as e:
    #         print(f"Exception during scaling worker: {e}")
    #         return False
          
       
    def send_single_ai_request(self, single_request_data):
        try:
            print('!!!!!!!!!!!!!!!!!!!!!!!!!')
            
            print(single_request_data)
            
            url = f'{self.ai_rate_limiter_url}/message/publish'

            response = requests.post(url, json=single_request_data, headers=self.headers)

            print("send_ai_request Response Body:", response.json())
            
                
            if response.status_code not in [200, 201]:
                return f"send ai request returned an error: {response.status_code} - {response.text}"

            print('000000000000000000----00000000000000000')
            
            merged_entry = {
                "ai_request": single_request_data,
                "ai_response": response.json()
            }


            # for tesing  
            with open('merged_entry.json', 'w', encoding='utf-8') as f:
                json.dump(merged_entry, f, ensure_ascii=False, indent=4)
                    

            return merged_entry

        except requests.RequestException as e:
            return f"Request to ai lambda failed: {e}"
        except Exception as e:
            return f"An unexpected error occurred: {e}"
       


    def send_ai_request(self, request_json_data):
        try:
            print('3333333333333333333333333333333333333333',request_json_data)
            submit_data_responses = []
            
            for single_request_data in request_json_data["ai_requests"]:

                merged_entry = self.send_single_ai_request(single_request_data)
                print(merged_entry,'merged_entryzsdqwe')
                if isinstance(merged_entry, dict):
                    print('this is if')
                    submit_data_responses.append(merged_entry)
                else:
                    print('this is else')
                    print(merged_entry,'sdfsdfsdfmerged_entry')                    
                    return merged_entry      #  this is the same as the below error catch logic
            
            # for tesing  
            with open('message_id_json.json', 'w', encoding='utf-8') as f:
                json.dump(submit_data_responses, f, ensure_ascii=False, indent=4)
            
            
            ai_response_json = self.get_result_data(submit_data_responses)

            if len(ai_response_json) == len(submit_data_responses):
                # final_ai_response = self.merge_and_sequence_ai_response(ai_response_json, request_json_data)
                print(ai_response_json,'send_ai_request---->>>ai_response_json')
                return ai_response_json
            else:
                return 'Request to ai lambda failed'


            # # for test             
            # return submit_data_responses


        except requests.RequestException as e:
            return f"Request to ai lambda failed: {e}"
        except Exception as e:
            return f"An unexpected error occurred: {e}"



    # def get_result_data(self, submitted_data, retry_message_id=3):
    #     try:
    #         # print(submitted_data, 'submitted_data')
    #         print('444444444444444444444444444444')
            
    #         wait_time = 30
    #         retry_count = 5 
    #         result_data = [] 
    #         error_data = []

    #         for single_request_data in submitted_data:
    #             ai_response_data  = single_request_data['ai_response'] 
    #             message_id = ai_response_data["message_id"]
    #             workspace_id = ai_response_data["workspace_id"]
            
    #             dd={
    #                 'ai_response_data':ai_response_data,
    #                 'message_id':message_id,
    #                 'workspace_id':workspace_id,
                    
    #             }
    #             # for tesing  
    #             with open('hhhhhhh.json', 'w', encoding='utf-8') as f:
    #                 json.dump(dd, f, ensure_ascii=False, indent=4)


    #             url = f'{self.ai_rate_limiter_url}/message/{message_id}'

    #             final_response = None
    #             is_500 = False
    #             is_pending = False
                
    #             for attempt in range(1, retry_count + 1):
    #                 try:
    #                     is_500 = False
    #                     is_pending = False
    #                     response = requests.get(url, headers=self.headers)
    #                     print(f"[Attempt {attempt}] Status Code:", response.status_code)

    #                     # if response.status_code == 200:
    #                     if response.status_code not in [200, 201]:
                            
    #                         response_data = response.json()
    #                         print(f"[Attempt {attempt}] Response Body:", response_data)

    #                         if response_data.get("status") == "success":
    #                             result_data.append(response_data)
    #                             break
    #                         else:
    #                             # final_response = response_data
    #                             is_pending = True
    #                             is_500 = False
    #                             print(f"[Attempt {attempt}] Status is pending. Retrying in {wait_time}s...")
    #                             if attempt < retry_count:
    #                                 time.sleep(wait_time)
    #                     else:
    #                         print(f"[Attempt {attempt}] Non-200 response: {response.status_code} -- {response.json()}")
                            
    #                         is_pending = False
    #                         is_500 = True
    #                         # if attempt < retry_count:
    #                         #     time.sleep(wait_time)

    #                 except requests.exceptions.RequestException as e:
    #                     print(f"[Attempt {attempt}] Request error: {e}")
    #                     if attempt < retry_count:
    #                         time.sleep(wait_time)
    #                     else:
    #                         print(f"Request failed after {retry_count} attempts. Error: {e}")
    #                         final_response = {
    #                             "error": str(e),
    #                             "message_id": message_id,
    #                             "workspace_id": workspace_id
    #                         }

    #             if is_500:
    #                 # Non-200 response
    #                 # workspace_id = single_request_data["ai_response"].get("workspace_id")
    #                 # clear_workspace_data = self.clear_workspace(workspace_id)
    #                 # print(clear_workspace_data,'clear_workspace_datasssex')

    #                 # scale_worker_data = self.scale_worker(workspace_id)
    #                 # print(scale_worker_data,'scale_worker_datasssex')
                    
    #                 merged_entry = self.send_single_ai_request(single_request_data['ai_request'])
    #                 if isinstance(merged_entry, dict):
    #                     error_data.append(merged_entry)
    #                 else:
    #                     return merged_entry      #  this is the same as the below error catch logic
                

    #             # If we never broke out with "success", append the final pending/error response
    #             if final_response and not is_pending and not is_500:
    #                 result_data.append(final_response)

    #         if len(error_data) > 0 and retry_message_id > 0:
    #             result_data.extend(self.get_result_data(error_data, retry_message_id=retry_message_id-1))

    #         return result_data
                        
    #     except requests.RequestException as e:
    #         return f"Request to AI lambda failed: {e}"
    #     except Exception as e:
    #         return f"An unexpected error occurred: {e}"



    # # Configure logger
    # logging.basicConfig(
    #     filename='ai_lambda.log',
    #     level=logging.INFO,
    #     format='%(asctime)s [%(levelname)s] %(message)s',
    #     datefmt='%Y-%m-%d %H:%M:%S'
    # )

    # def get_result_data(self, submitted_data, retry_message_id=3):
    #     try:
    #         wait_time = 30
    #         retry_count = 5 
    #         result_data = [] 
    #         error_data = []

    #         for single_request_data in submitted_data:
    #             ai_response_data = single_request_data['ai_response']
    #             message_id = ai_response_data["message_id"]
    #             workspace_id = ai_response_data["workspace_id"]

    #             dd = {
    #                 'ai_response_data': ai_response_data,
    #                 'message_id': message_id,
    #                 'workspace_id': workspace_id,
    #             }

    #             with open('hhhhhhh.json', 'w', encoding='utf-8') as f:
    #                 json.dump(dd, f, ensure_ascii=False, indent=4)

    #             url = f'{self.ai_rate_limiter_url}/message/{message_id}'

    #             final_response = None
    #             is_500 = False
    #             is_pending = False

    #             for attempt in range(1, retry_count + 1):
    #                 try:
    #                     is_500 = False
    #                     is_pending = False
    #                     response = requests.get(url, headers=self.headers)
    #                     logging.info(f"[Attempt {attempt}] Status Code: {response.status_code}")

    #                     if response.status_code not in [200, 201]:
    #                         response_data = response.json()
    #                         logging.info(f"[Attempt {attempt}] Response Body: {response_data}")

    #                         if response_data.get("status") == "success":
    #                             result_data.append(response_data)
    #                             break
    #                         else:
    #                             is_pending = True
    #                             is_500 = False
    #                             logging.warning(f"[Attempt {attempt}] Status is pending. Retrying in {wait_time}s...")
    #                             if attempt < retry_count:
    #                                 time.sleep(wait_time)
    #                     else:
    #                         logging.error(f"[Attempt {attempt}] Non-200 response: {response.status_code} -- {response.json()}")
    #                         is_pending = False
    #                         is_500 = True

    #                 except requests.exceptions.RequestException as e:
    #                     logging.error(f"[Attempt {attempt}] Request error: {e}")
    #                     if attempt < retry_count:
    #                         time.sleep(wait_time)
    #                     else:
    #                         logging.error(f"Request failed after {retry_count} attempts. Error: {e}")
    #                         final_response = {
    #                             "error": str(e),
    #                             "message_id": message_id,
    #                             "workspace_id": workspace_id
    #                         }

    #             if is_500:
    #                 merged_entry = self.send_single_ai_request(single_request_data['ai_request'])
    #                 if isinstance(merged_entry, dict):
    #                     error_data.append(merged_entry)
    #                 else:
    #                     return merged_entry

    #             if final_response and not is_pending and not is_500:
    #                 result_data.append(final_response)

    #         if len(error_data) > 0 and retry_message_id > 0:
    #             result_data.extend(self.get_result_data(error_data, retry_message_id=retry_message_id-1))

    #         return result_data

    #     except requests.RequestException as e:
    #         logging.error(f"Request to AI lambda failed: {e}")
    #         return f"Request to AI lambda failed: {e}"
    #     except Exception as e:
    #         logging.exception("An unexpected error occurred")
    #         return f"An unexpected error occurred: {e}"



    
    # def merge_and_sequence_ai_response(self, ai_response_json, request_json_data):
    #     try:
    #         print('5555555555555555555555555555')
    #         ai_requests = request_json_data.get("ai_requests", [])

    #         merged_ai_response = []

    #         for i, response in enumerate(ai_response_json):
    #             request_item = ai_requests[i] if i < len(ai_requests) else {}

    #             merged_response = {
    #                 **response,
    #                 "html_tag": request_item.get("html_tag"),
    #                 "sequence_index": request_item.get("sequence_index")
    #             }
    #             merged_ai_response.append(merged_response)

    #         final_ai_response = {
    #             "article_id": request_json_data.get("article_id"),
    #             "workspace_id": request_json_data.get("workspace_id"),
    #             "ai_response": merged_ai_response
    #         }

    #         random_filename = f"{uuid.uuid4().hex}_data.json"
    #         with open(random_filename, "w", encoding="utf-8") as f:
    #             json.dump(final_ai_response, f, ensure_ascii=False, indent=4)

    #         return final_ai_response

    #     except requests.RequestException as e:
    #         return f"merge and sequence result data failed: {e}"
    #     except Exception as e:
    #         return f"An unexpected error occurred: {e}"





















    # def merge_and_sequence_ai_response(self,ai_response_json, request_json_data):
    #     try:
    #         # === Merge html_tag into AI responses ===
    #         tag_map = {
    #             req["message_id"]: req.get("html_tag")
    #             for req in request_json_data.get("ai_requests", [])
    #         }

    #         merged_ai_response = []
    #         for response in ai_response_json:
    #             message_id = response.get("message_id")
    #             html_tag = tag_map.get(message_id)

    #             merged_response = {
    #                 **response,
    #                 "html_tag": html_tag
    #             }
    #             merged_ai_response.append(merged_response)

    #         final_ai_response = {
    #             "article_id": request_json_data.get("article_id"),
    #             "workspace_id": request_json_data.get("workspace_id"),
    #             "ai_response": merged_ai_response
    #         }
            
    #         random_filename = f"{uuid.uuid4().hex}_data.json"
    #         with open(random_filename, "w", encoding="utf-8") as f:
    #             json.dump(final_ai_response, f, ensure_ascii=False, indent=4)
                
    #         return final_ai_response

           
    #     except requests.RequestException as e:
    #         return f"merge and sequence result data failed: {e}"
    #     except Exception as e:
    #         return f"An unexpected error occurred: {e}"





      
    # def get_result_data(self, submitted_data):
    #     try:
    #         print(submitted_data, 'submitted_data')

    #         wait_time = 30
    #         retry_count = 5 
    #         result_data = []
            
    #         # submitted_data = [
    #         #     {
    #         #         "message":"Message queued for processing",
    #         #         "message_id":"38f68192-11a4-4676-8813-4d2196353c35",
    #         #         "provider":"openai",
    #         #         "sequence_index":"caaa4159-f8ce-437e-801d-4bf7dd9648e4-0",
    #         #         "status":"success",
    #         #         "workspace_id":"4f79ba74-84cc-43ec-bc4f-000000000006"
    #         #     },
    #         #     {
    #         #         "message":"Message queued for processing",
    #         #         "message_id":"38f68192-11a4-4676-8813-4d2196353c35",
    #         #         "provider":"openai",
    #         #         "sequence_index":"caaa4159-f8ce-437e-801d-4bf7dd9648e4-1",
    #         #         "status":"success",
    #         #         "workspace_id":"4f79ba74-84cc-43ec-bc4f-000000000006"
    #         #     }
    #         # ]

    #         for single_request_data in submitted_data:
    #             message_id = single_request_data["message_id"]
    #             workspace_id = single_request_data["workspace_id"]
    #             print(workspace_id,'mkmkmkmkmkmkmkmkmkmkmk')
                
    #             url = f'{self.ai_rate_limiter_url}/result/{workspace_id}/{message_id}'

    #             for attempt in range(1, retry_count + 1):
    #                 try:
    #                     response = requests.get(url, headers=self.headers)
    #                     print(f"[Attempt {attempt}] Status Code:", response.status_code)

    #                     if response.status_code == 200:
    #                         response_data = response.json()
    #                         print(f"[Attempt {attempt}] Response Body:", response_data)
    #                         result_data.append(response_data)
    #                         break  # Success, exit retry loop
    #                     else:
    #                         print(f"[Attempt {attempt}] Non-200 response: {response.status_code}")
    #                         if attempt < retry_count:
    #                             time.sleep(wait_time)

    #                 except requests.exceptions.RequestException as e:
    #                     print(f"[Attempt {attempt}] Request error: {e}")
    #                     if attempt < retry_count:
    #                         time.sleep(wait_time)
    #                     else:
    #                         print(f"Request failed after {retry_count} attempts. Error: {e}")
    #                         result_data.append({
    #                             "error": str(e),
    #                             "message_id": message_id,
    #                             "workspace_id": workspace_id
    #                         })

    #         # return result_data
    #         print(result_data,'sesesesesesesesese')
            
    #     except requests.RequestException as e:
    #         return f"Request to ai lambda failed: {e}"
    #     except Exception as e:
    #         return f"An unexpected error occurred: {e}"
 
 
