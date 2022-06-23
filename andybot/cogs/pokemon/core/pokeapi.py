import re
from collections import defaultdict
from datetime import timedelta
from typing import Tuple, Union

import requests
import requests_cache

from andybot.core.fuzzy_string import levenshtein_osa

non_alpha = re.compile('[^a-z0-9]+')
ignored_title_words = re.compile(r'\s?(pok[eé]mon|and)\s?', re.IGNORECASE)
requests_cache.install_cache('./data/pokeapi', expire_after=timedelta(days=7))
def _get_resource(url): return requests.get(url).json()['results']
_stat_list = _get_resource('https://pokeapi.co/api/v2/stat')
_type_list = _get_resource('https://pokeapi.co/api/v2/type')
_pkmn_list = _get_resource('https://pokeapi.co/api/v2/pokemon?limit=10000')
_game_list = _get_resource('https://pokeapi.co/api/v2/version-group')
_move_list = _get_resource('https://pokeapi.co/api/v2/move?limit=10000')

STATS_MAP = {
    stat['name']: int(index) for index, stat in enumerate(_stat_list)
    if index <= 5
}
TYPES_MAP = {
    type_['name']: int(index) for index, type_ in enumerate(_type_list)
    if type_['name'] not in {'unknown', 'shadow'}
}
POKEMON = {pokemon['name'] for pokemon in _pkmn_list}
GAMES = {game['name'] for game in _game_list}
MOVES = {move['name'] for move in _move_list}

del _stat_list, _type_list, _pkmn_list, _game_list, _move_list

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
    return get_by_url('/'.join(
        ['https://pokeapi.co/api/v2', resource, str(id_or_name), args]
    ))


def get_resource_index(url: str):
    split_url = url.strip('/').split('/')
    if len(split_url) < 2:
        return -1
    for possible_index in split_url[-2:]:
        if possible_index.isnumeric():
            return int(possible_index)
    return -1


def format_game(game: str) -> str:
    """Takes the words 'Pokemon' and 'and' out of a game title."""
    return re.sub(ignored_title_words, '-', game).strip('-')


def format_search(input: str) -> Tuple[str, str]:
    alpha_strs = non_alpha.split(input)
    return '-'.join(alpha_strs).lower(), '-'.join(reversed(alpha_strs)).lower()


def best_match(search: str, search_set: set) -> str:
    """Searches an iterable for the most similar string."""
    if search in search_set:
        return search

    matches = []
    search, reversed_search = format_search(search)

    for entry in search_set:
        matches.append((entry, levenshtein_osa(search, entry)))

    if search != reversed_search:
        for entry in search_set:
            matches.append((entry, levenshtein_osa(reversed_search, entry)))

    matches.sort(key=lambda t: t[1])
    return matches[0][0]


def best_match_pokemon(pokemon: str) -> str:
    return best_match(pokemon, POKEMON)


def best_match_move(move: str) -> str:
    return best_match(move, MOVES)


def best_match_game(game: str) -> str:
    return best_match(format_game(game), GAMES)


def is_final_evo(mon_name: str, evo_url: str) -> bool:
    cur_evo = get_by_url(evo_url)
    all_evos = [cur_evo['chain']]

    while all_evos:
        cur_evo = all_evos.pop()
        if cur_evo['species']['name'] == mon_name:
            return not bool(cur_evo['evolves_to'])
        for next_evo in cur_evo['evolves_to']:
            all_evos.append(next_evo)

    return False


def get_moves(pokemon: str, game: str) -> dict:
    mon_moves = defaultdict(list)
    mon_moves['level-up'] = defaultdict(list)
    mon_dict = get_by_resource('pokemon', pokemon)
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
        'effect_chance': move_dict['effect_chance'],
        'name': move_dict['name'],
        'power': move_dict['power'],
        'pp': move_dict['pp'],
        'priority': move_dict['priority'],
        'type': move_dict['type']['name'],
        'description': move_dict['effect_entries'][-1]['effect']
    }


def get_abilities(pokemon: str) -> list:
    mon_dict = get_by_resource('pokemon', pokemon)
    abilities_list = [None, None, None]  # Slot 1, slot 2, hidden ability

    for ability in mon_dict['abilities']:
        index = ability['slot']
        abilities_list[index - 1] = ability['ability']['name']

    return abilities_list


def get_types(pokemon: str) -> list:
    mon_dict = get_by_resource('pokemon', pokemon)
    types_list = [None, None]  # Slot 1, slot 2

    for type_ in mon_dict['types']:
        index = type_['slot']
        types_list[index - 1] = type_['type']['name']

    return types_list


def get_stats(pokemon: str) -> list:
    mon_dict = get_by_resource('pokemon', pokemon)
    stats_list = [-1 for i in range(6)]

    for stat in mon_dict['stats']:
        index = STATS_MAP[stat['stat']['name']]
        stats_list[index] = stat['base_stat']

    return stats_list


def get_type_dmg_to(type_: str) -> list:
    dmg_relations = get_by_resource('type', type_)['damage_relations']
    dmg_to = [1.0 for i in range(18)]
    double_dmg = dmg_relations['double_damage_to']
    half_dmg = dmg_relations['half_damage_to']
    no_dmg = dmg_relations['no_damage_to']

    for type_ in double_dmg:
        index = TYPES_MAP[type_['name']]
        dmg_to[index] = 2
    for type_ in half_dmg:
        index = TYPES_MAP[type_['name']]
        dmg_to[index] = 0.5
    for type_ in no_dmg:
        index = TYPES_MAP[type_['name']]
        dmg_to[index] = 0

    return dmg_to


def get_type_dmg_from(type_: str) -> list:
    dmg_relations = get_by_resource('type', type_)['damage_relations']
    dmg_from = [1.0 for i in range(18)]
    double_dmg = dmg_relations['double_damage_from']
    half_dmg = dmg_relations['half_damage_from']
    no_dmg = dmg_relations['no_damage_from']

    for type_ in double_dmg:
        index = TYPES_MAP[type_['name']]
        dmg_from[index] = 2
    for type_ in half_dmg:
        index = TYPES_MAP[type_['name']]
        dmg_from[index] = 0.5
    for type_ in no_dmg:
        index = TYPES_MAP[type_['name']]
        dmg_from[index] = 0

    return dmg_from


def get_pkmn_type_info(pokemon: str) -> list:
    slot_1, slot_2 = get_types(pokemon)
    dmg_from = get_type_dmg_from(slot_1)
    if slot_2 is not None:
        dmg_from_slot_2 = get_type_dmg_from(slot_2)
        for i in range(len(dmg_from)):
            dmg_from[i] *= dmg_from_slot_2[i]
    return dmg_from
