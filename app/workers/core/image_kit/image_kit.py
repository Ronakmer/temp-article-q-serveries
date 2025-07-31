
from imagekitio import ImageKit
import json, io, os, base64
from imagekitio.models import UploadFileRequestOptions
from PIL import Image
from imagekitio.models.UploadFileRequestOptions import UploadFileRequestOptions

import requests
import os
import time
import json
import uuid
# from app.workers.core.article_innovator_api_call.api_client.api_client import APIClient
import re
from app.config.config import IMAGE_KIT_PUBLIC_KEY, IMAGE_KIT_PRIVATE_KEY, IMAGE_KIT_URL_ENDPOINT

class UploadToImageKit:
    def __init__(self):
        # self.api_client = APIClient()
        # self.public_key = IMAGE_KIT_PUBLIC_KEY
        # self.private_key = IMAGE_KIT_PRIVATE_KEY
        # self.url_endpoint = IMAGE_KIT_URL_ENDPOINT

        print("iamge kit class initialized")


    def upload_to_imagekit(self, image, file_name, workspace_name):
        folder_path = f"articleInnovator/featured_image/{workspace_name}"
        try:
            print(f"Uploading to folder: {folder_path}")

            print(IMAGE_KIT_PUBLIC_KEY, IMAGE_KIT_PRIVATE_KEY, IMAGE_KIT_URL_ENDPOINT)

            
            imagekit = ImageKit(
                private_key=IMAGE_KIT_PRIVATE_KEY,
                public_key=IMAGE_KIT_PUBLIC_KEY,
                url_endpoint=IMAGE_KIT_URL_ENDPOINT
            )

            # Ensure image is in the correct format
            file_content = io.BytesIO()
            if not isinstance(image, Image.Image):
                return None, "Invalid image object."
            if image.format != 'WEBP':
                image = image.convert('RGB')
            image.save(file_content, format='WEBP')
            file_content.seek(0)

            binary_file = base64.b64encode(file_content.read())

            options = UploadFileRequestOptions(
                folder=folder_path,
                use_unique_file_name=True,
                tags=["articleInnovator", "imageGen"]
            )

            upload_result = imagekit.upload_file(
                file=binary_file,
                file_name=file_name,
                options=options
            )

            if hasattr(upload_result, 'url'):
                print(f"Upload successful: {upload_result.url}")
                return upload_result.url, None
            else:
                # return None, "Upload failed: URL missing."
                raise ValueError(None, "Upload failed: URL missing.")

        except Exception as e:
            # return None, f"Upload failed: {str(e)}"
            raise ValueError(None, f"Upload failed: {str(e)}")
