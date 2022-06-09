import logging
import os

import discord
from discord.ext import commands
from discord.ext.commands import Context

from src.utils.file import load_config

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(
    filename='discord.log', encoding='utf-8', mode='w+'
)
handler.setFormatter(logging.Formatter(
    '%(asctime)s:%(levelname)s:%(name)s: %(message)s'
))
logger.addHandler(handler)

intents = discord.Intents.default()
intents.messages = True
cfg = load_config()
bot = commands.Bot(command_prefix=cfg['command_prefix'], intents=intents)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    await bot.change_presence(activity=discord.Game('Glitches in my System'))


@bot.command()
async def test(ctx: Context, *args) -> None:
    cmd_args = ', '.join(args)
    await ctx.send(f'This is a test. It has {len(args)} arguments: {cmd_args}')


# Loads all cogs. Each cog must have a module-level setup function defined.
for file_name in os.listdir('./src/cogs'):
    if file_name.endswith('.py') and not file_name.startswith('__'):
        bot.load_extension(f'src.cogs.{file_name[:-3]}')


bot.run(cfg['token'])
