from typing import Generator

import discord
import yt_dlp
from discord.ext import commands
from discord.ext.commands import Context, Cog

from src.errors import NoSongInfoError

YT_DLP_OPTS = {
    'default_search': 'ytsearch',
    'format': 'bestaudio/best',
    'extract_flat': 'in_playlist',
    'noplaylist': True,
}

KEYS_TO_SAVE = (
    'title',
    'thumbnail',
    'duration',
    'url',
    'webpage_url',
)


class YouTubeVideo:
    def __init__(self, url: str) -> None:
        info = None
        with yt_dlp.YoutubeDL(YT_DLP_OPTS) as ydl:
            info = ydl.extract_info(url, download=False)
        if info is None:
            raise NoSongInfoError('The requested URL has no information.')
        for key in KEYS_TO_SAVE:
            setattr(self, key, info[key])
        self._stream_urls = self.get_audio_stream_urls(info['formats'])
        self._all_info = info

        # Just gets the first audio-based URL
        self.stream_url = next(self._stream_urls)

    def get_audio_stream_urls(self, formats: list[dict]
                              ) -> Generator[dict, None, None]:
        """Yields all URLs for formats that are audio-based."""
        for format_ in formats:
            if format_['acodec'] != 'opus':
                continue
            yield format_['url']


class Music(Cog):
    """Cog for playing music in voice call."""

    def __init__(self, client: discord.Client) -> None:
        self.client = client
        self.queue = []

    @commands.Cog.listener()
    async def play(self):
        print('andybot music player is ready.')

    @commands.command()
    async def test(self, ctx: Context):
        await ctx.send('This is a cog test.')

    @commands.command()
    async def play(self, ctx: Context): ...

    @commands.command(aliases=['pause', 'resume'])
    async def toggle(self, ctx: Context): ...

    @commands.command(name='next', aliases=['skip'])
    async def next_(self, ctx: Context): ...


def setup(client: discord.Client) -> None:
    client.add_cog(Music(client))
