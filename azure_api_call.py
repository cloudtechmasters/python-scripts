import requests
import base64
import json
import time
import logging
import os

# Azure AD Credentials
TENANT_ID = "your_tenant_id"
CLIENT_ID = "your_client_id"
CLIENT_SECRET = "your_client_secret"
SCOPE = "https://graph.microsoft.com/.default"
TOKEN_URL = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"

# API Endpoint
API_URL = "https://api.example.com/v1/completions"

# Token file path
TOKEN_FILE_PATH = "token_info.json"

# Set up logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Encode image to base64
def encode_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")

# Load token from file
def load_token():
    if os.path.exists(TOKEN_FILE_PATH):
        with open(TOKEN_FILE_PATH, "r") as file:
            return json.load(file)
    return None

# Save token to file
def save_token(token_data):
    with open(TOKEN_FILE_PATH, "w") as file:
        json.dump(token_data, file)

# Get OAuth Token
def get_oauth_token():
    token_info = load_token()
    current_time = time.time()
    
    # Reuse token if valid
    if token_info and current_time < token_info["expires_at"]:
        logger.info("Reusing existing token.")
        return token_info["access_token"]
    
    logger.info("Generating a new token.")
    payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "scope": SCOPE,
        "grant_type": "client_credentials",
    }
    
    response = requests.post(TOKEN_URL, data=payload)
    response.raise_for_status()
    token_data = response.json()
    
    # Save new token
    token_info = {
        "access_token": token_data["access_token"],
        "expires_at": current_time + 3600  # 1 hour expiration
    }
    save_token(token_info)
    return token_info["access_token"]

# API call with Image and Prompt
def call_api(token, image_base64, system_content, user_content):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    
    data = {
        "domainName": "GenerativeAI",
        "modelName": "gpt-4o",
        "modelPayload": {
            "messages": [
                {"role": "system", "content": system_content},
                {"role": "user", "content": [{"image": image_base64}, {"type": "text", "text": user_content}]}
            ],
            "temperature": 0.5,
            "top_p": 0.95,
            "max_tokens": 3000
        }
    }
    
    response = requests.post(API_URL, headers=headers, json=data)
    response.raise_for_status()
    return response.json()

# Main execution for multiple images
def main():
    try:
        # Image paths and respective system/user content
        image_data = [
            {
                "path": "image1.jpg",
                "system_content": "You are an AI assistant that describes the objects in an image.",
                "user_content": "What objects can you identify in this image?"
            },
            {
                "path": "image2.jpg",
                "system_content": "You are an AI assistant providing context based on images and text.",
                "user_content": "What context can you gather from the image and text?"
            }
        ]

        # Get OAuth token
        token = get_oauth_token()

        # Process each image
        for image_info in image_data:
            image_base64 = encode_image(image_info["path"])
            api_response = call_api(token, image_base64, image_info["system_content"], image_info["user_content"])
            logger.info(f"Response for {image_info['path']}: {json.dumps(api_response, indent=4)}")
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Error: {e}")

if __name__ == "__main__":
    main()
