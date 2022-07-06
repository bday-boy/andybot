import random
from math import floor, ceil
from typing import List, Tuple, Union

import numpy as np

MIN_IVS = 0
MAX_IVS = 31
MIN_EVS = 0
MAX_EVS = 252


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
    level_modifier = floor((2 * level / 5) + 2)
    numerator = floor(level_modifier * power * atk / def_)
    return floor(numerator / 50) + 2


def random_dmg_array(level: int, power: int, atk: int, def_: int, other: int = 1,
             random_num: float = 1.0) -> int:
    """Calculates the damage done from one Pokemon to another. random_num is
    a float in the range [0.85, 1] that defaults to 1 for maximum damage.

    Damage formula details: https://bulbapedia.bulbagarden.net/wiki/Damage
    """
    base = base_dmg(level, power, atk, def_)
    return floor(base * other * random_num)


def base_dmg_vector(level: int, power: int, atk: int, def_vec: np.ndarray
                    ) -> np.ndarray:
    """Calculates the base damage part of the damage formula as a vector."""
    level_modifier = floor((2 * level / 5) + 2)
    numerator = np.floor(level_modifier * power * atk / def_vec)
    return np.floor(numerator / 50) + 2


def calc_dmg_vector(level: int, power: int, atk: int, def_vec: np.ndarray,
                    other: int = 1, random_num: float = 1.0) -> np.ndarray:
    """Calculates the damage done from one Pokemon to another as a vector."""
    base = base_dmg_vector(level, power, atk, def_vec)
    return np.floor(base * other * random_num)


def calc_dmg_vector_random(level: int, power: int, atk: int,
                           def_vec: np.ndarray, other: int = 1
                           ) -> np.ndarray:
    """Calculates the damage done from one Pokemon to another as a vector."""
    base = base_dmg_vector(level, power, atk, def_vec)
    return np.floor(base * other * (random.randint(85, 100) / 100))


def highest_dmg(level: int, power: int, atk: int, def_: int, other: int = 1
                ) -> int:
    """Calculates the highest damage roll based on the given inputs."""
    return random_dmg_array(level, power, atk, def_, other, 1.0)


def lowest_dmg(level: int, power: int, atk: int, def_: int, other: int = 1
               ) -> int:
    """Calculates the highest damage roll based on the given inputs."""
    return random_dmg_array(level, power, atk, def_, other, 0.85)


def random_nature() -> float:
    """There are 25 natures total. Each stat has 4 natures that raise a given
    stat by 1.1x, 4 natures that lower by 1.1x, and 17 natures that don't
    affect it.
    """
    return random.choices((0.9, 1, 1.1), cum_weights=(4, 21, 25), k=1)


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


def non_hp_stat(base: int, IV: int, EV: int, level: int,
                nature: float = 1.0) -> int:
    """Calculates a Pokemon's in-game non-HP stat.

    Formula seen here: https://pokemon.fandom.com/wiki/Statistics
    """
    return floor((inner_stat_formula(base, IV, EV, level) + 5) * nature)


def hp_stat_extrema(base: int, level: int) -> Tuple[int, int]:
    return (
        hp_stat(base, MIN_IVS, MIN_EVS, level),
        hp_stat(base, MAX_IVS, MAX_EVS, level)
    )


def non_hp_stat_extrema(base: int, level: int, nature: float = 1.0
                        ) -> Tuple[int, int]:
    return (
        non_hp_stat(base, MIN_IVS, MIN_EVS, level, nature),
        non_hp_stat(base, MAX_IVS, MAX_EVS, level, nature)
    )


def hp_stat_range(base: int, level: int) -> int:
    lowest_hp, highest_hp = hp_stat_extrema(base, level)
    return list(range(lowest_hp, highest_hp + 1))


def non_hp_stat_range(base: int, level: int, nature: float = 1.0) -> int:
    lowest_non_hp, highest_non_hp = non_hp_stat_extrema(base, level, nature)
    return list(range(lowest_non_hp, highest_non_hp + 1))


def full_stat_ranges(bases: List[int], level: int, nature: float = 1.0
                     ) -> List[int]:
    stats = [hp_stat_extrema(bases[0], level)]
    for base in bases[1:]:
        stats.append(non_hp_stat_extrema(base, level, nature))
    return stats

###############################################################################
############################### Numpy versions ################################
###############################################################################


def random_nature_array(size: int) -> np.ndarray:
    """Creates an array of random natures modifiers for a single stat."""
    # Each stat has 4 natures that lower by 0.9x, 17 that are neutral, and
    # another 4 that raise by 1.1x
    p = np.array((4, 17, 4)) / 25
    natures = np.random.choice((0.9, 1.0, 1.1), size=size, p=p)
    return natures


def random_ev_array(size: int) -> np.ndarray:
    """Creates an array of random EVs."""
    evs = np.random.randint(0, (252 // 4) + 1, size=size) * 4
    return evs


def random_iv_array(size: int) -> np.ndarray:
    """Creates an array of random IVs."""
    ivs = np.random.randint(0, 31 + 1, size=size)
    return ivs


def random_inner_stat_array(base: int, level: int, size: int) -> np.ndarray:
    """Computes the inner part of the stat formula with random IVs and 0
    EVs.
    """
    random_ivs = random_iv_array(size)
    return np.floor((2 * base + random_ivs) * level / 100)


def random_hp_array(base: int, level: int, size: int) -> np.ndarray:
    """Creates an array of random values for a given stat. Assumes 0 EVs."""
    base_stats = random_inner_stat_array(base, level, size)
    return base_stats + level + 10


def random_stat_array(base: int, level: int, size: int) -> np.ndarray:
    """Creates an array of random values for a given stat. Assumes 0 EVs."""
    natures = random_nature_array(size)
    base_stats = random_inner_stat_array(base, level, size)
    return np.floor((base_stats + 5) * natures)


def base_dmg_array(level: int, power: int, atk: int,
                   def_array: np.ndarray) -> np.ndarray:
    """Calculates the base damage part of the damage formula. This is the
    part before all the external modifiers are applied. Technically, some
    games apply modifiers before the +2 is added, but the difference is
    negligible enough that it is outside the scope of this bot.
    """
    level_modifier = floor((2 * level / 5) + 2)
    numerator = np.floor(level_modifier * power * atk / def_array)
    return np.floor(numerator / 50) + 2


def random_dmg_array(level: int, power: int, atk: int, def_array: np.ndarray,
                     other: float = 1.0) -> int:
    """Calculates the damage done from one Pokemon to another. random_num is
    a float in the range [0.85, 1] that defaults to 1 for maximum damage.

    Damage formula details: https://bulbapedia.bulbagarden.net/wiki/Damage
    """
    array_size = def_array.shape[0]
    base = base_dmg_array(level, power, atk, def_array)
    random_array = np.random.random_integers(85, 100, size=array_size) / 100
    return np.floor(base * other * random_array)


def damage_as_hp_percent(dmg_array: np.ndarray,
                         hp: Union[int, np.ndarray]) -> np.ndarray:
    return 100 * dmg_array / hp
