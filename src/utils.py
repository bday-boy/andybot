import os.path as osp


def get_file_content(file_path: str, throw_error: bool = True) -> str:
    if not osp.isfile(file_path):
        if throw_error:
            raise FileNotFoundError()
        else:
            return ''
    file_content = ''
    with open(file_path, 'r') as file:
        file_content = file.read()
    return file_content


def get_token(token_path: str = 'token') -> str:
    return get_file_content(token_path).strip()


if __name__ == '__main__':
    get_token()
