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
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ],
        "generationConfig": {
            "responseModalities": ["Text", "Image"]
        }
    }
    headers = {
        "Content-Type": "application/json"
    }

    api_key_to_send_request=get_available_key()
    genai.configure(api_key=api_key_to_send_request)
    model = genai.GenerativeModel("gemini-2.0-flash")
    # API URL
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp-image-generation:generateContent?key={api_key_to_send_request}"
    response = requests.post(url, json=payload, headers=headers)
    response_data = response.json()
    image_base64 = response_data['candidates'][0]['content']['parts'][0]['inlineData']['data']  # Extract base64 image

    ### DEBUG
    # Decode and save image
    image_data = base64.b64decode(image_base64)
    image_path = "gemini_generated_image.png"
    with open(image_path, "wb") as img_file:
        img_file.write(image_data)
    

    return image_base64