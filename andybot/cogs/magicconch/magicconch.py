import random

import discord
from discord.ext import commands


class MagicConch(commands.Cog):
    """Cog for the magic conch from Spongebob."""
    prefix = ':shell: :speech_balloon:'
    wisdom = ('No.', 'No.', 'No.', 'No.', 'No.', "I don't think so.",
              'Maybe someday.', "Why don't you ask me again?", 'Yes.')

    def __init__(self, bot: discord.Client) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        print('andybot magic conch is ready.')

    @commands.command(aliases=['conch'])
    async def magicconch(self, ctx: commands.Context) -> None:
        """Ask the magic conch for guidance."""
        if random.random() < 0.95:
            await ctx.send(
                f'{MagicConch.prefix} {random.choice(MagicConch.wisdom)}'
            )
        else:
            await ctx.send(
                file=discord.File(r'./attachments/magic_conch_no.mp3')
            )


def setup(client: discord.Client) -> None:
    client.add_cog(MagicConch(client))
