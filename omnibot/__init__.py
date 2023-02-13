import importlib
from os import getenv

logging = importlib.import_module(getenv('LOG_MODULE', 'logging'))
