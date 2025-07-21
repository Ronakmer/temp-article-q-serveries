import requests
import os
import json
import time
import logging
from app.workers.core.article_innovator_api_call.api_client.api_client import APIClient
from app.workers.core.article_innovator_api_call.wordpress.add_category.add_category import AddCategory


class AIMessageResponseStore:
    def __init__(self):
        self.headers = {
            "Content-Type": "application/json"
        }
        
        self.api_client = APIClient()
        self.add_category_service = AddCategory()
        

    # def store_ai_message_response(self, data):
    #     try:
    #         message_data = data.get("message", {})

    #         # Validate required IDs
    #         article_id = message_data.get("article_id", "").strip()
    #         message_id = message_data.get("message_id", "").strip()

    #         if not article_id or not message_id:
    #             return {"success": False, "error": "Missing article_id or message_id"}

    #         # Prepare request payload (omit ai_request)
    #         request_data = {
    #             "article_id": article_id,
    #             "message_id": message_id,
    #             "article_message_count": message_data.get("article_message_count", 0),
    #             "article_message_total_count": message_data.get("article_message_total_count", 0),
    #             "ai_response": json.dumps(message_data),  # Convert full message to JSON string
    #             "ai_response_status": message_data.get("ai_response_status", "success"),
    #         }

    #         # Combine article_id and message_id as item_id
    #         request_item_id = f"{article_id}/{message_id}"
            
            
    #         max_retries = 3
    #         for attempt in range(1, max_retries + 1):
    #             stored_message = self.api_client.crud(
    #                 'ai-message',
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

    #         # # API call (PATCH)
    #         # stored_message = self.api_client.crud(
    #         #     'ai-message',
    #         #     'update',
    #         #     data=request_data,
    #         #     item_id=request_item_id
    #         # )

    #         # print(stored_message, 'stored_message [debug]')
            
    #         # return stored_message
            

    #     except Exception as e:
    #         print(f"[store_ai_message] Exception: {e}")
    #         return {"success": False, "error": f"Unexpected error: {str(e)}"}


 


    def store_ai_message_response(self, data):
        try:
            # print(data,'dataxxxxxxxxxx')
            message_data = data.get("message", {})
            
            if not isinstance(message_data, dict):
                return {"success": False, "error": "Invalid message data format"}


            # Validate required IDs (ensure they are strings before strip)
            article_id = str(message_data.get("article_id", "")).strip()
            message_id = str(message_data.get("message_id", "")).strip()
            ai_response = message_data.get("ai_response", {})

            if not article_id or not message_id:
                return {"success": False, "error": "Missing article_id or message_id"}

            # Prepare payload for update (store full message as JSON string)
            request_data = {
                "article_id": article_id,
                "message_id": message_id,
                "article_message_count": message_data.get("article_message_count", 0),
                "article_message_total_count": message_data.get("article_message_total_count", 0),  
                # "ai_response": json.dumps(message_data),  # full message JSON as string
                "ai_response": json.dumps(ai_response),  # full message JSON as string
                "ai_response_status": message_data.get("ai_response_status"),
            }

            # Use combined IDs as item_id for the update call
            request_item_id = f"{article_id}/{message_id}"

            max_retries = 3
            stored_message = None

            for attempt in range(1, max_retries + 1):
                stored_message = self.api_client.crud(
                    'ai-message',
                    'update',
                    data=request_data,
                    item_id=request_item_id
                )


                # print(f"[store_ai_message_response] Attempt {attempt}, Response: {stored_message}")
                
                if stored_message.get('status_code') == 200:
                    
                    return stored_message
                else:
                    print(f"[store_ai_message_response] Attempt {attempt} failed with status_code {stored_message.get('status_code')}. Retrying...")

            # All retries failed
            return {
                "success": False,
                "error": f"Failed to update after {max_retries} attempts",
                "last_response": stored_message,
            }

        except Exception as e:
            print(f"[store_ai_message_response] Exception: {e}")
            return {"success": False, "error": f"Unexpected error: {str(e)}"}
