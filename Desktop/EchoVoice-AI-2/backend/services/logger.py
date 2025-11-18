import logging
from logging import StreamHandler, Formatter

def get_logger(name=__name__):
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = StreamHandler()
        handler.setFormatter(Formatter('%(asctime)s %(levelname)s %(message)s'))
        logger.addHandler(handler)
        logger.setLevel(20)
    return logger
