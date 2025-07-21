
import requests
import os
import time
import json
import uuid
from app.workers.core.article_innovator_api_call.api_client.api_client import APIClient


class FetchCategory:
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
