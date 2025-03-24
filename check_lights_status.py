import requests
import base64
import json
import time
import logging
import os

# Azure AD Credentials
TENANT_ID = os.getenv("TENANT_ID", "your_tenant_id")
CLIENT_ID = os.getenv("CLIENT_ID", "your_client_id")
CLIENT_SECRET = os.getenv("CLIENT_SECRET", "your_client_secret")
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
    """Encode image to base64 format"""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")

# Load token from file
def load_token():
    """Load OAuth token from file if exists"""
    if os.path.exists(TOKEN_FILE_PATH):
        with open(TOKEN_FILE_PATH, "r") as file:
            return json.load(file)
    return None

# Save token to file
def save_token(token_data):
    """Save token data to file"""
    with open(TOKEN_FILE_PATH, "w") as file:
        json.dump(token_data, file)

# Get OAuth Token
def get_oauth_token():
    """Get or refresh OAuth token"""
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

# API call with multiple images in a single user role
def call_api(token, image_paths):
    """Call API to check lights status in multiple images"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    
    # Convert all images to base64
    images_base64 = [{"image": encode_image(img)} for img in image_paths]

    # Construct single system and user role with multiple images
    messages = [
        {
            "role": "system",
            "content": "You are an AI assistant trained to detect the status of lights on an AT&T Residential Gateway (RG). The lights should be identified as ON or OFF based on the visual data. If possible, identify which specific lights are ON."
        },
        {
            "role": "user",
            "content": images_base64 + [{"type": "text", "text": "Which lights are ON in these images of the AT&T Residential Gateway? Are any lights OFF?"}]
        }
    ]
    
    data = {
        "domainName": "GenerativeAI",
        "modelName": "gpt-4o",
        "modelPayload": {
            "messages": messages,
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
        # Image paths for multiple images of AT&T RG
        image_paths = ["gateway_image1.jpg", "gateway_image2.jpg", "gateway_image3.jpg"]

        # Get OAuth token
        token = get_oauth_token()

        # Call the API with images to check light status
        api_response = call_api(token, image_paths)
        logger.info(f"API Response: {json.dumps(api_response, indent=4)}")
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Error: {e}")

if __name__ == "__main__":
    main()
