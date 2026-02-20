import discord
from discord import app_commands
from discord.ext import commands

# ==============================
# 🎛 DROPDOWN VIEW
# ==============================
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
            emoji="<:keyboardwhite:1473903270022873118>",
            value="commands"
        ),
        discord.SelectOption(
            label="FAQ",
            emoji="<:icons8faq100:1470588789754953839>",
            value="faq"
        ),
        discord.SelectOption(
            label="Support",
            emoji="<:lovewhite:1470608017056600164>",
            value="support"
        ),
    ]
)
    async def select_callback(
        self,
        interaction: discord.Interaction,
        select: discord.ui.Select
    ):
        value = select.values[0]

        # ==============================
        # EMBED CONTENT
        # ==============================
        if value == "info":
            embed = discord.Embed(
                title="<:icon8:1470588914770251806> Information",
                description=(
                    "Bot Discord \n"
                    "Supports **Spotify, YouTube, SoundCloud**\n\n"
                    "Created by **Ryuz_V**"
                )
            )

        elif value == "commands":
            embed = discord.Embed(
                title="<:keyboardwhite:1473903270022873118>e Commands",
                description=(
                    "`/play` - Play music\n"
                    "`/pause` - Pause music\n"
                    "`/resume` - Resume music\n"
                    "`/skip` - Skip song\n"
                    "`/stop` - Stop music\n"
                    "`/loop` - Loop song\n"
                    "`/247` - Stay in voice channel\n"
                    "`/autoplay` - Smart autoplay"
                )
            )

        elif value == "faq":
            embed = discord.Embed(
                title="<:icons8faq100:1470588789754953839> FAQ",
                description=(
                    "**Q:** Why bot not playing?\n"
                    "**A:** Make sure you are in a voice channel.\n\n"
                    "**Q:** Autoplay not working?\n"
                    "**A:** Enable it using `/autoplay`."
                )
            )

        elif value == "support":
            embed = discord.Embed(
                title="<:lovewhite:1470608017056600164> Support",
                description=(
                    "Need help or want to report a bug?\n\n"
                    "📩 Contact the developer\n"
                    "🌐 Join support server (if available)"
                )
            )

        # Banner tetap
        embed.set_image(
            url="https://cdn.discordapp.com/attachments/1461031433689759826/1470602546371493950/uma-musume-agnes-tachyon.gif"
        )

        await interaction.response.edit_message(embed=embed, view=self)

# ==============================
# 📖 HELP COMMAND
# ==============================
class Help(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="help",
        description="Show help panel"
    )
    async def help(self, interaction: discord.Interaction):

        embed = discord.Embed(
            description=(
        "**<:icon8:1470588914770251806> Help Panel**\n"
        "\n"

        "**<:headphone8:1474074914930823413> What is Tracen Jukebox?**\n"
        "Tracen Jukebox is a modern Discord music bot designed to deliver "
        "high quality audio playback with smart features such as autoplay, "
        "24/7 mode, and multi-platform support including **Spotify, YouTube, "
        "and SoundCloud**.\n\n"

        "**<:list:1474083631709421618> Available Categories**\n"
        "<:icon8:1470588914770251806> **:** Information\n"
        "<:command8:1470588859896299780> **:** Commands\n"
        "<:icons8faq100:1470588789754953839> **:** FAQ\n"
        "<:lovewhite:1470608017056600164> **:** Support"
    )
)


        embed.set_image(
            url="https://cdn.discordapp.com/attachments/1461031433689759826/1470602546371493950/uma-musume-agnes-tachyon.gif"
        )

        await interaction.response.send_message(
            embed=embed,
            view=HelpDropdown()
        )

async def setup(bot: commands.Bot):
    await bot.add_cog(Help(bot))
