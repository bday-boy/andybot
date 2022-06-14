from collections import defaultdict
from datetime import timedelta
from typing import Union

import requests
import requests_cache

import andybot.cogs.pokemon.core.vars as pkmn

requests_cache.install_cache(
    './data/pokeapi', expire_after=timedelta(days=7)
)


def get_by_url(url: str) -> dict:
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f'Could not get resource from url {url}. {e}')
        raise e

    return response.json()


def get_by_resource(resource: str, id_or_name: Union[int, str] = '',
                    args: str = '') -> dict:
    url = '/'.join(
        ['https://pokeapi.co/api/v2', resource, str(id_or_name), args]
    )

    return get_by_url(url)


def is_final_evo(mon_name: str, evo_url: str) -> bool:
    cur_evo = get_by_url(evo_url)['chain']
    all_evos = [cur_evo]

    while all_evos:
        cur_evo = all_evos.pop()
        if cur_evo['species']['name'] == mon_name:
            return not bool(cur_evo['evolves_to'])
        for next_evo in cur_evo['evolves_to']:
            all_evos.append(next_evo)

    return False


def get_moves(mon_name: str, game: str) -> dict:
    mon_moves = defaultdict(list)
    mon_moves['level-up'] = defaultdict(list)
    mon_dict = get_by_resource('pokemon', mon_name)
    moves = mon_dict['moves']

    for move_entry in moves:
        for version_group_entry in move_entry['version_group_details']:
            if version_group_entry['version_group']['name'] == game:
                move = move_entry['move']
                method = version_group_entry['move_learn_method']['name']
                level = int(version_group_entry['level_learned_at'])
                move_info = get_move_info(move['name'])
                if level > 0:
                    mon_moves['level-up'][level].append(move_info)
                else:
                    mon_moves[method].append(move_info)
                break

    return mon_moves


def get_move_info(move: str) -> dict:
    move_dict = get_by_resource('move', move)
    return {
        'accuracy': move_dict['accuracy'],
        'damage_class': move_dict['damage_class']['name'],
        'name': move_dict['name'],
        'power': move_dict['power'],
        'pp': move_dict['pp'],
        'priority': move_dict['priority'],
        'type': move_dict['type']['name']
    }


def get_abilities(abilities: dict) -> list:
    abilities_list = [None, None, None]  # Slot 1, slot 2, hidden ability

    for ability in abilities:
        index = ability['slot']
        abilities_list[index - 1] = ability['ability']['name']

    return abilities_list


def get_types(types: dict) -> list:
    types_list = [None, None]  # Slot 1, slot 2

    for type_ in types:
        index = type_['slot']
        types_list[index - 1] = type_['type']['name']

    return types_list


def get_stats(stats: dict) -> list:
    stats_list = [-1 for i in range(6)]

    for stat in stats:
        index = pkmn.STATS_MAP[stat['stat']['name']]
        stats_list[index] = stat['base_stat']

    return stats_list


def get_type_dmg_to(damage_relations: dict) -> list:
    dmg_to = [1 for i in range(18)]
    double_dmg = damage_relations['double_damage_to']
    half_dmg = damage_relations['half_damage_to']
    no_dmg = damage_relations['no_damage_to']

    for type_ in double_dmg:
        index = pkmn.TYPES_MAP[type_['name']]
        dmg_to[index] = 2
    for type_ in half_dmg:
        index = pkmn.TYPES_MAP[type_['name']]
        dmg_to[index] = 0.5
    for type_ in no_dmg:
        index = pkmn.TYPES_MAP[type_['name']]
        dmg_to[index] = 0

    return dmg_to


def get_type_dmg_from(damage_relations: dict) -> list:
    dmg_from = [1 for i in range(18)]
    double_dmg = damage_relations['double_damage_from']
    half_dmg = damage_relations['half_damage_from']
    no_dmg = damage_relations['no_damage_from']

    for type_ in double_dmg:
        index = pkmn.TYPES_MAP[type_['name']]
        dmg_from[index] = 2
    for type_ in half_dmg:
        index = pkmn.TYPES_MAP[type_['name']]
        dmg_from[index] = 0.5
    for type_ in no_dmg:
        index = pkmn.TYPES_MAP[type_['name']]
        dmg_from[index] = 0

    return dmg_from


def get_resource_index(url: str):
    split_url = url.split('/')
    if len(split_url) < 2:
        return -1
    for possible_index in split_url[-2:]:
        if possible_index.isnumeric():
            return int(possible_index)
    return -1
