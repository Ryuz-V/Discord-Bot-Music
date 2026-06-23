import discord
from discord import app_commands
from discord.ext import commands

from music.player import queue, history, play_next


class Previous(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="previous",
        description="Play Previous Music"
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
                embed=embed
            )

        # 🎵 Ambil lagu sebelumnya
        current_song = history.pop()
        previous_song = history.pop()

        # Masukkan kembali ke queue
        queue.appendleft(current_song)
        queue.appendleft(previous_song)

        # 🛑 Stop lagu sekarang
        if vc.is_playing() or vc.is_paused():
            vc.is_previous_action = True
            vc.stop()
        else:
            await play_next(self.bot, vc, interaction.channel)

        # 🎨 EMBED SUCCESS (TITLE JADI DESKRIPSI)
        embed = discord.Embed(
            description=(
                "<:previous8:1505836696259006584> **Playing Previous Song**"
            )
        )

        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Previous(bot))
