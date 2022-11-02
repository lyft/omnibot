import pathlib
from os import path

ROOT_DIR = pathlib.Path(__file__).parent.parent.parent.absolute()
DATA_DIR = path.join(ROOT_DIR, "data")
MOCK_DIR = path.join(DATA_DIR, "mock")
TEST_CONFIG = path.join(DATA_DIR, "test_omnibot_config.yaml")


def get_mock_data(filepath: str):
    return open(path.join(MOCK_DIR, filepath))


def test_handler(container):
    return "{\"foo\": \"bar\"}"
