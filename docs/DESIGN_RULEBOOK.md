# Pride Bot - Design Rulebook & Guidelines

## Purpose
This document establishes permanent design rules and patterns for the Pride Discord Bot project. All code, features, and modifications MUST follow these guidelines to maintain consistency, quality, and maintainability.

---

## 🎨 Visual Design Rules

### Color Scheme
**RULE:** All embeds MUST use the standard bot color.

```python
# ✅ CORRECT
embed = discord.Embed(color=self.bot.color)

# ❌ WRONG - Never hardcode colors
embed = discord.Embed(color=0xFF0000)
```

**Standard Colors:**
- Primary: `self.bot.color` (0xFFFFFF - White)
- Error: `self.bot.error_color` (0xFFFFFF - White)

**Never:**
- Hardcode hex colors directly
- Use random or inconsistent colors
- Change colors per feature

---

### Emoji System
**RULE:** Always use bot's custom emojis for consistency.

```python
# ✅ CORRECT
await ctx.reply(f"{self.bot.yes} Success message")

# ❌ WRONG - Don't use Unicode emojis for these
await ctx.reply("✅ Success message")
```

**Standard Emojis:**
- Success: `self.bot.yes`
- Error: `self.bot.no`
- Warning: `self.bot.warning`
- Left Arrow: `self.bot.left`
- Right Arrow: `self.bot.right`
- Jump: `self.bot.goto`

**When to use Unicode emojis:**
- Decorative purposes only
- Category icons
- User-facing fun commands

---

### Embed Structure
**RULE:** Follow the standard embed pattern.

```python
# ✅ CORRECT PATTERN
embed = discord.Embed(
    title="Clear Title",
    description="Informative description",
    color=self.bot.color
)
embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
embed.add_field(name="Field Name", value="Field Value", inline=False)
embed.set_footer(text="Additional info", icon_url=ctx.author.display_avatar.url)
await ctx.reply(embed=embed)
```

**Embed Rules:**
- Always set author for user-specific commands
- Use clear, descriptive titles
- Keep descriptions concise (under 2000 characters)
- Use fields for organized information
- Include footers for metadata (page numbers, module names)

**Never:**
- Create walls of text in description
- Use more than 25 fields
- Skip setting the color
- Use images/thumbnails excessively

---

## 💬 Response System

### Context Response Methods
**RULE:** Use built-in context methods for standard responses.

```python
# ✅ CORRECT
await ctx.success("Operation completed!")
await ctx.error("Something went wrong")
await ctx.warning("Be careful!")
await ctx.neutral("Information message")

# ❌ WRONG - Don't manually create embeds for these
await ctx.reply(embed=discord.Embed(color=self.bot.color, description=f"{self.bot.yes} Operation completed!"))
```

**When to use each:**
- `ctx.success()` - Successful operations, confirmations
- `ctx.error()` - Failures, invalid input, errors
- `ctx.warning()` - Warnings, cautions, non-critical issues
- `ctx.neutral()` - Information without positive/negative connotation

**For interactions (slash commands):**
```python
await self.bot.ext.success(interaction, "Message", ephemeral=True)
await self.bot.ext.error(interaction, "Message", ephemeral=True)
await self.bot.ext.warning(interaction, "Message", ephemeral=True)
```

---

## 📝 Command Structure

### Command Metadata
**RULE:** All commands MUST have complete metadata.

```python
@commands.command(
    name="commandname",           # Required: command name
    description="What it does",   # Required: clear description
    usage="<arg1> [arg2]",        # Required: usage format
    brief="permission name",       # Required: permission or "any"
    aliases=["alias1", "alias2"]  # Optional: alternative names
)
```

**Usage Format Rules:**
- `<argument>` = Required parameter
- `[argument]` = Optional parameter
- `<arg1|arg2>` = One of multiple choices
- Clear, descriptive parameter names

**Examples:**
```python
usage="<member> <amount>"           # Ban command
usage="[amount]"                    # Purge with default
usage="<member> <role>"             # Role add/remove
usage="<setting> <on|off>"          # Toggle commands
```

---

### Permission Checks
**RULE:** Always check permissions properly.

