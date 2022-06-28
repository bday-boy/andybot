import discord
from discord.ext import commands
from numpy import ndarray

import andybot.cogs.pokemon.core.math as pokemath
import andybot.cogs.pokemon.core.pokeapi as pokeapi
from andybot.core.andybot import Andybot
from andybot.cogs.pokemon.core.plotter import damage_scatter


class Pokemon(commands.Cog):
    """Cog for Pokemon helper commands."""

    def __init__(self, bot: discord.Client) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('andybot pokemon helper is ready.')

    @commands.command(aliases=['wri', 'resistances'])
    async def weaknesses(self, ctx: commands.Context, *, pokemon: str) -> None:
        """Gets the weaknesses, resistances, and immunities of a Pokemon."""
        types_embed = Andybot.embed(title=pokemon)
        pokemon_match = pokeapi.best_match_pokemon(pokemon)
        type_info = pokeapi.get_pkmn_type_info(pokemon_match)
        for stat, index in pokeapi.TYPES_MAP.items():
            types_embed.add_field(name=stat, value=f'{type_info[index]:.2f}')
        await ctx.send(embed=types_embed)

    @commands.command()
    async def stats(self, ctx: commands.Context, *, pokemon: str) -> None:
        """Gets the stats of a Pokemon."""
        pokemon_match = pokeapi.best_match_pokemon(pokemon)
        stats = pokeapi.get_stats(pokemon_match)
        stats_embed = Andybot.embed(title=pokemon)
        for stat, index in pokeapi.STATS_MAP.items():
            stats_embed.add_field(name=stat, value=stats[index])
        await ctx.send(embed=stats_embed)

    @commands.command()
    async def move(self, ctx: commands.Context, *, move_name: str) -> None:
        """Gets the weaknesses, resistances, and immunities of a Pokemon."""
        move_match = pokeapi.best_match_move(move_name)
        move_name = pokeapi.reformat_match(move_match)
        move = pokeapi.get_move_info(move_match)
        filename = f'{move["type"]}-{move["damage_class"]}.png'
        move_thumbnail = discord.File(
            f'./attachments/pkmn/moves/{filename}',
            filename=filename
        )
        move_embed = Andybot.embed(
            title=move_name,
            description=move['description']
        ).set_thumbnail(
            url=f'attachment://{filename}'
        ).add_field(
            name='Power', value=move['power'] or '--'
        ).add_field(
            name='Accuracy', value=move['accuracy']
        ).add_field(
            name='PP', value=move['pp']
        ).add_field(
            name='Effect %', value=move['effect_chance'] or '--'
        ).add_field(
            name='Priority', value=move['priority']
        )
        await ctx.send(embed=move_embed, file=move_thumbnail)

    @commands.command()
    async def moves(self, ctx: commands.Context, pokemon: str,
                    game: str) -> None:
        """Gets the moves of a Pokemon."""
        mon_moves = pokeapi.get_moves(pokemon, game)
        moves_embed = Andybot.embed(title=pokemon)
        await ctx.send(embed=moves_embed)

    @commands.command(aliases=['dmg'])
    async def damage(self, ctx: commands.Context, attacker: str,
                     defender: str, attacker_level: int, defender_level: int,
                     move: str, attacker_attack: int, extra_mods: float = 1.0
                     ) -> None:
        """Creates a scatterplot of potential damage done to a Pokemon."""

    def _format_move(self, move: dict) -> str:
        pass

    def _damage(self, attacker: str, defender: str, attacker_level: int,
                defender_level: int, move: str, attacker_attack: int,
                extra_mods: float = 1.0) -> ndarray:
        pass


def setup(client: discord.Client) -> None:
    client.add_cog(Pokemon(client))
