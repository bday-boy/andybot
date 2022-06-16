from math import floor, ceil
from typing import List


def poke_round(num: float) -> float:
    """Apparently GameFreak has this implemented in the damage formula for
    some reason. It's similar to how traditional rounding works, but the
    number is rounded DOWN instead of up when the decimal is 0.5.
    """
    decimal = num % 1
    return floor(num) if decimal <= 0.5 else ceil(num)


def base_dmg(level: int, power: int, atk: int, def_: int) -> int:
    """Calculates the base damage part of the damage formula. This is the
    part before all the external modifiers are applied. Technically, some
    games apply modifiers before the +2 is added, but the difference is
    negligible enough that it is outside the scope of this bot.
    """
    level_mod = floor((2 * level / 5) + 2)
    numerator = floor(level_mod * power * atk / def_)
    return floor(numerator / 50) + 2


def calc_dmg(level: int, power: int, atk: int, def_: int, other: int = 1,
             random_num: float = 1.0) -> int:
    """Calculates the damage done from one Pokemon to another. random_num is
    a float in the range [0.85, 1] that defaults to 1 for maximum damage.

    Damage formula details: https://bulbapedia.bulbagarden.net/wiki/Damage
    """
    return floor(base_dmg(level, power, atk, def_) * other * random_num)


def inner_stat_formula(base: int, IV: int, EV: int, level: int) -> int:
    """Calculates the (2 x Base + IV + floor(0.25 x EV)) x Level part of the
    Pokemon stat formula, which both HP and other stats share.
    """
    return floor(
        (
            2 * base
            + IV
            + (EV // 4)
        ) * level / 100
    )


def hp_stat(base: int, IV: int, EV: int, level: int) -> int:
    """Calculates a Pokemon's in-game HP stat.
    
    Formula seen here: https://pokemon.fandom.com/wiki/Statistics
    """
    return inner_stat_formula(base, IV, EV, level) + level + 10


def other_stat(base: int, IV: int, EV: int, level: int,
               nature: float = 1.0) -> int:
    """Calculates a Pokemon's in-game non-HP stat.
    
    Formula seen here: https://pokemon.fandom.com/wiki/Statistics
    """
    return floor((inner_stat_formula(base, IV, EV, level) + 5) * nature)


def lowest_hp_stat(base: int, level: int) -> int:
    """Calculates the lowest HP stat value at the given level."""
    return hp_stat(base, 0, 0, level)


def lowest_other_stat(base: int, level: int, nature: float = 1.0) -> int:
    """Calculates the lowest non-HP stat value at the given level."""
    return other_stat(base, 0, 0, level, nature)


def lowest_hp_stat(base: int, level: int) -> int:
    """Calculates the highest HP stat value at the given level."""
    return hp_stat(base, 31, 252, level)


def lowest_other_stat(base: int, level: int, nature: float = 1.0) -> int:
    """Calculates the highest non-HP stat value at the given level."""
    return other_stat(base, 31, 252, level, nature)


def all_stats(bases: List[int]) -> List[int]:
    stats = [hp_stat(bases[0])]
    for base in bases[1:]:
        stats.append(other_stat(base))
    return all_stats
