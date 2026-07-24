# Discord Music Bot

Discord music bot written in Python 3.13.5+ and using several libraries such as discord.py, yt-dlp, FFmpeg, Wavelink / Lavalink and others. This bot supports several music platforms such as Spotify, YouTube, YouTube Music, and SoundCloud. 

## Table of content

- [Command List](#command-list)
- [Requirements](#requirements)
- [Getting started](#getting-started)
- [FAQ](#faq)
- [License](#license)

## Command List

| Command | File | Description |
| :--- | :--- | :--- |
| `/247` | `247.py` | Toggles 24/7 mode (keeps the bot in the voice channel indefinitely). |
| `/autoplay` | `autoplay.py` | Toggles autoplay mode to automatically play related songs. |
| `/connect` | `connect.py` | Connects the bot to your current voice channel. |
| `/help` | `help.py` | Displays the help menu and a list of all available commands. |
| `/leave` | `leave.py` | Disconnects the bot from the voice channel. |
| `/loop` | `loop.py` | Toggles loop for the current track or the entire queue. |
| `/lyric` | `lyric.py` | Fetches and displays the lyrics for the current or specified song. |
| `/pause` | `pause.py` | Pauses the currently playing track. |
| `/play` | `play.py` | Plays a song from a given name or URL. |
| `/previous` | `previous.py` | Plays the previous song in the queue history. |
| `/radio` | `radio.py` | Starts a continuous radio stream. |
| `/resume` | `resume.py` | Resumes a paused track. |
| `/skip` | `skip.py` | Skips the current track and plays the next one in the queue. |
| `/stop` | `stop.py` | Stops the music completely and clears the queue. |
| `/playlist create` | `playlist.py` | Create new empty playlist. |
| `/playlist delete` | `playlist.py` | Delete an entire playlist. |
| `/playlist list` | `playlist.py` | List all your playlist. |
| `/playlist play` | `playlist.py` | Play your playlist song. |
| `/playlist remove` | `playlist.py` | Remove your song in playlist. |
| `/playlist add` | `playlist.py` | Add your song to playlist. |
| `/playlist view` | `playlist.py` | View song in playlist. |

## Requirements

Make sure you have the following installed before running the bot:

| Requirement | Description |
| :--- | :--- | 
| [Python](https://www.python.org/downloads/) | The main programming language used to run this bot.|
| [discord.py](https://github.com/Rapptz/discord.py) | Main Discord API wrapper for Python. Used for slash commands, embeds, voice client, and all bot interactions. |
| [yt-dlp](https://github.com/yt-dlp/yt-dlp) | A powerful media downloader and extractor. Used to fetch audio streams from YouTube, YouTube Music, SoundCloud, and more. |
| [FFmpeg](https://ffmpeg.org/) | A multimedia framework used to process and stream audio to Discord voice channels. Must be installed separately and available in your system PATH. |

## Getting started

Before you begin, clone this repository and install all the tools on your local machine.

#### Installation
   ```bash
   # Clone the repository
   git clone https://github.com/Ryuz-V/Discord-Bot-Music.git

  # Enter into the directory
  cd Discord-Bot-Music

  #Install the dependencies
python -m pip install -r requirements.txt

  # Configure Discord Bot Token
  TOKEN="Insert_Your_Discord_Bot_Token_Here"
   ```

#### Required permissions
Make sure your bot has the `applications.commands` permission, which can be found under the OAuth2 tab on the [Developer Portal](https://discord.com/developers/home)

#### Configuration
After cloning the project and installing all dependencies, you need to add your Discord API token in the `config.py` file.

#### Starting the application
``` bash
python bot.py
```

## License

This project is licensed under the MIT License - [LICENSE.md](https://github.com/Ryuz-V/Discord-Bot-Music/blob/main/LICENSE) see the  file for details

``` bash
Scribble: 
I plan to create a music bot using this file. 
There will be a few additional commands, or perhaps some fixes and other updates. 
You can visit the link I’ll include in this Readme later—please stay tuned.
```