# commands/loop.py
import discord

async def setup(bot):

    @bot.tree.command(
        name="loop",
        description="Toggle loop lagu"
    )
    async def loop(interaction: discord.Interaction):

        vc = interaction.guild.voice_client
        if not vc or not vc.is_playing():
            embed = discord.Embed(
                title="<:Silang:1469196939072372952> No music is playing"
            )
            return await interaction.response.send_message(
                embed=embed,
                ephemeral=True
            )

        if not hasattr(bot, "looping"):
            bot.looping = False

        bot.looping = not bot.looping

        description = (
            "<:loop8:1470446368202948773> Loop ON"
            if bot.looping
            else "<:loop8:1470446368202948773> Loop OFF"
        )

        embed = discord.Embed(description=description)

        await interaction.response.send_message(embed=embed)
