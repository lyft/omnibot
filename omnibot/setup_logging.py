import logging
import logging.config
import os.path

import yaml

from omnibot import settings


try:
    with open(settings.LOG_CONFIG_FILE, "r") as fd:
        logging.info('Configuring logger from file')
        logconfig = yaml.safe_load(os.path.expandvars(fd.read()))
        logging.config.dictConfig(logconfig)
except FileNotFoundError:
    logging.warning(
        f'{settings.LOG_CONFIG_FILE} not found; skipping logging configuration'
    )
except Exception:
    logging.exception(
        f'Failed to load {settings.LOG_CONFIG_FILE}; skipping logging configuration'
    )
