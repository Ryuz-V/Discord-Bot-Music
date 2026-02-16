# commands/pause.py
import discord
from discord.ext import commands
from discord import app_commands

class Pause(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="pause", description="Pause TheMusic")
    async def pause(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client

        if vc and vc.is_playing():
            vc.pause()

            embed = discord.Embed(
                description="<:pause8:1469637308012826716> **Music Paused**",
            )
            embed.set_footer(text="User /resume to resume the music")

            await interaction.response.send_message(embed=embed)

        else:
            embed = discord.Embed(
                description="<:Silang:1469196939072372952> **No Music Playing**",
            )

            await interaction.response.send_message(
                embed=embed,
                ephemeral=True
            )

async def setup(bot):
    await bot.add_cog(Pause(bot))
