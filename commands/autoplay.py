import discord
from discord import app_commands
from discord.ext import commands
from music.player import autoplay_guilds

class AutoPlay(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="autoplay", description="Toggle smart autoplay")
    async def autoplay(self, interaction: discord.Interaction):

        guild_id = interaction.guild.id

        if guild_id in autoplay_guilds:
            autoplay_guilds.remove(guild_id)
            return await interaction.response.send_message(
                "❌ **Autoplay disabled**",
                ephemeral=True
            )

        autoplay_guilds.add(guild_id)
        await interaction.response.send_message(
            "✅ **Autoplay enabled**\nBot akan memutar lagu mirip & relevan 🔥",
            ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(AutoPlay(bot))
