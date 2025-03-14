import requests

# Replace these with your OAuth provider details
token_url = 'https://example.com/oauth/token'  # Token URL
client_id = 'your_client_id'
client_secret = 'your_client_secret'

# Prepare the payload
data = {
    'grant_type': 'client_credentials',
    'client_id': client_id,
    'client_secret': client_secret
}

# Request OAuth token
response = requests.post(token_url, data=data)

# Check if the request was successful
if response.status_code == 200:
    token = response.json().get('access_token')
    print(f'Access Token: {token}')
else:
    print(f'Failed to get token: {response.status_code}')
    print(response.text)
