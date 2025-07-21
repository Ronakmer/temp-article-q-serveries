from bs4 import BeautifulSoup, Tag
import uuid
import time
import json
import requests


class ContentProcessor:
    """Processes scraped HTML content for AI rewriting"""
    
    def __init__(self):
        self.supported_elements = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'ul', 'ol', 'blockquote', 'table']
    
    def extract_elements_in_sequence(self, html_content):
        """
        Extract elements from HTML content preserving their sequence
        
        Args:
            html_content (str): HTML content to process
            
        Returns:
            list: List of element dictionaries in their original sequence
        """
        # print(html_content, 'html_contentxxxxxxxxxxx')
        
        if not html_content:
            return []
            
        soup = BeautifulSoup(html_content, 'html.parser')
        elements = []
        
        # Simple but effective approach: iterate through all elements in document order
        for elem in soup.find_all(self.supported_elements):
            # Skip empty elements
            if not elem.get_text().strip():
                continue
                
            # Process based on element type
            if elem.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                # If it's the first h1, treat it as the title
                if elem.name == 'h1' and not any(e.get('html_tag') == 'title' for e in elements):
                    elements.append({
                        'html_tag': 'title',
                        'content': elem.get_text().strip()
                    })
                else:
                    elements.append({
                        'html_tag': elem.name,
                        'content': elem.get_text().strip()
                    })
            
            elif elem.name == 'p':
                elements.append({
                    'html_tag': 'paragraph',
                    'content': elem.get_text().strip()
                })
            
            elif elem.name in ['ul', 'ol']:
                list_items = [li.get_text().strip() for li in elem.find_all('li') if li.get_text().strip()]
                if list_items:
                    elements.append({
                        'html_tag': elem.name,
                        'items': list_items
                    })
            
            elif elem.name == 'blockquote':
                elements.append({
                    'html_tag': 'blockquote',
                    'content': elem.get_text().strip()
                })
            
            elif elem.name == 'table':
                elements.append({
                    'html_tag': 'table',
                    'content': str(elem)
                })
        
        # print(elements,'elementsx')
        
        return elements
    
    def merge_with_prompts(self, elements, prompt_data, system_prompt, model_name, article_id, workspace_slug_id):
        """
        Merge elements with appropriate prompts from input data
        
        Args:
            elements (list): Elements extracted from content
            prompt_data (dict): Prompts from input.json
            system_prompt (str): System prompt for AI
            model_name (str): AI model name to use
            article_id (str): Unique ID for the article
            workspace_slug_id (str): Workspace slug ID from input.json
            
        Returns:
            list: Elements with their corresponding prompts
        """
        merged_content = []
        
        for index, element in enumerate(elements, start=1):
            elem_type = element['html_tag']
            # sequence_index = f"{article_id}-{index}"
            sequence_index = f"{index}"
            
            element_data = {
                'message_id': str(uuid.uuid4()),
                'sequence_index': sequence_index,
                'workspace_id': workspace_slug_id,
                'model': model_name,
                'html_tag': elem_type,
                'system_prompt': system_prompt
            }
            
            if elem_type == 'title' and 'title_rephrase' in prompt_data:
                element_data['prompt'] = prompt_data['title_rephrase']
                element_data['content'] = element['content']
                merged_content.append(element_data)
            
            elif elem_type in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6'] and 'heading_rephrase' in prompt_data:
                element_data['prompt'] = prompt_data['heading_rephrase']
                element_data['content'] = element['content']
                merged_content.append(element_data)
            
            elif elem_type == 'paragraph' and 'para_rephrase' in prompt_data:
                element_data['prompt'] = prompt_data['para_rephrase']
                element_data['content'] = element['content']
                merged_content.append(element_data)
            
            elif elem_type in ['ul', 'ol'] and 'list_rephrase' in prompt_data:
                element_data['prompt'] = prompt_data['list_rephrase']
                element_data['content'] = "\n".join([f"- {item}" for item in element['items']])
                merged_content.append(element_data)
            
            elif elem_type == 'blockquote' and 'blockquote_rephrase' in prompt_data:
                element_data['prompt'] = prompt_data['blockquote_rephrase']
                element_data['content'] = element['content']
                merged_content.append(element_data)
            
            elif elem_type == 'table' and 'table_rephrase' in prompt_data:
                element_data['prompt'] = prompt_data['table_rephrase']
                element_data['content'] = element['content']
                merged_content.append(element_data)
        
        # print(merged_content,'merged_contentx')
        return merged_content
    

    def process_content(self, content_data, input_data, final_prompt_data):
        """
        Process the scraped content and prepare it for AI

        Args:
            content_data (dict): Scraped content data
            input_data (dict): Input configuration with message object

        Returns:
            dict: Processed data ready for AI
        """

        # print(input_data, 'raw_input_data')
        # print(final_prompt_data, 'final_prompt_datasdfsdfsaasdasdasdasdasd')

        # Extract message from input
        message = input_data.get('message', {})

        # Extract prompt-related info
        prompt_info = message.get("prompt", {})
        article_id = message.get("article_slug_id", "")
        # prompt_data = prompt_info.get("prompt_data", {})
        # system_prompt = prompt_data.get("system_rephrase", "")
        prompt_data = final_prompt_data.get('updated_prompt_data', {})
        system_prompt = prompt_data.get("system_rephrase", "")

        model_name = prompt_info.get("ai_rate_model", "deepseek/deepseek_v3")
        # print(model_name,'xxxxxxxxx***************************')
        # logging.error(f"{model_name},'xxxxxxxxx***************************'")
        
        # for test
        # model_name = "deepseek/deepseek_v3"


        # print(system_prompt, 'system_prompt_extracted')

        # Extract workspace ID
        workspace_slug_id = message.get('workspace', {}).get('slug_id', '')

        # Generate unique article ID
        # article_id = str(uuid.uuid4())

        processed_data = {
            'article_id': article_id,
            'workspace_id': workspace_slug_id,
            'ai_requests': []
        }

        # Initialize title and content
        content_html = None
        title_value = None

        for selector in content_data.get('selectors_output', []):
            # print(selector, 'selector_check')
            if selector['name'] == 'source_content':
                content_html = selector['value']
            elif selector['name'] == 'source_title':
                title_value = selector['value']

        # print(content_html, 'content_htmlxxxxxxxxxxx')
        # Process content elements
        if content_html:
            elements = self.extract_elements_in_sequence(content_html)
            # print(elements, 'extracted_elements')

            # Add title to elements if not already present
            if title_value and not any(e['html_tag'] == 'title' for e in elements):
                elements.insert(0, {
                    'html_tag': 'title',
                    'content': title_value
                })

            # Merge with prompt data
            # print(prompt_info, 'prompt_check')
            # print(prompt_data, 'prompt_data_check')

            processed_data['ai_requests'] = self.merge_with_prompts(
                elements,
                prompt_data,
                system_prompt,
                model_name,
                article_id,
                workspace_slug_id
            )

        print(processed_data, 'final_processed_data')

        return processed_data


    def fetch_content(self, scraper_data, sleep_time=5):
        """
        Fetch content from the URL returned by the scraper API
        
        Args:
            scraper_data (dict): The response from the scraper API
            
        Returns:
            dict: The content data or None if failed
        """
        
        # print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        # Extract public URL from response
        response_obj = scraper_data.get('response', {})
        public_url = response_obj.get('public_url')        

        self.sleep_time = sleep_time

        if not public_url:
            print("Error: No public URL found in scraper response")
            return None
            
        # Give S3 some time to make the file available (if configured)
        if self.sleep_time > 0:
            time.sleep(self.sleep_time)
        
        # print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@22')
        try:
            # Download content
            content_response = requests.get(public_url)
            
            if content_response.status_code != 200:
                print(f"Error: Failed to fetch content, status code {content_response.status_code}")
                return None
                
            # print(content_response.json(),'&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&')
            # Parse content
            try:
                return content_response.json()
            except json.JSONDecodeError:
                return content_response.text
                
        except Exception as e:
            print(f"Error fetching content: {e}")
            return None 
        
        
        