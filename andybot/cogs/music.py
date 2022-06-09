import asyncio
from collections import defaultdict, deque
from typing import Union

import discord
import yt_dlp
from discord.ext import commands

from andybot.utils.music_players import Song, YouTubeSong


class Playlist(deque):
    """Helper deque subclass to track a playlist."""

    def __init_subclass__(cls) -> None:
        return super().__init_subclass__()

    @property
    def next_song(self) -> Union[YouTubeSong, None]:
        if self.__len__() > 0:
            return self[0]
        else:
            return None


class GuildState:
    """Helper class to track a single guild's state."""

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.playlist = Playlist()
        self.song_history = []
        self.volume = 0.75
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

    def get_state(self, guild: discord.Guild) -> GuildState:
        """Gets the state for a given guild."""
        return self.states[guild.id]

    @commands.Cog.listener()
    async def on_ready(self):
        print('andybot music player is ready.')

    @commands.command()
    async def play(self, ctx: commands.Context, *, url: str) -> None:
        """Attempts to play the given URL. Currently does not support any
        other arguments.
        """
        client = ctx.guild.voice_client
        state = self.get_state(ctx.guild)

        try:
            song = YouTubeSong(url, ctx.author)
        except yt_dlp.DownloadError as e:
            await ctx.send(f"Couldn't download the video :pensive: {e}")
            return

        if client and client.channel:
            state.playlist.append(song)
            await ctx.send('Added to queue.')
        else:
            channel = ctx.author.voice.channel
            client = await channel.connect()
            self._play(client, state, song)
            await ctx.send(embed=song.embed(state.playlist.next_song))

    @commands.command(aliases=['pause', 'resume'])
    async def toggle(self, ctx: commands.Context):
        """Pauses or resumes the current song."""

    @commands.command(name='next', aliases=['skip', '>'])
    async def next_(self, ctx: commands.Context):
        """Skips to the next song."""

    @commands.command(aliases=['leave', 'die', 'begone', 'farethewell'])
    async def stop(self, ctx: commands.Context) -> None:
        """Attempts to play the given URL."""
        client = ctx.guild.voice_client
        state = self.get_state(ctx.guild)
        if client and client.channel:
            await client.disconnect()
            state.reset()
        else:
            raise commands.CommandError('Bot is not in a voice channel.')

    @commands.command(aliases=['v', 'vol'])
    async def volume(self, ctx: commands.Context, *, vol: Union[int, float]):
        """Sets the volume. Accepts any value between 0 and 200."""
        state = self.get_state(ctx.guild)

        if not 0 <= vol <= 200:
            ctx.send('Volume must be between 0 and 200.')
            raise commands.CommandError(
                'Volume can only be between 0 and 200.')

        vol /= 100
        state.volume = vol
        ctx.guild.voice_client.volume = vol

    def _play(self, client: discord.Client, state: GuildState,
              song: YouTubeSong) -> None:
        """Handles the actual playing of the song.

        TODO: Currently experiences some pretty choppy audio at times.
        """
        source = discord.PCMVolumeTransformer(
            discord.FFmpegPCMAudio(song.stream_url), volume=state.volume
        )
        state.now_playing = song

        def after(error):
            if state.playlist.next_song is not None:
                next_song = state.playlist.popleft()
                self._play(client, state, next_song)
            else:
                asyncio.run_coroutine_threadsafe(
                    client.disconnect(), self.bot.loop
                )

        client.play(source, after=after)


def setup(client: discord.Client) -> None:
    client.add_cog(Music(client))
