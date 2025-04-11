# import logging
# import logging.handlers
# import os
# import gzip
# import shutil
# import time
# from datetime import datetime
#
# # Configuration
# LOG_DIR = "logs"
# MAX_BYTES = 10 * 1024 * 1024  # 10MB
# BACKUP_COUNT = 1  # One rotated file per run, compressed to .gz
# RETENTION_DAYS = 30  # Delete files older than 30 days
#
#
# class GzipRotatingFileHandler(logging.handlers.RotatingFileHandler):
#     """Rotates logs by size, compresses rotated files, and deletes old files."""
#
#     def __init__(self, filename, maxBytes=0, backupCount=0):
#         # Ensure absolute path and directory exists
#         filename = os.path.abspath(filename)
#         os.makedirs(os.path.dirname(filename), exist_ok=True)
#         # Check write permissions
#         log_dir = os.path.dirname(filename)
#         if not os.access(log_dir, os.W_OK):
#             raise PermissionError(f"No write permission for {log_dir}")
#
#         super().__init__(filename, maxBytes=maxBytes, backupCount=backupCount)
#         self.compression_logger = logging.getLogger('Compression')
#         self._perform_maintenance()  # Run cleanup at startup
#
#     def doRollover(self):
#         """Rotate log file and compress the rotated file."""
#         super().doRollover()
#         # Compress the rotated file, if it exists
#         # Example: Job2_20250411_123456.log becomes Job2_20250411_123456.log.1,
#         # then compressed to Job2_20250411_123456.log.1.gz
#         old_log = f"{self.baseFilename}.1"
#         if os.path.exists(old_log):
#             compressed_log = f"{old_log}.gz"
#             try:
#                 with open(old_log, 'rb') as f_in:
#                     with gzip.open(compressed_log, 'wb') as f_out:
#                         shutil.copyfileobj(f_in, f_out)
#                 os.remove(old_log)
#                 self.compression_logger.info(f"Compressed {old_log} to {compressed_log}")
#             except (IOError, OSError) as e:
#                 self.compression_logger.error(f"Failed to compress {old_log}: {e}")
#         self._perform_maintenance()  # Clean up old files after rotation
#
#     def _perform_maintenance(self):
#         """Delete files older than RETENTION_DAYS (30 days)."""
#         # === 30-DAY DELETION LOGIC ===
#         now = time.time()
#         for root, _, files in os.walk(LOG_DIR):
#             for f in files:
#                 file_path = os.path.join(root, f)
#                 try:
#                     if os.path.getmtime(file_path) < now - (RETENTION_DAYS * 86400):
#                         os.remove(file_path)
#                         self.compression_logger.info(f"Deleted old file: {file_path}")
#                 except (IOError, OSError) as e:
#                     self.compression_logger.error(f"Failed to delete {file_path}: {e}")
#         # === END 30-DAY DELETION LOGIC ===
#
#
# def get_job_logger(job_name):
#     """Creates a logger for a job run with a unique timestamped log file."""
#     # Sanitize job_name to prevent invalid filenames
#     job_name = "".join(c for c in job_name if c.isalnum() or c in ('-', '_')).strip() or "default"
#     timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#     filename = f"{job_name}_{timestamp}.log"
#     log_path = os.path.join(LOG_DIR, job_name, filename)
#
#     # Create logger
#     logger = logging.getLogger(f"job_{job_name}_{timestamp}")
#     logger.setLevel(logging.INFO)  # Capture INFO, WARNING, ERROR, CRITICAL
#
#     # Set up rotating handler
#     handler = GzipRotatingFileHandler(
#         filename=log_path,
#         maxBytes=MAX_BYTES,
#         backupCount=BACKUP_COUNT
#     )
#     handler.setFormatter(logging.Formatter(
#         "%(asctime)s | %(levelname)s | %(message)s",
#         datefmt="%Y-%m-%d %H:%M:%S"
#     ))
#     logger.addHandler(handler)
#     logger.propagate = False
#
#     return logger
#
#
# # Configure compression logger (shared across all job loggers)
# compression_logger = logging.getLogger('Compression')
# compression_logger.setLevel(logging.INFO)  # Capture INFO, WARNING, ERROR, CRITICAL
# console_handler = logging.StreamHandler()
# console_handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
# compression_logger.addHandler(console_handler)

