from io import BufferedIOBase
from typing import Optional, Union

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
    file_cache = {}

    def __init__(self) -> None:
        pass

    @staticmethod
    def embed(new_embed: Optional[discord.Embed] = None, **kwargs
              ) -> discord.Embed:
        """Changes properties of an embed in-place and returns it to preserve
        the fluid Embed chaining that the original class offers.
        """
        if new_embed is None:
            new_embed = discord.Embed(**kwargs)
        new_embed.color = discord.Color.from_rgb(*Andybot.rgb_tuple)
        return new_embed

    @staticmethod
    def file(fp: Union[str, BufferedIOBase], filename: Optional[str] = None,
             *, spoiler: bool = False) -> discord.File:
        """Creates a new file if it doesn't exist, and uses the cached one
        if it does. Cache assumes file paths are unique.
        """
        if fp in Andybot.file_cache:
            cached_file = Andybot.file_cache[fp]
            cached_file.filename = filename
            cached_file.spoiler = spoiler
            return cached_file
        else:
            new_file = discord.File(fp, filename=filename, spoiler=spoiler)
            Andybot.file_cache[fp] = new_file
            return new_file


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
