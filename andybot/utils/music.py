import discord
import yt_dlp
from collections import deque
from typing import Any, List, Union

from andybot.errors import NoSongInfoError
from andybot.utils.fuzzy_string import lcs

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
        else:
            description = "\n".join(description[:5])

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


class Playlist(deque):
    """A simple FIFO used for queueing songs."""

    @property
    def next_song(self) -> Union[Any, None]:
        """Property that returns the next song if there is one, and None
        otherwise.
        """
        return self[0] if not self.is_empty() else None

    def add_song(self, item: Any) -> None:
        """Appends a song to the right of the Playlist, since Playlist is
        intended to be a FIFO queue.
        """
        self.append(item)

    def get_song(self) -> Any:
        """Pops the leftmost element of the queue, since Playlist is
        intended to be a FIFO queue.
        """
        return self.popleft()

    def is_empty(self) -> bool:
        """Checks whether the playlist is empty."""
        return self.__len__() == 0

    def skip(self, num_songs: int) -> List[Union[Any, None]]:
        """Skips ahead by a number of songs."""
        if num_songs < 0:
            raise ValueError('Number of songs to skip must be positive.')

        # Create a list of skipped songs so we can add them to our song
        # history
        skipped_songs = []
        for _ in range(num_songs):
            skipped_songs.append(self.get_song())
        return skipped_songs

    def skip_to(self, song_name: str) -> List[Union[Any, None]]:
        """Skips to a song by name."""
        if self.is_empty():
            raise ValueError('Cannot search an empty queue.')

        found_index = self.search_playlist(song_name)
        if found_index is not None:
            return self.skip(found_index)
        else:
            raise Exception("Couldn't find the song in the queue.")

    def search_playlist(self, song_name: str) -> List[Union[Any, None]]:
        """Finds the index (indexed from 0) of a song in the playlist."""
        if self.is_empty():
            raise ValueError('Cannot search an empty queue.')

        # Minimum required subsequence--if none of our songs match at least
        # as good as this, we assume it's not in the playlist
        min_len = len(song_name) * 0.75

        # Make sure we yell the song name so the lcs function knows
        # exactly what we're talking about
        song_search = song_name.upper()

        # Needs to be < 0 so self.skip raises an error if nothing is found
        best_match_index = None

        # Finds index of most similar song
        longest_subseq = 0
        for index, song in enumerate(self):
            subseq_len = lcs(song.upper(), song_search)
            if subseq_len >= min_len and longest_subseq < subseq_len:
                longest_subseq = subseq_len
                best_match_index = index

        return best_match_index
