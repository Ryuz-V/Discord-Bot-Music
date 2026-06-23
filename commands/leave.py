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
                description="<:Silang:1469196939072372952> **Bot Is Not In A Voice Channel**"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        await vc.disconnect()

        embed = discord.Embed(
            description="<:door8:1469763739271168303> **Bot Has Left The Voice Channel**"
        )
        await interaction.response.send_message(embed=embed)
