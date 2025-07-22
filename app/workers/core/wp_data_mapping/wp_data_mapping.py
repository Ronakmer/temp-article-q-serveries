import requests
import os
import uuid
import logging
import json
import time
import re



class WPDataMapping:
    def __init__(self):
        self.headers = {
            "Content-Type": "application/json"
        }
    
    
    def wp_data_mapping(self, category_supportive_prompt_data, all_stored_message):
        try:
            # 1. Extract template text
            if isinstance(category_supportive_prompt_data, dict):
                template_text = category_supportive_prompt_data.get('supportive_prompts', [{}])[0].get('data', {}).get('updated_text', '')
            elif isinstance(category_supportive_prompt_data, list) and category_supportive_prompt_data:
                template_text = str(category_supportive_prompt_data[0])
            else:
                template_text = str(category_supportive_prompt_data or '')

            # 2. Extract first stored message
            if isinstance(all_stored_message, dict):
                if isinstance(all_stored_message.get("data"), list) and all_stored_message["data"]:
                    first_item = all_stored_message["data"][0]
                else:
                    first_item = all_stored_message
            elif isinstance(all_stored_message, list) and all_stored_message:
                first_item = all_stored_message[0]
            else:
                return {"success": False, "error": "Invalid all_stored_message format"}

            # 3. Parse AI response
            ai_response_raw = first_item.get("ai_response", "")
            if not ai_response_raw:
                return {"success": False, "error": "AI response missing"}
            try:
                ai_response = json.loads(ai_response_raw)
            except json.JSONDecodeError:
                return {"success": False, "error": "Invalid AI response JSON"}

            # 4. Extract processed text
            processed_text = ai_response.get("result", {}).get("processed_text", "")
            if not processed_text:
                return {"success": False, "error": "Processed text missing"}

            # 5. Extract JSON block
            match = re.search(r'```json\s*(\{.*?\})\s*```', processed_text, re.DOTALL)
            json_string = match.group(1) if match else processed_text.strip()

            try:
                content_data = json.loads(json_string)
            except json.JSONDecodeError:
                return {"success": False, "error": "Invalid processed_text JSON"}

            title = content_data.get("title", "")
            content = content_data.get("content", "")

            # 6. Replace placeholders
            final_content = template_text.replace('[[generated_article_title]]', title)\
                                        .replace('[[generated_article_content]]', content)

            # 7. Save demo file
            os.makedirs('demo_json', exist_ok=True)
            with open('demo_json/wp_prompt_data.json', 'w', encoding='utf-8') as f:
                json.dump({"title": title, "content": content, "final_content": final_content},
                          f, ensure_ascii=False, indent=4)

            # return {"success": True, "title": title, "content": content, "final_content": final_content}
            return final_content

        except Exception as e:
            return {"success": False, "error": str(e)}
