import requests

url = "https://www.example.com"
response = requests.get(url, verify=True)

print("Response Status Code:", response.status_code)
print("Response Content:", response.text[:200])  # Print first 200 characters
