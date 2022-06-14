from datetime import timedelta

import requests
import requests_cache

requests_cache.install_cache('./data/pokeapi', expire_after=timedelta(days=7))
def get_resource(url): return requests.get(url).json()['results']


stats_json = get_resource('https://pokeapi.co/api/v2/stat')
types_json = get_resource('https://pokeapi.co/api/v2/type')
games_json = get_resource('https://pokeapi.co/api/v2/version-group')

STATS_MAP = {
    stat['name']: int(index) for index, stat in enumerate(stats_json)
    if index <= 5
}
TYPES_MAP = {
    type_['name']: int(index) for index, type_ in enumerate(types_json)
    if index <= 17
}
GAMES = [game['name'] for game in games_json]
