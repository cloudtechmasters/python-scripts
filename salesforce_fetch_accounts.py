import requests
import pandas as pd
import pyarrow.parquet as pq
import pyarrow as pa

# Configuration (replace with actual values)
SALESFORCE_SANDBOX_URL = "https://test.salesforce.com"
TOKEN_URL = f"{SALESFORCE_SANDBOX_URL}/services/oauth2/token"

CLIENT_ID = "your-salesforce-client-id"
CLIENT_SECRET = "your-salesforce-client-secret"
USERNAME = "your-salesforce-username"
PASSWORD = "your-salesforce-password"

def get_salesforce_token():
    """Authenticate and retrieve Salesforce access token and instance URL."""
    response = requests.post(
        TOKEN_URL,
        data={
            "grant_type": "password",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "username": USERNAME,
            "password": PASSWORD,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    response.raise_for_status()
    return response.json()["access_token"], response.json()["instance_url"]

def fetch_salesforce_accounts(token, instance_url):
    """Fetch Id and Name from the Account object in Salesforce."""
    response = requests.get(
        f"{instance_url}/services/data/v59.0/query",
        headers={"Authorization": f"Bearer {token}"},
        params={"q": "SELECT Id, Name FROM Account LIMIT 100"},
    )
    response.raise_for_status()
    return response.json()["records"]

def save_as_parquet(data, filename="salesforce_accounts.parquet"):
    """Save Salesforce account data as a Snappy-compressed Parquet file."""
    df = pd.DataFrame(data, columns=["Id", "Name"])
    pq.write_table(pa.Table.from_pandas(df), filename, compression="snappy")
    print(f"Data saved to {filename}")

if __name__ == "__main__":
    try:
        token, instance_url = get_salesforce_token()
        accounts = fetch_salesforce_accounts(token, instance_url)
        save_as_parquet(accounts)
    except Exception as e:
        print(f"Error: {e}")
