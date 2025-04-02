from bitwarden_secrets import BitwardenSecrets
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def main():
    try:
        # Initialize secrets manager
        secrets = BitwardenSecrets()

        # Retrieve secrets
        username = secrets.get_username()
        password = secrets.get_password()

        # Example usage in application
        print("\nRetrieved Secrets:")
        print(f"Username: {username}")
        print(f"Password: {'*' * len(password) if password else '<not found>'}")

    except Exception as e:
        logging.error(f"Application failed: {str(e)}")
        raise


if __name__ == "__main__":
    main()