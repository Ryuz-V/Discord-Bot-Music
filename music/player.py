import discord
import yt_dlp
import asyncio
import random
from collections import deque
from music.controls import MusicControl

queue = deque()
history = deque(maxlen=20)

idle_tasks = {}
always_on_guilds = set()
autoplay_guilds = set()
text_channels = {}
now_playing_messages = {}

YDL_OPTIONS = {
    "format": "bestaudio/best",
    "quiet": True,
    "noplaylist": True,
    "default_search": "ytsearch",
    "extractor_args": {"youtube": ["player_client=ios,android,web", "player_skip=webpage"]},
}

FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn",
}

async def start_idle_timer(vc: discord.VoiceClient, channel: discord.TextChannel = None):
    guild = vc.guild
    guild_id = guild.id

    if channel:
        text_channels[guild_id] = channel

    if guild_id in idle_tasks:
        return

    async def idle_check():
        await asyncio.sleep(180)

        if vc and not vc.is_playing() and guild_id not in always_on_guilds:
            await vc.disconnect()
            print(f"🔌 Disconnected from {guild.name}")

            send_channel = text_channels.get(guild_id) or guild.system_channel
            if not send_channel:
                for c in guild.text_channels:
                    if c.permissions_for(guild.me).send_messages:
                        send_channel = c
                        break

            if send_channel:
                embed = discord.Embed(
                    description="""No tracks have been playing for the past 3 minutes, leaving 👋

                    You can make bot stay in voice by using the command 24/7, for more information check out the perks command!"""
                )
                try:
                    await send_channel.send(embed=embed)
                except discord.Forbidden:
                    pass

        idle_tasks.pop(guild_id, None)

    idle_tasks[guild_id] = asyncio.create_task(idle_check())

def cancel_idle_timer(vc: discord.VoiceClient):
    task = idle_tasks.pop(vc.guild.id, None)
    if task:
        task.cancel()

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

