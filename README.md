# andybot

A Discord music bot to use for my friends if a bunch of bots get C&D'd again.

## Commands

All command aliases are subject to change. And I'm too lazy to frequently
update this README, so it may not accurately reflect the commands.

### Music

```
>>[play|add|p|+] <url>
Attempts to play the given URL. Currently does not support any other arguments.

>>[toggle|pause|resume] 
Pauses or resumes the current song.

>>[skip|next||] [num_songs=1]
Skips ahead by a certain number of songs. Default is the next song.

>>[search|skipto|?|goto] <song_search>
Skips ahead to a song by name. Immediately skips to best match.

>>[stop|leave|die|begone|farethewell] 
Attempts to play the given URL.

>>[volume|v|vol] <vol>
Sets the volume. Accepts any value between 0 and 200.

>>[queue|songs|q] 
Lists the current songs in the queue.

>>[history|h] 
Lists the song history.
```

### Meta

```
>>uptime
Sends the uptime of the bot in days, hours, minutes, and seconds.

>>[temperature|temp]
Sends the temperature of the bot.
```

## Dev stuff

### Dependencies

All Python dependencies are listed in requirements.txt, but there are some
external dependencies for the bot to run:

- ffmpeg
- opus-tools
- yt-dlp

It's probably a huge pain in the ass to install yt-dlp on Windows, but I know
they're all very easy to install on Linux with any package manager.
