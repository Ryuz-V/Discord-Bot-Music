import discord

async def setup(bot):

    @bot.tree.command(
        name="leave",
        description="Bot Leave The Voice Channel"
    )
    async def leave(interaction: discord.Interaction):
        vc = interaction.guild.voice_client

        if not vc:
            embed = discord.Embed(
                # You can add custom emojis here, for example: description="<:emoji_name:id> **Text**"
                description="**Bot Is Not In A Voice Channel**"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        await vc.disconnect()

        embed = discord.Embed(
            # You can add custom emojis here, for example: description="<:emoji_name:id> **Text**"
            description="**Bot Has Left The Voice Channel**"
        )
        await interaction.response.send_message(embed=embed)
