from typing import Tuple, Union


def hex_to_rgb(hex_string: Union[int, str]) -> Tuple[int, int, int]:
    """Converts a hex string or integer to an RGB tuple. RGBA will not work
    because this function isn't that smart lmao
    """
    try:
        rgb = int(hex_string.strip('#'), 16)
    except AttributeError:
        rgb = hex_string

    return (rgb >> 16) & 0xFF, (rgb >> 8) & 0xFF, rgb & 0xFF
