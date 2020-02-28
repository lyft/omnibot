from os import getenv
import importlib

logging = importlib.import_module(getenv('LOG_MODULE', 'logging'))
