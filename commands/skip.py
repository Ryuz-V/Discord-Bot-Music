import discord
from discord import app_commands
from discord.ext import commands

class Skip(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="next", description="Skip to next song")
    async def next(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client

        if not vc or not vc.is_playing():
            embed = discord.Embed(
                description="<:Silang:1469196939072372952> **No music is playing**"
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        vc.stop()

        embed = discord.Embed(
            description="<:icons8next96:1469973906939973683> **Skipped to next track**"
        )
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Skip(bot))
