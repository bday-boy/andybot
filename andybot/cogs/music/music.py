import asyncio
from collections import defaultdict
from typing import Tuple, Union

import discord
import yt_dlp
from discord.ext import commands

from andybot.core.andybot import Andybot, handle_base_exceptions
from andybot.core.checks import in_voice_call, in_voice_call_check, \
    is_playing_audio, is_playing_audio_check
from andybot.core.misc import escape_special_chars
from andybot.cogs.music.utils import Playlist, YouTubeSong

FFMPEG_OPTS = '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'


class GuildState:
    """Helper class to track a single guild's state."""

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.playlist = Playlist()
        self.volume = 0.1
        self.voice = None
        self.now_playing = None


class Music(commands.Cog):
    """Cog for playing music in voice call."""

    def __init__(self, bot: discord.Client) -> None:
        self.bot = bot
        self.states = defaultdict(GuildState)

    def get_state(self, ctx: commands.Context) -> GuildState:
        """Gets the state for a given guild."""
        return self.states[ctx.guild.id]

    def get_voice_client(self, ctx: commands.Context) -> discord.VoiceClient:
        return ctx.guild.voice_client

    def get_voice_info(self, ctx: commands.Context
                       ) -> Tuple[discord.VoiceClient, GuildState]:
        return self.get_voice_client(ctx), self.get_state(ctx)

    @commands.Cog.listener()
    async def on_ready(self):
        print('andybot music player is ready.')

    @commands.command(aliases=['add', 'p', '+'])
    async def play(self, ctx: commands.Context, *, url: str) -> None:
        """Attempts to play the given URL. Currently does not support any
        other arguments.
        """
        state = self.get_state(ctx)
        song = YouTubeSong(url, ctx.author)

        if not in_voice_call(ctx):
            channel = ctx.author.voice.channel
            await channel.connect()
            await ctx.guild.change_voice_state(channel=channel, self_deaf=True)

        state.playlist.add_song(song)
        escaped_title = escape_special_chars(song.title)
        await ctx.send(f'Added **{escaped_title}** to queue.')

        if not is_playing_audio(ctx):
            self._play(ctx)

    @play.error
    async def play_error(self, ctx: commands.Context, error: Exception):
        if isinstance(error, yt_dlp.DownloadError):
            await ctx.send(f"Couldn't download the video :pensive:")
        else:
            await handle_base_exceptions(ctx, error)

    @commands.check(in_voice_call_check)
    @commands.check(is_playing_audio_check)
    @commands.command(aliases=['pause', 'resume'])
    async def toggle(self, ctx: commands.Context):
        """Pauses or resumes the current song."""
        voice = self.get_voice_client(ctx)
        if voice.is_playing():
            voice.pause()
        else:
            voice.resume()

    @commands.check(in_voice_call_check)
    @commands.check(is_playing_audio_check)
    @commands.command(aliases=['next', '|'])
    async def skip(self, ctx: commands.Context, *, num_songs: int = 1) -> None:
        """Skips ahead by a certain number of songs. Default is the next
        song.
        """
        voice, state = self.get_voice_info(ctx)
        if voice and voice.channel:
            voice.stop()
            state.playlist.skip(num_songs - 1)
        else:
            raise commands.CommandError('Bot is not in a voice channel.')

    @commands.check(in_voice_call_check)
    @commands.check(is_playing_audio_check)
    @commands.command(aliases=['skipto', '?', 'goto'])
    async def search(self, ctx: commands.Context, *, song_search: str) -> None:
        """Skips ahead to a song by name. Immediately skips to best match."""
        # TODO: Add confirmation
        voice, state = self.get_voice_info(ctx)
        if voice and voice.channel:
            voice.stop()
            state.playlist.skip_to(song_search)
        else:
            raise commands.CommandError('Bot is not in a voice channel.')

    @commands.check(in_voice_call_check)
    @commands.command(aliases=['leave', 'die', 'begone', 'farethewell'])
    async def stop(self, ctx: commands.Context) -> None:
        """Stops the music and disconnects the bot from the voice call."""
        voice, state = self.get_voice_info(ctx)
        await voice.disconnect()
        state.reset()

    @commands.command(aliases=['v', 'vol'])
    async def volume(self, ctx: commands.Context, *, vol: Union[int, float]
                     ) -> None:
        """Sets the volume. Accepts any value between 0 and 200."""
        state = self.get_state(ctx)

        if not 0 <= vol <= 200:
            await ctx.send('Volume must be between 0 and 200.')
            raise commands.CommandError(
                'Volume can only be between 0 and 200.')

        vol /= 100
        state.volume = vol
        ctx.guild.voice_client.source.volume = vol

    @commands.check(in_voice_call_check)
    @commands.command(aliases=['songs', 'q'])
    async def queue(self, ctx: commands.Context) -> None:
        """Lists the current songs in the queue."""
        state = self.get_state(ctx)
        embed = discord.Embed(
            title=f'Now playing: {state.now_playing.title}',
            description=state.playlist.song_list
        )
        Andybot.format_embed(embed)
        await ctx.send(embed=embed)

    @commands.check(in_voice_call_check)
    @commands.command(aliases=['h'])
    async def history(self, ctx: commands.Context) -> None:
        """Lists the song history. Most recent songs are at the top."""
        state = self.get_state(ctx)
        embed = discord.Embed(
            title='Song history (most recent listed first)',
            description=state.playlist.history
        )
        Andybot.format_embed(embed)
        await ctx.send(embed=embed)

    def _play(self, ctx: commands.Context) -> None:
        """Handles the actual playing of the song.

        TODO: Currently experiences some pretty choppy audio at times. Seems
        to be pretty intermittent, so might just be my wifi/Discord at home
        being bad (since I'm running this bot from home).
        """
        voice, state = self.get_voice_info(ctx)
        song = state.playlist.get_song()
        source = discord.PCMVolumeTransformer(
            discord.FFmpegPCMAudio(song.url, before_options=FFMPEG_OPTS),
            volume=state.volume
        )
        state.now_playing = song
        asyncio.run_coroutine_threadsafe(
            ctx.send(embed=song.embed(state.playlist.next_song)), self.bot.loop
        )

        def after(error: Exception) -> None:
            if state.playlist.is_empty():
                voice.stop()
            else:
                self._play(ctx)

        voice.play(source, after=after)


def setup(client: discord.Client) -> None:
    client.add_cog(Music(client))
