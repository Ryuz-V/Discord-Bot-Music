import discord
from discord import app_commands
from discord.ext import commands

class Resume(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="resume",
        description="Resume The Music"
    )
    async def resume(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client

        if vc and vc.is_paused():
            vc.resume()

            embed = discord.Embed(
                description="<:resume8:1469637243646771404> **Music Resumed**"
            )

            await interaction.response.send_message(embed=embed)

        else:
            embed = discord.Embed(
                description="<:Silang:1469196939072372952> **Music Is Not Paused**"
            )

            await interaction.response.send_message(
                embed=embed,
                ephemeral=True
            )

async def setup(bot):
    await bot.add_cog(Resume(bot))
