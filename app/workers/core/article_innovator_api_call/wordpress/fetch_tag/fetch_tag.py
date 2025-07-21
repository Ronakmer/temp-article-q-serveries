
import requests
import os
from app.workers.core.article_innovator_api_call.api_client.api_client import APIClient
import time
import json
import uuid


class FetchTag:
    def __init__(self):
        self.api_client = APIClient()

    def fetch_tag(self, input_json_data):
        try:
            print("Input JSON Data:", input_json_data)

            message = input_json_data.get("message", {})
            # target_tag_ids = message.get("wp_tag_id", [])

            domain_slug_id = message.get("domain_id", {}).get("domain_slug_id")
            workspace_slug_id = message.get("workspace_id", {}).get("workspace_slug_id")

            if not domain_slug_id or not workspace_slug_id:
                return {"error": "Missing domain or workspace slug ID in input."}

            collected_tags = []

            # for tag_slug_id in target_tag_ids:
            params = {
                'domain_slug_id': domain_slug_id,
                'workspace_slug_id': workspace_slug_id,
                # 'wp_tag_id': tag_slug_id  # Pass one tag slug at a time
            }

            all_tags = self.api_client.crud('tag', 'read', '', params)
            if isinstance(all_tags, list):
                collected_tags.extend(all_tags)
            elif isinstance(all_tags, dict):
                collected_tags.append(all_tags)

            return {
                "success": True,
                "tags": collected_tags
            }

        except Exception as e:
            return {"error": f"An unexpected error occurred: {str(e)}"}
