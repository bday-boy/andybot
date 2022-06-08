import discord
import logging
from discord.ext import commands
from discord.ext.commands import Context

from src.config import load_config

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(
    filename='discord.log', encoding='utf-8', mode='w'
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


@bot.command()
async def test(ctx: Context, *args) -> None:
    cmd_args = ', '.join(args)
    await ctx.send(f'This is a test. It has {len(args)} arguments: {cmd_args}')


@bot.command()
async def play(ctx: Context, url: str, *args) -> None:
    """Attempts to play the given URL in a voice call."""


@bot.command()
async def pause(ctx: Context) -> None:
    """Pauses the current song, if any."""


@bot.command(name='next')
async def _next(ctx: Context) -> None:
    """Goes to the next song in the queue."""


bot.run(cfg['token'])
