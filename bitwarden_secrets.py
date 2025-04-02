import logging
import base64
from bitwarden_sdk import BitwardenClient, DeviceType, client_settings_from_dict
from dotenv import load_dotenv
import os

load_dotenv()

class BitwardenSecrets:
    def __init__(self):
        self.client = BitwardenClient(
            client_settings_from_dict({
                "deviceType": DeviceType.SDK,
                "identityUrl": "https://identity.bitwarden.com",
                "userAgent": "Python",
            })
        )
        # Authenticate without persisting state
        self.client.auth().login_access_token(
            os.getenv("BITWARDEN_ACCESS_TOKEN"),
            None  # No state file
        )
        self.secret_ids = {
            "username": base64.b64decode(os.getenv("SECRET_ID_USERNAME").encode()).decode(),
            "password": base64.b64decode(os.getenv("SECRET_ID_PASSWORD").encode()).decode()
        }

    def get_secret(self, name: str, default=None):
        try:
            if secret_id := self.secret_ids.get(name):
                response = self.client.secrets().get_by_ids([secret_id])
                if response.data.data:
                    return response.data.data[0].value
            return default
        except Exception as e:
            logging.error(f"Error getting secret '{name}': {str(e)}")
            return default

    def get_username(self):
        return self.get_secret("username")

    def get_password(self):
        return self.get_secret("password")