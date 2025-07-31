
import requests
import os
import time
import json
import uuid
from app.workers.core.article_innovator_api_call.api_client.api_client import APIClient
import re


class Author:
    def __init__(self):
        self.api_client = APIClient()

    def fetch_author(self, input_json_data):
        try:
            print("Input JSON Data:", input_json_data)

            message = input_json_data.get("message", {})
            # target_author_ids = message.get("wp_author_id", [])
            print(message,'messagezzz')
            domain_slug_id = message.get("domain_id", {}).get("domain_slug_id")
            workspace_slug_id = message.get("workspace_id", {}).get("workspace_slug_id")

            if not domain_slug_id or not workspace_slug_id:
                return {"error": "Missing domain or workspace slug ID in input."}

            collected_authors = []

            # for cat_slug_id in target_author_ids:
            params = {
                'domain_slug_id': domain_slug_id,
                'workspace_slug_id': workspace_slug_id,
                # 'wp_author_id': cat_slug_id  # Pass one author slug at a time
            }

            all_authors = self.api_client.crud('author', 'read', params=params)
            if isinstance(all_authors, list):
                collected_authors.extend(all_authors)
            elif isinstance(all_authors, dict):
                collected_authors.append(all_authors)

            print(all_authors,'all_authorsxxx')
            print(all_authors.json(),'all_authorsxxx')
            return {
                "success": True,
                "authors": collected_authors
            }

        except Exception as e:
            return {"error": f"An unexpected error occurred: {str(e)}"}






    # def add_author(self, new_author, domain_slug_id, workspace_slug_id):
    #     try:
    #         # Convert tuple to string if necessary
    #         domain_slug_id = domain_slug_id[0] if isinstance(domain_slug_id, tuple) else domain_slug_id
    #         workspace_slug_id = workspace_slug_id[0] if isinstance(workspace_slug_id, tuple) else workspace_slug_id

    #         print(domain_slug_id, workspace_slug_id, 'domain_slug_id, workspace_slug_id')
    #         print(new_author, 'new_author raw input')

    #         # Ensure new_author is a dictionary
    #         if isinstance(new_author, str):
    #             new_author = json.loads(new_author)

    #         ai_response = new_author.get("ai_response", {})
    #         if isinstance(ai_response, str):
    #             ai_response = json.loads(ai_response)

    #         result_data = ai_response.get("result", {})
    #         processed_text_raw = result_data.get("processed_text")

    #         if not processed_text_raw or not processed_text_raw.strip():
    #             print("[add_author] processed_text_raw is empty or None.")
    #             return {"success": False, "error": "processed_text_raw is empty or invalid"}

    #         # Remove code fences
    #         cleaned_text = re.sub(r'```json|```', '', processed_text_raw).strip()

    #         # Extract JSON part (array or object) from text
    #         match = re.search(r'(\{.*\}|\[.*\])', cleaned_text, re.DOTALL)
    #         if not match:
    #             print("[add_author] No valid JSON found in processed_text_raw")
    #             return {"success": False, "error": "No valid JSON found in processed_text_raw"}

    #         json_part = match.group(1)

    #         # Parse the extracted JSON
    #         try:
    #             processed_data = json.loads(json_part)
    #         except json.JSONDecodeError as e:
    #             print(f"[add_author] JSON decode error: {e} | Value: {json_part}")
    #             return {"success": False, "error": "Invalid JSON in processed_text_raw"}

    #         # Flatten nested [[ {...} ]] to [ {...} ]
    #         if isinstance(processed_data, list) and len(processed_data) == 1 and isinstance(processed_data[0], list):
    #             processed_data = processed_data[0]

    #         # Ensure authors is always a list of dicts
    #         authors = processed_data if isinstance(processed_data, list) else [processed_data]
    #         if not authors or not all(isinstance(c, dict) for c in authors):
    #             print("[add_author] Processed data is empty or invalid format.")
    #             return {"success": False, "error": "Processed data is empty or invalid"}

    #         # --- Create authors via API ---
    #         slug_ids = []
    #         for author in authors:
    #             name = author.get("name")
    #             description = author.get("description", "")
    #             slug = author.get("slug") or name.lower().replace(" ", "-")

    #             request_data = {
    #                 "name": name,
    #                 "slug": slug,
    #                 "description": description,
    #                 "domain_slug_id": domain_slug_id,
    #                 "workspace_slug_id": workspace_slug_id,
    #                 "derived_by": "ai"
    #             }

    #             max_retries = 3
    #             author_response = None

    #             for attempt in range(1, max_retries + 1):
    #                 try:
    #                     author_response = self.api_client.crud(
    #                         'author',
    #                         'create',
    #                         data=request_data
    #                     )

    #                     if isinstance(author_response, dict) and author_response.get('status_code') == 200:
    #                         print(author_response, 'sdfsfsdfauthor_responsesdfsdfsdf')
    #                         real_slug_id = author_response.get('data', {}).get('slug_id', '')
    #                         slug_ids.append(real_slug_id)
    #                         # slug_ids.append(slug)
    #                         print(f"[add_author] Success for '{name}' (slug: {slug}) on attempt {attempt}")
    #                         break
    #                     else:
    #                         print(f"[add_author] Attempt {attempt} failed for '{name}' with response: {author_response}")

    #                 except Exception as retry_error:
    #                     print(f"[add_author] Exception on attempt {attempt} for '{name}': {retry_error}")

    #                 if attempt == max_retries:
    #                     print(f"[add_author] Max retries reached for '{name}'")
    #                     slug_ids.append(f"{slug}-error")

    #         print(f"[add_author] Slugs added: {slug_ids}")
    #         return {"success": True, "slug_id": slug_ids}

    #     except Exception as e:
    #         print(f"[add_author] Exception: {e}")
    #         return {"success": False, "error": f"Unexpected error: {str(e)}"}



    def add_author(self, new_author, domain_slug_id, workspace_slug_id):
        try:
            # Convert tuple to string if necessary
            domain_slug_id = domain_slug_id[0] if isinstance(domain_slug_id, tuple) else domain_slug_id
            workspace_slug_id = workspace_slug_id[0] if isinstance(workspace_slug_id, tuple) else workspace_slug_id

            print(domain_slug_id, workspace_slug_id, 'domain_slug_id, workspace_slug_id')
            print(new_author, 'new_author raw input')

            # Ensure new_author is a dictionary
            if isinstance(new_author, str):
                new_author = json.loads(new_author)

            ai_response = new_author.get("ai_response", {})
            if isinstance(ai_response, str):
                ai_response = json.loads(ai_response)

            result_data = ai_response.get("result", {})
            processed_text_raw = result_data.get("processed_text")

            if not processed_text_raw or not processed_text_raw.strip():
                print("[add_author] processed_text_raw is empty or None.")
                return {"success": False, "error": "processed_text_raw is empty or invalid"}

            # Remove code fences
            cleaned_text = re.sub(r'```json|```', '', processed_text_raw).strip()

            # Extract JSON part (object only)
            match = re.search(r'(\{.*\})', cleaned_text, re.DOTALL)
            if not match:
                print("[add_author] No valid JSON object found in processed_text_raw")
                return {"success": False, "error": "No valid JSON object found in processed_text_raw"}

            json_part = match.group(1)

            # Parse the extracted JSON
            try:
                author = json.loads(json_part)
            except json.JSONDecodeError as e:
                print(f"[add_author] JSON decode error: {e} | Value: {json_part}")
                return {"success": False, "error": "Invalid JSON in processed_text_raw"}

            if not isinstance(author, dict):
                print("[add_author] Parsed author is not a dictionary.")
                return {"success": False, "error": "Author data is not a valid object"}

            name = author.get("name")
            if not name:
                return {"success": False, "error": "Author name is missing"}

            description = author.get("description", "")
            slug = author.get("slug") or name.lower().replace(" ", "-")

            request_data = {
                "name": name,
                "slug": slug,
                "description": description,
                "domain_slug_id": domain_slug_id,
                "workspace_slug_id": workspace_slug_id,
                "derived_by": "ai"
            }

            max_retries = 3
            for attempt in range(1, max_retries + 1):
                try:
                    response = self.api_client.crud('author', 'create', data=request_data)

                    if isinstance(response, dict) and response.get('status_code') == 200:
                        slug_id = response.get('data', {}).get('slug_id', '')
                        print(f"[add_author] Success for '{name}' on attempt {attempt}")
                        return {"success": True, "slug_id": slug_id}

                    print(f"[add_author] Attempt {attempt} failed with response: {response}")

                except Exception as retry_error:
                    print(f"[add_author] Exception on attempt {attempt} for '{name}': {retry_error}")

            print(f"[add_author] Max retries reached for '{name}'")
            return {"success": False, "error": f"Failed to create author '{name}'"}

        except Exception as e:
            print(f"[add_author] Exception: {e}")
            return {"success": False, "error": f"Unexpected error: {str(e)}"}
