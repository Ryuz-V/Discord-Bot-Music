import discord
import yt_dlp
import asyncio
import random
from collections import deque
from music.controls import MusicControl

# ==============================
# GLOBAL STATE
# ==============================
queue = deque()
history = deque(maxlen=20)

idle_tasks = {}
always_on_guilds = set()
autoplay_guilds = set()

# ==============================
# YTDLP & FFMPEG OPTIONS
# ==============================
YDL_OPTIONS = {
    "format": "bestaudio/best",
    "quiet": True,
    "noplaylist": True,
    "default_search": "ytsearch",
    "source_address": "0.0.0.0",
}

FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn",
}

# ==============================
# ⏳ IDLE TIMER (3 MENIT)
# ==============================
async def start_idle_timer(vc: discord.VoiceClient):
    guild = vc.guild
    guild_id = guild.id

    if guild_id in idle_tasks:
        return

    async def idle_check():
        await asyncio.sleep(180)

        if vc and not vc.is_playing() and guild_id not in always_on_guilds:
            await vc.disconnect()
            print(f"🔌 Disconnected from {guild.name}")

            channel = guild.system_channel
            if channel:
                embed = discord.Embed(
                    title="🚪 Bot left the voice channel",
                    description="Use /247 to keep the bot in the channel",
                )
                await channel.send(embed=embed)

        idle_tasks.pop(guild_id, None)

    idle_tasks[guild_id] = asyncio.create_task(idle_check())

def cancel_idle_timer(vc: discord.VoiceClient):
    task = idle_tasks.pop(vc.guild.id, None)
    if task:
        task.cancel()

# ==============================
# 🤖 AUTOPLAY QUERY BUILDER
# ==============================
def build_autoplay_query(song: dict) -> str:
    title = song.get("title", "")
    artist = title.split("-")[0]

    keywords = [
        artist.strip(),
        "official audio",
        "topic",
        "music",
    ]

    return " ".join(keywords)

# ==============================
# ▶️ PLAY NEXT SONG
# ==============================
async def play_next(
    bot: discord.Client,
    vc: discord.VoiceClient,
    channel: discord.TextChannel,
):
    cancel_idle_timer(vc)

    # QUEUE HABIS
    if not queue:
        await start_idle_timer(vc)
        return

    song = queue.popleft()
    history.append(song)
    requester = song.get("requester")

    # AMBIL STREAM URL
    with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
        info = ydl.extract_info(song["url"], download=False)
        if "entries" in info:
            info = info["entries"][0]

    source = info["url"]

    # ==============================
    # AFTER PLAYING CALLBACK
    # ==============================
    def after_playing(error):
        if error:
            print(f"Player error: {error}")

        guild_id = vc.guild.id

        # 🔁 LOOP MODE
        if getattr(bot, "looping", False):
            queue.appendleft(song)

        # 🤖 AUTOPLAY MODE
        elif guild_id in autoplay_guilds and not queue:
            try:
                query = build_autoplay_query(song)

                with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
                    results = ydl.extract_info(
                        f"ytsearch5:{query}",
                        download=False,
                    )["entries"]

                picked = random.choice(results[:3])

                queue.append({
                    "title": picked["title"],
                    "url": picked["webpage_url"],
                    "duration": picked.get("duration"),
                    "thumbnail": picked.get("thumbnail"),
                    "requester": None,
                    "source": "youtube",
                })

            except Exception as e:
                print(f"Autoplay error: {e}")

        asyncio.run_coroutine_threadsafe(
            play_next(bot, vc, channel),
            bot.loop,
        )

    # ▶️ PLAY AUDIO
    vc.play(
        discord.FFmpegPCMAudio(source, **FFMPEG_OPTIONS),
        after=after_playing,
    )

    # ==============================
    # NOW PLAYING EMBED
    # ==============================
    embed = discord.Embed(
        title="🎶 MUSIC PANEL",
        description=f"**{song['title']}**",
    )

    embed.add_field(
        name="Requested By",
        value=requester.mention if requester else "Autoplay",
        inline=True,
    )

    embed.add_field(
        name="Duration",
        value=f"{song.get('duration', 'Unknown')} sec",
        inline=True,
    )

    embed.add_field(
        name="Author",
        value=info.get("uploader", "Unknown"),
        inline=True,
    )

    view = MusicControl(vc)
    await channel.send(embed=embed, view=view)
