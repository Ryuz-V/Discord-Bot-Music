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

## FAQ
<details>
  <summary><b>Q: The bot works, but why do some specific songs instantly skip or produce no sound?</b></summary>
  <br>
  <b>A:</b> If Song A plays perfectly but Song B immediately stops or skips to the next track, it means YouTube blocked the bot from reading that specific video. This usually happens because of:
  <ul>
    <li><b>Age-Restricted Content:</b> YouTube prevents bots from accessing explicit or age-restricted videos without an active login.</li>
    <li><b>Geo-Blocking:</b> The song might be blocked in the region where your bot is hosted.</li>
    <li><b>Anti-Bot Measures:</b> YouTube aggressively blocks automated downloads on highly popular official music videos.</li>
  </ul>
  <b>How to fix it:</b> You need to provide a valid <code>cookies.txt</code> file so YouTube thinks your bot is a real user. Please refer to the <b>YouTube Age-Restriction & Blocking Fix</b> section above to set it up!
</details>

<details>
  <summary><b>Q: Why are there empty buttons or missing icons in the bot interface?</b></summary>
  <br>
  <b>A:</b> This happens due to technical limitations with using custom icons/emojis, requiring a temporary fallback to standard Discord emojis or dummy icons. A few buttons and embeds were overlooked during the transition and will be patched in upcoming updates!
</details>

<details>
  <summary><b>Q: The bot is online/connected, but why is it still not working or playing audio?</b></summary>
  <br>
  <b>A:</b> If the bot successfully connects to Discord but fails to process commands or output audio, please check the following:
  <ul>
    <li><b>Voice Channel Permissions:</b> Make sure the bot has <b>Connect</b> and <b>Speak</b> permissions in the specific voice channel.</li>
    <li><b>FFmpeg Installation:</b> Verify that FFmpeg is installed on your system and registered in your system's <code>PATH</code>.</li>
    <li><b>Discord Intents:</b> Ensure <b>Message Content Intent</b> is switched ON in the Discord Developer Portal.</li>
    <li><b>Stream Interruption:</b> YouTube might be blocking audio streams on unauthenticated requests. Double-check your <code>yt-dlp</code> version and <code>cookies.txt</code> configuration.</li>
  </ul>
</details>

<details>
  <summary><b>Q: Why is the music stuttering, lagging, or sounding robotic?</b></summary>
  <br>
  <b>A:</b> This usually happens due to network latency or resource limits on the host machine. Try these fixes:
  <ul>
    <li><b>FFmpeg Options:</b> Ensure you are using <code>-vn</code> in your FFmpeg options to completely ignore video processing, saving CPU power.</li>
    <li><b>Host Performance:</b> If you are hosting the bot on a free tier service or in the local computer, CPU spikes will cause audio stuttering.</li>
    <li><b>Voice Region:</b> Try changing the Discord server's voice region to a closer one.</li>
  </ul>
</details>

<details>
  <summary><b>Q: Why does it take a very long time for the bot to start playing a song or radio?</b></summary>
  <br>
  <b>A:</b> There are two common reasons for this delay:
  <ul>
    <li><b>Playlist Processing:</b> If you provided a link that contains a playlist, the extractor might be trying to process the entire playlist metadata before playing the first track. Ensure you use a direct video link, or verify that <code>'noplaylist': True</code> is set in your <code>YTDL_OPTIONS</code>.</li>
    <li><b>Network Latency:</b> A slow internet connection on the local computer the bot can cause significant delays. This is especially true when fetching live radio streams or large audio files, as the bot needs time to buffer the data before it can start playing.</li>
  </ul>
</details>



## License

This project is licensed under the MIT License - [LICENSE.md](https://github.com/Ryuz-V/Discord-Bot-Music/blob/main/LICENSE) see the  file for details

``` bash
Scribble: 
I plan to create a music bot using this file. 
There will be a few additional commands, or perhaps some fixes and other updates. 
You can visit the link I’ll include in this Readme later please stay tuned.
```
