import requests
import os
import time
import json
import uuid
# from app.workers.core.article_innovator_api_call.api_client.api_client import APIClient
from app.config.logger import LoggerSetup
from app.config.config import AI_RATE_LIMITER_URL



class AIRateLimiter:
    def __init__(self):
        logger_setup = LoggerSetup()
        # self.logger = logger_setup.setup_worker_logger()

        # self.api_client = APIClient()
        self.ai_rate_limiter_url = AI_RATE_LIMITER_URL
        self.headers = {
            "Content-Type": "application/json"
        }



    def scale_worker(self, worker_id, count=1):
        """Scale up worker instances"""
        scale_url = f"{self.ai_rate_limiter_url}/workers/scale/{worker_id}"   
        # self.logger.info(f"scale_url: {scale_url}")
        print(f"scale_url: {scale_url}")

        scale_data = {"count": count}
        
        headers = {'Content-Type': 'application/json'}

        try:
            response = requests.post(scale_url, json=scale_data, headers=headers)
            if response.status_code in [200, 201]:
                # self.logger.info(f"Successfully scaled worker {worker_id} with count {count}")
                print(f"Successfully scaled worker {worker_id} with count {count}")
                return True
            else:
                # self.logger.error(f"Failed to scale worker: {response.status_code} - {response.text}")
                print(f"Failed to scale worker: {response.status_code} - {response.text}")
                return False
        except requests.RequestException as e:
            # self.logger.error(f"Exception during scaling worker: {e}")
            print(f"Exception during scaling worker: {e}")
            return False
    
        
        