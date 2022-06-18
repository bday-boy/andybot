import matplotlib.pyplot as plt
import numpy as np

import andybot.cogs.pokemon.core.math as pokemath


def damage_scatter(attacker_level: int, defender_level: int, power: int,
                   atk: int, base_def: int, stab: bool, type_: float,
                   mods: float, hp: int) -> None:
    """Creates a simple 2D graph of the possible damage done to a defending
    Pokemon.
    """
    fig, ax = plt.subplots(figsize=(5, 2.7), layout='constrained')
    def_vec = pokemath.random_stat_array(base_def, defender_level)
    total_mods = (1.5 if stab else 1) * type_ * mods
    dmgs = pokemath.random_dmg_array(attacker_level, power, atk, def_vec,
                                     total_mods)
    hp_percent = pokemath.damage_as_hp_percent(dmgs, hp)
    ax.scatter(def_vec, hp_percent, label='Damages')
    ax.set_xlabel('Defense')
    ax.set_ylabel('Damage (as % of hp)')
    ax.set_title('Damage calculation')
    ax.legend()
    plt.grid()
    plt.savefig('./attachments/damage_scatter.png')


if __name__ == '__main__':
    damage_scatter(50, 50, 90, 134, 80, True, 1, 1.5, 165)
