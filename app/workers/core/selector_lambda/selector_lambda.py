import requests
import os
from app.config.config import SELECTOR_LAMBDA_URL


class ArticleSelectorService:
    def __init__(self):
        self.selector_lambda_url = SELECTOR_LAMBDA_URL
        self.headers = {
            "Content-Type": "application/json"
        }

    def get_selectors(self, input_json_data):
        try:
            target_url = input_json_data.get("message", {}).get("url", "")

            url = f'{self.selector_lambda_url}/selectors'

            if not self.selector_lambda_url:
                return "Selector Lambda URL is not found"

            data = {
                "url": target_url
            }

            response = requests.post(url, json=data, headers=self.headers)

            # print("get_selectors Status Code:", response.status_code)
            # print("get_selectors Response Body:", response.json())

            if response.status_code != 200:
                return f"Selector Lambda returned an error: {response.status_code} - {response.text}"

            response_data = response.json()
            return response_data
            # Proceed to get article data
            # self.scraper_service.get_scraped_article_data(response.json(), input_json_data)

        except requests.RequestException as e:
            return f"Request to selector lambda failed: {e}"
        except Exception as e:
            return f"An unexpected error occurred: {e}"
