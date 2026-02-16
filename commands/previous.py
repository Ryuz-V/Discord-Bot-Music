import discord
from discord import app_commands
from discord.ext import commands

from music.player import queue, history, play_next


class Previous(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="previous",
        description="Play previous song"
    )
    async def previous(self, interaction: discord.Interaction):

        vc = interaction.guild.voice_client

        # 🔒 Bot harus di voice
        if not vc or not vc.is_connected():
            embed = discord.Embed(
                description=(
                    "<:Silang:1469196939072372952> **Error**\n"
                    "Bot is not connected to a voice channel"
                )
            )
            return await interaction.response.send_message(
                embed=embed,
                ephemeral=True
            )

        # 🚫 Tidak ada lagu sebelumnya
        if len(history) < 2:
            embed = discord.Embed(
                description=(
                    "<:Silang:1469196939072372952> **Error**\n"
                    "No previous song available"
                )
            )
            return await interaction.response.send_message(
                embed=embed,
                ephemeral=True
            )

        # 🛑 Stop lagu sekarang
        if vc.is_playing() or vc.is_paused():
            vc.stop()

        # 🎵 Ambil lagu sebelumnya
        current_song = history.pop()
        previous_song = history.pop()

        # Masukkan kembali ke queue
        queue.appendleft(current_song)
        queue.appendleft(previous_song)

        # 🎨 EMBED SUCCESS (TITLE JADI DESKRIPSI)
        embed = discord.Embed(
            description=(
                "<:previous8:1472870054105321555> **Playing Previous Song**\n"
                f"**{previous_song['title']}**"
            )
        )

        await interaction.response.send_message(embed=embed)
        await play_next(self.bot, vc, interaction.channel)


async def setup(bot):
    await bot.add_cog(Previous(bot))
