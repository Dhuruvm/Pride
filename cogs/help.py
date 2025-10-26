import discord
from discord.ext import commands
from discord.ui import Select, View
from typing import Optional

class CategorySelect(Select):
    def __init__(self, bot: commands.Bot, categories: dict):
        self.bot = bot
        self.categories = categories
        
        options = []
        for cog_name, cog in categories.items():
            emoji = self.get_category_emoji(cog_name)
            description = cog.description[:100] if cog.description else "No description"
            options.append(
                discord.SelectOption(
                    label=cog_name,
                    description=description,
                    emoji=emoji
                )
            )
        
        super().__init__(
            placeholder="Choose a category...",
            min_values=1,
            max_values=1,
            options=options
        )
    
    def get_category_emoji(self, category_name: str) -> str:
        emojis = {
            "Moderation": "🛡️",
            "Music": "🎵",
            "Utility": "🔧",
            "Fun": "🎮",
            "Levels": "📊",
            "Ticket": "🎫",
            "Giveaway": "🎉",
            "VoiceMaster": "🎤",
            "Social": "👥",
            "Server": "🖥️",
            "Config": "⚙️",
        }
        return emojis.get(category_name, "📁")
    
    async def callback(self, interaction: discord.Interaction):
        category_name = self.values[0]
        cog = self.categories[category_name]
        
        commands_list = [cmd for cmd in cog.get_commands() if not cmd.hidden]
        
        embed = discord.Embed(
            title=f"Category: {category_name}",
            description=cog.description if cog.description else "No description available.",
            color=0xFFFFFF
        )
        
        if commands_list:
            command_text = ""
            for cmd in commands_list:
                cmd_brief = cmd.brief if cmd.brief else "any"
                command_text += f"{cmd.name}{'*' if cmd_brief != 'any' else ''}, "
            
            command_text = command_text.rstrip(", ")
            embed.add_field(
                name=f"{len(commands_list)} commands",
                value=f"```{command_text}```",
                inline=False
            )
        else:
            embed.add_field(
                name="Commands",
                value="No commands available",
                inline=False
            )
        
        await interaction.response.edit_message(embed=embed)

class HelpView(View):
    def __init__(self, bot: commands.Bot, categories: dict, author: discord.User):
        super().__init__(timeout=180)
        self.bot = bot
        self.author = author
        self.add_item(CategorySelect(bot, categories))
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author.id:
            await interaction.response.send_message(
                "This help menu is not for you!", 
                ephemeral=True
            )
            return False
        return True

class Help(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.color = 0xFFFFFF
    
    @commands.command(
        name="help",
        description="Show the help menu with all bot commands",
        usage="[command]",
        brief="any",
        aliases=["h", "commands"]
    )
    async def help_command(self, ctx: commands.Context, *, command_name: Optional[str] = None):
        if command_name:
            command = self.bot.get_command(command_name)
            if not command:
                return await ctx.warning(f"Command `{command_name}` not found")
            
            return await self.send_command_help(ctx, command)
        
        bot_name = self.bot.user.name
        bot_avatar = self.bot.user.display_avatar.url
        
        embed = discord.Embed(
            color=self.color
        )
        embed.set_author(name=bot_name, icon_url=bot_avatar)
        embed.set_thumbnail(url=bot_avatar)
        
        embed.add_field(
            name="information",
            value="[ ] = optional, < > = required",
            inline=False
        )
        
        invite_link = f"https://discord.com/api/oauth2/authorize?client_id={self.bot.user.id}&permissions=8&scope=bot"
        support_server = self.bot.support_server if hasattr(self.bot, 'support_server') and self.bot.support_server else "https://discord.gg/support"
        
        embed.add_field(
            name="Invite",
            value=f"[invite]({invite_link}) • [support]({support_server}) • [view on web](https://discord.com)",
            inline=False
        )
        
        embed.description = "Select a category from the dropdown menu below"
        
        categories = {}
        for cog_name, cog in self.bot.cogs.items():
            if cog_name in ["Help", "Jishaku"]:
                continue
            
            cog_commands = [cmd for cmd in cog.get_commands() if not cmd.hidden]
            if cog_commands:
                categories[cog_name] = cog
        
        view = HelpView(self.bot, categories, ctx.author)
        await ctx.reply(embed=embed, view=view)
    
    async def send_command_help(self, ctx: commands.Context, command: commands.Command):
        commandname = f"{str(command.parent)} {command.name}" if str(command.parent) != "None" else command.name
        
        embed = discord.Embed(
            color=self.color,
            title=commandname,
            description=command.description or "No description"
        )
        embed.set_author(
            name=ctx.author.name,
            icon_url=ctx.author.display_avatar.url
        )
        embed.add_field(
            name="aliases",
            value=', '.join(map(str, command.aliases)) or "none"
        )
        embed.add_field(
            name="permissions",
            value=command.brief or "any"
        )
        embed.add_field(
            name="usage",
            value=f"```{commandname} {command.usage if command.usage else ''}```",
            inline=False
        )
        embed.set_footer(
            text=f'module: {command.cog_name}',
            icon_url=ctx.author.display_avatar.url
        )
        
        await ctx.reply(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Help(bot))
