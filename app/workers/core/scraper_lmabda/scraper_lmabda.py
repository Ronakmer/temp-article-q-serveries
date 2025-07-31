import requests
import os
from app.config.config import SCRAPER_LAMBDA_URL



class ArticleScraperService:
    def __init__(self):
        self.scraper_lambda_url = SCRAPER_LAMBDA_URL
        self.headers = {
            "Content-Type": "application/json"
        }
        

    def get_scraped_article_data(self, selector_json_data, input_json_data):
        try:
            request_body_data = self.build_scraper_request_body(selector_json_data, input_json_data)

            url = f'{self.scraper_lambda_url}/prod/scrape'

            response = requests.post(url, json=request_body_data, headers=self.headers)

            # print("get_scraped_article_data Status Code:", response.status_code)
            # print("get_scraped_article_data Response Body:", response.json())

            if response.status_code != 200:
                raise ValueError(f"Scraped Lambda returned an error: {response.status_code} - {response.text}")

            # return_data = self.ai_rate_limiter_service.fetch_and_process_content(response.json(), input_json_data)

            response_data = response.json()
            return response_data

        except requests.RequestException as e:
            # return f"Request to scraped lambda failed: {e}"
            raise ValueError(f"Request to scraped lambda failed: {e}")
        except Exception as e:
            # return f"An unexpected error occurred: {e}"
            raise ValueError(f"An unexpected error occurred: {e}")



    def build_scraper_request_body(self, selector_json_data, input_json_data):
        target_url = input_json_data.get("message", {}).get("url", "")
        url_id = input_json_data.get("message", {}).get("url_slug_id", "unique-identifier")

        # Add "html": True to the "content" selector if not already set
        for selector in selector_json_data.get("selectors_data", []):
            if selector.get("name") == "source_content":
                selector["html"] = True

        request_body = {
            "url": target_url,
            "url_id": url_id,
            "selectors_data": selector_json_data.get("selectors_data", [])
        }

        return request_body
