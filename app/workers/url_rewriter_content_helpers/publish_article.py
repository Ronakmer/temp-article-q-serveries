import requests
import os
import json
import time
import logging
from app.workers.core.article_innovator_api_call.api_client.api_client import APIClient
# from app.workers.core.article_innovator_api_call.wordpress.add_category.add_category import AddCategory
from typing import Dict, List, Any
import re
import os
import requests
from PIL import Image, ImageFilter
from io import BytesIO
from PIL import Image, ImageFilter, ImageOps



class PublishArticle:
    def __init__(self):
        self.headers = {
            "Content-Type": "application/json"
        }
        
        self.api_client = APIClient()
        # self.add_category_service = AddCategory()



    def publish_article(self, all_stored_content_message_data, all_stored_wp_message_data, temp_article_id):
        try:
            get_input_json_datas = None
            wp_featured_image = None

            if not all_stored_content_message_data:
                # return {'success': False, 'error': 'Message data is empty'}
                raise ValueError({'success': False, 'error': 'Message data is empty'})

            # Normalize input
            if isinstance(all_stored_content_message_data, dict):
                all_stored_content_message_data = [all_stored_content_message_data]
            elif not isinstance(all_stored_content_message_data, list):
                # return {'success': False, 'error': 'Invalid message data format'}
                raise ValueError({'success': False, 'error': 'Invalid message data format'})

            # Extract ai_response
            first_item = all_stored_content_message_data[0]
            if "data" in first_item and isinstance(first_item["data"], list) and first_item["data"]:
                first_item = first_item["data"][0]

            ai_response_raw = first_item.get("ai_response", "")
            if not ai_response_raw:
                # return {'success': False, 'error': 'AI response missing'}
                raise ValueError({'success': False, 'error': 'AI response missing'})

            ai_response_dict = json.loads(ai_response_raw)
            processed_text = ai_response_dict.get("result", {}).get("processed_text", "")
            if not processed_text:
                # return {'success': False, 'error': 'Processed text missing'}
                raise ValueError({'success': False, 'error': 'Processed text missing'})

            # Extract JSON content
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', processed_text, re.DOTALL)
            json_string = json_match.group(1) if json_match else processed_text.strip()
            content_data = json.loads(json_string)

            generated_article_title = content_data.get("title", "")
            generated_article_content = content_data.get("content", "")


            # Fetch input_json_data
            try:
                from app.workers.url_rewriter_para_response_helpers.get_input_json_data import GetInputJson
                self.get_input_json_service = GetInputJson()
                get_input_json_datas = self.get_input_json_service.get_input_json_data_for_wp(temp_article_id)
            except Exception as e:
                # print({"status": "error", "step": "get_input_json_datas", "message": str(e)})
                raise ValueError({"status": "error", "step": "get_input_json_datas", "message": str(e)})
            
            try:
                wp_featured_image = self.image_process(get_input_json_datas)
                print(wp_featured_image,'wp_featured_imagesdfsdfs')
            except Exception as e:
                # print({"status": "error", "step": "image_process", "message": str(e)})
                raise ValueError({"status": "error", "step": "image_process", "message": str(e)})
            
                
            data_list = get_input_json_datas.get("data", [])
            if not data_list:
                # return {"success": False, "error": "No input_json_data found for article"}
                raise ValueError({"success": False, "error": "No input_json_data found for article"})

            input_data = data_list[0].get("input_json_data", {}).get("message", {})

            # Extract flags
            ai_flags = input_data.get("ai_content_flags", {})

            domain_slug_id = input_data.get("domain", {}).get("slug_id", ""),
            workspace_slug_id = input_data.get("workspace", {}).get("slug_id", ""),




            # # Default values from input_data
            # wp_category_slug_ids = input_data.get("wp_category", [])
            # wp_tag_slug_ids = input_data.get("wp_tag", [])
            # wp_author_slug_id = str(input_data.get("wp_author") or "").strip()

            # # If AI-selected categories/tags/authors are enabled, extract them from wp_data_list
            # if ai_flags.get("is_wp_categories_selected_by_ai") or \
            # ai_flags.get("is_wp_tags_selected_by_ai") or \
            # ai_flags.get("is_wp_authors_selected_by_ai"):
            #     wp_processed = self.process_wp_data(all_stored_wp_message_data)
                
            #     if ai_flags.get("is_wp_categories_selected_by_ai"):
            #         wp_category_slug_ids = wp_processed.get("categories", []) or wp_category_slug_ids
            #     if ai_flags.get("is_wp_tags_selected_by_ai"):
            #         wp_tag_slug_ids = wp_processed.get("tags", []) or wp_tag_slug_ids
            #     if ai_flags.get("is_wp_authors_selected_by_ai") and wp_processed.get("author"):
            #         wp_author_slug_id = wp_processed["author"]


            # Default values from input_data
            wp_category_slug_ids = input_data.get("wp_category", [])
            wp_tag_slug_ids = input_data.get("wp_tag", [])
            wp_author_slug_id = str(input_data.get("wp_author") or "").strip()

            # Process AI categories/tags/authors (selected or generated)
            if any([
                ai_flags.get("is_wp_categories_selected_by_ai"),
                ai_flags.get("is_wp_categories_generated_by_ai"),
                ai_flags.get("is_wp_tags_selected_by_ai"),
                ai_flags.get("is_wp_tags_generated_by_ai"),
                ai_flags.get("is_wp_authors_selected_by_ai"),
                ai_flags.get("is_wp_authors_generated_by_ai")
            ]):
                wp_processed = self.process_wp_data(all_stored_wp_message_data, domain_slug_id, workspace_slug_id)

                # Save the data to a JSON file
                with open('demo_json/wp_processed.json', 'w', encoding='utf-8') as f:
                    json.dump(wp_processed, f, ensure_ascii=False, indent=4)
                
                # Merge categories
                if ai_flags.get("is_wp_categories_selected_by_ai") or ai_flags.get("is_wp_categories_generated_by_ai"):
                    wp_category_slug_ids = list(set(wp_category_slug_ids + wp_processed.get("categories", [])))

                # Merge tags
                if ai_flags.get("is_wp_tags_selected_by_ai") or ai_flags.get("is_wp_tags_generated_by_ai"):
                    wp_tag_slug_ids = list(set(wp_tag_slug_ids + wp_processed.get("tags", [])))

                # Merge author
                if (ai_flags.get("is_wp_authors_selected_by_ai") or ai_flags.get("is_wp_authors_generated_by_ai")) and wp_processed.get("author"):
                    wp_author_slug_id = wp_processed["author"]



            # Prepare request payload
            request_data = {
                "article_slug_id": input_data.get("article_slug_id"),
                "article_type_slug_id": input_data.get("prompt", {}).get("article_type", {}).get("slug_id", ""),
                "author_slug_id": wp_author_slug_id,
                "domain_slug_id": input_data.get("domain", {}).get("slug_id", ""),
                "category_slug_id": wp_category_slug_ids,
                "tag_slug_id": wp_tag_slug_ids,
                "workspace_slug_id": input_data.get("workspace", {}).get("slug_id", ""),
                "wp_title": generated_article_title,
                "wp_content": generated_article_content,
                "article_status": input_data.get("article_status"),
                "wp_status": input_data.get("wp_status"),
                "wp_featured_image": wp_featured_image,
            }

            # Retry logic
            request_item_id = f"{input_data.get('article_slug_id')}"
            max_retries = 3
            for attempt in range(1, max_retries + 1):
                stored_message = self.api_client.crud(
                    'article', 'update', data=request_data, item_id=request_item_id
                )
                print(stored_message, f'stored_message [debug] attempt {attempt}')

                if stored_message.get('status_code') == 200:
                    return stored_message
                else:
                    print(f"Attempt {attempt} failed with status_code {stored_message.get('status_code')}. Retrying...")

            # return {
            #     "success": False,
            #     "error": f"Failed to update after {max_retries} attempts",
            #     "last_response": stored_message,
            # }
            raise ValueError({
                "success": False,
                "error": f"Failed to update after {max_retries} attempts",
                "last_response": stored_message,
            })

        except Exception as e:
            print(f"[publish_article] Exception: {e}")
            # return {"success": False, "error": f"Unexpected error: {str(e)}"}
            raise ValueError({"success": False, "error": f"Unexpected error publish_article: {str(e)}"})

    



    def fetch_slug_id(self, field_type, data_item, domain_slug_id, workspace_slug_id):
        """Fetch slug_id from API dynamically based on field_type."""

        print(f"Fetching slug_id for field_type: {field_type}, data_item: {data_item}")


        if field_type == "category":
            try:
                from app.workers.core.article_innovator_api_call.wordpress.category.category import Category
                category_service = Category()
                add_category_response = category_service.add_category(data_item, domain_slug_id, workspace_slug_id)
                print(f"Category added: {add_category_response}")
                if add_category_response.get("success"):
                    return add_category_response.get("slug_id")
                return None


            except Exception as e:
                print(f"Error new adding category: {e}")
                # return None
                raise ValueError(f"Error new adding category: {e}")
            
        if field_type == "tag":
            try:
                from app.workers.core.article_innovator_api_call.wordpress.tag.tag import Tag
                tag_service = Tag()
                add_tag_response = tag_service.add_tag(data_item, domain_slug_id, workspace_slug_id)
                print(f"tag added: {add_tag_response}")
                if add_tag_response.get("success"):
                    return add_tag_response.get("slug_id")
                return None


            except Exception as e:
                print(f"Error new adding tag: {e}")
                # return None
                raise ValueError(f"Error new adding tag: {e}")

        if field_type == "author":
            # print('this is author')
            try:
                from app.workers.core.article_innovator_api_call.wordpress.author.author import Author
                author_service = Author()
                add_author_response = author_service.add_author(data_item, domain_slug_id, workspace_slug_id)
                print(f"author added: {add_author_response}")
                if add_author_response.get("success"):
                    return add_author_response.get("slug_id")
                return None


            except Exception as e:
                print(f"Error new adding tag: {e}")
                # return None
                raise ValueError(f"Error new adding tag: {e}")
        
        return None


    def process_wp_data(self, wp_data_list, domain_slug_id, workspace_slug_id):
        
        print(wp_data_list,'wp_data_listsdfsdfsdfswqwa')
        categories, tags, author = [], [], None

        for item in wp_data_list.get("data", []):
            try:
                ai_response = json.loads(item.get("ai_response", "{}"))
                processed_text = ai_response.get("result", {}).get("processed_text", "")

                try:
                    # Remove Markdown formatting like ```json ... ```
                    if processed_text.startswith("```json") and processed_text.endswith("```"):
                        processed_text = processed_text[len("```json"): -len("```")].strip()
                    elif processed_text.startswith("```") and processed_text.endswith("```"):
                        processed_text = processed_text[len("```"): -len("```")].strip()
                except:
                    processed_text=processed_text


                # slug_id = None
                # try:
                #     data = json.loads(processed_text)
                #     if isinstance(data, list):
                #         slug_id = data[0].get("slug_id")
                #     elif isinstance(data, dict):
                #         slug_id = data.get("slug_id")
                # except:
                #     slug_id = None

                slug_id = None
                try:
                    data = json.loads(processed_text)
                    if isinstance(data, list):
                        if len(data) > 0 and isinstance(data[0], list):
                            # Handles [[{...}]]
                            slug_id = data[0][0].get("slug_id")
                        elif len(data) > 0 and isinstance(data[0], dict):
                            slug_id = data[0].get("slug_id")
                    elif isinstance(data, dict):
                        slug_id = data.get("slug_id")
                except Exception as e:
                    print(f"Error parsing processed_text: {e}")
                    slug_id = None

                print(slug_id, 'slug_id_ronksdfmsdf')
                
                field_type = item.get("message_field_type", "")
                print('field_type', field_type)

                # If slug_id missing, call endpoint
                if not slug_id:
                    print(f"{field_type} slug_id not found, calling endpoint...")
                    slug_id = self.fetch_slug_id(field_type, item, domain_slug_id, workspace_slug_id)
                    print(f"Fetched slug_id: {slug_id}")


                if slug_id:
                    if field_type == "category":
                        # categories.append(slug_id)
                        if isinstance(slug_id, list):
                            categories.extend(slug_id)  # Merge lists
                        else:
                            categories.append(slug_id)
                    elif field_type == "tag":
                        # tags.append(slug_id)

                        if isinstance(slug_id, list):
                            tags.extend(slug_id)  # Merge lists
                        else:
                            tags.append(slug_id)

                    elif field_type == "author":
                        author = slug_id

            except Exception as e:
                print(f"Error processing item {item.get('id')}: {e}")
                raise ValueError(f"Error processing item {item.get('id')}: {e}")

        return {"categories": categories, "tags": tags, "author": author}


    def image_process(self, input_json_data):
        try:
            print('======================== image_process ==========================================')
            input_data = input_json_data.get("data", [])[0].get("input_json_data", {}).get("message", {})
            article_slug_id = input_data.get("article_slug_id")
            workspace_name = input_data.get("workspace", {}).get("slug_id")


            if not input_data:
                return {"success": False, "error": "No message data found in input_json_data"}

            # Assign 'data' properly for internal use
            data = {"message": input_data}
            file_name = 'featured_image.webp'  
            imagekit_url = None

            try:
                from app.workers.core.selector_lambda.selector_lambda import ArticleSelectorService
                self.selector_service = ArticleSelectorService()

                # Step 1: Get selectors
                selector_data = self.selector_service.get_selectors(data)
                # print(selector_data,'----------------------selector_data----------------------')
                
            except Exception as e:
                print({"status": "error", "step": "get_selectors", "message": str(e)})
                raise ValueError({"status": "error", "step": "get_selectors", "message": str(e)})
   
            try:
                from app.workers.core.scraper_lmabda.scraper_lmabda import ArticleScraperService 
                self.scraper_service = ArticleScraperService()

                # Step 2: Scrape article data
                scraped_data = self.scraper_service.get_scraped_article_data(selector_data, data)
                # print(scraped_data,'----------------------scraped_data----------------------')
            except Exception as e:
                print({"status": "error", "step": "get_scraped_article_data", "message": str(e)})
                # return {"status": "error", "step": "get_scraped_article_data", "message": str(e)}
                raise ValueError({"status": "error", "step": "get_scraped_article_data", "message": str(e)})


            try:
                from app.workers.url_rewriter_content_helpers.content_processor import ContentProcessor
                self.content_processor_service = ContentProcessor()

                # Step 5: final prompt
                fetch_content_data = self.content_processor_service.fetch_content(scraped_data)
                # print(fetch_content_data,'----------------------fetch_content_data----------------------')
            except Exception as e:
                print({"status": "error", "step": "fetch_content", "message": str(e)})
                # return {"status": "error", "step": "final_prompt_creator", "message": str(e)}
                raise ValueError({"status": "error", "step": "final_prompt_creator", "message": str(e)})


            try:
                print('======================== download_top_image ==========================================')
                
                download_image = self.download_top_image(fetch_content_data)
                print(download_image,'sdfdownload_imagesdsdfsdfsdfsdf')
            except Exception as e:
                print({"status": "error", "step": "download_top_image", "message": str(e)})
                # return {"status": "error", "step": "final_prompt_creator", "message": str(e)}
                raise ValueError({"status": "error", "step": "final_prompt_creator", "message": str(e)})

            try:
                print('======================== upload_to_imagekit ==========================================')
                
                from app.workers.core.image_kit.image_kit import UploadToImageKit
                self.image_kit_service = UploadToImageKit()
                
                imagekit_url = self.image_kit_service.upload_to_imagekit(download_image, file_name, workspace_name)
                print(imagekit_url, 'imagekit_urlsdfsdfsdf')
            except Exception as e:
                print({"status": "error", "step": "upload_to_imagekit", "message": str(e)})
                # return {"status": "error", "step": "final_prompt_creator", "message": str(e)}
                raise ValueError({"status": "error", "step": "final_prompt_creator", "message": str(e)})

            return imagekit_url


        except Exception as e:
            # return {"success": False, "error": f"image_process: {e}"}
            raise ValueError({"success": False, "error": f"image_process: {e}"})





    # def download_top_image(self, fetch_content_data):
    #     try:
    #         os.makedirs('downloaded_images', exist_ok=True)

    #         top_image_url = fetch_content_data.get('top_image', '')
    #         if not top_image_url:
    #             print("No top_image found in the response.")
    #             return None

    #         response = requests.get(top_image_url)
    #         response.raise_for_status()

    #         image = Image.open(BytesIO(response.content))

    #         # Apply a sample filter
    #         filtered_image = image.filter(ImageFilter.EMBOSS)
    #         return filtered_image

    #     except Exception as e:
    #         print(f"Failed to download or process image: {e}")
    #         return None
    
    
    def download_top_image(self, fetch_content_data):
        try:
            os.makedirs('downloaded_images', exist_ok=True)

            top_image_url = fetch_content_data.get('top_image', '')
            if not top_image_url:
                print("No top_image found in the response.")
                return None

            print(f"Downloading image from: {top_image_url}")
            response = requests.get(top_image_url, stream=True)
            response.raise_for_status()

            # Check Content-Type
            content_type = response.headers.get('Content-Type', '')
            if 'image' not in content_type:
                print("The URL did not return an image.")
                return None

            image = Image.open(BytesIO(response.content)).convert("RGBA")

            # Add border
            border_size = 10
            border_color = "black"
            final_image = ImageOps.expand(image, border=border_size, fill=border_color)

            # # Save final image
            # final_path = os.path.join('downloaded_images', 'processed_image.png')
            # final_image.save(final_path)

            # print(f"Processed image saved at: {final_path}")
            return final_image

        except Exception as e:
            print(f"Failed to download or process image: {e}")
            raise ValueError(f"Failed to download or process image: {e}")
            # return None


