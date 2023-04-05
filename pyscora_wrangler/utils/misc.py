import logging
from .modules import CustomLoggerFormatter


def setup_logger(
    name: str, level: int = logging.INFO, Formatter: logging.Formatter = CustomLoggerFormatter
) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)

    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch.setFormatter(Formatter())

    logger.addHandler(ch)

    return logger
