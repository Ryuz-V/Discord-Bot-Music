import discord
from music.player import start_idle_timer

async def setup(bot):
    @bot.tree.command(
        name="connect",
        description="Bot Connect To Voice Channel"
    )
    async def connect(interaction: discord.Interaction):
        if not interaction.user.voice:
            embed = discord.Embed(
                description="<:Silang:1469196939072372952> **You must be in a voice channel to use this command**",
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        user_channel = interaction.user.voice.channel
        vc = interaction.guild.voice_client
        if vc and vc.channel != user_channel:
            embed = discord.Embed(
                description=f"<:Silang:1469196939072372952> **Bot is already in another voice channel**\n\nI'm currently in **{vc.channel.name}**",
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        if vc and vc.channel == user_channel:
            embed = discord.Embed(
                description="<:check8:1469745793308037297> **I'm already connected to your voice channel**",
            )
            await interaction.response.send_message(embed=embed)
            return
        await interaction.response.defer()
        try:
            vc = await user_channel.connect()
        except TimeoutError:
            embed = discord.Embed(
                description="<:Silang:1469196939072372952> **Connection Timed Out**\n\nFailed to connect to the voice channel. Discord's voice servers might be slow or blocking UDP traffic."
            )
            return await interaction.followup.send(embed=embed)
        except Exception as e:
            if isinstance(e, discord.ClientException):
                vc = interaction.guild.voice_client
            else:
                embed = discord.Embed(
                    description=f"<:Silang:1469196939072372952> **Failed to Connect**\n\nAn error occurred: `{str(e)}`"
                )
                return await interaction.followup.send(embed=embed)
        await start_idle_timer(vc, channel=interaction.channel)
        embed = discord.Embed(
            description=(
                f"<:check8:1469745793308037297> **The Bot Has Connected To The Voice Channel "
                f"{user_channel.name}**"
            ),
        )
        embed.set_footer(
            text="Use /play To Play A Song Or /help To See All Commands And Info"
        )
        await interaction.followup.send(embed=embed)
