import discord
from discord import app_commands
from discord.ext import commands
import aiohttp

class RadioView(discord.ui.View):
    def __init__(self, interaction: discord.Interaction, is_change: bool = False):
        super().__init__(timeout=180)
        self.interaction = interaction
        self.is_change = is_change
        self.current_page = 0
        self.stations = []
        self.total_pages = 1
        self.limit = 10

    async def fetch_stations(self):
        url = "https://de1.api.radio-browser.info/json/stations/search"
        params = {
            "limit": 500,
            "order": "clickcount",
            "reverse": "true",
            "hidebroken": "true"
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, headers={'User-Agent': 'Jukebox Bot'}) as response:
                if response.status == 200:
                    self.stations = await response.json()
                    self.total_pages = max(1, (len(self.stations) + self.limit - 1) // self.limit)

    def generate_embed(self):
        start_idx = self.current_page * self.limit
        end_idx = start_idx + self.limit
        page_stations = self.stations[start_idx:end_idx]

        description = f"Page **{self.current_page + 1}/{self.total_pages}**\n\n"
        
        for i, station in enumerate(page_stations, 1):
            name = station.get("name", "Unknown").strip()
            state = station.get("state", "").strip()
            country = station.get("country", "").strip()
            
            parts = []
            if state:
                parts.append(state)
            if country:
                parts.append(country)
                
            location = ", ".join(parts)
            
            if location:
                description += f"{i}. {name}, {location}\n"
            else:
                description += f"{i}. {name}\n"

        if not page_stations:
            description += "No stations found.\n"

        description += "\nnext page | previous page | go to page <page> | cancel"

        embed = discord.Embed(
            description=description,
            color=0x2b2d31
        )
        return embed

    def update_components(self):
        self.clear_items()
        
        start_idx = self.current_page * self.limit
        end_idx = start_idx + self.limit
        page_stations = self.stations[start_idx:end_idx]
        
        if page_stations:
            options = []
            for i, station in enumerate(page_stations, 1):
                name = station.get("name", "Unknown").strip()[:90]
                options.append(discord.SelectOption(label=f"{i}. {name}", value=str(start_idx + i - 1)))
            
            select = discord.ui.Select(placeholder="Make a selection", options=options, row=0)
            select.callback = self.select_callback
            self.add_item(select)
            
        btn_first = discord.ui.Button(label="<<", style=discord.ButtonStyle.secondary, disabled=self.current_page == 0, row=1)
        btn_prev = discord.ui.Button(emoji="⏮️", style=discord.ButtonStyle.secondary, disabled=self.current_page == 0, row=1)
        btn_next = discord.ui.Button(emoji="⏭️", style=discord.ButtonStyle.secondary, disabled=self.current_page >= self.total_pages - 1, row=1)
        btn_last = discord.ui.Button(label=">>", style=discord.ButtonStyle.secondary, disabled=self.current_page >= self.total_pages - 1, row=1)
        
        btn_first.callback = self.first_page
        btn_prev.callback = self.prev_page
        btn_next.callback = self.next_page
        btn_last.callback = self.last_page
        
        self.add_item(btn_first)
        self.add_item(btn_prev)
        self.add_item(btn_next)
        self.add_item(btn_last)

    async def first_page(self, interaction: discord.Interaction):
        self.current_page = 0
        self.update_components()
        await interaction.response.edit_message(embed=self.generate_embed(), view=self)

    async def prev_page(self, interaction: discord.Interaction):
        if self.current_page > 0:
            self.current_page -= 1
        self.update_components()
        await interaction.response.edit_message(embed=self.generate_embed(), view=self)

    async def next_page(self, interaction: discord.Interaction):
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
        self.update_components()
        await interaction.response.edit_message(embed=self.generate_embed(), view=self)

    async def last_page(self, interaction: discord.Interaction):
        self.current_page = self.total_pages - 1
        self.update_components()
        await interaction.response.edit_message(embed=self.generate_embed(), view=self)

    async def select_callback(self, interaction: discord.Interaction):
        if not interaction.user.voice:
            embed = discord.Embed(description="❌ **You must be in a voice channel**", color=0x2b2d31)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
            
        user_channel = interaction.user.voice.channel
        vc = interaction.guild.voice_client

        if vc and vc.channel != user_channel:
            embed = discord.Embed(
                description=f"❌ **Bot is already in another voice channel**\n\nI'm currently in **{vc.channel.name}**",
                color=0x2b2d31
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        await interaction.response.defer()
        for item in self.children:
            item.disabled = True
        try:
            await interaction.edit_original_response(view=self)
        except Exception:
            pass

        idx = int(interaction.data["values"][0])
        station = self.stations[idx]
        
        url = station.get("url_resolved") or station.get("url")
        name = station.get("name", "Radio").strip()
        
        if not vc:
            try:
                vc = await user_channel.connect(self_deaf=True)
            except TimeoutError:
                embed = discord.Embed(
                    description="❌ **Connection Timed Out**\n\nFailed to connect to the voice channel. Discord's voice servers might be slow or blocking UDP traffic.",
                    color=0x2b2d31
                )
                return await interaction.followup.send(embed=embed, ephemeral=True)
            except Exception as e:
                embed = discord.Embed(
                    description=f"❌ **Failed to Connect**\n\nAn error occurred: `{str(e)}`",
                    color=0x2b2d31
                )
                return await interaction.followup.send(embed=embed, ephemeral=True)
            
        from music.player import queue, play_next
        
        song = {
            "title": name,
            "author": "Radio Station",
            "duration": 0,
            "url": url,
            "thumbnail": station.get("favicon", ""),
            "source": "radio",
            "requester": interaction.user
        }
        
        try:
            await interaction.delete_original_response()
        except Exception:
            pass

        if self.is_change:
            queue.clear()
            queue.append(song)
            if vc.is_playing() or vc.is_paused():
                vc.skip_request = True
                vc.stop()
            else:
                await play_next(interaction.client, vc, interaction.channel)
        else:
            queue.append(song)
            if not vc.is_playing() and not vc.is_paused():
                await play_next(interaction.client, vc, interaction.channel)


class Radio(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @app_commands.command(name="radio", description="Play Internet Radio Stations Cross The World")
    async def radio(self, interaction: discord.Interaction):
        await interaction.response.defer()
        view = RadioView(interaction)
        await view.fetch_stations()
        
        if not view.stations:
            embed = discord.Embed(
                description="❌ **No radio stations found.**",
                color=0x2b2d31
            )
            return await interaction.followup.send(embed=embed)
            
        view.update_components()
        await interaction.followup.send(embed=view.generate_embed(), view=view)
async def setup(bot):
    await bot.add_cog(Radio(bot))