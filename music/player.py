# music/player.py
import discord
import yt_dlp
import asyncio
from collections import deque
from music.controls import MusicControl

queue = deque()
history = deque(maxlen=20)  # simpan 20 lagu terakhir 

idle_tasks = {}

always_on_guilds = set()

YDL_OPTIONS = {
    "format": "bestaudio/best",
    "quiet": True,
    "noplaylist": True,
}

FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn"
}

# ==============================
# ⏳ START IDLE TIMER (3 MENIT)
# ==============================
async def start_idle_timer(vc: discord.VoiceClient):
    guild = vc.guild
    guild_id = guild.id

    if guild_id in idle_tasks:
        return

    async def idle_check():
        await asyncio.sleep(180)

        if vc and not vc.is_playing() and guild_id not in always_on_guilds:

            # 🔌 DISCONNECT
            await vc.disconnect()
            print(f"🔌 Disconnected from {guild.name}")

            channel = guild.system_channel
            if channel:
                embed = discord.Embed(
                    title="<:door8:1469763739271168303> Bot Has Leave The Channel",
                    description="Use /247 to make bot stay in the channel"
                )
                await channel.send(embed=embed)

        idle_tasks.pop(guild_id, None)

    idle_tasks[guild_id] = asyncio.create_task(idle_check())

# ==============================
# ❌ CANCEL IDLE TIMER
# ==============================
def cancel_idle_timer(vc: discord.VoiceClient):
    task = idle_tasks.pop(vc.guild.id, None)
    if task:
        task.cancel()


# ==============================
# ▶️ PLAY NEXT
# ==============================
async def play_next(
    bot: discord.Client,
    vc: discord.VoiceClient,
    channel: discord.TextChannel
):
    cancel_idle_timer(vc)

    if not queue:
        await start_idle_timer(vc)
        return

    song = queue.popleft()
    history.append(song)
    requester: discord.Member | None = song.get("requester")

    with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
        info = ydl.extract_info(song["url"], download=False)
        if "entries" in info:
            info = info["entries"][0]

    source = info["url"]

    # ==============================
    # 🎵 AFTER PLAYING (LOOP FIX)
    # ==============================
    def after_playing(error):
        if error:
            print(f"Player error: {error}")

        if getattr(bot, "looping", False):
            queue.appendleft(song)

        asyncio.run_coroutine_threadsafe(
            play_next(bot, vc, channel),
            bot.loop
        )

    vc.play(
        discord.FFmpegPCMAudio(source, **FFMPEG_OPTIONS),
        after=after_playing
    )

    embed = discord.Embed(
        title="<a:vinyl:1468959873969426629> ᴍᴜꜱɪᴄ ᴘᴀɴᴇʟ",
        description=f"**{song['title']}**"
    )

    embed.add_field(
        name="Requested By",
        value=requester.mention if requester else "Unknown",
        inline=True
    )

    embed.add_field(
        name="Music Duration",
        value=f"**{song.get('duration', 'Unknown')} sec**",
        inline=True
    )

    embed.add_field(
        name="Music Author",
        value=f"**{info.get('uploader', 'Unknown')}**",
        inline=True
    )

    view = MusicControl(vc)
    await channel.send(embed=embed, view=view)
