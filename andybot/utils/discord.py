import discord
from discord.ext.commands import Context


async def playing_song(ctx: Context) -> bool:
    client = ctx.guild.voice_client
    
