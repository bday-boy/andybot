import json
import os.path as osp
from typing import Any


def get_file_content(file_path: str, throw_error: bool = True,
                     default: Any = '') -> str:
    if not osp.isfile(file_path):
        if throw_error:
            raise FileNotFoundError()
        else:
            return default
    file_content = default
    with open(file_path, 'r') as file:
        file_content = file.read()
    return file_content


def load_config(config_path: str = 'config.json') -> dict:
    config_str = get_file_content(config_path, default='{}')
    return json.loads(config_str)


if __name__ == '__main__':
    cfg = load_config()
    a = 0
