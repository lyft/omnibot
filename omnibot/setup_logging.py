import os.path
import logging
import logging.config

import yaml

from omnibot import settings

logger = logging.getLogger(__name__)


try:
    with open(settings.LOG_CONFIG_FILE, "r") as fd:
        logger.info('Configuring logger from file')
        logconfig = yaml.safe_load(os.path.expandvars(fd.read()))
        logging.config.dictConfig(logconfig)
        logger = logging.getLogger(__name__)
except FileNotFoundError:
    logger.warning(
        f'{settings.LOG_CONFIG_FILE} not found; skipping logging configuration'
    )
except Exception:
    logger.exception(
        f'Failed to load {settings.LOG_CONFIG_FILE}; skipping logging configuration'
    )
