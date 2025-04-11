from logging_config import get_job_logger, log_execution_time

# Create logger for Job1
logger = get_job_logger("Job1")

@log_execution_time(logger)
def arithmetic_operations():
    """Performs basic arithmetic operations and logs the results."""
    logger.info("Starting arithmetic calculations...")
    a, b = 10, 5
    sum_result = a + b
    diff_result = a - b
    logger.info(f"Addition: {a} + {b} = {sum_result}")
    logger.info(f"Subtraction: {a} - {b} = {diff_result}")
    logger.info("Finished arithmetic calculations.")

if __name__ == "__main__":
    arithmetic_operations()