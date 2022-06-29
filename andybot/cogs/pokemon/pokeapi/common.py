import re
from datetime import timedelta
from typing import Iterable, Tuple

import requests
import requests_cache

from andybot.core.fuzzy_string import levenshtein_osa

non_alphanumeric = re.compile('[^a-z0-9]+')
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


def reformat_match(match: str) -> str:
    """Takes a """
    return ' '.join(s.capitalize() for s in match.split('-'))


def format_game(game: str) -> str:
    """Takes the words 'Pokemon' and 'and' out of a game title, since they are
    missing from the game titles in PokeAPI.
    """
    return re.sub(ignored_title_words, '-', game).strip('-')


def get_Search_attempts(input: str) -> Tuple[str, str]:
    """Since some items in PokeAPI are a bit backwards from how humans usually
    type them out (i.e. venusaur-mega rather than Mega Venusaur), this
    function exists to create two different possible searches that the user
    may be looking for.
    """
    alpha_strs = non_alphanumeric.split(input)
    return (
        '-'.join(alpha_strs).lower(),
        '-'.join(reversed(alpha_strs)).lower()
    )


def best_match(search: str, search_space: Iterable) -> str:
    """Searches an iterable for the most similar string and returns the best
    match, even if none of the matches are very good. Max search length is 50.
    """
    if len(search) > 50:
        raise ValueError(f'The search {search} is WAY too long.')

    search, reversed_search = get_Search_attempts(search)
    if search in search_space:
        return search

    matches = []

    for entry in search_space:
        matches.append((entry, levenshtein_osa(search, entry)))

    if search != reversed_search:
        for entry in search_space:
            matches.append((entry, levenshtein_osa(reversed_search, entry)))

    matches.sort(key=lambda t: t[1])
    return matches[0][0]


def best_match_pokemon(pokemon: str) -> str:
    return best_match(pokemon, POKEMON)


def best_match_move(move: str) -> str:
    return best_match(move, MOVES)


def best_match_game(game: str) -> str:
    return best_match(format_game(game), GAMES)
