
import requests
import os
import time
import json
import uuid
from app.workers.core.article_innovator_api_call.api_client.api_client import APIClient
import re


class Category:
    def __init__(self):
        self.api_client = APIClient()

    def fetch_category(self, input_json_data):
        try:
            print("Input JSON Data:", input_json_data)

            message = input_json_data.get("message", {})
            # target_category_ids = message.get("wp_category_id", [])
            print(message,'messagezzz')
            domain_slug_id = message.get("domain_id", {}).get("domain_slug_id")
            workspace_slug_id = message.get("workspace_id", {}).get("workspace_slug_id")

            if not domain_slug_id or not workspace_slug_id:
                return {"error": "Missing domain or workspace slug ID in input."}

            collected_categories = []

            # for cat_slug_id in target_category_ids:
            params = {
                'domain_slug_id': domain_slug_id,
                'workspace_slug_id': workspace_slug_id,
                # 'wp_category_id': cat_slug_id  # Pass one category slug at a time
            }

            all_categories = self.api_client.crud('category', 'read', params=params)
            if isinstance(all_categories, list):
                collected_categories.extend(all_categories)
            elif isinstance(all_categories, dict):
                collected_categories.append(all_categories)

            print(all_categories,'all_categoriesxxx')
            print(all_categories.json(),'all_categoriesxxx')
            return {
                "success": True,
                "categories": collected_categories
            }

        except Exception as e:
            return {"error": f"An unexpected error occurred: {str(e)}"}

   


    # def add_category(self, new_category):
    #     try:
    #         message_data = new_category.get("data", {}).get("data", {})
    #         article_id = message_data.get("article_id")

    #         try:
    #             from app.workers.url_rewriter_para_response_helpers.get_input_json_data import GetInputJson
    #             self.get_input_json_service = GetInputJson()
    #             get_input_json_data = self.get_input_json_service.get_input_json_data_for_wp(article_id)
    #         except Exception as e:
    #             print({"status": "error", "step": "get_input_json_data", "message": str(e)})

    #         input_data = get_input_json_data.get("data", [])[0].get("input_json_data", {}).get("message", {})
    #         domain_slug_id = input_data.get("domain", {}).get("slug_id", {})
    #         workspace_slug_id = input_data.get("workspace", {}).get("slug_id", {})

    #         print('domain_slug_id', domain_slug_id)
    #         print('workspace_slug_id', workspace_slug_id)

    #         # Step 2: Extract and parse the AI response JSON
    #         ai_response_str = message_data.get("ai_response", "")
    #         if not ai_response_str:
    #             return {"success": False, "error": "Missing ai_response"}

    #         ai_response_json = json.loads(ai_response_str)
    #         processed_text_raw = ai_response_json.get("result", {}).get("processed_text", "")

    #         if not processed_text_raw:
    #             return {"success": False, "error": "Processed text not found in AI response"}

    #         # Fix: clean up and double parse the processed_text
    #         try:
    #             processed_text_json = json.loads(processed_text_raw)  # first parse
    #             if isinstance(processed_text_json, list):
    #                 categories = processed_text_json[0]  # take first list level
    #             else:
    #                 raise ValueError("Expected a list structure inside processed_text")
    #         except json.JSONDecodeError as json_err:
    #             return {"success": False, "error": f"Invalid JSON in processed_text: {json_err}"}
    #         except Exception as e:
    #             return {"success": False, "error": f"Error processing categories: {e}"}

    #         add_categories = []

    #         for category in categories:
    #             name = category.get("name")
    #             slug = category.get("slug", None)  # Optional: generate from name if needed
    #             description = category.get("description", "")
    #             cat_workspace_slug_id = category.get("workspace_slug_id", workspace_slug_id)
    #             cat_domain_slug_id = category.get("domain_slug_id", domain_slug_id)

    #             request_data = {
    #                 "name": name,
    #                 "slug": slug,
    #                 "description": description,
    #                 "domain_slug_id": cat_domain_slug_id,
    #                 "workspace_slug_id": cat_workspace_slug_id,
    #                 "derived_by": "ai"
    #             }

    #             max_retries = 3
    #             category_response = None

    #             for attempt in range(1, max_retries + 1):
    #                 try:
    #                     category_response = self.api_client.crud(
    #                         'category',
    #                         'create',
    #                         data=request_data
    #                     )

    #                     if isinstance(category_response, dict) and category_response.get('status_code') == 200:
    #                         add_categories.append(category_response)
    #                         print(f"[add_category] Success for '{name}' on attempt {attempt}")
    #                         break
    #                     else:
    #                         print(f"[add_category] Attempt {attempt} failed for '{name}' with response: {category_response}")

    #                 except Exception as retry_error:
    #                     print(f"[add_category] Exception on attempt {attempt} for '{name}': {retry_error}")

    #                 if attempt == max_retries:
    #                     print(f"[add_category] Max retries reached for '{name}'")
    #                     add_categories.append({
    #                         "name": name,
    #                         "error": "Max retries exceeded",
    #                         "last_response": category_response,
    #                     })

    #         return {
    #             "success": True,
    #             "categories": add_categories
    #         }

    #     except Exception as e:
    #         print(f"[add_category] Exception: {e}")
    #         return {"success": False, "error": f"Unexpected error: {str(e)}"}







  

    # def add_category(self, new_category, domain_slug_id, workspace_slug_id):
    #     try:
            
    #         # If they are tuples, convert to string
    #         if isinstance(domain_slug_id, tuple):
    #             domain_slug_id = domain_slug_id[0]
    #         if isinstance(workspace_slug_id, tuple):
    #             workspace_slug_id = workspace_slug_id[0]

    #         print(domain_slug_id, workspace_slug_id, 'domain_slug_id, workspace_slug_id')
    #         if isinstance(new_category, str):
    #             new_category = json.loads(new_category)

    #         ai_response = new_category.get("ai_response", {})
    #         if isinstance(ai_response, str):
    #             ai_response = json.loads(ai_response)

    #         result_data = ai_response.get("result", {})
    #         processed_text_raw = result_data.get("processed_text")

    #         if not processed_text_raw or not processed_text_raw.strip():
    #             print("[add_category] processed_text_raw is empty or None.")
    #             return {"success": False, "error": "processed_text_raw is empty or invalid"}

    #         # Extract only the first JSON-like array using regex
    #         match = re.search(r'(\[\[.*\]\])', processed_text_raw, re.DOTALL)
    #         if match:
    #             json_part = match.group(1)
    #         else:
    #             print("[add_category] No valid JSON found in processed_text_raw")
    #             return {"success": False, "error": "No valid JSON found in processed_text_raw"}

    #         try:
    #             processed_data = json.loads(json_part)
    #         except json.JSONDecodeError as decode_err:
    #             print(f"[add_category] JSON decode error: {decode_err} | Value: {json_part}")
    #             return {"success": False, "error": f"Invalid JSON in processed_text_raw: {json_part}"}

    #         if not processed_data or not isinstance(processed_data, list):
    #             print("Processed data is empty or invalid format.")
    #             return

    #         # Continue with existing category logic...
    #         categories = processed_data[0]
    #         add_categories = []

    #         for category in categories:
    #             name = category.get("name")
    #             slug = category.get("slug", name.lower().replace(" ", "-"))
    #             description = category.get("description")
    #             cat_workspace_slug_id = workspace_slug_id
    #             cat_domain_slug_id = domain_slug_id

    #             request_data = {
    #                 "name": name,
    #                 "slug": slug,
    #                 "description": description,
    #                 "domain_slug_id": cat_domain_slug_id,
    #                 "workspace_slug_id": cat_workspace_slug_id,
    #                 "derived_by": "ai"
    #             }

    #             max_retries = 3
    #             category_response = None

    #             for attempt in range(1, max_retries + 1):
    #                 try:
    #                     category_response = self.api_client.crud(
    #                         'category',
    #                         'create',
    #                         data=request_data
    #                     )

    #                     if isinstance(category_response, dict) and category_response.get('status_code') == 200:
    #                         add_categories.append(category_response)
    #                         print(f"[add_category] Success for '{name}' on attempt {attempt}")
    #                         break
    #                     else:
    #                         print(f"[add_category] Attempt {attempt} failed for '{name}' with response: {category_response}")

    #                 except Exception as retry_error:
    #                     print(f"[add_category] Exception on attempt {attempt} for '{name}': {retry_error}")

    #                 if attempt == max_retries:
    #                     print(f"[add_category] Max retries reached for '{name}'")
    #                     add_categories.append({
    #                         "name": name,
    #                         "error": "Max retries exceeded",
    #                         "last_response": category_response,
    #                     })

    #         print(f"[add_category] Categories added: {add_categories}")
    #         return {
    #             "success": True,
    #             "categories": add_categories
    #         }

    #     except Exception as e:
    #         print(f"[add_category] Exception: {e}")
    #         return {"success": False, "error": f"Unexpected error: {str(e)}"}






    def add_category(self, new_category, domain_slug_id, workspace_slug_id):
        try:
            # Convert tuple to string if necessary
            domain_slug_id = domain_slug_id[0] if isinstance(domain_slug_id, tuple) else domain_slug_id
            workspace_slug_id = workspace_slug_id[0] if isinstance(workspace_slug_id, tuple) else workspace_slug_id

            print(domain_slug_id, workspace_slug_id, 'domain_slug_id, workspace_slug_id')
            print(new_category, 'new_category raw input')

            # Ensure new_category is a dictionary
            if isinstance(new_category, str):
                new_category = json.loads(new_category)

            ai_response = new_category.get("ai_response", {})
            if isinstance(ai_response, str):
                ai_response = json.loads(ai_response)

            result_data = ai_response.get("result", {})
            processed_text_raw = result_data.get("processed_text")

            if not processed_text_raw or not processed_text_raw.strip():
                print("[add_category] processed_text_raw is empty or None.")
                return {"success": False, "error": "processed_text_raw is empty or invalid"}

            # Remove code fences
            cleaned_text = re.sub(r'```json|```', '', processed_text_raw).strip()

            # Extract JSON part (array or object) from text
            match = re.search(r'(\{.*\}|\[.*\])', cleaned_text, re.DOTALL)
            if not match:
                print("[add_category] No valid JSON found in processed_text_raw")
                return {"success": False, "error": "No valid JSON found in processed_text_raw"}

            json_part = match.group(1)

            # Parse the extracted JSON
            try:
                processed_data = json.loads(json_part)
            except json.JSONDecodeError as e:
                print(f"[add_category] JSON decode error: {e} | Value: {json_part}")
                return {"success": False, "error": "Invalid JSON in processed_text_raw"}

            # Flatten nested [[ {...} ]] to [ {...} ]
            if isinstance(processed_data, list) and len(processed_data) == 1 and isinstance(processed_data[0], list):
                processed_data = processed_data[0]

            # Ensure categories is always a list of dicts
            categories = processed_data if isinstance(processed_data, list) else [processed_data]
            if not categories or not all(isinstance(c, dict) for c in categories):
                print("[add_category] Processed data is empty or invalid format.")
                return {"success": False, "error": "Processed data is empty or invalid"}

            # --- Create categories via API ---
            slug_ids = []
            for category in categories:
                name = category.get("name")
                description = category.get("description", "")
                slug = category.get("slug") or name.lower().replace(" ", "-")

                request_data = {
                    "name": name,
                    "slug": slug,
                    "description": description,
                    "domain_slug_id": domain_slug_id,
                    "workspace_slug_id": workspace_slug_id,
                    "derived_by": "ai"
                }

                max_retries = 3
                category_response = None

                for attempt in range(1, max_retries + 1):
                    try:
                        category_response = self.api_client.crud(
                            'category',
                            'create',
                            data=request_data
                        )

                        if isinstance(category_response, dict) and category_response.get('status_code') == 200:
                            print(category_response, 'sdfsfsdfcategory_responsesdfsdfsdf')
                            real_slug_id = category_response.get('data', {}).get('slug_id', '')
                            slug_ids.append(real_slug_id)
                            # slug_ids.append(slug)
                            print(f"[add_category] Success for '{name}' (slug: {slug}) on attempt {attempt}")
                            break
                        else:
                            print(f"[add_category] Attempt {attempt} failed for '{name}' with response: {category_response}")

                    except Exception as retry_error:
                        print(f"[add_category] Exception on attempt {attempt} for '{name}': {retry_error}")

                    if attempt == max_retries:
                        print(f"[add_category] Max retries reached for '{name}'")
                        slug_ids.append(f"{slug}-error")

            print(f"[add_category] Slugs added: {slug_ids}")
            return {"success": True, "slug_id": slug_ids}

        except Exception as e:
            print(f"[add_category] Exception: {e}")
            return {"success": False, "error": f"Unexpected error: {str(e)}"}
