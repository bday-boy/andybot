import discord
from discord.ext import commands


class Pokemon(commands.Cog):
    """Cog for Pokemon helper commands."""

    def __init__(self, bot: discord.Client) -> None:
        self.bot = bot


def setup(client: discord.Client) -> None:
    client.add_cog(Pokemon(client))
