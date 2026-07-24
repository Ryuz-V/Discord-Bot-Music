import discord
from discord import app_commands
from discord.ext import commands
from music.player import autoplay_guilds

class AutoPlay(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="autoplay", description="Toggle Autoplay")
    async def autoplay(self, interaction: discord.Interaction):

        guild_id = interaction.guild.id

        if guild_id in autoplay_guilds:
            autoplay_guilds.remove(guild_id)
            # You can add custom emojis here, for example: description="<:emoji_name:id> **Text**"
            embed = discord.Embed(description="**Autoplay disabled**")
            return await interaction.response.send_message(embed=embed)

        autoplay_guilds.add(guild_id)
        # You can add custom emojis here, for example: description="<:emoji_name:id> **Text**"
        embed = discord.Embed(description="**Autoplay enabled**")
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(AutoPlay(bot))