```python
# ✅ CORRECT - Use decorators
@commands.has_permissions(manage_messages=True)
async def purge(self, ctx, amount: int):
    pass

# ✅ CORRECT - Check bot permissions too
@commands.command()
@commands.has_permissions(ban_members=True)
async def ban(self, ctx, member: discord.Member):
    if not ctx.guild.me.guild_permissions.ban_members:
        return await ctx.warning("I don't have ban members permission!")
    # Rest of code
```

**Permission Hierarchy Check:**
```python
# ✅ CORRECT - Check role hierarchy
if role.position >= ctx.guild.me.top_role.position:
    return await ctx.warning("I cannot manage this role")

if role.position >= ctx.author.top_role.position and ctx.author.id != ctx.guild.owner_id:
    return await ctx.warning("You cannot manage this role")
```

---

### Command Groups
**RULE:** Use groups for related commands.

```python
# ✅ CORRECT
@commands.group(invoke_without_command=True)
async def config(self, ctx):
    """Show config help"""
    await ctx.send_help(ctx.command)

@config.command(name="prefix")
async def config_prefix(self, ctx, prefix: str):
    """Set server prefix"""
    pass

@config.command(name="color")
async def config_color(self, ctx, color: str):
    """Set embed color"""
    pass
```

**Usage:**
- `;config` - Shows help for all subcommands
- `;config prefix !` - Runs specific subcommand
- Keeps related features organized

---

## 🗄️ Database Patterns

### Database Safety
**RULE:** Always check database availability.

```python
# ✅ CORRECT
if not self.bot.db:
    return await ctx.warning("Database features are disabled")

data = await self.bot.db.fetchrow("SELECT * FROM table WHERE id = $1", id)
```

**Never:**
- Assume database is always available
- Skip error handling for database operations
- Use f-strings for SQL queries (SQL injection risk)

---

### Query Patterns
**RULE:** Use parameterized queries.

```python
# ✅ CORRECT - Parameterized
await self.bot.db.execute(
    "INSERT INTO table (col1, col2) VALUES ($1, $2)",
    value1, value2
)

# ❌ WRONG - SQL injection vulnerable
await self.bot.db.execute(
    f"INSERT INTO table (col1) VALUES ('{user_input}')"
)
```

**Common Operations:**
```python
# Fetch single row
row = await self.bot.db.fetchrow("SELECT * FROM table WHERE id = $1", id)

# Fetch multiple rows
rows = await self.bot.db.fetch("SELECT * FROM table WHERE guild_id = $1", guild_id)

# Fetch single value
count = await self.bot.db.fetchval("SELECT COUNT(*) FROM table")

# Insert/Update/Delete
await self.bot.db.execute("INSERT INTO table (col) VALUES ($1)", value)

# Check existence
exists = await self.bot.db.fetchrow("SELECT * FROM table WHERE id = $1", id)
if exists:
    # Update
else:
    # Insert
```

---

### Redis Cache Patterns
**RULE:** Use Redis for temporary, frequently-accessed data.

```python
# ✅ CORRECT - Set with expiry
await self.bot.redis.set(f"cooldown:{user_id}", "true", ex=60)

# ✅ CORRECT - Get data
data = await self.bot.redis.get(f"cache:{guild_id}")

# ✅ CORRECT - Delete
await self.bot.redis.delete(f"temp:{key}")
```

**Best Practices:**
- Use descriptive key names with prefixes: `cooldown:`, `cache:`, `temp:`
- Always set expiry times (`ex=seconds`)
- Use for: cooldowns, rate limits, temporary state
- Don't use for: permanent data, critical data

---

## 🎮 UI Components

### Button Views
**RULE:** Persistent views must have `timeout=None`.

```python
# ✅ CORRECT - Persistent view
class MyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="Click", custom_id="unique_id")
    async def button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Clicked!")

# Must register in setup_hook
bot.add_view(MyView())
```

**Temporary Views:**
```python
# ✅ CORRECT - Temporary view (auto-cleanup)
class TempView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=180)  # 3 minutes
```

**Rules:**
- Persistent views: `timeout=None` + `custom_id` required
- Temporary views: set reasonable timeout (60-300 seconds)
- Always validate user in callbacks
- Register persistent views in `setup_hook()`

---

### Select Menus
**RULE:** Use select menus for multiple choices.

