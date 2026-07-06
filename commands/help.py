# you can edit this file to add more information whaever you like

import discord
from discord import app_commands
from discord.ext import commands

class HelpDropdown(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    @discord.ui.select(
    placeholder="Select to view the commands",
    options=[
        discord.SelectOption(
            label="Information",
            emoji="<:icon8:1470588914770251806>",
            value="info"
        ),
        discord.SelectOption(
            label="Commands",
            emoji="<:command8:1470588859896299780>",
            value="commands"
        ),
    # add more options here if you want to add more categories and dont forget to add the elif statement in the select_callback function
    ] 
)
    async def select_callback(
        self,
        interaction: discord.Interaction,
        select: discord.ui.Select
    ):
        value = select.values[0]
        if value == "info":
            embed = discord.Embed(
            description=(
            "<:icon8:1470588914770251806> **Information**\n\n"
            "The modern Discord music bot designed to deliver "
            "high quality audio playback with smart features such as autoplay, "
            "24/7 mode, and multi-platform support including **Spotify, YouTube, "
            "and SoundCloud**.\n\n"
            "Created by **Ryuz_V**"
        )
    )
        elif value == "commands":
            embed = discord.Embed(
        description=(
            "<:command8:1470588859896299780> **Commands**\n\n"
            "```ansi\n"
            "\u001b[32mHere are the music commands:\u001b[0m\n"
            "```\n"
            "`/play` **:** Play music\n"
            "`/pause` **:** Pause music\n"
            "`/resume` **:** Resume music\n"
            "`/next` **:** Skip song\n"
            "`/stop` **:** Stop music\n"
            "`/loop` **:** Loop song\n"
            "`/247` **:** Stay in voice channel\n"
            "`/autoplay` **:** Smart autoplay\n"
            "`/radio` **:** Play radio station\n"
            "`/lyric` **:** Show lyrics Music\n"
            "`/connect` **:** Connect to voice channel\n"
            "`/leave` **:** Disconnect from voice channel\n"
            "`/help` **:** Show help information\n"
            "`/lyrics` **:** Show lyrics of the current song\n"
            "`/playlist add` **:** Add song to playlist\n"
            "`/playlist create` **:** Create a playlist\n"
            "`/playlist delete` **:** Delete a playlist\n"
            "`/playlist list` **:** List all playlists\n"
            "`/playlist play` **:** Play a playlist\n"
            "`/playlist remove` **:** Remove song from playlist\n"
            "`/playlist view` **:** View a playlist\n"
            "`/previous` **:** Play previous song\n"
        )
    )
        embed.set_image(
            url="https://cdn.discordapp.com/attachments/1461031433689759826/1470602546371493950/uma-musume-agnes-tachyon.gif" #url gif or img and if you wish to remove it from line 63 to 65 detele it
        )
        await interaction.response.edit_message(embed=embed, view=self)
class Help(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    @app_commands.command(
        name="help",
        description="Show Help Panel"
    )
    async def help(self, interaction: discord.Interaction):
        embed = discord.Embed(
            description=(
        "**<:icon8:1470588914770251806> Help Panel**\n"
        "\n"
        "**<:headphone8:1474074914930823413> What is the modern Discord music bot?**\n"
        "The modern Discord music bot designed to deliver "
        "high quality audio playback with smart features such as autoplay, "
        "24/7 mode, and multi-platform support including **Spotify, YouTube, "
        "and SoundCloud**.\n\n"
        "**<:list:1474083631709421618> Available Categories**\n"
        "<:icon8:1470588914770251806> **:** Information\n"
        "<:command8:1470588859896299780> **:** Commands\n"
        # you can add more categories here if you want to add more categories and dont forget to add the elif statement in the select_callback function
    )
)
        embed.set_image(
            url="https://cdn.discordapp.com/attachments/1461031433689759826/1470602546371493950/uma-musume-agnes-tachyon.gif" #url gif or img and if you wish to remove it from line 89 to 91 detele it
        )
        await interaction.response.send_message(
            embed=embed,
            view=HelpDropdown()
        )
async def setup(bot: commands.Bot):
    await bot.add_cog(Help(bot))
