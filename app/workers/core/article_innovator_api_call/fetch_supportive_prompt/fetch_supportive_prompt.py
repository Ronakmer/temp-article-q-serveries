
import requests
import os
import time
import json
import uuid
from app.workers.core.article_innovator_api_call.api_client.api_client import APIClient


class FetchSupportivePrompt:
    def __init__(self):
        self.api_client = APIClient()

    # def fetch_supportive_prompt(self, supportive_prompts_slug_id, domain_slug_id=None):
        # try:
        #     collected_supportive_prompts = []
        #     # print(slug_id,'slug_idxx')
        #     # for supportive_prompt_slug_id in target_supportive_prompt_ids:
        #     params = {
        #         'domain_slug_id': domain_slug_id,
        #         # 'workspace_slug_id': workspace_slug_id,
        #         'slug_id':supportive_prompts_slug_id   
        #     }

        #     all_supportive_prompts = self.api_client.crud('supportive-prompt-variable', 'read', params=params)
        #     if isinstance(all_supportive_prompts, list):
        #         collected_supportive_prompts.extend(all_supportive_prompts)
        #     elif isinstance(all_supportive_prompts, dict):
        #         collected_supportive_prompts.append(all_supportive_prompts)

        #     return {
        #         "supportive_prompts": collected_supportive_prompts
        #     }

        # except Exception as e:
        #     return {"error": f"An unexpected error occurred: {str(e)}"}
        
        

    def fetch_supportive_prompt(self, supportive_prompts_slug_id, domain_slug_id=None):
        """
        Fetch supportive prompts with built-in retry logic (3 attempts, 1s delay).
        """
        max_retries = 3
        delay = 1  # seconds

        params = {
            'domain_slug_id': domain_slug_id,
            'slug_id': supportive_prompts_slug_id
        }

        last_exception = None

        for attempt in range(1, max_retries + 1):
            try:
                all_supportive_prompts = self.api_client.crud(
                    'supportive-prompt-variable', 'read', params=params
                )

                collected_supportive_prompts = []
                if isinstance(all_supportive_prompts, list):
                    collected_supportive_prompts.extend(all_supportive_prompts)
                elif isinstance(all_supportive_prompts, dict):
                    collected_supportive_prompts.append(all_supportive_prompts)

                return {"supportive_prompts": collected_supportive_prompts}

            except Exception as e:
                last_exception = e
                print(f"[Attempt {attempt}/{max_retries}] Error: {e}")
                if attempt < max_retries:
                    time.sleep(delay)

        # return {"error": f"Failed after {max_retries} attempts: {last_exception}"}
        raise ValueError(f"Failed after {max_retries} attempts: {last_exception}")

