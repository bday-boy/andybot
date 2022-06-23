from typing import Optional

import discord
from discord.ext import commands

from andybot.core.file import cfg
from andybot.core.misc import hex_to_rgb


class Andybot:
    """Class for keeping certain aspects of the bot consistent, such as
    embed color.
    """

    rgb_hex = cfg['color']
    rgb_tuple = hex_to_rgb(cfg['color'])

    def __init__(self) -> None:
        pass

    @staticmethod
    def embed(embed: Optional[discord.Embed] = None, **kwargs
              ) -> discord.Embed:
        """Changes properties of an embed in-place and returns it to preserve
        the fluid Embed chaining that the original class offers.
        """
        if embed is None:
            embed = discord.Embed(**kwargs)
        embed.color = discord.Color.from_rgb(*Andybot.rgb_tuple)
        return embed


class AndybotHelp(commands.MinimalHelpCommand):
    """Simple help command. I really only made this to override the original
    help command because it was failing command checks even when I told it
    not to do them lmao
    """

    def __init__(self, **options):
        super().__init__(**options)
        self.verify_checks = False

    async def send_pages(self):
        destination = self.get_destination()
        help_embed = Andybot.embed(description='')
        for page in self.paginator.pages:
            help_embed.description += page
        await destination.send(embed=help_embed)


async def handle_base_exceptions(ctx: commands.Context,
                                 error: Exception) -> bool:
    if isinstance(error, discord.HTTPException):
        await ctx.send('Something went wrong with an HTTP request.')
    elif isinstance(error, discord.ClientException):
        await ctx.send('Something went wrong with the discord client.')
    elif isinstance(error, discord.DiscordException):
        await ctx.send('Something unknown went wrong with discord.')
    await ctx.send(repr(error))
