import discord
import aiohttp
import urllib.parse
import re

async def fetch_lyrics(title, artist=""):
    clean_title = re.sub(r'\(.*?\)|\[.*?\]', '', title)
    clean_title = re.sub(r'(?i)(official|music video|lyric video|audio|video)', '', clean_title)
    clean_title = " ".join(clean_title.split())
    if not clean_title:
        clean_title = title

    clean_artist = ""
    if artist and artist != "Unknown":
        clean_artist = re.sub(r'(?i)(official|vevo|topic|- topic)', '', artist)
        clean_artist = " ".join(clean_artist.split())

    search_query = f"{clean_title} {clean_artist}".strip()
    query = urllib.parse.quote(search_query)
    url = f"https://lrclib.net/api/search?q={query}"
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers={'User-Agent': 'Mozilla/5.0'}) as response:
                if response.status == 200:
                    data = await response.json()
                    if data:
                        return data[0].get("syncedLyrics") or data[0].get("plainLyrics")
        except Exception as e:
            print(f"Error fetching lyrics: {e}")
            pass
    return None

async def setup(bot):
    @bot.tree.command(
        name="lyric",
        description="Displaying The Lyrics Of The Currently Playing Music"
    )
    async def lyric(interaction: discord.Interaction):
        from music.player import history
        
        vc = interaction.guild.voice_client
        if not vc or not (vc.is_playing() or vc.is_paused()):
            embed = discord.Embed(
                description="<:Silang:1469196939072372952> **No music is playing**",
                color=0x2b2d31
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
            
        if len(history) == 0:
            embed = discord.Embed(
                description="<:Silang:1469196939072372952> **No song in history to fetch lyrics for.**",
                color=0x2b2d31
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        current_song = history[-1]
        title = current_song.get("title", "Unknown")
        artist = current_song.get("author", "")
        
        await interaction.response.defer(ephemeral=False)
        
        lyrics = await fetch_lyrics(title, artist)
        
        if not lyrics:
            embed = discord.Embed(
                description=f"<:Silang:1469196939072372952> Lirik untuk **{title}** tidak ditemukan.",
                color=0x2b2d31
            )
            return await interaction.followup.send(embed=embed)
        if len(lyrics) > 4000:
            lyrics = lyrics[:3997] + "..."
            
        embed = discord.Embed(
            title=f"<:lirik:1506193967316996166> Lyrics: {title}",
            description=lyrics,
            color=0x2b2d31
        )
        
        thumbnail = current_song.get("thumbnail")
        if thumbnail:
            embed.set_thumbnail(url=thumbnail)
            
        await interaction.followup.send(embed=embed)
