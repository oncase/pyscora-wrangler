import logging
import json
import numpy as np
from typing import Any
from decimal import Decimal
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

class ItemEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> int | Decimal | Any | float:
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return Decimal(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, float):
            return Decimal(obj)
        else:
            return super(ItemEncoder, self).default(obj)


def get_data_decoded(data: Any) -> Any:
    new_data = ItemEncoder().encode(data)
    data_parsed = json.loads(new_data)

    return data_parsed


def get_data_encoded(data: Any) -> Any:
    data_dumped = json.dumps(data, cls=ItemEncoder)
    data_parsed = json.loads(data_dumped, parse_float=Decimal)

    return data_parsed
