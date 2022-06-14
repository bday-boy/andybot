import discord
from discord.ext import commands

import andybot.cogs.pokemon.core.pokeapi as pokeapi
from andybot.core.andybot import Andybot


class Pokemon(commands.Cog):
    """Cog for Pokemon helper commands."""

    def __init__(self, bot: discord.Client) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('andybot pokemon helper is ready.')

    @commands.command()
    async def test(self, ctx: commands.Context, *, amt: int) -> None:
        """Gets the weaknesses, resistances, and immunities of a Pokemon."""
        test_embed = Andybot.format_embed(
            description=f'```\n{"-" * int(amt)}```')
        await ctx.send(embed=test_embed)

    @commands.command(aliases=['wri'])
    async def weaknesses(self, ctx: commands.Context, *, pokemon: str) -> None:
        """Gets the weaknesses, resistances, and immunities of a Pokemon."""
        types_embed = Andybot.format_embed(title=pokemon)
        type_info = pokeapi.get_pkmn_type_info(pokemon.lower())
        for stat, index in pokeapi.TYPES_MAP.items():
            types_embed.add_field(name=stat, value=f'{type_info[index]:.2f}')
        await ctx.send(embed=types_embed)

    @commands.command()
    async def stats(self, ctx: commands.Context, *, pokemon: str) -> None:
        """Gets the stats of a Pokemon."""
        stats = pokeapi.get_stats(pokemon)
        stats_embed = Andybot.format_embed(title=pokemon)
        for stat, index in pokeapi.STATS_MAP.items():
            stats_embed.add_field(name=stat, value=stats[index])
        await ctx.send(embed=stats_embed)

    @commands.command()
    async def move(self, ctx: commands.Context, *, move_name: str) -> None:
        """Gets the weaknesses, resistances, and immunities of a Pokemon."""
        move = pokeapi.get_move_info(move_name.lower())
        move_embed = Andybot.format_embed(
            title=move_name,
            description=move['description']
        )
        move_embed.add_field(
            name='Type', value=move['type'].capitalize()
        )
        move_embed.add_field(
            name='Category', value=move['damage_class'].capitalize()
        )
        move_embed.add_field(name='Power', value=move['power'] or '--')
        move_embed.add_field(name='Accuracy', value=move['accuracy'])
        move_embed.add_field(name='PP', value=move['pp'])
        move_embed.add_field(
            name='Effect chance', value=move['effect_chance'] or '--'
        )
        move_embed.add_field(name='Priority', value=move['priority'])
        await ctx.send(embed=move_embed)

    @commands.command()
    async def moves(self, ctx: commands.Context, *, pokemon: str,
                    game: str) -> None:
        """Gets the stats of a Pokemon."""
        mon_moves = pokeapi.get_moves(pokemon, game)
        moves_embed = Andybot.format_embed(title=pokemon)
        await ctx.send(embed=moves_embed)

    def _format_move(self, move: dict) -> str:
        pass


def setup(client: discord.Client) -> None:
    client.add_cog(Pokemon(client))
