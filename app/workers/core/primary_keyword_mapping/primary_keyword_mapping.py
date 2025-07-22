import requests
import os
import uuid
import logging
import json
import time
# from app.workers.core.calculate_priority.calculate_priority import CalculatePriority
# from app.workers.core.article_innovator_api_call.ai_message.ai_message import AIMessage
# from app.workers.core.ai_rate_limiter.ai_rate_limiter import AIRateLimiter


class PrimaryKeywordMapping:
    def __init__(self):
        self.headers = {
            "Content-Type": "application/json"
        }
        
        # self.calculate_priority_service = CalculatePriority()
        # self.ai_rate_limiter_service = AIRateLimiter()
        # self.ai_message_service = AIMessage()
    
    def primary_keyword_mapping(self, prompt_data, processed_data):
        try:
                        
            selector_map = processed_data
            print(selector_map, 'selector_mapxxxxxxxxxx')

            # Replace placeholders in prompt_data
            processed_prompts = []
            for prompt in prompt_data:
                for key, value in selector_map.items():
                    placeholder = f"[[{key}]]"
                    if placeholder in prompt:
                        prompt = prompt.replace(placeholder, str(value))
                processed_prompts.append(prompt)


            # Convert list to a single string (joined by newlines)
            final_string = "\n".join(processed_prompts)


            # print(processed_prompts,'processed_promptsxxxxxxxxxx')
            # Save the file directly to the existing 'demo_json' folder
            with open('demo_json/processed_prompts.json', 'w', encoding='utf-8') as f:
                json.dump(processed_prompts, f, ensure_ascii=False, indent=4)


            return final_string
        except Exception as e:
            print(f"Error in primary_keyword_mapping: {e}")
            return f"An unexpected error occurred: {e}"