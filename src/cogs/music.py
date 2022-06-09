import asyncio
from collections import defaultdict, deque
from typing import Union

import discord
import yt_dlp
from discord.ext import commands
from discord.ext.commands import Context, Cog

from src.utils.music_players import Song, YouTubeSong


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
        self.playlist = Playlist()
        self.now_playing = None
        self.volume = 0.75

    def reset(self) -> None:
        self.playlist = Playlist()
        self.now_playing = None
        self.volume = 0.75


class Music(Cog):
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
    async def play(self, ctx: Context, *, url: str) -> None:
        """Attempts to play the given URL."""
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
    async def toggle(self, ctx: Context):
        """Pauses or resumes the current song."""

    @commands.command(name='next', aliases=['skip'])
    async def next_(self, ctx: Context):
        """Skips to the next song."""

    @commands.command(aliases=['leave', 'die', 'begone', 'farethewell'])
    async def stop(self, ctx: Context) -> None:
        """Attempts to play the given URL."""
        client = ctx.guild.voice_client
        state = self.get_state(ctx.guild)
        if client and client.channel:
            await client.disconnect()
            state.reset()
        else:
            raise commands.CommandError('Bot is not in a voice channel.')

    @commands.command(name='next', aliases=['vol'])
    async def volume(self, ctx: Context):
        """Skips to the next song."""

    def _play(self, client: discord.Client, state: GuildState,
              song: YouTubeSong) -> None:
        source = discord.PCMVolumeTransformer(
            discord.FFmpegPCMAudio(song.stream_url), volume=state.volume
        )
        state.now_playing = song

        def after(error):
            if len(state.playlist) > 0:
                next_song = state.playlist.popleft()
                self._play(client, state, next_song)
            else:
                asyncio.run_coroutine_threadsafe(
                    client.disconnect(), self.bot.loop
                )

        client.play(source, after=after)


def setup(client: discord.Client) -> None:
    client.add_cog(Music(client))
