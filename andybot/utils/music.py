import pytz
import random
from collections import deque
from datetime import datetime
from typing import Any, Iterable, List, Union

import discord
import yt_dlp

from andybot.core import Andybot
from andybot.utils.fuzzy_string import lcs

YT_DLP_OPTS = {
    'default_search': 'ytsearch',
    'format': 'bestaudio/best',
    'extract_flat': 'in_playlist',
    'noplaylist': True,
}

KEYS_TO_SAVE = (
    'url',
    'title',
    'thumbnail',
    'duration',
    'webpage_url',
    'description',
)

QUALITIES = {
    'low': 1,
    'medium': 2,
    'high': 3,
}


class NoSongInfoError(Exception):
    """Raised when a song is downloaded but doesn't have any information."""


class NoSongFoundError(Exception):
    """Raised when a song queue search fails."""


class Song:
    """Base class for all songs."""


class YouTubeSong(Song):
    """yt-dlp helper class that downloads video information and stores it
    in class attributes for easy use.
    """

    def __init__(self, url: str, requester: discord.User = None) -> None:
        info = None
        with yt_dlp.YoutubeDL(YT_DLP_OPTS) as ydl:
            info = ydl.extract_info(url, download=False)
        if info is None:
            raise NoSongInfoError('The requested URL has no information.')
        for key in KEYS_TO_SAVE:
            setattr(self, key, info[key])
        self.requester = requester
        self._all_info = info

    # TODO: Implement more robust way of getting stream link. Mayve set to
    # info.get('url') in __init__ and have getter/setter that checks if it's
    # None and downloads if it is
    # @property
    # def url(self) -> str:
    #     pass

    def embed(self, next_song: Song) -> discord.Embed:
        """Creates an embed with information about the song and the next
        song in the queue.
        """
        now = datetime.now(pytz.utc)
        # Add requested by and timestamp
        embed = discord.Embed(
            title=self.title,
            url=self.url,
            timestamp=now
        ).set_author(
            name=self.requester,
            icon_url=self.requester.avatar_url
        ).set_image(
            url=self.thumbnail
        ).set_footer(
            text=f'Next song: {next_song.title if next_song else "none"}'
        )
        return Andybot.format_embed(embed)


class Playlist(deque):
    """A simple FIFO queue used for queueing songs. Has a max length of 100."""

    def __init__(self, iterable: Iterable = ()) -> None:
        self.song_history = []
        super(Playlist, self).__init__(iterable=iterable, maxlen=100)

    @property
    def next_song(self) -> Union[Any, None]:
        """Property that returns the next song if there is one, and None
        otherwise.
        """
        return self[0] if not self.is_empty() else None

    @property
    def history(self) -> str:
        """Property that returns the song history as a numbered list."""
        if self.song_history:
            return 'History:\n' + '\n'.join(
                song.title for song in reversed(self.song_history)
            )
        else:
            return 'No song history yet.'

    @property
    def song_list(self) -> str:
        """Property that returns the queue as a numbered list."""
        numbered_queue = []
        for i, song in enumerate(self):
            numbered_queue.append(f'{i + 1:03d}. {song.title}')
        if numbered_queue:
            return 'Current queue:\n' + '\n'.join(numbered_queue)
        else:
            return 'No songs in queue yet.'

    def is_empty(self) -> bool:
        """Checks whether the playlist is empty."""
        return self.__len__() == 0

    def add_song(self, song: Song) -> None:
        """Appends a song to the right of the Playlist, since Playlist is
        intended to be a FIFO queue.
        """
        if self.__len__() < self.maxlen:
            self.append(song)
        else:
            raise IndexError('Queue max length reached.')

    def add_songs(self, songs: Iterable) -> None:
        """Adds multiple songs to the right of the Playlist."""
        for song in songs:
            self.add_song(song)

    def get_song(self) -> Song:
        """Pops the leftmost element of the queue, since Playlist is
        intended to be a FIFO queue.
        """
        song = self.popleft()
        self.song_history.append(song)
        return song

    def del_song(self, song_name: str) -> None:
        """Deletes a song from the queue."""
        found_index = self.search_playlist(song_name)
        if found_index is not None:
            del self[found_index]
        else:
            raise NoSongFoundError(
                f'Could not find "{song_name}" in the queue.'
            )

    def skip(self, num_songs: int) -> None:
        """Skips ahead by a number of songs."""
        if num_songs < 0:
            raise ValueError('Number of songs to skip must be positive or 0.')

        for _ in range(num_songs):
            self.popleft()

    def skip_to(self, song_name: str) -> None:
        """Skips to a song by name."""
        found_index = self.search_playlist(song_name)
        if found_index is not None:
            return self.skip(found_index)
        else:
            raise NoSongFoundError(
                f'Could not find "{song_name}" in the queue.'
            )

    def search_playlist(self, song_name: str) -> Union[int, None]:
        """Finds the index (indexed from 0) of a song in the playlist."""
        return self.search_song_list(song_name, self)

    def search_history(self, song_name: str) -> Union[Song, None]:
        """Finds the index (indexed from 0) of a song in the playlist."""
        found_index = self.search_song_list(song_name, self.song_history)
        if found_index is not None:
            return self.song_history[found_index]
        else:
            raise NoSongFoundError(
                f'Could not find "{song_name}" in the queue.'
            )

    def search_song_list(self, song_name: str, song_list: Iterable[Song]
                         ) -> Union[int, None]:
        """Finds the index (indexed from 0) of a song in the playlist."""
        if len(song_list) == 0:
            raise IndexError('Cannot search an empty song list.')

        # Minimum required subsequence--if none of our songs match at least
        # as good as this, we assume it's not in the playlist
        min_len = len(song_name) * 0.8

        # Make sure we yell the song name so the lcs function knows
        # exactly what we're talking about
        song_search = song_name.upper()

        # Default is none for no match
        best_match_index = None

        # Finds index of most similar song
        longest_subseq = 0
        for index, song in enumerate(song_list):
            subseq_len = lcs(song.title.upper(), song_search)
            if subseq_len >= min_len and longest_subseq < subseq_len:
                longest_subseq = subseq_len
                best_match_index = index

        return best_match_index

    def shuffle(self) -> None:
        """Shuffles the playlist. Since Python implements a deque as a
        doubly-linked list, shuffling a deque itself is incredibly
        slow (in terms of computer time, at least--it still only takes like
        6 ms for a 1000-item deque lol) because they have O(n) random access
        time. However, this should really only become a problem with long
        queues, which this playlist won't allow.
        """
        random.shuffle(self)
