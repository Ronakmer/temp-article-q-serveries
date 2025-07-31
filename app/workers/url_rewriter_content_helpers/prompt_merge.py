import requests
import os
import time
import json
import uuid
from app.workers.core.article_innovator_api_call.api_client.api_client import APIClient
from app.workers.url_rewriter_content_helpers.content_processor import ContentProcessor

from copy import deepcopy
import re

class FinalPromptCreator:
    def __init__(self):
        self.api_client = APIClient()
        self.content_processor_service = ContentProcessor()


    def merge_prompt_data(self, base_prompt_data, processed_data, fetch_content_data, get_single_ai_response_data=None):
        try:
            """
            Merge base prompt instructions with content and title.
            """
            primary_keyword = ""
            # if get_single_ai_response_data is not None:
            #     primary_keyword = self._extract_primary_keyword(self, get_single_ai_response_data)

            # # Extract prompt data
            # prompt_data = self._extract_prompt_data(self, base_prompt_data)
            # print(prompt_data, 'prompt_datasdfsdfsdfsdfsdfsdfsdf')

            # # Replace [[primary_keyword]] everywhere in prompt_data
            # if primary_keyword:
            #     prompt_data = self._replace_primary_keyword(self, prompt_data, primary_keyword)


            # merged_prompt = self._replace_prompt_placeholders(self, prompt_data, processed_data)
            
            primary_keyword = self._extract_primary_keyword(get_single_ai_response_data)
            template_data = self._extract_prompt_data(base_prompt_data)

            if primary_keyword:
                prompt_with_keyword = self._replace_primary_keyword(template_data, primary_keyword)
            else:
                prompt_with_keyword = template_data

            merged_prompt = self._replace_prompt_placeholders(prompt_with_keyword, processed_data)
            # print(merged_prompt, 'merged_prompt_datssdfsdfsdfa')

            # Convert all string values in merged_prompt into one final string
            final_text_parts = []
            for key, value in merged_prompt.items():
                if isinstance(value, str):
                    final_text_parts.append(value)

            # Join all prompt sections into one final string
            final_prompt = "\n\n".join(final_text_parts)

            # Remove extra spaces, tabs, and newlines
            final_prompt = re.sub(r'\s+', ' ', final_prompt).strip()
            
            
            print(final_prompt, 'final_prompt_datssdfsdfsdfa')        
            
            

            return final_prompt
        except ValueError as e:
            # print(f"ValueError in _extract_primary_keyword: {e}")
            raise ValueError(f"error in merge_prompt_data:{e}")



    def _extract_primary_keyword(self, key_word_response_data):
        """Extract primary keyword from the AI response data."""
        try:
            
            # for tesing  
            with open('demo_json/key_word_response_data.json', 'w', encoding='utf-8') as f:
                json.dump(key_word_response_data, f, ensure_ascii=False, indent=4)


            # Navigate through the nested structure safely
            if not key_word_response_data or 'message' not in key_word_response_data:
                raise ValueError("Invalid key_word_response_data structure: missing 'message'")
                
            message = key_word_response_data['message']
            if 'ai_response' not in message:
                raise ValueError("Invalid key_word_response_data structure: missing 'ai_response'")
                
            ai_response = message['ai_response']
            if 'result' not in ai_response:
                raise ValueError("Invalid key_word_response_data structure: missing 'result'")
                
            result = ai_response['result']
            if 'processed_text' not in result:
                raise ValueError("Invalid key_word_response_data structure: missing 'processed_text'")
                
            processed_text = result['processed_text']
            
            # Try to parse as JSON first (more reliable than regex)
            try:
                # Extract JSON from markdown code blocks if present
                json_match = re.search(r'```json\s*(\{.*?\})\s*```', processed_text, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                else:
                    # Look for JSON object directly
                    json_match = re.search(r'\{.*?"primary_keyword".*?\}', processed_text, re.DOTALL)
                    if json_match:
                        json_str = json_match.group(0)
                    else:
                        json_str = processed_text
                
                # Parse the JSON
                json_data = json.loads(json_str)
                return json_data.get('primary_keyword', '')
                
            except json.JSONDecodeError:
                # Fallback to regex if JSON parsing fails
                match = re.search(r'"primary_keyword":\s*"([^"]+)"', processed_text)
                return match.group(1) if match else ''
                
        except ValueError as e:
            print(f"ValueError in _extract_primary_keyword: {e}")
            return ''
        except Exception as e:
            print(f"Unexpected error in _extract_primary_keyword: {e}")
            return ''
        
        

    

    def _extract_prompt_data(self, base_prompt_data):
        """Extract all keys from updated_prompt_data if present, otherwise return all keys in base_prompt_data."""
        try:
            base_data = base_prompt_data.get('base_prompt_data', [])
            if base_data and isinstance(base_data[0], dict):
                data = base_data[0].get('data', {})
                updated_prompt_data = data.get('updated_prompt_data', {})
                if isinstance(updated_prompt_data, dict) and updated_prompt_data:
                    return updated_prompt_data  # Return all keys from updated_prompt_data
        except (KeyError, IndexError, TypeError):
            pass

        # Fallback: return all keys from base_prompt_data
        return base_prompt_data


    def _replace_primary_keyword(self, data, primary_keyword):
        """Recursively replace [[primary_keyword]] in all string values of data."""
        if isinstance(data, str):
            return data.replace("[[primary_keyword]]", primary_keyword)
        elif isinstance(data, dict):
            return {k: self._replace_primary_keyword(v, primary_keyword) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._replace_primary_keyword(item, primary_keyword) for item in data]
        return data




    def _replace_prompt_placeholders(self, prompt_data, processed_data):
        """
        Replace placeholders [[source_title]] and [[source_content]] 
        in the prompt_data with values from processed_data.
        
        Args:
            prompt_data (dict): Dictionary containing prompt templates with placeholders.
            processed_data (dict): Dictionary containing 'source_title' and 'source_content' values.

        Returns:
            dict: Updated prompt_data with placeholders replaced.
        """
        updated_data = {}
        for key, value in prompt_data.items():
            if isinstance(value, str):
                updated_data[key] = (
                    value.replace('[[source_title]]', processed_data.get('source_title', ''))
                        .replace('[[source_content]]', processed_data.get('source_content', ''))
                )
            else:
                updated_data[key] = value
        return updated_data
