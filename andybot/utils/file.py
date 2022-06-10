import json
import os.path as osp
from typing import Any


def get_file_content(file_path: str, throw_error: bool = True,
                     default: Any = '') -> str:
    """Loads a file's content as a string. Uses rb mode so this function is
    unicode safe.

    Raises FileNotFoundError if throw_error is True and the given file_path is
    not a file.
    """
    if not osp.isfile(file_path):
        if throw_error:
            raise FileNotFoundError()
        else:
            return default
    file_content = default
    with open(file_path, 'rb') as file:
        file_content = file.read()
    return file_content


def load_config(config_path: str = 'config.json') -> dict:
    """Loads the config.json found in the top level of the project. Returns
    an empty dictionary by default if no error is thrown.
    """
    config_str = get_file_content(config_path, default='{}')
    return json.loads(config_str)


cfg = load_config()
