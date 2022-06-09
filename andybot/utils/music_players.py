import discord
import yt_dlp

from andybot.errors import NoSongInfoError

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
    'description',
)

QUALITIES = {
    'low': 1,
    'medium': 2,
    'high': 3
}


class Song:
    """Base class for all songs."""


class YouTubeSong(Song):
    """yt-dlp helper class that downloads video information and stores it
    in class attributes for easy use.
    """

    def __init__(self, url: str, author: discord.User = None) -> None:
        info = None
        with yt_dlp.YoutubeDL(YT_DLP_OPTS) as ydl:
            info = ydl.extract_info(url, download=False)
        if info is None:
            raise NoSongInfoError('The requested URL has no information.')
        for key in KEYS_TO_SAVE:
            setattr(self, key, info[key])
        self.stream_url = self.get_highest_quality_stream(info['formats'])
        self.author = author
        self._all_info = info

    def get_highest_quality_stream(self, formats: list[dict]) -> str:
        """Finds the highest quality stream URL and returns it."""
        audio_only = filter(
            lambda d: 'audio only' in d['format'], formats
        )
        best_quality = max(
            audio_only, key=lambda d: QUALITIES.get(d['format_note'], 0)
        )
        return best_quality['url']

    def embed(self, next_song: Song) -> discord.Embed:
        """Creates an embed with information about the song and the next
        song in the queue.
        """
        description = self.description[:256].split('\n')
        if len(description) > 5 or len(self.description) > 256:
            description = "\n".join(description[:5]) + '...'
        
        return discord.Embed(
            color=discord.Color.from_rgb(r=0x77, g=0xDD, b=0x77),
            description=description,
            title=self.title,
            url=self.url,
        ).set_author(
            name=self.author
        ).set_thumbnail(
            url=self.thumbnail
        ).set_footer(
            text=f'Next song: {next_song.title if next_song else "none"}'
        )
