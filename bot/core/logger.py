import logging
import sys

def get_logger(name: str, level=logging.DEBUG):
    logger = logging.getLogger(name)
    if not logger.hasHandlers():
        logger.setLevel(level)
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.propagate = False
    return logger