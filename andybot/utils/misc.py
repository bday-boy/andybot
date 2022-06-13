import re
from typing import Tuple, Union

discord_markdown_chars = re.compile(r'([*_~`\|])')


def hex_to_rgb(hex_string: Union[int, str]) -> Tuple[int, int, int]:
    """Converts a hex string or integer to an RGB tuple. RGBA will not work
    because this function isn't that smart lmao
    """
    try:
        rgb = int(hex_string.strip('#'), 16)
    except AttributeError:
        rgb = hex_string

    return (rgb >> 16) & 0xFF, (rgb >> 8) & 0xFF, rgb & 0xFF


def escape_special_chars(text: str) -> str:
    """Places an extra backslash in front of backslashes as well as any
    characters that could be interpreted as Markdown in Discord.
    """
    return discord_markdown_chars.sub(r'\\\1', text)
