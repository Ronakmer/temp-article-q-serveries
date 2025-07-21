
import requests
import os
from app.workers.core.article_innovator_api_call.api_client.api_client import APIClient
import time
import json
import uuid


class FetchAuthor:
    def __init__(self):
        self.api_client = APIClient()

    def fetch_author(self, input_json_data):
        try:
            print("Input JSON Data:", input_json_data)

            message = input_json_data.get("message", {})
            # target_author_ids = message.get("wp_author_id", [])

            domain_slug_id = message.get("domain_id", {}).get("domain_slug_id")
            workspace_slug_id = message.get("workspace_id", {}).get("workspace_slug_id")

            if not domain_slug_id or not workspace_slug_id:
                return {"error": "Missing domain or workspace slug ID in input."}

            collected_authors = []

            # for author_slug_id in target_author_ids:
            params = {
                'domain_slug_id': domain_slug_id,
                'workspace_slug_id': workspace_slug_id,
                # 'wp_author_id': author_slug_id  # Pass one author slug at a time
            }

            all_authors = self.api_client.crud('author', 'read', '', params)
            if isinstance(all_authors, list):
                collected_authors.extend(all_authors)
            elif isinstance(all_authors, dict):
                collected_authors.append(all_authors)

            return {
                "success": True,
                "authors": collected_authors
            }

        except Exception as e:
            return {"error": f"An unexpected error occurred: {str(e)}"}
