import logging
import os
from os import path as osp

import discord
from discord.ext import commands

from andybot.core.andybot import Andybot, AndybotHelp
from andybot.core.file import cfg

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(
    filename='./logs/discord.log', encoding='utf-8', mode='w+'
)
handler.setFormatter(logging.Formatter(
    '%(asctime)s:%(levelname)s:%(name)s: %(message)s'
))
logger.addHandler(handler)

intents = discord.Intents.default()
intents.messages = True
bot = commands.Bot(command_prefix=cfg['command_prefix'], intents=intents)
bot.help_command = AndybotHelp()


@bot.event
async def on_ready() -> None:
    print(f'Logged in as {bot.user}')
    await bot.change_presence(activity=discord.Game('Glitches in my System'))


@bot.command()
async def about(ctx: commands.Context) -> None:
    """Sends a brief description of the bot."""
    desc = (
        "I'm Andybot, a general purpose bot made by Birthday Boy. "
        "Currently, my only capabilites are to be used as a basic music bot "
        "and to send various information about Pokemon.\n\n"
        "My code can be found [here](https://github.com/bday-boy/andybot)."
    )
    about_embed = Andybot.embed(
        title='Hello there!',
        description=desc
    ).set_thumbnail(
        url=bot.user.avatar_url
    )
    await ctx.send(embed=about_embed)


# Loads all cogs. Each cog must have a module-level setup function defined.
cogs_dir = './andybot/cogs'
for file_name in os.listdir(cogs_dir):
    if osp.isdir(osp.join(cogs_dir, file_name)) and not file_name.startswith('__'):
        bot.load_extension(f'andybot.cogs.{file_name}.{file_name}')


bot.run(cfg['token'])
