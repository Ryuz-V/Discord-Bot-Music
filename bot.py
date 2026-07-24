# bot.py
import discord
from discord.ext import commands, tasks
import os
import config
import asyncio


class MusicBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.voice_states = True

        super().__init__(
            command_prefix="!",
            intents=intents
        )

        self.status_list = [
            "24/7 Bot Music",
            "Free Use For All User",
            "Use /play To Play Music",
            "Use /help To See All Commands"
        ]
        self.status_index = 0

        self.idle_tasks = {}

    async def setup_hook(self):
        for file in os.listdir("./commands"):
            if file.endswith(".py") and not file.startswith("_"):
                await self.load_extension(f"commands.{file[:-3]}")

        await self.tree.sync()
        print("✅ Slash commands synced")

        self.rotate_status.start()

    @tasks.loop(seconds=30)
    async def rotate_status(self):
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.listening,
                name=self.status_list[self.status_index]
            )
        )

        self.status_index = (self.status_index + 1) % len(self.status_list)

    @rotate_status.before_loop
    async def before_rotate_status(self):
        await self.wait_until_ready()

    async def start_idle_timer(self, guild: discord.Guild):
        if guild.id in self.idle_tasks:
            return

        async def idle_check():
            await asyncio.sleep(180)  # 3 minutes auto-disconnect timer

            vc = guild.voice_client
            if vc and not vc.is_playing():
                await vc.disconnect()
                print(f"🔌 Disconnected from {guild.name} (Idle 3 minutes)")

            self.idle_tasks.pop(guild.id, None)

        task = self.loop.create_task(idle_check())
        self.idle_tasks[guild.id] = task

    def cancel_idle_timer(self, guild: discord.Guild):
        task = self.idle_tasks.pop(guild.id, None)
        if task:
            task.cancel()

    async def on_voice_state_update(self, member, before, after):
        if member == self.user and before.channel is not None and after.channel is None:
            if hasattr(self, "looping"):
                self.looping = False
            
            try:
                from music.player import autoplay_guilds, now_playing_messages
                
                if member.guild.id in autoplay_guilds:
                    autoplay_guilds.remove(member.guild.id)
                
                msg = now_playing_messages.pop(member.guild.id, None)
                if msg:
                    try:
                        await msg.delete()
                    except:
                        pass
            except ImportError:
                pass

        elif member == self.user and before.channel is not None and after.channel is not None and before.channel.id != after.channel.id:
            try:
                from music.player import now_playing_messages, text_channels, history
                from music.controls import MusicControl, RadioControl
                
                guild_id = member.guild.id
                vc = member.guild.voice_client

                old_msg = now_playing_messages.pop(guild_id, None)
                embed_to_send = None
                is_radio = False
                
                if old_msg:
                    if old_msg.embeds:
                        embed_to_send = old_msg.embeds[0]
                        if embed_to_send.title and "RADIO" in embed_to_send.title.upper():
                            is_radio = True
                    try:
                        await old_msg.delete()
                    except:
                        pass

                new_channel = after.channel
                text_channels[guild_id] = new_channel

                if vc and (vc.is_playing() or vc.is_paused()):
                    view = RadioControl(vc) if is_radio else MusicControl(vc)
                    
                    if embed_to_send:
                        try:
                            new_msg = await new_channel.send(embed=embed_to_send, view=view)
                            now_playing_messages[guild_id] = new_msg
                        except discord.Forbidden:
                            print(f"❌ Bot tidak memiliki izin untuk mengirim pesan di VC: {new_channel.name}")
                    elif history:
                        current_song = history[-1]
                        
                        embed_title = "<a:vinyl:1468959873969426629> RADIO PANEL" if current_song.get("source") == "radio" else "<a:vinyl:1468959873969426629> MUSIC PANEL"
                        embed = discord.Embed(
                            title=embed_title,
                            description=f"**{current_song.get('title', 'Unknown')}**",
                        )

                        if current_song.get("thumbnail"):
                            embed.set_thumbnail(url=current_song["thumbnail"])

                        requester = current_song.get("requester")
                        embed.add_field(
                            name="Requested By",
                            value=requester.mention if requester else "Autoplay",
                            inline=True,
                        )
                        
                        embed.add_field(
                            name="Duration",
                            value=f"{current_song.get('duration', 'Unknown')} sec",
                            inline=True,
                        )
                        
                        embed.add_field(
                            name="Author",
                            value=current_song.get("author", "Unknown"),
                            inline=True,
                        )

                        view = RadioControl(vc) if current_song.get("source") == "radio" else MusicControl(vc)
                        
                        try:
                            new_msg = await new_channel.send(embed=embed, view=view)
                            now_playing_messages[guild_id] = new_msg
                        except discord.Forbidden:
                            # You can add custom emojis here, for example: description="<:emoji_name:id> **Text**"
                            print(f"Bot din't have permission to send message in VC: {new_channel.name}")

            except Exception as e:
                # You can add custom emojis here, for example: description="<:emoji_name:id> **Text**"
                print(f"Terjadi kesalahan saat memindahkan panel bot: {e}")

        # Auto-disconnect if bot is left alone
        vc = member.guild.voice_client
        if vc and vc.channel:
            non_bot_members = [m for m in vc.channel.members if not m.bot]
            if not non_bot_members:
                await vc.disconnect()
                print(f"🔌 Disconnected from {member.guild.name} (Voice channel empty)")
                
                if hasattr(self, "looping"):
                    self.looping = False
                
                try:
                    from music.player import autoplay_guilds, now_playing_messages
                    if member.guild.id in autoplay_guilds:
                        autoplay_guilds.remove(member.guild.id)
                    msg = now_playing_messages.pop(member.guild.id, None)
                    if msg:
                        try:
                            await msg.delete()
                        except:
                            pass
                except ImportError:
                    pass

bot = MusicBot()
bot.run(config.TOKEN)
