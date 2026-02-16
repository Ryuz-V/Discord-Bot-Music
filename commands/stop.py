import discord
from discord import app_commands
from discord.ext import commands
from music.player import queue

class Stop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="stop",
        description="Stop The Music"
    )
    async def stop(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client

        queue.clear()

        if vc and vc.is_connected():
            vc.stop()
            await vc.disconnect()

            embed = discord.Embed(
                description="<:berhenti:1469188566532886588> **Stopped Playing**"
            )

            await interaction.response.send_message(embed=embed)

        else:
            embed = discord.Embed(
                description="<:Silang:1469196939072372952> **The Bot Is Not currently in the voice channel**"
            )

            await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Stop(bot))
