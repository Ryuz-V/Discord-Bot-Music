import discord

class MusicControl(discord.ui.View):
    def __init__(self, vc):
        super().__init__(timeout=None)
        self.vc = vc

    @discord.ui.button(label="⏮ Back", style=discord.ButtonStyle.secondary)
    async def back(self, interaction: discord.Interaction, button: discord.ui.Button):

        # 🚫 Tidak ada lagu sebelumnya
        if len(history) < 2:
            return await interaction.response.send_message(
                "❌ No previous song available",
                ephemeral=True
            )

        # 🛑 Stop lagu sekarang
        if self.vc.is_playing() or self.vc.is_paused():
            self.vc.stop()

        # 🎵 Ambil lagu sebelumnya
        current_song = history.pop()
        previous_song = history.pop()

        # Kembalikan ke queue
        queue.appendleft(current_song)
        queue.appendleft(previous_song)

        await interaction.response.defer()
        await play_next(self.bot, self.vc, self.channel)

    @discord.ui.button(label="⏸ Pause", style=discord.ButtonStyle.secondary)
    async def pause(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.vc.is_playing():
            self.vc.pause()
            button.label = "▶ Resume"
        else:
            self.vc.resume()
            button.label = "⏸ Pause"

        await interaction.response.edit_message(view=self)

    @discord.ui.button(label="⏹ Stop", style=discord.ButtonStyle.secondary)
    async def stop(self, interaction: discord.Interaction, button: discord.ui.Button):
        from music.player import queue  # anti circular import

        if self.vc.is_playing() or self.vc.is_paused():
            self.vc.stop()

        queue.clear()

        if self.vc.is_connected():
            await self.vc.disconnect()

        await interaction.response.defer()

    @discord.ui.button(label="⏭ Skip", style=discord.ButtonStyle.secondary)
    async def skip(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.vc.is_playing():
            self.vc.stop()

        await interaction.response.defer()

    @discord.ui.button(
        label="Loop",
        emoji="<:repeat:1468936138847949025>",
        style=discord.ButtonStyle.secondary
    )
    async def loop(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()

    @discord.ui.button(
        label="Autoplay",
        emoji="<:autoplay:1468936098834284584>",
        style=discord.ButtonStyle.secondary
    )
    async def autoplay(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
