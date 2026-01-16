import os
import logging
from logging.handlers import TimedRotatingFileHandler


def setup_logger(log_dir: str = "logs", log_filename: str = "app.log"):
    os.makedirs(log_dir, exist_ok=True)

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    if logger.hasHandlers():
        logger.handlers.clear()

    log_format = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    formatter = logging.Formatter(log_format)

    log_filepath = os.path.join(log_dir, log_filename)

    file_handler = TimedRotatingFileHandler(
        filename=log_filepath,
        when="M",
        interval=5,
        backupCount=20,
        encoding="utf-8"
    )

    file_handler.suffix = "%Y-%m-%d_%H-%M-%S"
    file_handler.setFormatter(formatter)

    if os.path.exists(log_filepath) and os.path.getsize(log_filepath) > 0:
        file_handler.doRollover()

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    logging.getLogger("uvicorn").handlers = logger.handlers
    logging.getLogger("uvicorn.access").handlers = logger.handlers

    return logger