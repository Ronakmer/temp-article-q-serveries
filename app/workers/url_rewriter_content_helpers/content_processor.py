from bs4 import BeautifulSoup, Tag
import uuid
import time
import json
import requests
import os

class ContentProcessor:

    def __init__(self, sleep_time=5):
        self.sleep_time = sleep_time
        

    def fetch_content(self, scraper_data):
        """
        Fetch content from the URL returned by the scraper API.
        
        Args:
            scraper_data (dict): The response from the scraper API
            
        Returns:
            dict: Cleaned and structured content data or None if failed
        """
        response_obj = scraper_data.get('response', {})
        public_url = response_obj.get('public_url')

        if not public_url:
            print("❌ Error: No public URL found in scraper response")
            raise ValueError("❌ Error: No public URL found in scraper response")
            # return None

        # Wait for S3 to make file available
        if self.sleep_time > 0:
            time.sleep(self.sleep_time)

        try:
            content_response = requests.get(public_url)

            if content_response.status_code != 200:
                print(f"❌ Error: Failed to fetch content, status code {content_response.status_code}")
                raise ValueError(f"❌ Error: Failed to fetch content, status code {content_response.status_code}")
                # return None

            # Load JSON from response
            data = content_response.json()

            # Clean HTML from source_content
            for item in data.get("selectors_output", []):
                if item["name"] == "source_content":
                    item["value"] = self.clean_html(item["value"])

            
            os.makedirs('demo_json', exist_ok=True)
            # Save cleaned JSON to file
            with open('demo_json/content_response.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

            return data

        except Exception as e:
            print(f"❌ Error fetching or parsing content: {e}")
            raise ValueError(f"❌ Error fetching or parsing content: {e}")
            # return None


    def clean_html(self, raw_html):
        """Clean raw HTML content and return plain text."""
        soup = BeautifulSoup(raw_html, "html.parser")

        # Optional: Remove ads and unnecessary tags
        for tag in soup(["script", "style", "ins", "iframe", "noscript"]):
            tag.decompose()

        # Return cleaned text (or you can return HTML with `soup.prettify()`)
        return soup.get_text(separator="\n").strip()



    def process_content(self, content_data, input_data=None, final_prompt_data=None):
        try:
            # # Extract selectors_output from content_data
            selectors = content_data.get('selectors_output', []) if content_data else []

            # # Initialize title and content
            content_html = None
            title_value = None

            for selector in selectors:
                if selector.get('name') == 'source_content':
                    content_html = selector.get('value')
                elif selector.get('name') == 'source_title':
                    title_value = selector.get('value')

            # # Directly extract values from content_data
            # content_html = content_data.get('source_content', None) if content_data else None
            # title_value = content_data.get('source_title', None) if content_data else None


            # # Create processed data dictionary
            processed_data = {
                'source_title': title_value,
                'source_content': content_html
            }
            
            # print(processed_data, 'processed_datasdfsdfsdfsfsdf')


            # Save cleaned JSON to file
            with open('demo_json/processed_data.json', 'w', encoding='utf-8') as f:
                json.dump(processed_data, f, ensure_ascii=False, indent=4)

            return processed_data

        except Exception as e:
            # Log or handle the error
            print(f"[process_content] Error: {e}")
            raise ValueError(f"[process_content] Error: {e}")
