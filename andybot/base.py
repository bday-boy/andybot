import discord

from andybot.utils.file import cfg
from andybot.utils.misc import hex_to_rgb


class Andybot:
    color = hex_to_rgb(cfg['color'])

    def __init__(self) -> None:
        pass

    @staticmethod
    def format_embed(embed: discord.Embed) -> discord.Embed:
        """Changes properties of an embed in-place and returns it to preserve
        the fluid Embed chaining that the original class offers.
        """
        embed.color = Andybot.color
        return embed
