from typing import Tuple
import matplotlib.pyplot as plt
import numpy as np

import andybot.cogs.pokemon.core.math as pokemath


def dmg_array(level: int, power: int, atk: int, def_range: Tuple[int],
              stab: bool, type_: float, mods: float, roll: float,
              hp: int) -> np.ndarray:
    full_modifier = (1.5 if stab else 1) * type_ * mods
    dmgs = np.asarray([
        pokemath.calc_dmg(level, power, atk, d, full_modifier, roll)
        for d in def_range
    ])
    return 100 * dmgs / hp


def plot_damage(attacker_level: int, defender_level: int, power: int, atk: int,
                def_: int, stab: bool, type_: float, mods: float, hp: int
                ) -> None:
    """Creates a simple 2D graph."""
    fig, ax = plt.subplots(figsize=(5, 2.7), layout='constrained')
    def_range = pokemath.non_hp_stat_range(def_, defender_level)
    lowest_dmgs = dmg_array(
        attacker_level, power, atk, def_range, stab, type_, mods, 0.85, hp
    )
    highest_dmgs = dmg_array(
        attacker_level, power, atk, def_range, stab, type_, mods, 1, hp
    )
    ax.fill_between(def_range, lowest_dmgs, highest_dmgs, alpha=0.25)
    ax.plot(def_range, highest_dmgs, label='Highest roll')
    ax.plot(def_range, lowest_dmgs, label='Lowest roll')
    ax.set_xlabel('Defense')
    ax.set_ylabel('Damage (as % of hp)')
    ax.set_title('Damage calculation')
    ax.legend()
    plt.grid()
    plt.savefig('./attachments/damage.png')


if __name__ == '__main__':
    plot_damage(100, 50, 120, 389, 75, False, 2, 2, 165)
