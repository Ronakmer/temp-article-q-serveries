import requests
import os
import time
import json
import uuid
from app.workers.core.article_innovator_api_call.api_client.api_client import APIClient
from app.workers.url_rewriter_para_request_helpers.content_processor import ContentProcessor

from copy import deepcopy
import re

class FinalPromptCreator:
    def __init__(self):
        self.api_client = APIClient()
        self.content_processor = ContentProcessor()

    def final_prompt_creator(self, base_prompt_data, key_word_response_data, scraped_data):
        try:
            # print(base_prompt_data, 'base_prompt_data')
            # print(key_word_response_data, 'key_word_response_data')
            # print(scraped_data, 'scraped_dataxxcvd')
            
            # Step 1: Validate and extract the primary keyword
            if key_word_response_data is not None:
                primary_keyword = self._extract_primary_keyword(key_word_response_data)
            else:
                primary_keyword = None
            
            # if not primary_keyword:
            #     print("Warning: No primary keyword found in processed_text")
            #     return {"Error: No primary keyword found in processed_text"}

            # Step 2: Create selector_map from scraped_data (dynamic for source_ prefixed keys)
            selector_map = self._create_selector_map(scraped_data)
                    
            # Step 3: Validate and extract prompt data
            prompt_data = self._extract_prompt_data(base_prompt_data)
            
            # Step 4: Replace placeholders in the title_rephrase prompt
            if 'title_rephrase' not in prompt_data:
                return {"success": False, "error": "title_rephrase not found in prompt_data"}
                
            title_template = prompt_data['title_rephrase']

            # Replace placeholders
            title_filled = title_template.replace('[[source_title]]', selector_map.get('source_title', ''))
            if primary_keyword:
                title_filled = title_filled.replace('[[primary_keyword]]', primary_keyword)

            # Update the prompt data
            prompt_data['title_rephrase'] = title_filled

            # Output the final updated prompt_data
            print(json.dumps(prompt_data, indent=2), 'final_updated_prompt_data')

            # Return the updated prompt data
            return {
                "success": True,
                "updated_prompt_data": prompt_data,
                # "primary_keyword": primary_keyword,
                # "selector_map": selector_map
            }

        except KeyError as e:
            error_msg = f"Missing required key in data structure: {str(e)}"
            print(f"KeyError: {error_msg}")
            return {"success": False, "error": error_msg}
        
        except Exception as e:
            error_msg = f"An unexpected error occurred: {str(e)}"
            print(f"Exception: {error_msg}")
            return {"success": False, "error": error_msg}

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

    def _create_selector_map(self, scraped_data):
        """Create selector map from scraped data."""
        selector_map = {}
        
        try:
            # Get processed content data from ContentProcessor
            fetch_content_data = self.content_processor.fetch_content(scraped_data)
            # print(f"Fetched content data: {fetch_content_data}")
            
            if not fetch_content_data:
                print("Warning: No fetch_content_data returned from ContentProcessor")
                # Fallback to original scraped_data
                data_to_process = scraped_data
            else:
                # Use the processed content data
                data_to_process = fetch_content_data
            
            if not data_to_process:
                print("Warning: No data to process")
                return selector_map

            if 'selectors_output' in data_to_process:
                # Handle selectors_output format
                selectors_output = data_to_process['selectors_output']
                if isinstance(selectors_output, list):
                    selector_map = {item['name']: item['value'] for item in selectors_output if isinstance(item, dict) and 'name' in item and 'value' in item}
                else:
                    print("Warning: selectors_output is not a list")
            else:
                # Dynamically extract all keys that start with 'source_'
                selector_map = {key: value for key, value in data_to_process.items() if isinstance(key, str) and key.startswith('source_')}
                
            # Optional: Print what was found for debugging
            if selector_map:
                print(f"Found selector keys: {list(selector_map.keys())}")
            else:
                print("Warning: No selector data found in processed data")
                
        except Exception as e:
            print(f"Error creating selector_map: {e}")
            
        return selector_map

    def _extract_prompt_data(self, base_prompt_data):
        """Extract and validate prompt data from base_prompt_data."""
        try:
            
            if not base_prompt_data or 'base_prompt_data' not in base_prompt_data:
                raise ValueError("Invalid base_prompt_data structure: missing 'base_prompt_data'")
                
            base_prompt_list = base_prompt_data['base_prompt_data']
            if not isinstance(base_prompt_list, list) or len(base_prompt_list) == 0:
                raise ValueError("Invalid base_prompt_data structure: 'base_prompt_data' is not a non-empty list")
                
            first_item = base_prompt_list[0]
            if 'data' not in first_item:
                raise ValueError("Invalid base_prompt_data structure: missing 'data' in first item")
                
            data = first_item['data']
            if 'updated_prompt_data' not in data:
                raise ValueError("Invalid base_prompt_data structure: missing 'updated_prompt_data'")
                
            return data['updated_prompt_data']
            
        except ValueError as e:
            print(f"ValueError in _extract_prompt_data: {e}")
            raise
        except Exception as e:
            print(f"Unexpected error in _extract_prompt_data: {e}")
            raise

