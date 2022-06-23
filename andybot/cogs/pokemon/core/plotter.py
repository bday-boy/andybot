import matplotlib.pyplot as plt

import andybot.cogs.pokemon.core.math as pokemath


def damage_scatter(attacker_level: int, defender_level: int, power: int,
                   atk: int, base_def: int, stab: bool, type_: float,
                   mods: float, base_hp: int) -> None:
    """Creates a simple 2D graph of the possible damage done to a defending
    Pokemon.
    """
    fig, ax = plt.subplots(figsize=(5, 2.7), layout='constrained')
    samples = 250
    def_vec = pokemath.random_stat_array(base_def, defender_level, samples)
    total_mods = (1.5 if stab else 1) * type_ * mods
    dmgs = pokemath.random_dmg_array(attacker_level, power, atk, def_vec,
                                     total_mods)
    hps = pokemath.random_hp_array(base_hp, defender_level, samples)
    hp_percent = pokemath.damage_as_hp_percent(dmgs, hps)
    ax.scatter(def_vec, hp_percent, label='Damages', alpha=0.5)
    ax.set_xlabel('Defense')
    ax.set_ylabel('Damage (as % of hp)')
    ax.set_title(f'Random damage calculation with {samples} samples')
    ax.legend()
    plt.grid()
    plt.savefig('./attachments/damage_scatter.png')


if __name__ == '__main__':
    damage_scatter(100, 100, 80, 372, 85, True, 2, 1.5, 90)
