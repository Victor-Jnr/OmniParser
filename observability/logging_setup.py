import os
import logging
from logging.handlers import RotatingFileHandler


def setup_logging(log_dir: str, app_log_filename: str = "app.log", level: int = logging.INFO) -> logging.Logger:
    """
    Configure root logging to log to both console and a rotating file handler.

    - Console: human-readable
    - File: rotating file at log_dir/app_log_filename (10 MB x 10 backups)
    """
    os.makedirs(log_dir, exist_ok=True)

    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Avoid duplicate handlers if this is called multiple times
    if root_logger.handlers:
        for handler in list(root_logger.handlers):
            root_logger.removeHandler(handler)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Rotating file handler
    app_log_path = os.path.join(log_dir, app_log_filename)
    file_handler = RotatingFileHandler(app_log_path, maxBytes=10 * 1024 * 1024, backupCount=10, encoding='utf-8')
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    # Reduce verbosity of noisy loggers if needed
    logging.getLogger('werkzeug').setLevel(logging.INFO)

    return root_logger


