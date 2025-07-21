import requests
import os
import json
import time
import logging
from app.workers.core.article_innovator_api_call.api_client.api_client import APIClient
from app.workers.url_rewriter_para_request_helpers.get_single_ai_response import GetSingleAiResponse
from app.workers.url_rewriter_para_response_helpers.ai_message_response_store import AIMessageResponseStore

class GetInputJson:
    def __init__(self):
        self.headers = {
            "Content-Type": "application/json"
        }
        
        self.api_client = APIClient()
        self.get_single_ai_response_service = GetSingleAiResponse()
        self.ai_message_response_store_service = AIMessageResponseStore()
 

    # def get_input_json_data(self, request_data, article_id):
    #     try:           
    #         message_data = request_data.get("message", {})
            
    #         if not isinstance(message_data, dict):
    #             return {"success": False, "error": "Invalid message data format"}

    #         # Validate required IDs (ensure they are strings before strip)
    #         article_id = str(message_data.get("article_id", "")).strip()
           
    #         params = {
    #             'article_slug_id': article_id,
    #         }

    #         input_json_data = self.api_client.crud('input-json', 'read', params=params)
                   
    #         # Save original input
    #         with open('demo_json/input_json_data.json', 'w', encoding='utf-8') as f:
    #             json.dump(input_json_data, f, ensure_ascii=False, indent=4)
 
    #         return input_json_data            

    #     except Exception as e:
    #         print(f"[get_input_json_data] Exception: {e}")
    #         return {"success": False, "error": f"Unexpected error: {str(e)}"}




    def get_input_json_data_to_article_innovator(self, request_data):
        try:           
            message_data = request_data.get("message", {})
            
            if not isinstance(message_data, dict):
                return {"success": False, "error": "Invalid message data format"}

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
            return {"success": False, "error": f"Unexpected error: {str(e)}"}




    # def get_input_json_data_to_article_innovator(self, request_data):
    #     try:
    #         # Extract article_id from request_data
    #         if request_data is not None:
    #             message_data = request_data.get("message", {})
    #             if not isinstance(message_data, dict):
    #                 return {"success": False, "error": "Invalid message data format"}
    #             article_id = str(message_data.get("article_id", "")).strip()
    #         else:
    #             return {"success": False, "error": "Missing request_data"}

    #         if not article_id:
    #             return {"success": False, "error": "Missing article_id"}

    #         params = {
    #             'article_slug_id': article_id,
    #         }

    #         input_json_data = self.api_client.crud('input-json', 'read', params=params)

    #         # Save original input
    #         with open('demo_json/input_json_data.json', 'w', encoding='utf-8') as f:
    #             json.dump(input_json_data, f, ensure_ascii=False, indent=4)

    #         return input_json_data

    #     except Exception as e:
    #         print(f"[get_input_json_data] Exception: {e}")
    #         return {"success": False, "error": f"Unexpected error: {str(e)}"}











    def get_input_json_data_for_wp(self, article_id):
        try:
            # Use article_id if provided; else get from request_data
            
            article_id = str(article_id).strip()
            
            if not article_id:
                return {"success": False, "error": "Missing article_id"}

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
            return {"success": False, "error": f"Unexpected error: {str(e)}"}
