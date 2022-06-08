import discord

from utils import get_token

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f'Logged in as {client.user}')


@client.event
async def on_message(msg: discord.Message):
    if msg.author == client.user:
        return
    
    if msg.content.startswith('$hello'):
        await msg.channel.send('Hello!')


client.run(get_token())
