import requests
import os
import json
import time
import logging
from app.workers.core.article_innovator_api_call.api_client.api_client import APIClient
from app.workers.core.calculate_priority.calculate_priority import CalculatePriority



class AIMessage:
    def __init__(self):
        self.headers = {
            "Content-Type": "application/json"
        }
        self.api_client = APIClient()
        self.calculate_priority_service = CalculatePriority()
        
      
    def store_ai_message_request(self, data):
        try:

            print(data, 'dataxxxxxxxxxx!!!!!!!!!1')

            # Extract required fields from the incoming data
            article_id = str(data.get("article_id", "")).strip()
            message_id = str(data.get("message_id", "")).strip()

            if not article_id or not message_id:
                raise ValueError({"success": False, "error": "Missing article_id or message_id"})

            request_data = {
                "article_id": article_id,
                "message_id": message_id,
                "article_message_total_count": data.get("article_message_total_count", 0),
                # "article_message_count": data.get("article_message_count", 1),
                # "ai_request": json.dumps(data.get("prompt", [])),  # store as JSON string
                "ai_request": json.dumps(data),  # store as JSON string
                "ai_request_status": data.get("ai_request_status", ""),
                "message_field_type": data.get("message_field_type", ""),
                "message_priority": data.get("message_priority", ""),
                # "article_message_count":1,
            }

            max_retries = 3
            stored_message = None

            for attempt in range(1, max_retries + 1):
                stored_message = self.api_client.crud(
                    'ai-message',
                    'create',
                    data=request_data
                )

                # print(f"[store_ai_message_request] Attempt {attempt}, Response: {stored_message}")

                if stored_message.get('status_code') == 200:
                    return stored_message
                else:
                    print(f"[store_ai_message_request] Attempt {attempt} failed. Retrying...")

            return {
                "success": False,
                "error": f"Failed to update after {max_retries} attempts",
                "last_response": stored_message,
            }


        except Exception as e:
            print(f"[store_ai_message_request] Exception: {e}")
            # return {"success": False, "error": f"Unexpected error: {str(e)}"}
            raise ValueError({"success": False, "error": f"Unexpected error: {str(e)}"})
        
        
        


    def check_if_prompt_already_stored(self, article_id, message_field_type):
        try:
            params = {
                'article_slug_id': article_id,
                'message_field_type': message_field_type,
            }

            all_messages = self.api_client.crud('ai-message', 'read', params=params)

            if all_messages.get("success") is True and "data" in all_messages and all_messages["data"]:
                return {
                    "success": True,
                    "data": all_messages["data"]
                }

            return {
                "success": False,
                "message": "No message data found."
            }
            # raise ValueError("No message data found.")


        except Exception as e:
            print(f"[get_stored_message] Exception: {e}")
            # return {
            #     "success": False,
            #     "message": str(e)
            # }
            raise ValueError(f"[get_stored_message] Exception: {e}")



    # def store_ai_message_response(self, data, message_retry_count=3):
    #     """
    #     Store AI message response or trigger retry if ai_response_status indicates failure.
    #     """
    #     try:
    #         message_data = data.get("message", {})
    #         if not isinstance(message_data, dict):
    #             # return {"success": False, "error": "Invalid message data format"}
    #             raise ValueError({"success": False, "error": "Invalid message data format"})

    #         # IDs
    #         article_id = str(message_data.get("article_id", "")).strip()
    #         message_id = str(message_data.get("message_id", "")).strip()
    #         if not article_id or not message_id:
    #             # return {"success": False, "error": "Missing article_id or message_id"}
    #             raise ValueError({"success": False, "error": "Missing article_id or message_id"})

    #         ai_response = message_data.get("ai_response", {})
    #         ai_response_status = message_data.get("ai_response_status")
    #         message_field_type = message_data.get("message_field_type")

    #         # Helper: detect failure
    #         def is_failure(status):
    #             if status is False or status is None:
    #                 return True
    #             s = str(status).strip().lower()
    #             return s in {"failed", "fail", "error", "false"}

    #         # Prepare normal request payload
    #         request_data = {
    #             "article_id": article_id,
    #             "message_id": message_id,
    #             "article_message_count": message_data.get("article_message_count", 0),
    #             "article_message_total_count": message_data.get("article_message_total_count", 0),
    #             "ai_response": json.dumps(ai_response),
    #             "ai_response_status": ai_response_status,
    #         }

    #         request_item_id = f"{article_id}/{message_id}"

    #         # If AI response failed → schedule retry
    #         if is_failure(ai_response_status):
    #             # ✅ Get existing retry_count from DB
    #             retry_count = 0
    #             message_priority = 0
    #             db_record = None
    #             try:
    #                 existing_data = self.get_ai_message(article_id, message_id)
    #                 if existing_data.get("success") and existing_data["data"]:
    #                     db_record = existing_data["data"][0]  # Assuming data is a list
    #                     retry_count = int(db_record.get("retry_count", 0))
    #                     message_priority = int(db_record.get("message_priority", 0))
    #             except Exception as e:
    #                 # print(f"[store_ai_message_response] Error fetching retry_count: {e}")
    #                 raise ValueError(f"[store_ai_message_response] Error fetching retry_count: {e}")

    #             # ✅ Increment retry count
    #             retry_count += 1
    #             base_priority = self.calculate_priority_service.extract_base_priority(message_priority, message_field_type)
    #             priority = self.calculate_priority_service.calculate_priority(base_priority, f'retry_{message_field_type}')

    #             if retry_count > message_retry_count:
    #                 return {
    #                     "success": False,
    #                     "error": f"Retry limit reached ({message_retry_count})",
    #                     "retry_count": retry_count
    #                 }

    #             retry_payload = {
    #                 "article_id": article_id,
    #                 "message_id": message_id,
    #                 "ai_request_status": "retry",
    #                 "retry_count": retry_count,
    #                 "message_priority": priority,

    #             }

    #             # Update DB with retry status
    #             try:
    #                 resp_retry = self.api_client.crud(
    #                     "ai-message",
    #                     "update",
    #                     data=retry_payload,
    #                     item_id=request_item_id
    #                 )
    #             except Exception as e:
    #                 print(f"[store_ai_message_response] Retry status update exception: {e}")
    #                 resp_retry = {"status_code": None, "error": str(e)}

    #             # Call retry_message method (adjust args as needed)
    #             try:
    #                 from app.workers.url_rewriter_content_helpers.ai_rate_limiter_request import AIRateLimiterService
    #                 self.retry_failed_messages_service = AIRateLimiterService()

    #                 self.retry_failed_messages_service.retry_failed_messages(resp_retry=resp_retry)
    #             except Exception as e:
    #                 print(f"[store_ai_message_response] retry_message exception: {e}")

    #             return {
    #                 "success": False,
    #                 "error": "AI response failed; retry scheduled.",
    #                 "retry_count": retry_count,
    #                 "retry_update_response": resp_retry,
    #             }

    #         # Normal flow: store AI response
    #         max_retries = 3
    #         stored_message = None
    #         for attempt in range(1, max_retries + 1):
    #             stored_message = self.api_client.crud(
    #                 "ai-message",
    #                 "update",
    #                 data=request_data,
    #                 item_id=request_item_id
    #             )
    #             if stored_message.get("status_code") == 200:
    #                 return stored_message
    #             else:
    #                 print(f"[store_ai_message_response] Attempt {attempt} failed with status_code {stored_message.get('status_code')}. Retrying...")

    #         # All attempts failed
    #         return {
    #             "success": False,
    #             "error": f"Failed to update after {max_retries} attempts",
    #             "last_response": stored_message,
    #         }

    #     except Exception as e:
    #         print(f"[store_ai_message_response] Exception: {e}")
    #         return {"success": False, "error": f"Unexpected error: {str(e)}"}



    def store_ai_message_response(self, data, message_retry_count=3):
        """
        Store AI message response or trigger retry if ai_response_status indicates failure.
        Raises ValueError or RuntimeError on error conditions.
        """
        try:
            message_data = data.get("message", {})
            if not isinstance(message_data, dict):
                raise ValueError("Invalid message data format")

            article_id = str(message_data.get("article_id", "")).strip()
            message_id = str(message_data.get("message_id", "")).strip()
            if not article_id or not message_id:
                raise ValueError("Missing article_id or message_id")

            ai_response = message_data.get("ai_response", {})
            ai_response_status = message_data.get("ai_response_status")
            message_field_type = message_data.get("message_field_type")

            def is_failure(status):
                if status is False or status is None:
                    return True
                s = str(status).strip().lower()
                return s in {"failed", "fail", "error", "false"}

            request_data = {
                "article_id": article_id,
                "message_id": message_id,
                "article_message_count": message_data.get("article_message_count", 0),
                "article_message_total_count": message_data.get("article_message_total_count", 0),
                "ai_response": json.dumps(ai_response),
                "ai_response_status": ai_response_status,
            }

            request_item_id = f"{article_id}/{message_id}"

            if is_failure(ai_response_status):
                retry_count = 0
                message_priority = 0
                try:
                    existing_data = self.get_ai_message(article_id, message_id)
                    if existing_data.get("success") and existing_data["data"]:
                        db_record = existing_data["data"][0]
                        retry_count = int(db_record.get("retry_count", 0))
                        message_priority = int(db_record.get("message_priority", 0))
                except Exception as e:
                    raise RuntimeError(f"[store_ai_message_response] Error fetching retry_count: {e}")

                retry_count += 1
                base_priority = self.calculate_priority_service.extract_base_priority(message_priority, message_field_type)
                priority = self.calculate_priority_service.calculate_priority(base_priority, f'retry_{message_field_type}')

                if retry_count > message_retry_count:
                    raise RuntimeError(f"Retry limit reached ({message_retry_count})")

                retry_payload = {
                    "article_id": article_id,
                    "message_id": message_id,
                    "ai_request_status": "retry",
                    "retry_count": retry_count,
                    "message_priority": priority,
                }

                try:
                    resp_retry = self.api_client.crud(
                        "ai-message",
                        "update",
                        data=retry_payload,
                        item_id=request_item_id
                    )
                except Exception as e:
                    raise RuntimeError(f"[store_ai_message_response] Retry status update exception: {e}")

                try:
                    from app.workers.url_rewriter_content_helpers.ai_rate_limiter_request import AIRateLimiterService
                    self.retry_failed_messages_service = AIRateLimiterService()
                    self.retry_failed_messages_service.retry_failed_messages(resp_retry=resp_retry)
                except Exception as e:
                    raise RuntimeError(f"[store_ai_message_response] retry_message exception: {e}")

                raise RuntimeError(f"AI response failed; retry scheduled. Retry count: {retry_count}")

            # Normal flow: store AI response
            max_retries = 3
            for attempt in range(1, max_retries + 1):
                stored_message = self.api_client.crud(
                    "ai-message",
                    "update",
                    data=request_data,
                    item_id=request_item_id
                )
                if stored_message.get("status_code") == 200:
                    return stored_message
                print(f"[store_ai_message_response] Attempt {attempt} failed. Retrying...")

            raise RuntimeError(f"Failed to update after {max_retries} attempts")

        except Exception as e:
            print(f"[store_ai_message_response] Exception: {e}")
            raise  # Reraise the last caught exception






    def get_all_stored_content_message(self, article_id, message_field_type):
        try:
           
            params = {
                'article_slug_id': article_id,
                'message_field_type': message_field_type,
            }

            all_messages = self.api_client.crud('ai-message', 'read', params=params)
            
            if all_messages.get("success") and "data" in all_messages:
                # Save the data to a JSON file
                with open('demo_json/all_message_data.json', 'w', encoding='utf-8') as f:
                    json.dump(all_messages["data"], f, ensure_ascii=False, indent=4)

            print(all_messages, '----------------------all_messages----------------------')                    
            return all_messages            

        except Exception as e:
            print(f"[get_all_stored_message] Exception: {e}")
            # return {"success": False, "error": f"Unexpected error: {str(e)}"}
            raise ValueError({"success": False, "error": f"Unexpected error: {str(e)}"})







    def get_ai_message(self, article_id, message_id):
        try:
            params = {
                'article_slug_id': article_id,
                'message_id': message_id,
            }

            message_data = self.api_client.crud('ai-message', 'read', params=params)

            if message_data.get("success") is True and "data" in message_data and message_data["data"]:
                return {
                    "success": True,
                    "data": message_data["data"]
                }

            # return {
            #     "success": False,
            #     "message": "No message data found."
            # }

            raise ValueError("No message data found.")

        except Exception as e:
            print(f"[get_stored_message] Exception: {e}")
            # return {
            #     "success": False,
            #     "message": str(e)
            # }
            raise ValueError(f"[get_stored_message] Exception: {e}")
            
            
    
    def get_input_json_data_to_article_innovator(self, request_data):
        try:           
            message_data = request_data.get("message", {})
            
            if not isinstance(message_data, dict):
                # return {"success": False, "error": "Invalid message data format"}
                raise ValueError({"success": False, "error": "Invalid message data format"})

            # Validate required IDs (ensure they are strings before strip)
            article_id = str(message_data.get("article_id", "")).strip()
           
            params = {
                'article_slug_id': article_id,
            }

            input_json_data = self.api_client.crud('input-json', 'read', params=params)
                   
            # Save original input
            with open('demo_json/input_json_data.json', 'w', encoding='utf-8') as f:
                json.dump(input_json_data, f, ensure_ascii=False, indent=4)
 
            return input_json_data            

        except Exception as e:
            print(f"[get_input_json_data] Exception: {e}")
            # return {"success": False, "error": f"Unexpected error: {str(e)}"}
            raise ValueError({"success": False, "error": f"Unexpected error: {str(e)}"})



    def get_all_stored_wp_message(self, article_id):
        try:
            params = {
                'article_slug_id': article_id,
                'publish_article': 'true',
            }

            response = self.api_client.crud('ai-message', 'read', params=params)

            if response.get("success") and isinstance(response.get("data"), list):
                all_messages = response["data"]
                successful_messages = [m for m in all_messages if m.get("ai_response_status") == "success"]

                # Save all messages to file
                os.makedirs('demo_json', exist_ok=True)
                with open('demo_json/final_all_wp_message_data.json', 'w', encoding='utf-8') as f:
                    json.dump(response, f, indent=4)

                return {
                    "success": True,
                    "total_messages": len(all_messages),
                    "total_successful_messages": len(successful_messages),
                    "data": successful_messages
                }

            # return {"success": False, "message": "No data found"}
            raise ValueError({"success": False, "message": "No data found"})
        except Exception as e:
            # return {"success": False, "message": str(e)}
            raise ValueError({"success": False, "message": str(e)})


    def get_all_stored_message(self, article_id):
        try:
            params = {
                'article_slug_id': article_id,
            }

            response = self.api_client.crud('ai-message', 'read', params=params)

            if response.get("success") and isinstance(response.get("data"), list):
                all_messages = response["data"]
                successful_messages = [m for m in all_messages if m.get("ai_response_status") == "success"]

                # Save all messages to file
                os.makedirs('demo_json', exist_ok=True)
                with open('demo_json/final_all_message_data.json', 'w', encoding='utf-8') as f:
                    json.dump(response, f, indent=4)

                # ✅ Check if all messages are successful
                all_success = len(all_messages) > 0 and len(successful_messages) == len(all_messages)

                return {
                    "success": True,
                    "total_messages": len(all_messages),
                    "total_successful_messages": len(successful_messages),
                    "all_success": all_success,
                    "data": successful_messages
                }

            # return {"success": False, "message": "No data found"}
            raise ValueError({"success": False, "message": "No data found"})
        except Exception as e:
            raise ValueError({"success": False, "message": str(e)})
