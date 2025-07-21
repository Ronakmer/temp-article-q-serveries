
import requests
import os
import time
import json
import uuid
from app.workers.core.article_innovator_api_call.api_client.api_client import APIClient
from app.workers.core.calculate_priority.calculate_priority import CalculatePriority


class CreateWpBasePrompt:
    
    def __init__(self):
        self.api_client = APIClient()
        self.calculate_priority_service = CalculatePriority()



    def create_wp_base_prompt(self, category_supportive_prompt_data, formated_article_content_data, input_json_data, message_type):
        try:
            # Step 1: Extract template text
            template_text = category_supportive_prompt_data['supportive_prompts'][0]['data']['updated_text']

            # Step 2: Replace placeholders
            prompt_data = template_text \
                .replace('[[generated_article_title]]', formated_article_content_data['generated_title']) \
                .replace('[[generated_article_content]]', formated_article_content_data['generated_content'])

            # print(prompt_data)

            # Step 3: Extract the first input record from input_json_data
            input_record = input_json_data.get("data", [])[0]
            message_data = input_record.get("input_json_data", {}).get("message", {})

            # Step 4: Extract required fields
            article_slug_id = message_data.get("article_slug_id")
            article_priority = message_data.get("article_priority", 100)
            workspace_slug_id = message_data.get("workspace", {}).get("slug_id", "")
            ai_model = message_data.get("prompt", {}).get("ai_rate_model", "deepseek/deepseek_v3")

            # Step 5: Calculate priority
            priority = self.calculate_priority_service.calculate_priority(article_priority, 'primary_keyword')

            # Step 6: Prepare single AI request
            single_ai_request = {
                "article_id": article_slug_id,
                "model": ai_model,
                "system_prompt": "You are a helpful assistant.",
                "sequence_index": 1,
                "html_tag": "",
                "response_format": "json",
                "message_id": str(uuid.uuid4()),
                "article_message_total_count": 1,
                "prompt": prompt_data,
                "ai_request_status": "sent",
                "message_field_type": message_type,
                "message_priority": priority,
                "content": "",
                "workspace_id": workspace_slug_id,
            }

            return single_ai_request
        
        except Exception as e:
            return {
                "error": f"An unexpected error occurred: {str(e)}"
            }
