import logging
import os
import sys

LOG_LEVEL_ENVIRONMENT_VARIABLE = "LOG_LEVEL"

log_level_config = os.environ.get(LOG_LEVEL_ENVIRONMENT_VARIABLE, None)
log_level = logging.INFO
if log_level_config is not None:
    log_level = logging.getLevelName(log_level_config)
    if not isinstance(log_level, int):
        log_level = logging.INFO


logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] [%(name)s] %(message)s"
)


def get_logger(name: str):
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    return logger