import logging
import logging.handlers
import os
import gzip
import shutil
import time
from datetime import datetime
from functools import wraps

# Configuration
LOG_DIR = "logs"
MAX_BYTES = 10 * 1024 * 1024  # 10MB
BACKUP_COUNT = 1  # One rotated file per run, compressed to .gz
RETENTION_DAYS = 30  # Delete files older than 30 days


def log_execution_time(logger):
    """Decorator to log the start, end, and elapsed time of a method."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            logger.info(f"Starting {func.__name__}...")
            try:
                result = func(*args, **kwargs)
                end_time = time.perf_counter()
                elapsed_time = end_time - start_time
                logger.info(f"Finished {func.__name__}, took {elapsed_time:.3f} seconds")
                return result
            except Exception as e:
                logger.error(f"Error in {func.__name__}: {e}")
                raise

        return wrapper

    return decorator


class GzipRotatingFileHandler(logging.handlers.RotatingFileHandler):
    """Rotates logs by size, compresses rotated files, and deletes old files."""

    def __init__(self, filename, maxBytes=0, backupCount=0):
        # Ensure absolute path and directory exists
        filename = os.path.abspath(filename)
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        # Check write permissions
        log_dir = os.path.dirname(filename)
        if not os.access(log_dir, os.W_OK):
            raise PermissionError(f"No write permission for {log_dir}")

        super().__init__(filename, maxBytes=maxBytes, backupCount=backupCount)
        self.compression_logger = logging.getLogger('Compression')
        self._perform_maintenance()  # Run cleanup at startup

    def doRollover(self):
        """Rotate log file and compress the rotated file."""
        super().doRollover()
        # Compress the rotated file, if it exists
        # Example: Job2_20250411_123456.log becomes Job2_20250411_123456.log.1,
        # then compressed to Job2_20250411_123456.log.1.gz
        old_log = f"{self.baseFilename}.1"
        if os.path.exists(old_log):
            compressed_log = f"{old_log}.gz"
            try:
                with open(old_log, 'rb') as f_in:
                    with gzip.open(compressed_log, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                os.remove(old_log)
                self.compression_logger.info(f"Compressed {old_log} to {compressed_log}")
            except (IOError, OSError) as e:
                self.compression_logger.error(f"Failed to compress {old_log}: {e}")
        self._perform_maintenance()  # Clean up old files after rotation

    def _perform_maintenance(self):
        """Delete files older than RETENTION_DAYS (30 days)."""
        now = time.time()
        for root, _, files in os.walk(LOG_DIR):
            for f in files:
                file_path = os.path.join(root, f)
                try:
                    if os.path.getmtime(file_path) < now - (RETENTION_DAYS * 86400):
                        os.remove(file_path)
                        self.compression_logger.info(f"Deleted old file: {file_path}")
                except (IOError, OSError) as e:
                    self.compression_logger.error(f"Failed to delete {file_path}: {e}")


def get_job_logger(job_name):
    """Creates a logger for a job run with a unique timestamped log file."""
    # Sanitize job_name to prevent invalid filenames
    job_name = "".join(c for c in job_name if c.isalnum() or c in ('-', '_')).strip() or "default"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{job_name}_{timestamp}.log"
    log_path = os.path.join(LOG_DIR, job_name, filename)

    # Create logger
    logger = logging.getLogger(f"job_{job_name}_{timestamp}")
    logger.setLevel(logging.INFO)  # Capture INFO, WARNING, ERROR, CRITICAL

    # Set up rotating handler
    handler = GzipRotatingFileHandler(
        filename=log_path,
        maxBytes=MAX_BYTES,
        backupCount=BACKUP_COUNT
    )
    handler.setFormatter(logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    ))
    logger.addHandler(handler)
    logger.propagate = False

    return logger


# Configure compression logger (shared across all job loggers)
compression_logger = logging.getLogger('Compression')
compression_logger.setLevel(logging.INFO)  # Capture INFO, WARNING, ERROR, CRITICAL
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
compression_logger.addHandler(console_handler)