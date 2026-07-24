import discord
from discord import app_commands
from discord.ext import commands
import json
import os
import asyncio

from music.player import queue, play_next
from commands.play import get_song_info, format_duration, is_youtube_url, is_soundcloud_url
from music.spotify import is_spotify_url, get_spotify_info

PLAYLIST_FILE = "playlists.json"

def load_playlists():
    if os.path.exists(PLAYLIST_FILE):
        with open(PLAYLIST_FILE, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                migrated = False
                for uid, playlists in data.items():
                    for pname, pdata in playlists.items():
                        if isinstance(pdata, list):
                            playlists[pname] = {"thumbnail": None, "songs": pdata}
                            migrated = True
                if migrated:
                    save_playlists(data)
                return data
            except Exception:
                return {}
    return {}

def save_playlists(data):
    with open(PLAYLIST_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

class Playlist(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    playlist = app_commands.Group(name="playlist", description="Manage your music playlists")

    async def playlist_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        data = load_playlists()
        user_id = str(interaction.user.id)
        if user_id not in data:
            return []
        
        playlists = data[user_id].keys()
        return [
            app_commands.Choice(name=pl, value=pl)
            for pl in playlists if current.lower() in pl.lower()
        ][:25]

    @playlist.command(name="create", description="Create a new empty playlist.")
    async def create(self, interaction: discord.Interaction, name: str, thumbnail: str = None):
        data = load_playlists()
        user_id = str(interaction.user.id)
        
        if user_id not in data:
            data[user_id] = {}
        
        if name in data[user_id]:
            return await interaction.response.send_message(
                # You can add custom emojis here, for example: description="<:emoji_name:id> **Text**"
                embed=discord.Embed(description=f"**Playlist `{name}` already exists!**"),
                ephemeral=True
            )
            
        data[user_id][name] = {"thumbnail": thumbnail, "songs": []}
        save_playlists(data)
        
        # You can add custom emojis here, for example: description="<:emoji_name:id> **Text**"
        embed = discord.Embed(description=f"**Playlist `{name}` has been created successfully!**")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @playlist.command(name="add", description="Add a song to a playlist.")
    @app_commands.autocomplete(name=playlist_autocomplete)
    async def add(self, interaction: discord.Interaction, name: str, url: str):
        await interaction.response.defer(thinking=True, ephemeral=True)
        
        data = load_playlists()
        user_id = str(interaction.user.id)
        
        if user_id not in data or name not in data[user_id]:
            return await interaction.followup.send(
                # You can add custom emojis here, for example: description="<:emoji_name:id> **Text**"
                embed=discord.Embed(description=f"**Playlist `{name}` not found!**"),
                ephemeral=True
            )
            
        loop = asyncio.get_running_loop()
        
        if is_spotify_url(url):
            try:
                spotify_metadata = await loop.run_in_executor(None, get_spotify_info, url)
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
        else:
            try:
                song = await loop.run_in_executor(None, get_song_info, url)
            except Exception:
                song = None

        if not song:
            return await interaction.followup.send(
                # You can add custom emojis here, for example: description="<:emoji_name:id> **Text**"
                embed=discord.Embed(description=f"**Could not find any music for `{url}`.**"),
                ephemeral=True
            )
            
        data[user_id][name]["songs"].append(song)
        save_playlists(data)
        
        embed = discord.Embed(
            # You can add custom emojis here, for example: description="<:emoji_name:id> **Text**"
            description=f"**Added `{song['title']}` to playlist `{name}`!**"
        )
        if song.get("thumbnail"):
            embed.set_thumbnail(url=song["thumbnail"])
            
        await interaction.followup.send(embed=embed, ephemeral=True)

    @playlist.command(name="play", description="Play all songs from a playlist.")
    @app_commands.autocomplete(name=playlist_autocomplete)
    async def play_playlist(self, interaction: discord.Interaction, name: str):
        data = load_playlists()
        user_id = str(interaction.user.id)
        
        if user_id not in data or name not in data[user_id]:
            return await interaction.response.send_message(
                # You can add custom emojis here, for example: description="<:emoji_name:id> **Text**"
                embed=discord.Embed(description=f"**Playlist `{name}` not found!**"),
                ephemeral=True
            )
            
        playlist_data = data[user_id][name]
        songs = playlist_data["songs"]
        if not songs:
            return await interaction.response.send_message(
                # You can add custom emojis here, for example: description="<:emoji_name:id> **Text**"
                embed=discord.Embed(description=f"**Playlist `{name}` is empty!**"),
                ephemeral=True
            )

        if not interaction.user.voice:
            return await interaction.response.send_message(
                # You can add custom emojis here, for example: description="<:emoji_name:id> **Text**"
                embed=discord.Embed(description="**You must be in a voice channel**"),
                ephemeral=True
            )

        user_channel = interaction.user.voice.channel
        vc = interaction.guild.voice_client

        if vc and vc.channel != user_channel:
            return await interaction.response.send_message(
                # You can add custom emojis here, for example: description="<:emoji_name:id> **Text**"
                embed=discord.Embed(description=f"**Bot is already in another voice channel**\n\nI'm currently in **{vc.channel.name}**"),
                ephemeral=True
            )

        await interaction.response.defer(thinking=True)

        if not vc:
            try:
                vc = await user_channel.connect(self_deaf=True)
            except asyncio.TimeoutError:
                return await interaction.followup.send(
                    # You can add custom emojis here, for example: description="<:emoji_name:id> **Text**"
                    embed=discord.Embed(description="**Connection Timed Out**\n\nFailed to connect to the voice channel.")
                )
            except Exception as e:
                return await interaction.followup.send(
                    # You can add custom emojis here, for example: description="<:emoji_name:id> **Text**"
                    embed=discord.Embed(description=f"**Failed to Connect**\n\nAn error occurred: `{str(e)}`")
                )

        added_count = 0
        for song in songs:
            queue.append({
                **song,
                "requester": interaction.user
            })
            added_count += 1

        embed = discord.Embed(
            title=name.title(),
            color=0x7e2920
        )
        embed.set_author(name=f"Playlist by {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)
        
        if playlist_data.get("thumbnail"):
            embed.set_thumbnail(url=playlist_data["thumbnail"])
        elif songs and songs[0].get("thumbnail"):
            embed.set_thumbnail(url=songs[0]["thumbnail"])
            
        description = ""
        for i, song in enumerate(songs[:10], 1):
            dur = format_duration(song.get('duration', 0))
            description += f"`{i}` **{song['title']}**\n> {song.get('author', 'Unknown')} • `{dur}`\n\n"
            
        if len(songs) > 10:
            description += f"**... and {len(songs) - 10} more songs**"
            
        embed.description = description
        
        await interaction.followup.send(embed=embed)

        if not vc.is_playing() and not vc.is_paused():
            await play_next(self.bot, vc, interaction.channel)

    @playlist.command(name="list", description="List all your playlists.")
    async def list_playlists(self, interaction: discord.Interaction):
        data = load_playlists()
        user_id = str(interaction.user.id)
        
        if user_id not in data or not data[user_id]:
            return await interaction.response.send_message(
                # You can add custom emojis here, for example: description="<:emoji_name:id> **Text**"
                embed=discord.Embed(description="**You don't have any playlists yet!**"),
                ephemeral=True
            )

        # You can add custom emojis here, for example: description="<:emoji_name:id> **Text**"
        embed = discord.Embed(title=f"{interaction.user.display_name}'s Playlists")
        for pl_name, pl_data in data[user_id].items():
            embed.add_field(name=pl_name, value=f"{len(pl_data['songs'])} songs", inline=False)
            
        await interaction.response.send_message(embed=embed)

    @playlist.command(name="view", description="View songs in a playlist.")
    @app_commands.autocomplete(name=playlist_autocomplete)
    async def view(self, interaction: discord.Interaction, name: str):
        data = load_playlists()
        user_id = str(interaction.user.id)
        
        if user_id not in data or name not in data[user_id]:
            return await interaction.response.send_message(
                # You can add custom emojis here, for example: description="<:emoji_name:id> **Text**"
                embed=discord.Embed(description=f"**Playlist `{name}` not found!**"),
                ephemeral=True
            )
            
        playlist_data = data[user_id][name]
        songs = playlist_data["songs"]
        if not songs:
            return await interaction.response.send_message(
                # You can add custom emojis here, for example: description="<:emoji_name:id> **Text**"
                embed=discord.Embed(description=f"**Playlist `{name}` is empty!**")
            )

        embed = discord.Embed(
            title=name.title(),
            color=0x7e2920
        )
        embed.set_author(name=f"Playlist by {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)
        
        if playlist_data.get("thumbnail"):
            embed.set_thumbnail(url=playlist_data["thumbnail"])
        elif songs and songs[0].get("thumbnail"):
            embed.set_thumbnail(url=songs[0]["thumbnail"])
            
        description = f"**{len(songs)} songs** in this playlist\n\n"
        for i, song in enumerate(songs[:15], 1): # Show up to 15 in view
            dur = format_duration(song.get('duration', 0))
            description += f"`{i}` **{song['title']}**\n> {song.get('author', 'Unknown')} • `{dur}`\n\n"
            
        if len(songs) > 15:
            description += f"**... and {len(songs) - 15} more songs**"
            
        embed.description = description
        
        await interaction.response.send_message(embed=embed)

    @playlist.command(name="remove", description="Remove a specific song from a playlist.")
    @app_commands.autocomplete(name=playlist_autocomplete)
    async def remove(self, interaction: discord.Interaction, name: str, song_number: int):
        data = load_playlists()
        user_id = str(interaction.user.id)
        
        if user_id not in data or name not in data[user_id]:
            return await interaction.response.send_message(
                # You can add custom emojis here, for example: description="<:emoji_name:id> **Text**"
                embed=discord.Embed(description=f"**Playlist `{name}` not found!**"),
                ephemeral=True
            )
            
        songs = data[user_id][name]["songs"]
        if song_number < 1 or song_number > len(songs):
            return await interaction.response.send_message(
                # You can add custom emojis here, for example: description="<:emoji_name:id> **Text**"
                embed=discord.Embed(description=f"**Invalid song number! Use `/playlist view {name}` to see the numbers.**"),
                ephemeral=True
            )
            
        removed_song = songs.pop(song_number - 1)
        save_playlists(data)
        
        await interaction.response.send_message(
            # You can add custom emojis here, for example: description="<:emoji_name:id> **Text**"
            embed=discord.Embed(description=f"**Removed `{removed_song['title']}` from playlist `{name}`!**"),
            ephemeral=True
        )

    @playlist.command(name="delete", description="Delete an entire playlist.")
    @app_commands.autocomplete(name=playlist_autocomplete)
    async def delete(self, interaction: discord.Interaction, name: str):
        data = load_playlists()
        user_id = str(interaction.user.id)
        
        if user_id not in data or name not in data[user_id]:
            return await interaction.response.send_message(
                # You can add custom emojis here, for example: description="<:emoji_name:id> **Text**"
                embed=discord.Embed(description=f"**Playlist `{name}` not found!**"),
                ephemeral=True
            )
            
        del data[user_id][name]
        save_playlists(data)
        
        await interaction.response.send_message(
            # You can add custom emojis here, for example: description="<:emoji_name:id> **Text**"
            embed=discord.Embed(description=f"**Playlist `{name}` has been deleted!**"),
            ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(Playlist(bot))
