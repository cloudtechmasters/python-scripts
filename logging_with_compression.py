# import logging
# import logging.handlers
# import os
# import gzip
# import shutil
# import time
# from datetime import datetime
# from functools import wraps
#
# LOG_DIR = "logs"
# MAX_BYTES = 10 * 1024 * 1024  # 10MB
# BACKUP_COUNT = 0  # No backups since we'll compress immediately
#
#
# def ensure_log_directory(log_path):
#     """Ensure log directory exists and is writable"""
#     log_dir = os.path.dirname(log_path)
#     try:
#         os.makedirs(log_dir, exist_ok=True)
#         # Verify directory is writable
#         test_file = os.path.join(log_dir, '.test')
#         with open(test_file, 'w') as f:
#             f.write('test')
#         os.remove(test_file)
#         return True
#     except Exception as e:
#         print(f"Failed to create/access log directory {log_dir}: {e}")
#         return False
#
#
# class SuccessBasedGzipHandler(logging.Handler):
#     """Handler that replaces .log with .gz when job succeeds"""
#
#     def __init__(self, filename):
#         super().__init__()
#         self.filename = filename
#         self.job_successful = False
#         self.log_file = None
#
#     def set_job_success(self, success):
#         self.job_successful = success
#
#     def emit(self, record):
#         """Write to the log file directly"""
#         if self.log_file is None:
#             self.log_file = open(self.filename, 'a')
#         self.log_file.write(self.format(record) + '\n')
#
#     def close(self):
#         """Replace .log with .gz if job succeeded"""
#         if self.log_file:
#             self.log_file.close()
#             self.log_file = None
#
#         if self.job_successful and os.path.exists(self.filename):
#             try:
#                 # Compress the log file
#                 gz_filename = f"{self.filename}.gz"
#                 with open(self.filename, 'rb') as f_in:
#                     with gzip.open(gz_filename, 'wb') as f_out:
#                         shutil.copyfileobj(f_in, f_out)
#
#                 # Remove the original log file
#                 os.remove(self.filename)
#             except Exception as e:
#                 print(f"Failed to compress log: {e}")
#         super().close()
#
#
# def get_job_logger(job_name):
#     """Create and configure logger for a job"""
#     # Sanitize job name
#     job_name = "".join(c for c in job_name if c.isalnum() or c in ("-", "_")).strip() or "default"
#     timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#     filename = f"{job_name}_{timestamp}.log"
#     log_path = os.path.join(LOG_DIR, job_name, filename)
#
#     if not ensure_log_directory(log_path):
#         raise RuntimeError(f"Could not create log directory for {log_path}")
#
#     logger = logging.getLogger(f"job_{job_name}_{timestamp}")
#     logger.setLevel(logging.INFO)
#
#     # Clear existing handlers to avoid duplicates
#     logger.handlers = []
#
#     # Create success-based handler (only this one)
#     success_handler = SuccessBasedGzipHandler(log_path)
#     success_handler.setFormatter(logging.Formatter(
#         "%(asctime)s | %(levelname)s | %(message)s",
#         datefmt="%Y-%m-%d %H:%M:%S"
#     ))
#     logger.addHandler(success_handler)
#
#     logger.propagate = False
#     return logger, success_handler
#
#
# def log_execution_time(logger, success_handler):
#     """Decorator to track execution time and success"""
#
#     def decorator(func):
#         @wraps(func)
#         def wrapper(*args, **kwargs):
#             start_time = time.time()
#             logger.info(f"Starting {func.__name__}...")
#
#             try:
#                 result = func(*args, **kwargs)
#                 elapsed_time = time.time() - start_time
#                 logger.info(f"Finished {func.__name__} in {elapsed_time:.2f} seconds")
#                 success_handler.set_job_success(True)
#                 return result
#             except Exception as e:
#                 logger.error(f"Error in {func.__name__}: {str(e)}")
#                 success_handler.set_job_success(False)
#                 raise
#
#         return wrapper
#
#     return decorator
#
#
# def shutdown_logging():
#     """Properly shutdown logging system"""
#     logging.shutdown()
import logging
import os
import gzip
import shutil
import time
from datetime import datetime
from functools import wraps

LOG_DIR = "logs"


def ensure_log_directory(log_path):
    """Ensure log directory exists and is writable"""
    log_dir = os.path.dirname(log_path)
    try:
        os.makedirs(log_dir, exist_ok=True)
        # Verify directory is writable
        test_file = os.path.join(log_dir, '.test')
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        return True
    except Exception as e:
        print(f"Failed to create/access log directory {log_dir}: {e}")
        return False


class SuccessBasedGzipHandler(logging.Handler):
    """Handler that compresses and removes .log on success, keeps .log on failure"""

    def __init__(self, filename):
        super().__init__()
        self.filename = filename
        self.job_successful = False
        self.log_file = None

    def set_job_success(self, success):
        self.job_successful = success

    def emit(self, record):
        """Write to the log file"""
        if self.log_file is None:
            self.log_file = open(self.filename, 'a')
        self.log_file.write(self.format(record) + '\n')

    def close(self):
        """Compress to .gz on success (removing .log), keep .log on failure"""
        if self.log_file:
            self.log_file.close()
            self.log_file = None

        if os.path.exists(self.filename):
            if self.job_successful:
                try:
                    # Compress the log file
                    gz_filename = f"{self.filename}.gz"
                    with open(self.filename, 'rb') as f_in:
                        with gzip.open(gz_filename, 'wb') as f_out:
                            shutil.copyfileobj(f_in, f_out)

                    # Remove the original log file
                    os.remove(self.filename)
                except Exception as e:
                    print(f"Failed to compress log: {e}")
            # On failure, .log file remains unchanged
        super().close()


def get_job_logger(job_name):
    """Create and configure logger for a job"""
    # Sanitize job name
    job_name = "".join(c for c in job_name if c.isalnum() or c in ("-", "_")).strip() or "default"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{job_name}_{timestamp}.log"
    log_path = os.path.join(LOG_DIR, job_name, filename)

    if not ensure_log_directory(log_path):
        raise RuntimeError(f"Could not create log directory for {log_path}")

    logger = logging.getLogger(f"job_{job_name}_{timestamp}")
    logger.setLevel(logging.INFO)

    # Clear existing handlers
    logger.handlers = []

    # Create our custom handler
    success_handler = SuccessBasedGzipHandler(log_path)
    success_handler.setFormatter(logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    ))
    logger.addHandler(success_handler)

    logger.propagate = False
    return logger, success_handler


def log_execution_time(logger, success_handler):
    """Decorator to track execution time and success"""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            logger.info(f"Starting {func.__name__}...")

            try:
                result = func(*args, **kwargs)
                elapsed_time = time.time() - start_time
                logger.info(f"Finished {func.__name__} in {elapsed_time:.2f} seconds")
                success_handler.set_job_success(True)
                return result
            except Exception as e:
                logger.error(f"Error in {func.__name__}: {str(e)}")
                success_handler.set_job_success(False)
                raise

        return wrapper

    return decorator


def shutdown_logging():
    """Properly shutdown logging system"""
    logging.shutdown()
