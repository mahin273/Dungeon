import random
import logging

def random_position(width, height, exclude=None):
    if exclude is None:
        exclude = set()
    while True:
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        if (x, y) not in exclude:
            return (x, y)

def setup_logger(name='dungeon_duel'):
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger
