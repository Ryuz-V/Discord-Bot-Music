import discord
from discord import app_commands
from discord.ext import commands
import yt_dlp
import asyncio
from music.spotify import is_spotify_url, get_spotify_query
from music.player import queue, play_next


def get_song_info(query: str):
    ydl_opts = {
        "format": "bestaudio/best",
        "quiet": True,
        "noplaylist": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:

        # 🔗 SoundCloud link → langsung extract
        if is_soundcloud_url(query):
            info = ydl.extract_info(query, download=False)

        # 🔗 YouTube link → langsung extract
        elif is_youtube_url(query):
            info = ydl.extract_info(query, download=False)

        # 🔍 BUKAN LINK → YouTube search ONLY
        else:
            info = ydl.extract_info(
                f"ytsearch1:{query}",
                download=False
            )["entries"][0]

        if "entries" in info:
            info = info["entries"][0]

        return {
            "title": info["title"],
            "duration": info.get("duration", 0),
            "url": info["webpage_url"],
            "thumbnail": info.get("thumbnail"),
            "source": (
                "soundcloud" if is_soundcloud_url(query)
                else "youtube"
            )
        }


def format_duration(seconds): 
    if not seconds: return "0:00" 
    seconds = int(seconds) 
    m, s = divmod(seconds, 60) 
    return f"{m}:{s:02d}"


class Play(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="play", description="Play a song")
    async def play(self, interaction: discord.Interaction, query: str):

        # ==============================
        # 🔒 USER HARUS DI VOICE
        # ==============================
        if not interaction.user.voice:
            embed = discord.Embed(
                title="<:Silang:1469196939072372952> You must be in a voice channel",
            )
            return await interaction.response.send_message(
                embed=embed,
                ephemeral=True
            )

        user_channel = interaction.user.voice.channel
        vc = interaction.guild.voice_client

        # ==============================
        # 🔒 BOT SUDAH DI VC LAIN?
        # ==============================
        if vc and vc.channel != user_channel:
            embed = discord.Embed(
                title="<:Silang:1469196939072372952> Bot is already in another voice channel",
                description=f"I'm currently in **{vc.channel.name}**",
            )
            return await interaction.response.send_message(
                embed=embed,
                ephemeral=True
            )

        await interaction.response.defer(thinking=True)

        # ==============================
        # 🔌 CONNECT JIKA BELUM CONNECT
        # ==============================
        if not vc:
            vc = await user_channel.connect(self_deaf=True)

        # ==============================
        # 🔎 SEARCH SONG (ASYNC SAFE)
        # ==============================
        loop = asyncio.get_running_loop()
        if is_spotify_url(query):
            query = await loop.run_in_executor(None, get_spotify_query, query)

        song = await loop.run_in_executor(None, get_song_info, query)

        queue.append({
            **song,
            "requester": interaction.user
        })

        # ==============================
        # 🎵 EMBED QUEUE MESSAGE
        # ==============================
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

        # ==============================
        # ▶️ AUTO PLAY JIKA TIDAK SEDANG PLAY
        # ==============================
        if not vc.is_playing() and not vc.is_paused():
            await play_next(self.bot, vc, interaction.channel)

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


async def setup(bot):
    await bot.add_cog(Play(bot))

