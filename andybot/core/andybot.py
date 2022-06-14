import discord
from discord.ext import commands

from andybot.core.file import cfg
from andybot.core.misc import hex_to_rgb


class Andybot:
    color = hex_to_rgb(cfg['color'])

    def __init__(self) -> None:
        pass

    @staticmethod
    def format_embed(embed: discord.Embed) -> discord.Embed:
        """Changes properties of an embed in-place and returns it to preserve
        the fluid Embed chaining that the original class offers.
        """
        embed.color = discord.Color.from_rgb(*Andybot.color)
        return embed


async def handle_base_exceptions(ctx: commands.Context,
                                 error: Exception) -> bool:
    if isinstance(error, discord.HTTPException):
        await ctx.send('Something went wrong with an HTTP request.')
    elif isinstance(error, discord.ClientException):
        await ctx.send('Something went wrong with the discord client.')
    elif isinstance(error, discord.DiscordException):
        await ctx.send('Something unknown went wrong with discord.')
    await ctx.send(repr(error))
