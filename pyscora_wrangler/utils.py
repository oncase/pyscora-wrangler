import logging
from .constants import *


class CustomLoggerFormatter(logging.Formatter):
    default_string = '(%(asctime)s - %(name)s) - %(levelname)s: %(message)s'

    FORMATS = {
        logging.DEBUG: GREY + default_string + RESET,
        logging.INFO: BLUE + default_string + RESET,
        logging.WARNING: YELLOW + default_string + RESET,
        logging.ERROR: RED + default_string + RESET,
        logging.CRITICAL: BOLD_RED + default_string + RESET,
    }

    def format(self, record: logging.LogRecord) -> str:
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)

        return formatter.format(record)


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