```python
# ✅ CORRECT
class MySelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Option 1", description="Description", emoji="🎮"),
            discord.SelectOption(label="Option 2", description="Description", emoji="🎵"),
        ]
        super().__init__(
            placeholder="Choose an option...",
            min_values=1,
            max_values=1,
            options=options
        )
    
    async def callback(self, interaction: discord.Interaction):
        selected = self.values[0]
        await interaction.response.send_message(f"You selected: {selected}")
```

**When to use:**
- More than 5 options (buttons limited to 5 per row)
- Categorized choices
- Navigation menus

---

### Dynamic Items
**RULE:** Use dynamic items for flexible, persistent components.

```python
# ✅ CORRECT - Dynamic button pattern
class DynamicButton(discord.ui.DynamicItem[discord.ui.Button], template=r'PREFIX:(?P<id>[0-9]+)'):
    def __init__(self, item_id: int):
        super().__init__(
            discord.ui.Button(
                label="Button",
                custom_id=f'PREFIX:{item_id}',
            )
        )
        self.item_id = item_id
    
    @classmethod
    async def from_custom_id(cls, interaction: discord.Interaction, item: discord.ui.Button, match, /):
        item_id = int(match['id'])
        return cls(item_id)
    
    async def callback(self, interaction: discord.Interaction):
        # Handle click
        pass

# Register in setup_hook
bot.add_dynamic_items(DynamicButton)
```

---

## 📊 Pagination

### PaginatorView Pattern
**RULE:** Use existing PaginatorView for multi-page embeds.

```python
# ✅ CORRECT
embeds = [
    discord.Embed(title="Page 1", description="Content 1", color=self.bot.color),
    discord.Embed(title="Page 2", description="Content 2", color=self.bot.color),
    discord.Embed(title="Page 3", description="Content 3", color=self.bot.color),
]
await ctx.paginator(embeds)

# Or use helper methods
await ctx.paginate(contents, title="List Title")  # For lists
await ctx.index(contents, title="Indexed List")   # For numbered lists
```

**Never:**
- Create custom paginator when existing one works
- Forget to set page numbers in footers
- Make navigation confusing

---

## 🔧 Error Handling

### Global Error Handler
**RULE:** Use global error handler; don't duplicate error handling in commands.

The bot has a global error handler in `bot.py` that handles:
- CommandNotFound
- MissingPermissions
- CommandOnCooldown
- MissingRequiredArgument
- BadArgument
- And more...

```python
# ✅ CORRECT - Let global handler manage it
@commands.command()
async def mycommand(self, ctx, member: discord.Member):
    # Just write the logic
    await ctx.success(f"Hello {member.mention}")

# ❌ WRONG - Unnecessary try/except
@commands.command()
async def mycommand(self, ctx, member: discord.Member):
    try:
        await ctx.success(f"Hello {member.mention}")
    except commands.MemberNotFound:
        await ctx.error("Member not found")  # Global handler already does this!
```

**When to use try/except:**
- External API calls
- File operations
- Database-specific errors
- Custom error scenarios not covered globally

---

### Database Error Handling
**RULE:** Handle database-specific errors gracefully.

```python
# ✅ CORRECT
try:
    await self.bot.db.execute("INSERT INTO table (unique_col) VALUES ($1)", value)
    await ctx.success("Added successfully!")
except Exception as e:
    if "unique constraint" in str(e).lower():
        await ctx.warning("This already exists!")
    else:
        await ctx.error("Database error occurred")
```

---

## 🏗️ Code Organization

### File Structure
**RULE:** Organize code logically.

```
bot/
  bot.py         - Main bot class
  helpers.py     - Context helpers, help command
  ext.py         - Extension utilities
  database.py    - Database schema
  headers.py     - HTTP session
  dynamicrolebutton.py - Dynamic UI components

cogs/
  moderation.py  - Moderation commands
  music.py       - Music commands
  utility.py     - Utility commands
  [feature].py   - One cog per feature category

events/
  on_member_join.py  - Join events
  on_message.py      - Message events
  [event].py         - One file per event type
```

---

### Cog Structure
**RULE:** Follow standard cog template.

