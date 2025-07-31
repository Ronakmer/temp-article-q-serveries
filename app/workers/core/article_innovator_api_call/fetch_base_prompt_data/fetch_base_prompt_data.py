

import requests
import os
import time
import json
import uuid
from app.workers.core.article_innovator_api_call.api_client.api_client import APIClient


class FetchBasePromptData:
    def __init__(self):
        self.api_client = APIClient()


    def fetch_base_prompt_data(self, prompt_slug_id, domain_slug_id):
        try:
            collected_base_prompt_data = []
            # print(prompt_slug_id,'prompt_slug_id')
            # for supportive_prompt_slug_id in target_supportive_prompt_ids:
            params = {
                'domain_slug_id': domain_slug_id,
                # 'workspace_slug_id': workspace_slug_id,
                'prompt_slug_id':prompt_slug_id   
            }

            all_base_prompt_data = self.api_client.crud('article-type-variable', 'read', params=params)
            if isinstance(all_base_prompt_data, list):
                collected_base_prompt_data.extend(all_base_prompt_data)
            elif isinstance(all_base_prompt_data, dict):
                collected_base_prompt_data.append(all_base_prompt_data)

            # print(collected_base_prompt_data,'collected_base_prompt_dataxxx')
            return {
                "base_prompt_data": collected_base_prompt_data
            }

        except Exception as e:
            raise ValueError(f"An unexpected error occurred in fetch_base_prompt_data: {e}")













