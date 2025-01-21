import logging


def create_logger() -> logging.Logger:

    logger = logging.getLogger('shikimori-client')

    console_handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    console_handler.setFormatter(formatter)

    logger.setLevel(logging.INFO)
    logger.addHandler(console_handler)

    return logger
