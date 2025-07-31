
import os
import requests
from PIL import Image, ImageOps
from io import BytesIO

def download_top_image(fetch_content_data):
    try:
        # Create output folder
        os.makedirs('downloaded_images', exist_ok=True)

        # Get the image URL
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

        # Load image and convert to RGBA
        image = Image.open(BytesIO(response.content)).convert("RGBA")

        # # Save original image
        # original_path = os.path.join('downloaded_images', 'original_image.png')
        # image.save(original_path)

        # === Add Border ===
        border_size = 10  # in pixels
        border_color = "black"
        bordered_image = ImageOps.expand(image, border=border_size, fill=border_color)

        # Save bordered image
        bordered_path = os.path.join('downloaded_images', 'image_with_border.png')
        bordered_image.save(bordered_path)

        print(f"Image with border saved at: {bordered_path}")

    except Exception as e:
        print(f"Error: {e}")
        return None

# Test input
sample_data = {
    'top_image': 'https://topmovierankings.com/wp-content/uploads/2024/03/Side-Hustlers-Season-2.jpg'
}

# Run it
download_top_image(sample_data)
