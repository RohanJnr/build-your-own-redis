from typing import Callable

from loguru import logger


def log_command(func: Callable) -> Callable:
    """
    A decorator to log the function call with its arguments into the AOF logger.

    Args:
        func (Callable): function

    Returns:
        Callable: wrapper function
    """
    aof_logger = logger.bind(loc="aof")

    def wrapper(self, *args, **kwargs):
        aof_logger.info(f"{func.__name__}|{args}")
        val = func(self, *args, **kwargs)
        return val

    return wrapper
