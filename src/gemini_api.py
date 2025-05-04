from .config import API_KEY
from .api_keys import get_available_key
import google.generativeai as genai
from PIL import Image
import base64
import requests

def analize_image_with_prompt(prompt, image_base64):
    # Send text and image (Base64) to Gemini API to analize using gemini-2.0-flash model.
    api_key_to_send_request=get_available_key()
    if not api_key_to_send_request:
        raise Exception("Rate limit exceeded")
    genai.configure(api_key=api_key_to_send_request)
    model = genai.GenerativeModel("gemini-2.0-flash")

    ### DEBUG
    # Displaying what we are sending to the API (Image + Text)
    # print("Sending request to Gemini API with image and text...")
    # print("Text:", prompt[:100])  # Display only the first 100 characters for brevity
    
    # Send request to Gemini API
    response = model.generate_content(
        contents=[prompt, {"mime_type": "image/png", "data": image_base64}]
    )
    ### DEBUG
    # Print the API response to the console
    # print("Received API Response:", response)
    # print("Response Text:", response.text[:200])  # Display only the first 200 characters for brevity

    return response 

def generate_image_based_on_prompt(prompt):
    # Generate image from pollinations with given prompt
    width=1024
    height=1024
    seed=42
    model="flux"
    get_url = f"https://pollinations.ai/p/{prompt}?width={width}&height={height}&seed={seed}&model={model}"

    response = requests.get(get_url)
    response.raise_for_status()
    image_base64=base64.b64encode(response.content).decode('utf-8')

    return image_base64
