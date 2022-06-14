from datetime import timedelta

import requests
import requests_cache

requests_cache.install_cache('./data/pokeapi', expire_after=timedelta(days=7))
def _get_resource(url): return requests.get(url).json()['results']


_stats_json = _get_resource('https://pokeapi.co/api/v2/stat')
_types_json = _get_resource('https://pokeapi.co/api/v2/type')
_games_json = _get_resource('https://pokeapi.co/api/v2/version-group')

STATS_MAP = {
    stat['name']: int(index) for index, stat in enumerate(_stats_json)
    if index <= 5
}
TYPES_MAP = {
    type_['name']: int(index) for index, type_ in enumerate(_types_json)
    if index <= 17
}
GAMES = [game['name'] for game in _games_json]
