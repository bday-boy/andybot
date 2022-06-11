import logging
import os

import discord
from discord.ext import commands

from andybot.utils.file import cfg

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


@bot.event
async def on_ready() -> None:
    print(f'Logged in as {bot.user}')
    await bot.change_presence(activity=discord.Game('Glitches in my System'))


# Loads all cogs. Each cog must have a module-level setup function defined.
for file_name in os.listdir('./andybot/cogs'):
    if file_name.endswith('.py') and not file_name.startswith('__'):
        bot.load_extension(f'andybot.cogs.{file_name[:-3]}')


bot.run(cfg['token'])
