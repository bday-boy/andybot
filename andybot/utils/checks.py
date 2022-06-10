from discord.ext import commands


def in_voice_call(ctx: commands.Context) -> bool:
    voice = ctx.guild.voice_client
    return voice and voice.channel


async def in_voice_call_check(ctx: commands.Context) -> bool:
    if in_voice_call(ctx):
        return True
    else:
        await ctx.send('Bot is not in a voice call.')
        raise commands.CommandError('Bot is not in a voice channel.')


def is_playing_audio(ctx: commands.Context) -> bool:
    voice = ctx.guild.voice_client
    return in_voice_call(ctx) and voice.source


async def is_playing_audio_check(ctx: commands.Context) -> bool:
    if is_playing_audio(ctx):
        return True
    else:
        await ctx.send('No audio is playing.')
        raise commands.CommandError('Bot is not playing audio.')
