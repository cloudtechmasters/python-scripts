import requests
from logging_config import get_job_logger, log_execution_time

# Create logger for Job2
logger = get_job_logger("Job2")

@log_execution_time(logger)
def call_api(valid=True):
    """Simulates an API call, logging success or failure."""
    logger.info("Calling API...")

    if valid:
        url = "https://jsonplaceholder.typicode.com/todos/1"  # Valid API URL
    else:
        url = "https://jsonplaceholder.typicode.com/invalid_endpoint"  # Invalid URL

    try:
        response = requests.get(url)
        response.raise_for_status()
        logger.info(f"API Response: {response.json()}")
    except requests.RequestException as e:
        logger.error(f"Failed API call: {e}")

if __name__ == "__main__":
    # Test valid API call (should succeed)
    call_api(valid=True)
    # Test invalid API call (should fail)
    call_api(valid=False)