```python
import discord
from discord.ext import commands
from typing import Optional

class CogName(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.color = 0xFFFFFF
    
    @commands.command(
        name="command",
        description="Description",
        usage="<args>",
        brief="permission"
    )
    async def command_name(self, ctx: commands.Context):
        """Command logic"""
        pass

async def setup(bot: commands.Bot):
    await bot.add_cog(CogName(bot))
```

**Rules:**
- Always include `__init__(self, bot)`
- Always include `async def setup(bot)`
- Group related commands in same cog
- Keep cogs focused (single responsibility)

---

## 🎯 Best Practices

### Naming Conventions

**Commands:**
- Lowercase, single word or compound: `userinfo`, `serverinfo`
- Clear, descriptive names
- Aliases for common abbreviations

**Functions:**
- snake_case: `get_user_data()`, `check_permissions()`
- Verb-based for actions: `create_ticket()`, `delete_message()`

**Classes:**
- PascalCase: `PrideContext`, `ModerationCog`
- Descriptive, specific names

**Variables:**
- snake_case: `user_id`, `guild_config`
- Descriptive, not abbreviated

---

### Performance

**RULE:** Optimize database queries.

```python
# ✅ CORRECT - Batch operations
async with self.bot.db.acquire() as conn:
    async with conn.transaction():
        for item in items:
            await conn.execute("INSERT INTO table VALUES ($1)", item)

# ❌ WRONG - Multiple individual queries
for item in items:
    await self.bot.db.execute("INSERT INTO table VALUES ($1)", item)
```

**RULE:** Use Redis for frequent reads.

```python
# ✅ CORRECT - Cache frequently accessed data
cached = await self.bot.redis.get(f"guild_config:{guild_id}")
if cached:
    return cached

data = await self.bot.db.fetchrow("SELECT * FROM config WHERE guild_id = $1", guild_id)
await self.bot.redis.set(f"guild_config:{guild_id}", data, ex=300)  # Cache 5 min
return data
```

---

### Code Comments

**RULE:** Comment complex logic only.

```python
# ✅ CORRECT - Comments explain WHY, not WHAT
# Check hierarchy to prevent users from managing roles above them
if role.position >= ctx.author.top_role.position:
    return await ctx.warning("Cannot manage this role")

# ❌ WRONG - Obvious comments
# Send a success message
await ctx.success("Done!")
```

**When to comment:**
- Complex algorithms
- Non-obvious business logic
- Workarounds for known issues
- Important security checks

**Never comment:**
- Obvious code
- What the code does (code should be self-explanatory)
- Outdated information

---

## 🚀 Deployment

### Environment Variables
**RULE:** Use environment variables for configuration.

```python
# ✅ CORRECT
token = os.environ.get("DISCORD_TOKEN")
database_url = os.environ.get("DATABASE_URL")

# ❌ WRONG - Hardcoded secrets
token = "MTIzNDU2Nzg5..."  # NEVER!
```

**Required:**
- `DISCORD_TOKEN` - Bot token

**Optional:**
- `DATABASE_URL` - PostgreSQL connection
- `REDIS_URL` - Redis connection
- `PROXIES` - Proxy list
- Custom API keys

---

### Graceful Shutdown
**RULE:** Clean up resources on shutdown.

```python
# Already implemented in main.py
finally:
    if bot.db:
        await bot.db.close()
    if bot.redis:
        await bot.redis.close()
    await bot.close()
```

**Always close:**
- Database connections
- Redis connections
- HTTP sessions
- File handles

---

## ✅ Summary Checklist

Before committing code, verify:

- [ ] Uses `self.bot.color` for embeds
- [ ] Uses bot emoji properties (`self.bot.yes`, etc.)
- [ ] Includes complete command metadata
- [ ] Checks permissions properly
- [ ] Uses context response methods
- [ ] Has database availability checks
- [ ] Uses parameterized queries
- [ ] Follows naming conventions
- [ ] Has proper error handling
- [ ] Documented complex logic
- [ ] No hardcoded secrets
- [ ] Persistent views registered in setup_hook
- [ ] Follows file organization structure

---

## 🔄 Future Changes

If you need to modify these rules:
1. Discuss with team first
2. Update this document
3. Refactor existing code to match
4. Document the change reason

**This rulebook ensures consistency, maintainability, and quality across the entire Pride Bot project.**
