# commands/247.py
import discord
from discord import app_commands
from discord.ext import commands
from music.player import always_on_guilds


class AlwaysOn(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="247",
        description="Toggle 24/7 mode"
    )
    async def toggle_247(self, interaction: discord.Interaction):

        if not interaction.user.voice:
            embed = discord.Embed(
                title="<:Silang:1469196939072372952> **You must be in a voice channel**"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        guild_id = interaction.guild.id

        if guild_id in always_on_guilds:
            always_on_guilds.remove(guild_id)

            embed = discord.Embed(
                title="<:24hours:1471541469201567861> 24/7 Mode Disable",
                description="The bot will automatically leave the channel if it is not turned on"
            )

            await interaction.response.send_message(embed=embed)

        else:
            always_on_guilds.add(guild_id)

            embed = discord.Embed(
                title="<:24hours:1471541469201567861> 247 Mode Enabled",
                description="/247 again to disable mode"
            )

            await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(AlwaysOn(bot))
