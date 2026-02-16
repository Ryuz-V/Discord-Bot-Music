import discord
from music.player import start_idle_timer


async def setup(bot):

    @bot.tree.command(
        name="connect",
        description="Bot Connect To Voice Channel"
    )
    async def connect(interaction: discord.Interaction):

        # ==============================
        # 🔒 USER HARUS DI VOICE
        # ==============================
        if not interaction.user.voice:
            embed = discord.Embed(
                title="<:Silang:1469196939072372952> You must be in a voice channel to use this command",
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        user_channel = interaction.user.voice.channel
        vc = interaction.guild.voice_client

        # ==============================
        # 🔒 BOT SUDAH DI VC LAIN?
        # ==============================
        if vc and vc.channel != user_channel:
            embed = discord.Embed(
                title="<:Silang:1469196939072372952> Bot is already in another voice channel",
                description=f"I'm currently in **{vc.channel.name}**",
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # ==============================
        # ✅ BOT SUDAH DI VC YANG SAMA
        # ==============================
        if vc and vc.channel == user_channel:
            embed = discord.Embed(
                description="<:check8:1469745793308037297> **I'm already connected to your voice channel**",
            )
            await interaction.response.send_message(embed=embed)
            return

        # ==============================
        # 🔌 CONNECT BOT
        # ==============================
        vc = await user_channel.connect()

        # 🔥 Start idle timer setelah connect
        await start_idle_timer(vc)

        embed = discord.Embed(
            description=(
                f"<:check8:1469745793308037297> **The Bot Has Connected To The Voice Channel "
                f"{user_channel.name}**"
            ),
        )
        embed.set_footer(
            text="Use /play To Play A Song Or /help To See All Commands And Info"
        )

        await interaction.response.send_message(embed=embed)
