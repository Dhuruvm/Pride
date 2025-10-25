import discord
from discord.ext import commands
from discord.ui import View

class vmbuttons(View):
    def __init__(self):
        super().__init__(timeout=None)

async def setup(bot: commands.Bot):
    pass
