import discord
from discord.ext import commands
from typing import Optional, Union
import asyncio
from datetime import datetime, timedelta
import re

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.color = 0xFFFFFF
    
    async def create_case(self, guild_id: int, user_id: int, moderator_id: int, action: str, reason: Optional[str] = None):
        """Create a moderation case in the database"""
        if not self.bot.db:
            return None
        
        reason_text = reason if reason else "No reason provided"
        case_id = await self.bot.db.fetchval(
            "INSERT INTO cases (guild_id, user_id, moderator_id, action, reason, timestamp) VALUES ($1, $2, $3, $4, $5, $6) RETURNING case_id",
            guild_id, user_id, moderator_id, action, reason_text, datetime.now()
        )
        return case_id
    
    @commands.command(
        name="cleanup",
        description="Clean up bot messages",
        usage="<amount>",
        brief="manage messages"
    )
    @commands.has_permissions(manage_messages=True)
    async def cleanup(self, ctx, amount: int = 10):
        """Clean up bot messages from the channel"""
        if amount < 1 or amount > 100:
            return await ctx.warning("Amount must be between 1 and 100")
        
        def check(m):
            return m.author.bot
        
        deleted = await ctx.channel.purge(limit=amount + 1, check=check)
        await ctx.success(f"Cleaned up **{len(deleted) - 1}** bot messages")
    
    @commands.command(
        name="purge",
        description="Purge messages from the channel",
        usage="<amount> [member]",
        brief="manage messages",
        aliases=["clear", "clean"]
    )
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, amount: int, member: Optional[discord.Member] = None):
        """Purge messages from the channel"""
        if amount < 1 or amount > 1000:
            return await ctx.warning("Amount must be between 1 and 1000")
        
        def check(m):
            if member:
                return m.author.id == member.id
            return True
        
        deleted = await ctx.channel.purge(limit=amount + 1, check=check)
        target = f" from {member.mention}" if member else ""
        await ctx.success(f"Purged **{len(deleted) - 1}** messages{target}")
    
    @commands.command(
        name="selfpurge",
        description="Purge your own messages",
        usage="<amount>",
        brief="any"
    )
    async def selfpurge(self, ctx, amount: int = 10):
        """Purge your own messages"""
        if amount < 1 or amount > 100:
            return await ctx.warning("Amount must be between 1 and 100")
        
        def check(m):
            return m.author.id == ctx.author.id
        
        deleted = await ctx.channel.purge(limit=amount + 1, check=check)
        await ctx.success(f"Purged **{len(deleted) - 1}** of your messages")
    
    @commands.command(
        name="role",
        description="Add or remove a role from a member",
        usage="<member> <role>",
        brief="manage roles"
    )
    @commands.has_permissions(manage_roles=True)
    async def role(self, ctx, member: discord.Member, *, role: discord.Role):
        """Add or remove a role from a member"""
        if role.position >= ctx.guild.me.top_role.position:
            return await ctx.warning("I cannot manage this role")
        
        if role.position >= ctx.author.top_role.position and ctx.author.id != ctx.guild.owner_id:
            return await ctx.warning("You cannot manage this role")
        
        if role in member.roles:
            await member.remove_roles(role)
            return await ctx.success(f"Removed {role.mention} from {member.mention}")
        else:
            await member.add_roles(role)
            return await ctx.success(f"Added {role.mention} to {member.mention}")
    
    @commands.command(
        name="denyperm",
        description="Deny a permission for a member in the channel",
        usage="<member> <permission>",
        brief="manage channels"
    )
    @commands.has_permissions(manage_channels=True)
    async def denyperm(self, ctx, member: discord.Member, permission: str):
        """Deny a permission for a member in the channel"""
        perms = {
            "send_messages": discord.PermissionOverwrite(send_messages=False),
            "view_channel": discord.PermissionOverwrite(view_channel=False),
            "connect": discord.PermissionOverwrite(connect=False),
            "speak": discord.PermissionOverwrite(speak=False),
            "read_messages": discord.PermissionOverwrite(read_messages=False)
        }
        
        if permission.lower() not in perms:
            return await ctx.warning(f"Invalid permission. Available: {', '.join(perms.keys())}")
        
        await ctx.channel.set_permissions(member, overwrite=perms[permission.lower()])
        await ctx.success(f"Denied **{permission}** for {member.mention} in this channel")
    
    @commands.command(
        name="lockdown",
        description="Lock the channel",
        usage="[reason]",
        brief="manage channels",
        aliases=["lock"]
    )
    @commands.has_permissions(manage_channels=True)
    async def lockdown(self, ctx, *, reason: str = "No reason provided"):
        """Lock the channel"""
        overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
        overwrite.send_messages = False
        await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        
        embed = discord.Embed(
            description=f"🔒 This channel has been locked by {ctx.author.mention}\n**Reason:** {reason}",
            color=self.color
        )
        await ctx.send(embed=embed)
    
    @commands.command(
        name="unlockdown",
        description="Unlock the channel",
        usage="[reason]",
        brief="manage channels",
        aliases=["unlock"]
    )
    @commands.has_permissions(manage_channels=True)
    async def unlockdown(self, ctx, *, reason: str = "No reason provided"):
        """Unlock the channel"""
        overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
        overwrite.send_messages = None
        await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        
        embed = discord.Embed(
            description=f"🔓 This channel has been unlocked by {ctx.author.mention}\n**Reason:** {reason}",
            color=self.color
        )
        await ctx.send(embed=embed)
    
    @commands.command(
        name="hide",
        description="Hide the channel",
        usage="",
        brief="manage channels"
    )
    @commands.has_permissions(manage_channels=True)
    async def hide(self, ctx):
        """Hide the channel"""
        overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
        overwrite.view_channel = False
        await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        await ctx.success("Channel hidden")
    
    @commands.command(
        name="reveal",
        description="Reveal the channel",
        usage="",
        brief="manage channels"
    )
    @commands.has_permissions(manage_channels=True)
    async def reveal(self, ctx):
        """Reveal the channel"""
        overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
        overwrite.view_channel = None
        await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        await ctx.success("Channel revealed")
    
    @commands.command(
        name="slowmode",
        description="Set slowmode for the channel",
        usage="<seconds>",
        brief="manage channels"
    )
    @commands.has_permissions(manage_channels=True)
    async def slowmode(self, ctx, seconds: int):
        """Set slowmode for the channel"""
        if seconds < 0 or seconds > 21600:
            return await ctx.warning("Slowmode must be between 0 and 21600 seconds (6 hours)")
        
        await ctx.channel.edit(slowmode_delay=seconds)
        if seconds == 0:
            await ctx.success("Slowmode disabled")
        else:
            await ctx.success(f"Slowmode set to **{seconds}** seconds")
    
    @commands.command(
        name="nsfw",
        description="Toggle NSFW status for the channel",
        usage="",
        brief="manage channels"
    )
    @commands.has_permissions(manage_channels=True)
    async def nsfw(self, ctx):
        """Toggle NSFW status for the channel"""
        if not isinstance(ctx.channel, discord.TextChannel):
            return await ctx.warning("This command only works in text channels")
        
        await ctx.channel.edit(nsfw=not ctx.channel.nsfw)
        status = "enabled" if ctx.channel.nsfw else "disabled"
        await ctx.success(f"NSFW {status} for this channel")
    
    @commands.command(
        name="topic",
        description="Set the channel topic",
        usage="<topic>",
        brief="manage channels"
    )
    @commands.has_permissions(manage_channels=True)
    async def topic(self, ctx, *, topic: str):
        """Set the channel topic"""
        if not isinstance(ctx.channel, discord.TextChannel):
            return await ctx.warning("This command only works in text channels")
        
        await ctx.channel.edit(topic=topic)
        await ctx.success(f"Channel topic set to: {topic}")
    
    @commands.command(
        name="drag",
        description="Drag a member to a voice channel",
        usage="<member> <channel>",
        brief="move members"
    )
    @commands.has_permissions(move_members=True)
    async def drag(self, ctx, member: discord.Member, *, channel: discord.VoiceChannel):
        """Drag a member to a voice channel"""
        if not member.voice:
            return await ctx.warning(f"{member.mention} is not in a voice channel")
        
        await member.move_to(channel)
        await ctx.success(f"Moved {member.mention} to {channel.mention}")
    
    @commands.command(
        name="moveall",
        description="Move all members from one voice channel to another",
        usage="<from_channel> <to_channel>",
        brief="move members"
    )
    @commands.has_permissions(move_members=True)
    async def moveall(self, ctx, from_channel: discord.VoiceChannel, to_channel: discord.VoiceChannel):
        """Move all members from one voice channel to another"""
        members = from_channel.members
        if not members:
            return await ctx.warning(f"{from_channel.mention} has no members")
        
        for member in members:
            await member.move_to(to_channel)
        
        await ctx.success(f"Moved **{len(members)}** members from {from_channel.mention} to {to_channel.mention}")
    
    @commands.command(
        name="newusers",
        description="Show recently joined users",
        usage="[amount]",
        brief="any"
    )
    async def newusers(self, ctx, amount: int = 10):
        """Show recently joined users"""
        if amount < 1 or amount > 50:
            return await ctx.warning("Amount must be between 1 and 50")
        
        members = sorted(ctx.guild.members, key=lambda m: m.joined_at, reverse=True)[:amount]
        
        embed = discord.Embed(
            title="Recently Joined Users",
            description="\n".join([f"{i+1}. {m.mention} - <t:{int(m.joined_at.timestamp())}:R>" for i, m in enumerate(members)]),
            color=self.color
        )
        await ctx.send(embed=embed)
    
    @commands.command(
        name="audit",
        description="View recent audit log entries",
        usage="[limit]",
        brief="view audit log"
    )
    @commands.has_permissions(view_audit_log=True)
    async def audit(self, ctx, limit: int = 10):
        """View recent audit log entries"""
        if limit < 1 or limit > 25:
            return await ctx.warning("Limit must be between 1 and 25")
        
        entries = [entry async for entry in ctx.guild.audit_logs(limit=limit)]
        
        description = []
        for entry in entries:
            description.append(f"**{entry.action.name}** by {entry.user.mention} - <t:{int(entry.created_at.timestamp())}:R>")
        
        embed = discord.Embed(
            title="Recent Audit Log",
            description="\n".join(description),
            color=self.color
        )
        await ctx.send(embed=embed)
    
    @commands.command(
        name="kick",
        description="Kick a member from the server",
        usage="<member> [reason]",
        brief="kick members"
    )
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        """Kick a member from the server"""
        if member.top_role >= ctx.author.top_role and ctx.author.id != ctx.guild.owner_id:
            return await ctx.warning("You cannot kick this member")
        
        if member.top_role >= ctx.guild.me.top_role:
            return await ctx.warning("I cannot kick this member")
        
        try:
            await member.send(f"You were kicked from **{ctx.guild.name}** by {ctx.author} for: {reason}")
        except:
            pass
        
        await member.kick(reason=f"{ctx.author}: {reason}")
        await self.create_case(ctx.guild.id, member.id, ctx.author.id, "kick", reason)
        await ctx.success(f"Kicked {member.mention} for: {reason}")
    
    @commands.command(
        name="ban",
        description="Ban a member from the server",
        usage="<member> [reason]",
        brief="ban members"
    )
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: Union[discord.Member, discord.User], *, reason: str = "No reason provided"):
        """Ban a member from the server"""
        if isinstance(member, discord.Member):
            if member.top_role >= ctx.author.top_role and ctx.author.id != ctx.guild.owner_id:
                return await ctx.warning("You cannot ban this member")
            
            if member.top_role >= ctx.guild.me.top_role:
                return await ctx.warning("I cannot ban this member")
            
            try:
                await member.send(f"You were banned from **{ctx.guild.name}** by {ctx.author} for: {reason}")
            except:
                pass
        
        await ctx.guild.ban(member, reason=f"{ctx.author}: {reason}")
        await self.create_case(ctx.guild.id, member.id, ctx.author.id, "ban", reason)
        await ctx.success(f"Banned {member.mention} for: {reason}")
    
    @commands.command(
        name="softban",
        description="Softban a member (ban and unban to delete messages)",
        usage="<member> [reason]",
        brief="ban members"
    )
    @commands.has_permissions(ban_members=True)
    async def softban(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        """Softban a member"""
        if member.top_role >= ctx.author.top_role and ctx.author.id != ctx.guild.owner_id:
            return await ctx.warning("You cannot softban this member")
        
        if member.top_role >= ctx.guild.me.top_role:
            return await ctx.warning("I cannot softban this member")
        
        await ctx.guild.ban(member, reason=f"{ctx.author}: {reason}", delete_message_days=7)
        await ctx.guild.unban(member, reason="Softban")
        await self.create_case(ctx.guild.id, member.id, ctx.author.id, "softban", reason)
        await ctx.success(f"Softbanned {member.mention} for: {reason}")
    
    @commands.command(
        name="hardban",
        description="Ban a user and prevent them from being unbanned",
        usage="<user_id> [reason]",
        brief="administrator"
    )
    @commands.has_permissions(administrator=True)
    async def hardban(self, ctx, user_id: int, *, reason: str = "No reason provided"):
        """Hardban a user"""
        if not self.bot.db:
            return await ctx.warning("Database not available")
        
        user = await self.bot.fetch_user(user_id)
        await ctx.guild.ban(user, reason=f"{ctx.author}: {reason}")
        
        await self.bot.db.execute(
            "INSERT INTO hardban (guild_id, user_id, moderator_id, reason) VALUES ($1, $2, $3, $4)",
            ctx.guild.id, user_id, ctx.author.id, reason
        )
        
        await self.create_case(ctx.guild.id, user_id, ctx.author.id, "hardban", reason)
        await ctx.success(f"Hardbanned user {user.mention} for: {reason}")
    
    @commands.command(
        name="hardbanlist",
        description="View all hardbanned users",
        usage="",
        brief="administrator"
    )
    @commands.has_permissions(administrator=True)
    async def hardbanlist(self, ctx):
        """View all hardbanned users"""
        if not self.bot.db:
            return await ctx.warning("Database not available")
        
        hardbans = await self.bot.db.fetch(
            "SELECT user_id, reason FROM hardban WHERE guild_id = $1",
            ctx.guild.id
        )
        
        if not hardbans:
            return await ctx.warning("No hardbanned users")
        
        description = []
        for hb in hardbans[:10]:
            user = await self.bot.fetch_user(hb['user_id'])
            description.append(f"{user.mention} - {hb['reason']}")
        
        embed = discord.Embed(
            title="Hardbanned Users",
            description="\n".join(description),
            color=self.color
        )
        await ctx.send(embed=embed)
    
    @commands.command(
        name="massban",
        description="Ban multiple users at once",
        usage="<user_ids...> [reason]",
        brief="ban members"
    )
    @commands.has_permissions(ban_members=True)
    async def massban(self, ctx, user_ids: commands.Greedy[int], *, reason: str = "No reason provided"):
        """Ban multiple users at once"""
        if not user_ids:
            return await ctx.warning("Please provide user IDs to ban")
        
        if len(user_ids) > 50:
            return await ctx.warning("You can only ban up to 50 users at once")
        
        banned = 0
        for user_id in user_ids:
            try:
                user = await self.bot.fetch_user(user_id)
                await ctx.guild.ban(user, reason=f"{ctx.author}: {reason}")
                await self.create_case(ctx.guild.id, user_id, ctx.author.id, "ban", reason)
                banned += 1
            except:
                continue
        
        await ctx.success(f"Banned **{banned}** users for: {reason}")
    
    @commands.command(
        name="unban",
        description="Unban a user from the server",
        usage="<user_id> [reason]",
        brief="ban members"
    )
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, user_id: int, *, reason: str = "No reason provided"):
        """Unban a user from the server"""
        if self.bot.db:
            hardban = await self.bot.db.fetchrow(
                "SELECT * FROM hardban WHERE guild_id = $1 AND user_id = $2",
                ctx.guild.id, user_id
            )
            if hardban:
                return await ctx.warning("This user is hardbanned and cannot be unbanned")
        
        user = await self.bot.fetch_user(user_id)
        await ctx.guild.unban(user, reason=f"{ctx.author}: {reason}")
        await self.create_case(ctx.guild.id, user_id, ctx.author.id, "unban", reason)
        await ctx.success(f"Unbanned {user.mention} for: {reason}")
    
    @commands.command(
        name="nickname",
        description="Change a member's nickname",
        usage="<member> <nickname>",
        brief="manage nicknames",
        aliases=["nick"]
    )
    @commands.has_permissions(manage_nicknames=True)
    async def nickname(self, ctx, member: discord.Member, *, nickname: Optional[str] = None):
        """Change a member's nickname"""
        if member.top_role >= ctx.author.top_role and ctx.author.id != ctx.guild.owner_id:
            return await ctx.warning("You cannot change this member's nickname")
        
        if member.top_role >= ctx.guild.me.top_role:
            return await ctx.warning("I cannot change this member's nickname")
        
        await member.edit(nick=nickname)
        if nickname:
            await ctx.success(f"Changed {member.mention}'s nickname to **{nickname}**")
        else:
            await ctx.success(f"Removed {member.mention}'s nickname")
    
    @commands.command(
        name="timeout",
        description="Timeout a member",
        usage="<member> <duration> [reason]",
        brief="moderate members"
    )
    @commands.has_permissions(moderate_members=True)
    async def timeout(self, ctx, member: discord.Member, duration: str, *, reason: str = "No reason provided"):
        """Timeout a member"""
        if member.top_role >= ctx.author.top_role and ctx.author.id != ctx.guild.owner_id:
            return await ctx.warning("You cannot timeout this member")
        
        if member.top_role >= ctx.guild.me.top_role:
            return await ctx.warning("I cannot timeout this member")
        
        time_regex = re.compile(r"(\d+)([smhd])")
        matches = time_regex.findall(duration)
        
        if not matches:
            return await ctx.warning("Invalid duration format. Use: 10s, 5m, 2h, 1d")
        
        seconds = 0
        for value, unit in matches:
            value = int(value)
            if unit == 's':
                seconds += value
            elif unit == 'm':
                seconds += value * 60
            elif unit == 'h':
                seconds += value * 3600
            elif unit == 'd':
                seconds += value * 86400
        
        if seconds < 1 or seconds > 2419200:
            return await ctx.warning("Duration must be between 1 second and 28 days")
        
        until = discord.utils.utcnow() + timedelta(seconds=seconds)
        await member.timeout(until, reason=f"{ctx.author}: {reason}")
        await self.create_case(ctx.guild.id, member.id, ctx.author.id, "timeout", f"{duration} - {reason}")
        await ctx.success(f"Timed out {member.mention} for **{duration}** - {reason}")
    
    @commands.command(
        name="untimeout",
        description="Remove timeout from a member",
        usage="<member>",
        brief="moderate members"
    )
    @commands.has_permissions(moderate_members=True)
    async def untimeout(self, ctx, member: discord.Member):
        """Remove timeout from a member"""
        if not member.is_timed_out():
            return await ctx.warning(f"{member.mention} is not timed out")
        
        await member.timeout(None)
        await ctx.success(f"Removed timeout from {member.mention}")
    
    @commands.command(
        name="warn",
        description="Warn a member",
        usage="<member> <reason>",
        brief="manage messages"
    )
    @commands.has_permissions(manage_messages=True)
    async def warn(self, ctx, member: discord.Member, *, reason: str):
        """Warn a member"""
        if not self.bot.db:
            return await ctx.warning("Database not available")
        
        await self.bot.db.execute(
            "INSERT INTO warns (guild_id, user_id, moderator_id, reason, timestamp) VALUES ($1, $2, $3, $4, $5)",
            ctx.guild.id, member.id, ctx.author.id, reason, datetime.now()
        )
        
        warns = await self.bot.db.fetch(
            "SELECT * FROM warns WHERE guild_id = $1 AND user_id = $2",
            ctx.guild.id, member.id
        )
        
        await self.create_case(ctx.guild.id, member.id, ctx.author.id, "warn", reason)
        
        try:
            await member.send(f"You were warned in **{ctx.guild.name}** by {ctx.author} for: {reason}")
        except:
            pass
        
        await ctx.success(f"Warned {member.mention} for: {reason} (Total warnings: {len(warns)})")
    
    @commands.command(
        name="warnings",
        description="View warnings for a member",
        usage="<member>",
        brief="any"
    )
    async def warnings(self, ctx, member: Optional[discord.Member] = None):
        """View warnings for a member"""
        if not self.bot.db:
            return await ctx.warning("Database not available")
        
        member = member or ctx.author
        
        warns = await self.bot.db.fetch(
            "SELECT * FROM warns WHERE guild_id = $1 AND user_id = $2 ORDER BY timestamp DESC",
            ctx.guild.id, member.id
        )
        
        if not warns:
            return await ctx.warning(f"{member.mention} has no warnings")
        
        description = []
        for i, warn in enumerate(warns[:10], 1):
            mod = ctx.guild.get_member(warn['moderator_id'])
            mod_name = mod.mention if mod else f"<@{warn['moderator_id']}>"
            description.append(f"**{i}.** {warn['reason']} - by {mod_name}")
        
        embed = discord.Embed(
            title=f"Warnings for {member}",
            description="\n".join(description),
            color=self.color
        )
        embed.set_footer(text=f"Total warnings: {len(warns)}")
        await ctx.send(embed=embed)
    
    @commands.command(
        name="strip",
        description="Remove all roles from a member",
        usage="<member>",
        brief="manage roles"
    )
    @commands.has_permissions(manage_roles=True)
    async def strip(self, ctx, member: discord.Member):
        """Remove all roles from a member"""
        if member.top_role >= ctx.author.top_role and ctx.author.id != ctx.guild.owner_id:
            return await ctx.warning("You cannot strip this member")
        
        if member.top_role >= ctx.guild.me.top_role:
            return await ctx.warning("I cannot strip this member")
        
        roles = [r for r in member.roles if r != ctx.guild.default_role and r < ctx.guild.me.top_role]
        await member.remove_roles(*roles, reason=f"Stripped by {ctx.author}")
        await ctx.success(f"Stripped **{len(roles)}** roles from {member.mention}")
    
    @commands.command(
        name="pin",
        description="Pin a message",
        usage="<message_id>",
        brief="manage messages"
    )
    @commands.has_permissions(manage_messages=True)
    async def pin(self, ctx, message_id: int):
        """Pin a message"""
        try:
            message = await ctx.channel.fetch_message(message_id)
            await message.pin()
            await ctx.success("Message pinned")
        except:
            await ctx.warning("Could not find or pin that message")
    
    @commands.command(
        name="unpin",
        description="Unpin a message",
        usage="<message_id>",
        brief="manage messages"
    )
    @commands.has_permissions(manage_messages=True)
    async def unpin(self, ctx, message_id: int):
        """Unpin a message"""
        try:
            message = await ctx.channel.fetch_message(message_id)
            await message.unpin()
            await ctx.success("Message unpinned")
        except:
            await ctx.warning("Could not find or unpin that message")
    
    @commands.command(
        name="nuke",
        description="Clone and delete the channel to clear all messages",
        usage="",
        brief="manage channels"
    )
    @commands.has_permissions(manage_channels=True)
    async def nuke(self, ctx):
        """Nuke the channel"""
        new_channel = await ctx.channel.clone(reason=f"Nuked by {ctx.author}")
        await ctx.channel.delete()
        
        embed = discord.Embed(
            description=f"💥 Channel nuked by {ctx.author.mention}",
            color=self.color
        )
        await new_channel.send(embed=embed)
    
    @commands.group(
        name="jail",
        description="Jail system commands",
        invoke_without_command=True
    )
    async def jail(self, ctx):
        """Jail system commands"""
        await ctx.send_help(ctx.command)
    
    @jail.command(
        name="setup",
        description="Setup jail role",
        usage="<role>",
        brief="administrator"
    )
    @commands.has_permissions(administrator=True)
    async def jail_setup(self, ctx, role: discord.Role):
        """Setup jail role"""
        if not self.bot.db:
            return await ctx.warning("Database not available")
        
        await self.bot.db.execute(
            "INSERT INTO jail (guild_id, role_id) VALUES ($1, $2) ON CONFLICT (guild_id) DO UPDATE SET role_id = $2",
            ctx.guild.id, role.id
        )
        await ctx.success(f"Jail role set to {role.mention}")
    
    @commands.command(
        name="jailed",
        description="View all jailed members",
        usage="",
        brief="any"
    )
    async def jailed(self, ctx):
        """View all jailed members"""
        if not self.bot.db:
            return await ctx.warning("Database not available")
        
        jail_data = await self.bot.db.fetchrow("SELECT role_id FROM jail WHERE guild_id = $1", ctx.guild.id)
        if not jail_data:
            return await ctx.warning("Jail system not setup")
        
        role = ctx.guild.get_role(jail_data['role_id'])
        if not role:
            return await ctx.warning("Jail role not found")
        
        if not role.members:
            return await ctx.warning("No jailed members")
        
        embed = discord.Embed(
            title="Jailed Members",
            description="\n".join([m.mention for m in role.members]),
            color=self.color
        )
        await ctx.send(embed=embed)
    
    @commands.command(
        name="unjail",
        description="Unjail a member",
        usage="<member>",
        brief="manage roles"
    )
    @commands.has_permissions(manage_roles=True)
    async def unjail(self, ctx, member: discord.Member):
        """Unjail a member"""
        if not self.bot.db:
            return await ctx.warning("Database not available")
        
        jail_data = await self.bot.db.fetchrow("SELECT role_id FROM jail WHERE guild_id = $1", ctx.guild.id)
        if not jail_data:
            return await ctx.warning("Jail system not setup")
        
        role = ctx.guild.get_role(jail_data['role_id'])
        if not role:
            return await ctx.warning("Jail role not found")
        
        if role not in member.roles:
            return await ctx.warning(f"{member.mention} is not jailed")
        
        await member.remove_roles(role)
        await ctx.success(f"Unjailed {member.mention}")
    
    @commands.command(
        name="temprole",
        description="Give a member a role temporarily",
        usage="<member> <role> <duration>",
        brief="manage roles"
    )
    @commands.has_permissions(manage_roles=True)
    async def temprole(self, ctx, member: discord.Member, role: discord.Role, duration: str):
        """Give a member a role temporarily"""
        if role.position >= ctx.guild.me.top_role.position:
            return await ctx.warning("I cannot manage this role")
        
        time_regex = re.compile(r"(\d+)([smhd])")
        matches = time_regex.findall(duration)
        
        if not matches:
            return await ctx.warning("Invalid duration format. Use: 10s, 5m, 2h, 1d")
        
        seconds = 0
        for value, unit in matches:
            value = int(value)
            if unit == 's':
                seconds += value
            elif unit == 'm':
                seconds += value * 60
            elif unit == 'h':
                seconds += value * 3600
            elif unit == 'd':
                seconds += value * 86400
        
        await member.add_roles(role)
        await ctx.success(f"Gave {member.mention} {role.mention} for **{duration}**")
        
        await asyncio.sleep(seconds)
        
        if role in member.roles:
            await member.remove_roles(role)
    
    @commands.command(
        name="chunkban",
        description="Ban all members who joined within a time range",
        usage="<start_time> <end_time>",
        brief="ban members"
    )
    @commands.has_permissions(ban_members=True)
    async def chunkban(self, ctx, start_minutes: int, end_minutes: int = 0):
        """Ban all members who joined within a time range"""
        now = datetime.now()
        start_time = now - timedelta(minutes=start_minutes)
        end_time = now - timedelta(minutes=end_minutes)
        
        to_ban = [m for m in ctx.guild.members if start_time <= m.joined_at <= end_time]
        
        if not to_ban:
            return await ctx.warning("No members found in that time range")
        
        msg = await ctx.send(f"Found **{len(to_ban)}** members. React with ✅ to confirm ban.")
        await msg.add_reaction("✅")
        
        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) == "✅" and reaction.message.id == msg.id
        
        try:
            await self.bot.wait_for('reaction_add', timeout=30.0, check=check)
        except asyncio.TimeoutError:
            return await ctx.warning("Chunkban cancelled")
        
        banned = 0
        for member in to_ban:
            try:
                await member.ban(reason=f"Chunkban by {ctx.author}")
                banned += 1
            except:
                continue
        
        await ctx.success(f"Banned **{banned}** members")
    
    @commands.command(
        name="modhistory",
        description="View moderation history for a member",
        usage="<member>",
        brief="any",
        aliases=["history"]
    )
    async def modhistory(self, ctx, member: Optional[Union[discord.Member, discord.User]] = None):
        """View moderation history for a member"""
        if not self.bot.db:
            return await ctx.warning("Database not available")
        
        member = member or ctx.author
        
        cases = await self.bot.db.fetch(
            "SELECT * FROM cases WHERE guild_id = $1 AND user_id = $2 ORDER BY timestamp DESC LIMIT 10",
            ctx.guild.id, member.id
        )
        
        if not cases:
            return await ctx.warning(f"{member.mention} has no moderation history")
        
        description = []
        for case in cases:
            mod = ctx.guild.get_member(case['moderator_id'])
            mod_name = mod.mention if mod else f"<@{case['moderator_id']}>"
            timestamp = f"<t:{int(case['timestamp'].timestamp())}:R>"
            description.append(f"**Case #{case['case_id']}** - {case['action']} by {mod_name} {timestamp}\n{case['reason']}")
        
        embed = discord.Embed(
            title=f"Moderation History for {member}",
            description="\n\n".join(description),
            color=self.color
        )
        await ctx.send(embed=embed)
    
    @commands.command(
        name="picperms",
        description="Allow/deny image permissions for a member",
        usage="<member>",
        brief="manage messages"
    )
    @commands.has_permissions(manage_messages=True)
    async def picperms(self, ctx, member: discord.Member):
        """Toggle image permissions for a member"""
        overwrite = ctx.channel.overwrites_for(member)
        
        if overwrite.attach_files is False:
            overwrite.attach_files = None
            overwrite.embed_links = None
            await ctx.channel.set_permissions(member, overwrite=overwrite)
            await ctx.success(f"Restored image permissions for {member.mention}")
        else:
            overwrite.attach_files = False
            overwrite.embed_links = False
            await ctx.channel.set_permissions(member, overwrite=overwrite)
            await ctx.success(f"Removed image permissions from {member.mention}")
    
    @commands.command(
        name="imute",
        description="Image mute a member (prevent sending images)",
        usage="<member>",
        brief="manage messages"
    )
    @commands.has_permissions(manage_messages=True)
    async def imute(self, ctx, member: discord.Member):
        """Image mute a member"""
        overwrite = ctx.channel.overwrites_for(member)
        overwrite.attach_files = False
        overwrite.embed_links = False
        await ctx.channel.set_permissions(member, overwrite=overwrite)
        await ctx.success(f"Image muted {member.mention}")
    
    @commands.command(
        name="rmute",
        description="Reaction mute a member (prevent adding reactions)",
        usage="<member>",
        brief="manage messages"
    )
    @commands.has_permissions(manage_messages=True)
    async def rmute(self, ctx, member: discord.Member):
        """Reaction mute a member"""
        overwrite = ctx.channel.overwrites_for(member)
        overwrite.add_reactions = False
        await ctx.channel.set_permissions(member, overwrite=overwrite)
        await ctx.success(f"Reaction muted {member.mention}")
    
    @commands.group(
        name="set",
        description="Server configuration commands",
        invoke_without_command=True
    )
    async def set(self, ctx):
        """Server configuration commands"""
        await ctx.send_help(ctx.command)
    
    @set.command(
        name="prefix",
        description="Set the server prefix",
        usage="<prefix>",
        brief="administrator"
    )
    @commands.has_permissions(administrator=True)
    async def set_prefix(self, ctx, prefix: str):
        """Set the server prefix"""
        if not self.bot.db:
            return await ctx.warning("Database not available")
        
        await self.bot.db.execute(
            "INSERT INTO prefixes (guild_id, prefix) VALUES ($1, $2) ON CONFLICT (guild_id) DO UPDATE SET prefix = $2",
            ctx.guild.id, prefix
        )
        await ctx.success(f"Server prefix set to `{prefix}`")
    
    @commands.command(
        name="protect",
        description="Protect a member from moderation",
        usage="<member>",
        brief="administrator"
    )
    @commands.has_permissions(administrator=True)
    async def protect(self, ctx, member: discord.Member):
        """Protect a member from moderation"""
        if not self.bot.db:
            return await ctx.warning("Database not available")
        
        check = await self.bot.db.fetchrow(
            "SELECT * FROM mod WHERE guild_id = $1 AND user_id = $2",
            ctx.guild.id, member.id
        )
        
        if check:
            await self.bot.db.execute(
                "DELETE FROM mod WHERE guild_id = $1 AND user_id = $2",
                ctx.guild.id, member.id
            )
            await ctx.success(f"Removed protection from {member.mention}")
        else:
            await self.bot.db.execute(
                "INSERT INTO mod (guild_id, user_id) VALUES ($1, $2)",
                ctx.guild.id, member.id
            )
            await ctx.success(f"Protected {member.mention} from moderation")

async def setup(bot):
    await bot.add_cog(Moderation(bot))
