import logging
import logging.handlers
import os
import gzip
import shutil
import time
from datetime import datetime
from functools import wraps

LOG_DIR = "logs"
MAX_BYTES = 10 * 1024 * 1024  # 10MB
BACKUP_COUNT = 1  # One rotated file per run, compressed to .gz

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
    """Rotates logs by size and compresses rotated files, logging to job logger."""
    def __init__(self, filename, maxBytes=0, backupCount=0, job_logger=None):
        filename = os.path.abspath(filename)
        try:
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            log_dir = os.path.dirname(filename)
            if not os.access(log_dir, os.W_OK):
                raise PermissionError(f"No write permission for {log_dir}")
        except Exception as e:
            if job_logger:
                job_logger.error(f"Failed to create directory {os.path.dirname(filename)}: {e}")
            raise
        super().__init__(filename, maxBytes=maxBytes, backupCount=backupCount)
        self.job_logger = job_logger  # Use job logger for compression events

    def doRollover(self):
        """Rotate log file and compress the rotated file if job succeeds."""
        try:
            # Close current stream and rotate manually
            if self.stream:
                self.stream.close()
                self.stream = None
            if os.path.exists(self.baseFilename):
                rotated_log = f"{self.baseFilename}.1"
                if os.path.exists(rotated_log):
                    os.remove(rotated_log)  # Remove old .log.1 if it exists
                os.rename(self.baseFilename, rotated_log)

            # Check if the job was successful and only compress if successful
            if os.path.exists(rotated_log):
                compressed_log = f"{rotated_log}.gz"
                try:
                    with open(rotated_log, "rb") as f_in:
                        with gzip.open(compressed_log, "wb") as f_out:
                            shutil.copyfileobj(f_in, f_out)
                    os.remove(rotated_log)  # Delete .log.1 after compression
                except (IOError, OSError) as e:
                    if self.job_logger:
                        self.job_logger.error(f"Failed to compress {rotated_log}: {e}")
        except Exception as e:
            if self.job_logger:
                self.job_logger.error(f"Error during rotation/compression: {e}")
            raise

def get_job_logger(job_name):
    """Creates a logger for a job run with a unique timestamped log file."""
    job_name = "".join(c for c in job_name if c.isalnum() or c in ("-", "_")).strip() or "default"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{job_name}_{timestamp}.log"
    log_path = os.path.join(LOG_DIR, job_name, filename)

    logger = logging.getLogger(f"job_{job_name}_{timestamp}")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()  # Clear existing handlers to prevent duplicates

    handler = GzipRotatingFileHandler(
        filename=log_path,
        maxBytes=MAX_BYTES,
        backupCount=BACKUP_COUNT,
        job_logger=logger  # Pass job logger to handler
    )
    handler.setFormatter(logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    ))
    logger.addHandler(handler)
    logger.propagate = False

    return logger
