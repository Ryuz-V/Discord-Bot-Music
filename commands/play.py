import discord
from discord import app_commands
from discord.ext import commands
import yt_dlp
import asyncio

from music.spotify import is_spotify_url, get_spotify_info
from music.player import queue, play_next
def is_soundcloud_url(text: str) -> bool:
    return "soundcloud.com" in text

def is_youtube_url(text: str) -> bool:
    return "youtube.com" in text or "youtu.be" in text

def format_duration(seconds):
    if not seconds:
        return "0:00"

    seconds = int(seconds)
    m, s = divmod(seconds, 60)
    return f"{m}:{s:02d}"

def get_song_info(query: str):
    ydl_opts = {
        "format": "bestaudio/best",
        "quiet": True,
        "noplaylist": True,
        "extractor_args": {"youtube": ["player_client=ios,android,web", "player_skip=webpage"]},
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:

        try:
            if is_soundcloud_url(query):
                info = ydl.extract_info(query, download=False)
            elif is_youtube_url(query):
                info = ydl.extract_info(query, download=False)
            else:
                extract = ydl.extract_info(f"ytsearch1:{query}", download=False)
                if not extract or "entries" not in extract or not extract["entries"]:
                    return None
                info = extract["entries"][0]

            if not info:
                return None

            if "entries" in info:
                if not info["entries"]:
                    return None
                info = info["entries"][0]

            if "url" not in info:
                return None

            return {
                "title": info["title"],
                "author": info.get("uploader") or info.get("creator") or info.get("channel", "Unknown"),
                "duration": info.get("duration", 0),
                "url": info["webpage_url"],
                "thumbnail": info.get("thumbnail"),
                "source": "soundcloud" if is_soundcloud_url(query) else "youtube"
            }
        except Exception:
            return None

class Play(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="play", description="Play A Music")
    async def play(self, interaction: discord.Interaction, query: str):

        if not interaction.user.voice:
            embed = discord.Embed(
                # You can add custom emojis here, for example: description="<:emoji_name:id> **Text**"
                description="**You must be in a voice channel**",
            )
            return await interaction.response.send_message(
                embed=embed
            )

        user_channel = interaction.user.voice.channel
        vc = interaction.guild.voice_client

        if vc and vc.channel != user_channel:
            embed = discord.Embed(
                # You can add custom emojis here, for example: description="<:emoji_name:id> **Text**"
                description=f"**Bot is already in another voice channel**\n\nI'm currently in **{vc.channel.name}**",
            )
            return await interaction.response.send_message(
                embed=embed
            )

        await interaction.response.defer(thinking=True)

        if not vc:
            try:
                vc = await user_channel.connect(self_deaf=True)
            except asyncio.TimeoutError:
                embed = discord.Embed(
                    # You can add custom emojis here, for example: description="<:emoji_name:id> **Text**"
                    description="**Connection Timed Out**\n\nFailed to connect to the voice channel. Discord's voice servers might be slow or blocking UDP traffic."
                )
                return await interaction.followup.send(embed=embed)
            except Exception as e:
                embed = discord.Embed(
                    # You can add custom emojis here, for example: description="<:emoji_name:id> **Text**"
                    description=f"**Failed to Connect**\n\nAn error occurred: `{str(e)}`"
                )
                return await interaction.followup.send(embed=embed)

        loop = asyncio.get_running_loop()

        if is_spotify_url(query):
            try:
                spotify_metadata = await loop.run_in_executor(None, get_spotify_info, query)
                if spotify_metadata:
                    song = await loop.run_in_executor(None, get_song_info, spotify_metadata["search_query"])
                    if song:
                        song["title"] = spotify_metadata["title"]
                        song["author"] = spotify_metadata["author"]
                        song["thumbnail"] = spotify_metadata["thumbnail"] or song.get("thumbnail")
                        song["source"] = "spotify"
                        song["search_query"] = spotify_metadata["search_query"]
                else:
                    song = None
            except Exception:
                song = None
                
            if not song:
                embed = discord.Embed(
                    # You can add custom emojis here, for example: description="<:emoji_name:id> **Text**"
                    description="**Failed to load Spotify link**\n\nMake sure it's a valid track link, and the song is available to stream."
                )
                return await interaction.followup.send(embed=embed)
        else:
            try:
                song = await loop.run_in_executor(None, get_song_info, query)
            except Exception:
                song = None
                
            if not song:
                embed = discord.Embed(
                    # You can add custom emojis here, for example: description="<:emoji_name:id> **Text**"
                    description=f"**Music Not Found**\n\nCould not find any music for `{query}`. Please try another keyword or link."
                )
                return await interaction.followup.send(embed=embed)

        queue.append({
            **song,
            "requester": interaction.user
        })

        embed = discord.Embed(
            description=f"**{song['title']}** `[{format_duration(song['duration'])}]`",
        )

        embed.set_author(
            name=f"Song Added To Queue (#{len(queue)})",
            icon_url=interaction.user.display_avatar.url
        )

        if song.get("thumbnail"):
            embed.set_thumbnail(url=song["thumbnail"])

        await interaction.followup.send(embed=embed)

        if not vc.is_playing() and not vc.is_paused():
            await play_next(self.bot, vc, interaction.channel)
async def setup(bot):
    await bot.add_cog(Play(bot))
