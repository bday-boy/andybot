from typing import Iterable

LEFT = '╠'
RIGHT = '╣'
CENTER = '╬'
BOTTOM = '╩'
TOP = '╦'
VERTICAL = '║'
HORIZONTAL = '═'
CORNER_TL = '╔'
CORNER_TR = '╗'
CORNER_BL = '╚'
CORNER_BR = '╝'
MAX_LEN = 61
MAX_WAY_WIDTH = 3
MAX_NAME_WIDTH = 13
MAX_TYPE_WIDTH = 13
MAX_CATEGORY_WIDTH = 13
MAX_POWER_WIDTH = 13
MAX_ACCURACY_WIDTH = 13
MAX_PP_WIDTH = 13
MAX_EFFECT_WIDTH = 13
CATEGORIES = {
    'status': '---',
    'physical': 'P',
    'special': 'S'
}


"""Example:
╔═════╦═══════════════╦═════════╦═════╦═════╦═════╦════╦═════╗
║ way ║ name          ║ type    ║ Cat ║ Pow ║ Acc ║ PP ║  %  ║
╠═════╬═══════════════╬═════════╬═════╬═════╬═════╬════╬═════╣
╚═════╩═══════════════╩═════════╩═════╩═════╩═════╩════╩═════╝
"""


def moves_table(moves: dict, method: str) -> Iterable[int]:
    moves_rows = []
    for move in moves:
        name = move['name']
        type_ = move['type']
        move_tuple = (
            method,
            move['name'][:13],
            move['type'][:7],
            CATEGORIES[move['damage_class']],
            move['power'],
            move['accuracy'],
            move['pp'],
            move['effect_chance'] or '--',
        )
        moves_rows.append(f"║ {' ║ '.join(move_tuple)} ║")
