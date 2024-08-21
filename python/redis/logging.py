import sys
from loguru import logger


logger.remove()

logger.add(
    sys.stdout,
    colorize=True,
    format="<green>{time}</green> | <magenta>{level}</magenta> | <magenta>{process}.{module}."
    "{function}</magenta> | <level>{message}</level>",
    level="INFO",
    filter=lambda record: record["extra"]["loc"] == "stdout"
    if "loc" in record["extra"]
    else False,
)

stdout_logger = logger.bind(loc="stdout")


