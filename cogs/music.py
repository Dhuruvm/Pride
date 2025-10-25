import discord
from discord.ext import commands
import pomice

class Music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    async def start_nodes(self):
        """Start the Lavalink nodes"""
        try:
            await self.bot.pomice.create_node(
                bot=self.bot,
                host="127.0.0.1",
                port="2333",
                password="youshallnotpass",
                identifier="MAIN",
                secure=False
            )
            print("Music node started successfully")
        except Exception as e:
            print(f"Failed to start music node: {e}")

async def setup(bot: commands.Bot):
    await bot.add_cog(Music(bot))
