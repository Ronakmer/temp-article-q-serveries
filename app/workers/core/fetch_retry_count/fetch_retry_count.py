import requests
import os
import time
import json
import uuid
from app.workers.core.article_innovator_api_call.api_client.api_client import APIClient


class FetchRetryCount:
    def __init__(self):
        self.api_client = APIClient()

    def fetch_retry_count(self, slug_id):
        try:
            collected_retry_count = []
            print(slug_id,'slug_idxx')
            # for supportive_prompt_slug_id in target_supportive_prompt_ids:
            
            request_data = {
                'slug_id':slug_id   
            }

            # Use combined IDs as item_id for the update call
            request_item_id = f"{slug_id}"

            all_retry_count = self.api_client.crud('ai-message', 'update', data=request_data,item_id=request_item_id)

            if isinstance(all_retry_count, list):
                collected_retry_count.extend(all_retry_count)
            elif isinstance(all_retry_count, dict):
                collected_retry_count.append(all_retry_count)

            return {
                "retry_count": collected_retry_count
            }

        except Exception as e:
            return {"error": f"An unexpected error occurred: {str(e)}"}
