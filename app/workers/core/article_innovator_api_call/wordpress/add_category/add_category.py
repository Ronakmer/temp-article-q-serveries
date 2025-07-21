
import requests
import os
import time
import json
import uuid
from app.workers.core.article_innovator_api_call.api_client.api_client import APIClient
# from app.workers.url_rewriter_para_response_helpers.get_input_json_data import GetInputJson


class AddCategory:
    
    def __init__(self):
        self.api_client = APIClient()
        # self.get_input_json_service = GetInputJson()

  
  
  
    # def add_category(self, input_json_data, new_category):
    #     try:
    #         print("Input JSON Data:", input_json_data)

    #         message = input_json_data.get("message", {})
    #         print(message, 'messagezzz')
    #         domain_slug_id = message.get("domain_id", {}).get("domain_slug_id")
    #         workspace_slug_id = message.get("workspace_id", {}).get("workspace_slug_id")

    #         result_data = new_category.get("result", {})
    #         processed_text_raw = result_data.get("processed_text")

    #         # Parse the string to a Python object
    #         processed_data = json.loads(processed_text_raw)

    #         if not processed_data or not isinstance(processed_data, list):
    #             print("Processed data is empty or invalid format.")
    #             return

    #         categories = processed_data[0]  # List of category dicts

    #         add_categories = []

    #         for category in categories:
    #             name = category.get("name")
    #             slug = category.get("slug")
    #             description = category.get("description")
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
    #                         break  # Success, exit retry loop
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














    # def add_category(self, new_category):
    #     try:
    
    #         message_data = new_category.get("data", {}).get("data", {})
    #         article_id = new_category.get("article_id")

    #         try:
    #             from app.workers.url_rewriter_para_response_helpers.get_input_json_data import GetInputJson
    #             self.get_input_json_service = GetInputJson()

    #             get_input_json_data = self.get_input_json_service.get_input_json_data_for_wp(article_id)
    #             # print(get_input_json_data, '----------------------get_input_json_data----------------------')
    #         except Exception as e:
    #             print({"status": "error", "step": "get_input_json_data", "message": str(e)})

    #         input_data = get_input_json_data.get("data", [])[0].get("input_json_data", {}).get("message", {})

    #         domain_slug_id = input_data.get("domain", {}).get("slug_id", {})
    #         workspace_slug_id = input_data.get("workspace", {}).get("slug_id", {})


    #         print('domain_slug_id',domain_slug_id)
    #         print('workspace_slug_id',workspace_slug_id )

    #         # Step 2: Extract and parse the AI response JSON
    #         ai_response_str = message_data.get("ai_response", "")
    #         if not ai_response_str:
    #             return {"success": False, "error": "Missing ai_response"}

    #         ai_response_json = json.loads(ai_response_str)
    #         processed_text_raw = ai_response_json.get("result", {}).get("processed_text", "")

    #         if not processed_text_raw:
    #             return {"success": False, "error": "Processed text not found in AI response"}

    #         processed_data = json.loads(processed_text_raw)


    #         # If it's a dict wrapped in triple brackets, extract accordingly
    #         if isinstance(processed_data, dict):
    #             categories = [processed_data.get("category")]
    #         elif isinstance(processed_data, list):
    #             categories = processed_data
    #         else:
    #             print("Processed data is in unexpected format.")
    #             return

    #         add_categories = []

    #         for category in categories:
    #             name = category.get("name")
    #             slug = category.get("slug")  # fallback to name-based slug
    #             description = category.get("description")
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
    #                         break  # Success, exit retry loop
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







    def add_category(self, new_category):
        try:
            message_data = new_category.get("data", {}).get("data", {})
            article_id = message_data.get("article_id")

            try:
                from app.workers.url_rewriter_para_response_helpers.get_input_json_data import GetInputJson
                self.get_input_json_service = GetInputJson()
                get_input_json_data = self.get_input_json_service.get_input_json_data_for_wp(article_id)
            except Exception as e:
                print({"status": "error", "step": "get_input_json_data", "message": str(e)})

            input_data = get_input_json_data.get("data", [])[0].get("input_json_data", {}).get("message", {})
            domain_slug_id = input_data.get("domain", {}).get("slug_id", {})
            workspace_slug_id = input_data.get("workspace", {}).get("slug_id", {})

            print('domain_slug_id', domain_slug_id)
            print('workspace_slug_id', workspace_slug_id)

            # Step 2: Extract and parse the AI response JSON
            ai_response_str = message_data.get("ai_response", "")
            if not ai_response_str:
                return {"success": False, "error": "Missing ai_response"}

            ai_response_json = json.loads(ai_response_str)
            processed_text_raw = ai_response_json.get("result", {}).get("processed_text", "")

            if not processed_text_raw:
                return {"success": False, "error": "Processed text not found in AI response"}

            # Fix: clean up and double parse the processed_text
            try:
                processed_text_json = json.loads(processed_text_raw)  # first parse
                if isinstance(processed_text_json, list):
                    categories = processed_text_json[0]  # take first list level
                else:
                    raise ValueError("Expected a list structure inside processed_text")
            except json.JSONDecodeError as json_err:
                return {"success": False, "error": f"Invalid JSON in processed_text: {json_err}"}
            except Exception as e:
                return {"success": False, "error": f"Error processing categories: {e}"}

            add_categories = []

            for category in categories:
                name = category.get("name")
                slug = category.get("slug", None)  # Optional: generate from name if needed
                description = category.get("description", "")
                cat_workspace_slug_id = category.get("workspace_slug_id", workspace_slug_id)
                cat_domain_slug_id = category.get("domain_slug_id", domain_slug_id)

                request_data = {
                    "name": name,
                    "slug": slug,
                    "description": description,
                    "domain_slug_id": cat_domain_slug_id,
                    "workspace_slug_id": cat_workspace_slug_id,
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
                            add_categories.append(category_response)
                            print(f"[add_category] Success for '{name}' on attempt {attempt}")
                            break
                        else:
                            print(f"[add_category] Attempt {attempt} failed for '{name}' with response: {category_response}")

                    except Exception as retry_error:
                        print(f"[add_category] Exception on attempt {attempt} for '{name}': {retry_error}")

                    if attempt == max_retries:
                        print(f"[add_category] Max retries reached for '{name}'")
                        add_categories.append({
                            "name": name,
                            "error": "Max retries exceeded",
                            "last_response": category_response,
                        })

            return {
                "success": True,
                "categories": add_categories
            }

        except Exception as e:
            print(f"[add_category] Exception: {e}")
            return {"success": False, "error": f"Unexpected error: {str(e)}"}