async def play_next(
    bot: discord.Client,
    vc: discord.VoiceClient,
    channel: discord.TextChannel,
):
    cancel_idle_timer(vc)

    if not queue:
        await start_idle_timer(vc, channel=channel)
        
        msg = now_playing_messages.pop(vc.guild.id, None)
        if msg:
            embed = discord.Embed(
                title="Queue Ended!",
                description="All songs have been played! You can add songs again\nusing `/play` command.\nCheckout our [premium plans](https://discord.gg/) for best music experience!",
                color=0x2b2d31
            )
            embed.set_author(name=f"{bot.user.display_name} ✨", icon_url=bot.user.display_avatar.url if bot.user.display_avatar else None)
            
            view = discord.ui.View()
            view.add_item(discord.ui.Button(label="Vote Now", url="https://top.gg/", emoji="🔗"))
            view.add_item(discord.ui.Button(label="Premium", url="https://patreon.com/"))
            
            try:
                await msg.edit(embed=embed, view=view)
            except Exception as e:
                print(f"Error editing queue ended message: {e}")

        return

    song = queue.popleft()
    history.append(song)
    requester = song.get("requester")

    def extract_stream():
        try:
            with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
                query = song.get("search_query") or song["url"]
                if song.get("source") == "spotify" and not query.startswith("ytsearch"):
                    query = f"ytsearch1:{query}"
                    
                info = ydl.extract_info(query, download=False)
                if not info:
                    return None
                if "entries" in info:
                    if not info["entries"]:
                        return None
                    info = info["entries"][0]
                return info
        except Exception:
            return None

    loop = bot.loop
    info = await loop.run_in_executor(None, extract_stream)
    
    if not info or "url" not in info:
        embed = discord.Embed(
            # You can add custom emojis here, for example: description="<:emoji_name:id> **Text**"
            description=f"**Playback Error**\n\nFailed to play **{song.get('title', 'Unknown')}**. Stream not found. Skipping..."
        )
        try:
            await channel.send(embed=embed)
        except:
            pass
        asyncio.run_coroutine_threadsafe(play_next(bot, vc, channel), bot.loop)
        return
        
    source = info["url"]

    if "webpage_url" in info:
        song["url"] = info["webpage_url"]

    def after_playing(error):
        if error:
            print(f"Player error: {error}")

        if not vc or not vc.is_connected():
            return

        guild_id = vc.guild.id

        is_skip = getattr(vc, 'skip_request', False)
        is_prev = getattr(vc, 'is_previous_action', False)
        is_stop = getattr(vc, 'stop_request', False)

        # Reset flags
        if hasattr(vc, 'skip_request'): del vc.skip_request
        if hasattr(vc, 'is_previous_action'): del vc.is_previous_action
        if hasattr(vc, 'stop_request'): del vc.stop_request

        if is_stop:
            return

        if getattr(bot, "looping", False) and not is_skip and not is_prev:
            queue.appendleft(song)

        elif guild_id in autoplay_guilds and not queue and not is_prev:
            try:
                import re
                
                def fallback_autoplay():
                    query = build_autoplay_query(song)
                    with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
                        res = ydl.extract_info(f"ytsearch5:{query} related music", download=False)
                        return res.get("entries", [])

                url = song.get("url", "")
                video_id = None
                match = re.search(r"(?:v=|/)([0-9A-Za-z_-]{11}).*", url)
                if match:
                    video_id = match.group(1)

                entries = []
                if video_id:
                    mix_url = f"https://www.youtube.com/watch?v={video_id}&list=RD{video_id}"
                    opts = YDL_OPTIONS.copy()
                    opts["extract_flat"] = True
                    opts["playlist_end"] = 15
                    opts["noplaylist"] = False
                    
                    with yt_dlp.YoutubeDL(opts) as ydl:
                        info = ydl.extract_info(mix_url, download=False)
                        entries = [e for e in info.get("entries", []) if e.get("id") != video_id and e.get("title")]
                
                if not entries:
                    entries = fallback_autoplay()
                    
                if entries:
                    picked = random.choice(entries[:5])
                    
                    thumb = None
                    if picked.get("thumbnail"):
                        thumb = picked.get("thumbnail")
                    elif picked.get("thumbnails") and len(picked["thumbnails"]) > 0:
                        thumb = picked["thumbnails"][0]["url"]
                        
                    queue.append({
                        "title": picked.get("title"),
                        "author": picked.get("uploader") or picked.get("channel") or "Unknown",
                        "url": picked.get("url") or picked.get("webpage_url"),
                        "duration": picked.get("duration"),
                        "thumbnail": thumb,
                        "requester": None,
                        "source": "youtube",
                    })
                else:
                    print("Autoplay failed: No entries found")
            except Exception as e:
                print(f"Autoplay error: {e}")

        asyncio.run_coroutine_threadsafe(
            play_next(bot, vc, channel),
            bot.loop,
        )

    audio_source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(source, **FFMPEG_OPTIONS))
    audio_source.volume = getattr(vc, 'current_volume', 1.0)

    vc.play(
        audio_source,
        after=after_playing,
    )

    embed_title = "<a:vinyl:1468959873969426629> RADIO PANEL" if song.get("source") == "radio" else "<a:vinyl:1468959873969426629> MUSIC PANEL"
    embed = discord.Embed(
        title=embed_title,
        description=f"**{song['title']}**",
    )

    if song.get("thumbnail"):
        embed.set_thumbnail(url=song["thumbnail"])

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
        value=song.get("author") or info.get("uploader", "Unknown"),
        inline=True,
    )

    from music.controls import MusicControl, RadioControl
    view = RadioControl(vc) if song.get("source") == "radio" else MusicControl(vc)
    existing_msg = now_playing_messages.get(vc.guild.id)
    
    if existing_msg:
        try:
            await existing_msg.edit(embed=embed, view=view)
        except Exception:
            msg = await channel.send(embed=embed, view=view)
            now_playing_messages[vc.guild.id] = msg
    else:
        msg = await channel.send(embed=embed, view=view)
        now_playing_messages[vc.guild.id] = msg
