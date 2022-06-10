import asyncio
from collections import defaultdict, deque
from typing import Tuple, Union

import discord
import yt_dlp
from discord.ext import commands

from andybot.utils.checks import in_voice_call, in_voice_call_check, \
    is_playing_audio, is_playing_audio_check
from andybot.utils.music import Playlist, Song, YouTubeSong


class GuildState:
    """Helper class to track a single guild's state."""

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.playlist = Playlist()
        self.song_history = []
        self.volume = 0.1
        self.voice = None
        self._now_playing = None

    @property
    def now_playing(self) -> Song:
        return self._now_playing

    @now_playing.setter
    def now_playing(self, song: Song) -> None:
        self.song_history.append(song)
        self._now_playing = song


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

    @commands.command(aliases=['add', 'queue'])
    async def play(self, ctx: commands.Context, *, url: str) -> None:
        """Attempts to play the given URL. Currently does not support any
        other arguments.
        """
        state = self.get_state(ctx)

        try:
            song = YouTubeSong(url, ctx.author)
        except yt_dlp.DownloadError as yt_error:
            await ctx.send(f"Couldn't download the video :pensive: {yt_error}")
            raise yt_error

        if not in_voice_call(ctx):
            channel = ctx.author.voice.channel
            await channel.connect()
            await ctx.guild.change_voice_state(channel=channel, self_deaf=True)

        state.playlist.add_song(song)
        await ctx.send('Added to queue.')

        if not is_playing_audio(ctx):
            self._play(ctx)

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
        """Skips ahead by a certain number of songs."""
        voice, state = self.get_voice_info(ctx)
        if voice and voice.channel:
            await voice.stop()
            skipped_songs = state.playlist.skip(num_songs)
            state.playlist.extend(skipped_songs)
        else:
            raise commands.CommandError('Bot is not in a voice channel.')

    @commands.check(in_voice_call_check)
    @commands.command(aliases=['leave', 'die', 'begone', 'farethewell'])
    async def stop(self, ctx: commands.Context) -> None:
        """Attempts to play the given URL."""
        voice, state = self.get_voice_info(ctx)
        await voice.disconnect()
        state.reset()

    @commands.command(aliases=['v', 'vol'])
    async def volume(self, ctx: commands.Context, *, vol: Union[int, float]
                     ) -> None:
        """Sets the volume. Accepts any value between 0 and 200."""
        state = self.get_state(ctx)

        if not 0 <= vol <= 200:
            ctx.send('Volume must be between 0 and 200.')
            raise commands.CommandError(
                'Volume can only be between 0 and 200.')

        vol /= 100
        state.volume = vol
        ctx.guild.voice_client.source.volume = vol

    def _play(self, ctx: commands.Context) -> None:
        """Handles the actual playing of the song.

        TODO: Currently experiences some pretty choppy audio at times. Seems
        to be pretty intermittent, so might just be my wifi/Discord at home
        being bad (since I'm running this bot from home).
        """
        voice, state = self.get_voice_info(ctx)
        song = state.playlist.get_song()
        source = discord.PCMVolumeTransformer(
            discord.FFmpegPCMAudio(song.stream_url), volume=state.volume
        )
        state.now_playing = song
        asyncio.run_coroutine_threadsafe(
            ctx.send(embed=song.embed(state.playlist.next_song)), self.bot.loop
        )

        def after(error: Exception) -> None:
            if not state.playlist.is_empty():
                self._play(ctx)

        voice.play(source, after=after)


def setup(client: discord.Client) -> None:
    client.add_cog(Music(client))
