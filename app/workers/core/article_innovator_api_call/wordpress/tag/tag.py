
import requests
import os
import time
import json
import uuid
from app.workers.core.article_innovator_api_call.api_client.api_client import APIClient
import re


class Tag:
    def __init__(self):
        self.api_client = APIClient()

    def fetch_tag(self, input_json_data):
        try:
            print("Input JSON Data:", input_json_data)

            message = input_json_data.get("message", {})
            # target_tag_ids = message.get("wp_tag_id", [])
            print(message,'messagezzz')
            domain_slug_id = message.get("domain_id", {}).get("domain_slug_id")
            workspace_slug_id = message.get("workspace_id", {}).get("workspace_slug_id")

            if not domain_slug_id or not workspace_slug_id:
                return {"error": "Missing domain or workspace slug ID in input."}

            collected_tags = []

            # for cat_slug_id in target_tag_ids:
            params = {
                'domain_slug_id': domain_slug_id,
                'workspace_slug_id': workspace_slug_id,
                # 'wp_tag_id': cat_slug_id  # Pass one tag slug at a time
            }

            all_tags = self.api_client.crud('tag', 'read', params=params)
            if isinstance(all_tags, list):
                collected_tags.extend(all_tags)
            elif isinstance(all_tags, dict):
                collected_tags.append(all_tags)

            print(all_tags,'all_tagsxxx')
            print(all_tags.json(),'all_tagsxxx')
            return {
                "success": True,
                "tags": collected_tags
            }

        except Exception as e:
            return {"error": f"An unexpected error occurred: {str(e)}"}







    def add_tag(self, new_tag, domain_slug_id, workspace_slug_id):
        try:
            # Convert tuple to string if necessary
            domain_slug_id = domain_slug_id[0] if isinstance(domain_slug_id, tuple) else domain_slug_id
            workspace_slug_id = workspace_slug_id[0] if isinstance(workspace_slug_id, tuple) else workspace_slug_id

            print(domain_slug_id, workspace_slug_id, 'domain_slug_id, workspace_slug_id')
            print(new_tag, 'new_tag raw input')

            # Ensure new_tag is a dictionary
            if isinstance(new_tag, str):
                new_tag = json.loads(new_tag)

            ai_response = new_tag.get("ai_response", {})
            if isinstance(ai_response, str):
                ai_response = json.loads(ai_response)

            result_data = ai_response.get("result", {})
            processed_text_raw = result_data.get("processed_text")

            if not processed_text_raw or not processed_text_raw.strip():
                print("[add_tag] processed_text_raw is empty or None.")
                return {"success": False, "error": "processed_text_raw is empty or invalid"}

            # Remove code fences
            cleaned_text = re.sub(r'```json|```', '', processed_text_raw).strip()

            # Extract JSON part (array or object) from text
            match = re.search(r'(\{.*\}|\[.*\])', cleaned_text, re.DOTALL)
            if not match:
                print("[add_tag] No valid JSON found in processed_text_raw")
                return {"success": False, "error": "No valid JSON found in processed_text_raw"}

            json_part = match.group(1)

            # Parse the extracted JSON
            try:
                processed_data = json.loads(json_part)
            except json.JSONDecodeError as e:
                print(f"[add_tag] JSON decode error: {e} | Value: {json_part}")
                return {"success": False, "error": "Invalid JSON in processed_text_raw"}

            # Flatten nested [[ {...} ]] to [ {...} ]
            if isinstance(processed_data, list) and len(processed_data) == 1 and isinstance(processed_data[0], list):
                processed_data = processed_data[0]

            # Ensure tags is always a list of dicts
            tags = processed_data if isinstance(processed_data, list) else [processed_data]
            if not tags or not all(isinstance(c, dict) for c in tags):
                print("[add_tag] Processed data is empty or invalid format.")
                return {"success": False, "error": "Processed data is empty or invalid"}

            # --- Create tags via API ---
            slug_ids = []
            for tag in tags:
                name = tag.get("name")
                description = tag.get("description", "")
                slug = tag.get("slug") or name.lower().replace(" ", "-")

                request_data = {
                    "name": name,
                    "slug": slug,
                    "description": description,
                    "domain_slug_id": domain_slug_id,
                    "workspace_slug_id": workspace_slug_id,
                    "derived_by": "ai"
                }

                max_retries = 3
                tag_response = None

                for attempt in range(1, max_retries + 1):
                    try:
                        tag_response = self.api_client.crud(
                            'tag',
                            'create',
                            data=request_data
                        )

                        if isinstance(tag_response, dict) and tag_response.get('status_code') == 200:
                            print(tag_response, 'sdfsfsdftag_responsesdfsdfsdf')
                            real_slug_id = tag_response.get('data', {}).get('slug_id', '')
                            slug_ids.append(real_slug_id)
                            # slug_ids.append(slug)
                            print(f"[add_tag] Success for '{name}' (slug: {slug}) on attempt {attempt}")
                            break
                        else:
                            print(f"[add_tag] Attempt {attempt} failed for '{name}' with response: {tag_response}")

                    except Exception as retry_error:
                        print(f"[add_tag] Exception on attempt {attempt} for '{name}': {retry_error}")

                    if attempt == max_retries:
                        print(f"[add_tag] Max retries reached for '{name}'")
                        slug_ids.append(f"{slug}-error")

            print(f"[add_tag] Slugs added: {slug_ids}")
            return {"success": True, "slug_id": slug_ids}

        except Exception as e:
            print(f"[add_tag] Exception: {e}")
            return {"success": False, "error": f"Unexpected error: {str(e)}"}
