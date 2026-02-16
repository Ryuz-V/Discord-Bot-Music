# =========== 
# help commands
# ============= 

import discord
from discord import app_commands
from discord.ext import commands

class Help(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="help",
        description="Show help panel"
    )
    async def help(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="**Help Panel**",
            description=(
                "__**What Is This Bot?**__\n"
                "Cool music Discord bot with complete features and support for music platforms "
                "such as Spotify, YouTube, and SoundCloud, created by **Ryuz_V**.\n\n"
                "__**Category**__\n"
                "<:icon8:1470588914770251806> : **Information**\n"
                "<:command8:1470588859896299780> : **Commands**\n"
                "<:icons8faq100:1470588789754953839> : **FAQ**\n"
                "<:lovewhite:1470608017056600164> : **Support**"
            ),
        )

        # Banner image
        embed.set_image(
            url="https://cdn.discordapp.com/attachments/1461031433689759826/1470602546371493950/uma-musume-agnes-tachyon.gif"
        )

        await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Help(bot))
