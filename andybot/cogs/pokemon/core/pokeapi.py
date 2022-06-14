from datetime import timedelta
from typing import Union

import requests
import requests_cache

import andybot.cogs.pokemon.core.vars as pkmn


class PokeAPI:
    """An API wrapper class made to:
    1. Cache requests
    2. Make requests more convenient and safe
    3. Parse PokeAPI results in convenient ways (checking if final evolution,
    getting pokemon abilities as a list, etc.)
    """

    def __init__(self):
        requests_cache.install_cache(
            './data/pokeapi', expire_after=timedelta(days=7)
        )

    def get_by_url(self, url: str) -> dict:
        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f'Could not get resource from url {url}. {e}')
            raise e

        return response.json()

    def get_by_resource(self, resource: str, index: Union[str, int] = '',
                        args: str = '') -> dict:
        url = '/'.join(filter(
            None, ['https://pokeapi.co/api/v2', resource, str(index), args])
        )

        return self.get_by_url(url)

    def is_final_evo(self, mon_name: str, evo_url: str) -> bool:
        cur_evo = self.get_by_url(evo_url)['chain']
        all_evos = [cur_evo]

        while all_evos:
            cur_evo = all_evos.pop()
            if cur_evo['species']['name'] == mon_name:
                return not bool(cur_evo['evolves_to'])
            for next_evo in cur_evo['evolves_to']:
                all_evos.append(next_evo)

        return False

    def get_abilities(self, abilities: dict) -> list:
        abilities_list = [None, None, None]  # Slot 1, slot 2, hidden ability

        for ability in abilities:
            index = ability['slot']
            abilities_list[index - 1] = ability['ability']['name']

        return abilities_list

    def get_types(self, types: dict) -> list:
        types_list = [None, None]  # Slot 1, slot 2

        for type_ in types:
            index = type_['slot']
            types_list[index - 1] = type_['type']['name']

        return types_list

    def get_stats(self, stats: dict) -> list:
        stats_list = [-1 for i in range(6)]

        for stat in stats:
            index = pkmn.STATS_MAP[stat['stat']['name']]
            stats_list[index] = stat['base_stat']

        return stats_list

    def get_type_dmg_to(self, damage_relations: dict) -> list:
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

    def get_type_dmg_from(self, damage_relations: dict) -> list:
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

    def get_resource_index(self, url: str):
        split_url = url.split('/')
        if len(split_url) < 2:
            return -1
        for possible_index in split_url[-2:]:
            if possible_index.isnumeric():
                return int(possible_index)
        return -1
