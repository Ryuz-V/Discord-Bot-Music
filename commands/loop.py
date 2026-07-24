import discord

async def setup(bot):

    @bot.tree.command(
        name="loop",
        description="Toggle Loop Music"
    )
    async def loop(interaction: discord.Interaction):

        vc = interaction.guild.voice_client
        if not vc or not vc.is_playing():
            embed = discord.Embed(
                # You can add custom emojis here, for example: description="<:emoji_name:id> **Text**"
                description="**No music is playing**"
            )
            return await interaction.response.send_message(
                embed=embed,
                ephemeral=True
            )

        if not hasattr(bot, "looping"):
            bot.looping = False

        bot.looping = not bot.looping

        description = (
            # You can add custom emojis here, for example: description="<:emoji_name:id> **Text**"
            "Loop ON"
            if bot.looping
            # You can add custom emojis here, for example: description="<:emoji_name:id> **Text**"
            else "Loop OFF"
        )

        embed = discord.Embed(description=description)

        await interaction.response.send_message(embed=embed)
