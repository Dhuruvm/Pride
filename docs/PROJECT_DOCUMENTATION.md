# Pride Discord Bot - Complete Project Documentation

## Table of Contents
1. [Project Overview](#project-overview)
2. [Folder Structure Explained](#folder-structure-explained)
3. [Core Components](#core-components)
4. [Design Patterns](#design-patterns)
5. [Database System](#database-system)
6. [How Everything Works Together](#how-everything-works-together)

---

## Project Overview

Pride is a powerful Discord bot that helps server owners manage their communities. Think of it like a Swiss Army knife for Discord servers - it has tools for moderation (like kicking troublemakers), fun features (like music and giveaways), and utility functions (like welcome messages and level systems).

**What makes this bot special:**
- It's built to handle lots of servers at once (multi-server support)
- Everything is customizable per server
- It stores data safely in a database so nothing gets lost
- It has a beautiful, consistent design with embeds and buttons

---

## Folder Structure Explained

### `bot/` - The Brain of the Bot
This folder contains the core code that makes everything work:

**`bot.py`** - The Main Bot Class
- This is like the control center of your bot
- Contains the `Pride` class which is the actual bot
- Handles startup, connecting to Discord, loading features
- Sets up important things like colors, emojis, database connections
- **Key Features:**
  - Bot colors: `0xFFFFFF` (white) for embeds
  - Custom emojis: approve, deny, warning icons
  - Command prefix system (customizable per server and per user)
  - Connects to PostgreSQL database for storing data
  - Connects to Redis for fast temporary storage
  - Loads all commands and features from the cogs folder

**`helpers.py`** - Helper Functions
- Contains `PrideContext` - this extends Discord's basic message context
- Adds custom response methods that make coding easier:
  - `ctx.success()` - Shows a green checkmark message
  - `ctx.error()` - Shows a red X message  
  - `ctx.warning()` - Shows a warning message
  - `ctx.paginate()` - Creates multi-page embeds with navigation buttons
- Contains `HelpCommand` - The default help system (we're creating a better one!)
- Contains `StartUp` - Loads all your commands when the bot starts

**`ext.py`** - Extension Functions
- The `Client` class provides utility functions used across the bot
- **Useful Functions:**
  - `human_format()` - Converts big numbers (1000 → 1K)
  - `relative_time()` - Shows how long ago something happened ("2 days ago")
  - `is_dangerous()` - Checks if a role has admin permissions
  - `uptime` - Shows how long the bot has been running
  - `ping` - Shows bot latency in milliseconds
- Contains `PaginatorView` - The button system for navigating multi-page embeds
  - Left/Right arrows to change pages
  - Jump to specific page with modal
  - Delete button to remove the message

**`database.py`** - Database Tables Setup
- Creates all the database tables when the bot starts
- Think of tables like Excel spreadsheets - each one stores different information
- **Major Tables:**
  - `prefixes` - Custom command prefixes for each server
  - `levels` - XP and level data for members
  - `tickets` - Support ticket system
  - `marry` - Marriage system for fun
  - `lastfm` - Music listening data
  - `warns` - Warning records for moderation
  - `cases` - Moderation action history
  - And 80+ more tables for all features!

**`headers.py`** - HTTP Request Handler
- The `Session` class handles downloading stuff from the internet
- Used for getting images, making API calls, etc.
- Has smart features like:
  - Proxy rotation (to avoid rate limits)
  - File size limits (won't download files bigger than 500MB)
  - JSON parsing with orjson (super fast)
  - Converts data to different formats (text, bytes, JSON)

**`dynamicrolebutton.py`** - Dynamic Role Buttons
- Creates clickable buttons that give/remove roles
- Uses regex pattern matching: `RB:{message_id}:{role_id}`
- When clicked, toggles the role on/off for that user
- Persists across bot restarts (timeout=None)

---

### `cogs/` - Feature Modules

Think of cogs like apps on your phone - each one adds specific features to the bot.

**`moderation.py`** - Server Management Commands
- Over 45+ moderation commands
- **Key Commands:**
  - `cleanup` - Remove bot messages
  - `purge` - Delete multiple messages at once
  - `role` - Add/remove roles from members
  - `ban/unban` - Ban or unban users
  - `kick` - Kick users from server
  - `mute/unmute` - Prevent users from talking
  - `warn` - Give warnings to users
  - `hardban` - Permanent ban system
  - `lockdown/unlockdown` - Lock channels
  - `nuke` - Delete and recreate channel
- Creates moderation cases in database for tracking
- Permission-based system (you need proper permissions to use these)

**`voicemaster.py`** - Voice Channel Management
- Lets users create temporary voice channels
- Buttons to control your temporary voice channel
- Currently skeleton code (needs implementation)

**`ticket.py`** - Support Ticket System
- `CreateTicket` view - Button to open new support tickets
- `DeleteTicket` view - Button to close tickets
- Creates private channels for support conversations
- Currently skeleton code (needs implementation)

**`giveaway.py`** - Giveaway System
- `GiveawayView` - Persistent button for entering giveaways
- Tracks participants in database
- Currently skeleton code (needs implementation)

**`music.py`** - Music Player
- Integrates with Lavalink server for playing music
- Commands to play, pause, skip songs
- Queue management
- Currently skeleton code (needs implementation)

---

### `events/` - Event Handlers

This folder handles things that happen in Discord (like when someone joins the server).

Currently empty - events can be added here like:
- `on_member_join` - Welcome new members
- `on_message` - React to messages
- `on_guild_join` - Setup when bot joins new server

---

### `rivalapi/` - Custom API Integration

**`rivalapi.py`** - Wrapper for RivalAPI service
- Minimal implementation currently
- Can be expanded for custom API features

---

### Root Files

**`main.py`** - The Entry Point
- This is what runs when you start the bot
- Checks for DISCORD_TOKEN environment variable
- Creates the bot instance
- Handles graceful shutdown:
  - Closes database connections properly
  - Closes Redis connections
  - Prevents data loss

**`pyproject.toml`** - Project Configuration
- Lists all the Python libraries the bot needs
- Managed by `uv` package manager
- Dependencies include:
  - discord.py - Discord API wrapper
  - asyncpg - PostgreSQL database
  - redis - Redis cache
  - pomice - Music system
  - jishaku - Debug tools

**`replit.md`** - Project Memory
- Stores important information about the project
- Architecture decisions
- Recent changes
- User preferences

---

## Core Components

### 1. Embed System

The bot uses Discord embeds for beautiful messages. Embeds are like fancy message boxes with:
- Titles
- Descriptions
- Fields (organized information)
- Colors (currently white: 0xFFFFFF)
- Footers
- Images/thumbnails

**Standard Pattern:**
```python
embed = discord.Embed(
    title="Title Here",
    description="Description here",
    color=self.bot.color  # Always use bot.color for consistency
)
embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
embed.add_field(name="Field Name", value="Field Value")
embed.set_footer(text="Footer text")
await ctx.reply(embed=embed)
```

### 2. Context Response System

Instead of typing `await ctx.send(embed=discord.Embed(...))` every time, we use shortcuts:

- `await ctx.success("Message")` - Green checkmark
- `await ctx.error("Message")` - Red X
- `await ctx.warning("Message")` - Warning icon
- `await ctx.neutral("Message")` - No icon

### 3. Button & View System

Discord UI components (buttons, dropdowns) use the View system:
- Views contain UI components (buttons, select menus, etc.)
- `timeout=None` makes them persist across bot restarts
- Custom IDs help identify which button was clicked
- Callbacks handle the button clicks

**Dynamic Items:**
- Use regex patterns for flexibility
- Example: `DynamicRoleButton` uses pattern `RB:{message_id}:{role_id}`
- Must be registered in `setup_hook()` with `bot.add_dynamic_items()`

### 4. Pagination System

Multi-page embeds use the `PaginatorView`:
- Automatically adds navigation buttons
- Left/Right arrows to navigate
- Jump to page modal
- Delete button
- Tracks current page with `self.i`

### 5. Permission System

Commands check permissions before running:
```python
@commands.has_permissions(manage_messages=True)
async def command(self, ctx):
    # Command code
```

Also checks if bot has permission:
```python
if not ctx.guild.me.guild_permissions.manage_messages:
    return await ctx.warning("I need manage messages permission!")
```

### 6. Database Pattern

All database operations use asyncpg:
```python
# Get data
data = await self.bot.db.fetchrow("SELECT * FROM table WHERE id = $1", id)

# Insert data
await self.bot.db.execute("INSERT INTO table (col) VALUES ($1)", value)

# Update data
await self.bot.db.execute("UPDATE table SET col = $1 WHERE id = $2", value, id)
```

Always check if database exists:
```python
if not self.bot.db:
    return await ctx.warning("Database not available")
```

### 7. Redis Cache Pattern

Use Redis for temporary/frequently accessed data:
```python
# Store data
await self.bot.redis.set("key", value, ex=3600)  # ex = seconds until expiry

# Get data
data = await self.bot.redis.get("key")

# Delete data
await self.bot.redis.delete("key")
```

Redis automatically handles JSON serialization.

---

## Design Patterns

### 1. Consistent Color Scheme
- All embeds use `self.bot.color` (0xFFFFFF - white)
- Error embeds use `self.bot.error_color` (0xFFFFFF)
- Never hardcode colors - always use bot properties

### 2. Emoji System
Custom emojis for consistent visual language:
- `self.bot.yes` - Approve/success icon
- `self.bot.no` - Deny/error icon
- `self.bot.warning` - Warning icon
- `self.bot.left` / `self.bot.right` - Navigation arrows
- `self.bot.goto` - Jump to page icon

### 3. Command Structure

**Single Commands:**
```python
@commands.command(
    name="command_name",
    description="What this command does",
    usage="<required> [optional]",
    brief="required permission or 'any'",
    aliases=["alias1", "alias2"]
)
@commands.has_permissions(permission_name=True)
async def command_name(self, ctx, param: type):
    # Command logic
```

**Command Groups:**
```python
@commands.group(invoke_without_command=True)
async def groupname(self, ctx):
    # Shows help for group
    await ctx.create_pages()

@groupname.command(name="subcommand")
async def groupname_subcommand(self, ctx):
    # Subcommand logic
```

### 4. Error Handling Pattern

The bot handles errors globally in `bot.py`:
- CommandNotFound - Ignored
- MissingPermissions - Shows permission needed
- CommandOnCooldown - Shows retry time
- MissingRequiredArgument - Shows command help
- BadArgument - Shows specific error

Individual commands don't need try/except for these.

### 5. Reskin System

Users can change how their messages appear:
- Messages check for reskin in database
- If enabled, creates webhook with custom name/avatar
- Sends message through webhook instead of bot

### 6. Prefix System

Two-tier prefix system:
- Guild prefix (applies to whole server)
- Self prefix (personal prefix overrides guild prefix)
- Default prefix: `;`
- Retrieved by `PrideContext.getprefix()`

---

## Database System

### How It Works

1. **Connection:** Bot connects to PostgreSQL on startup
2. **Table Creation:** `create_db()` runs and creates all tables if they don't exist
3. **Queries:** Commands use `self.bot.db` to read/write data
4. **Async:** All database operations are async (use `await`)

### Important Tables Explained

**Moderation:**
- `cases` - Tracks all moderation actions (bans, kicks, etc.)
- `warns` - Warning history for users
- `jail` - Users who are jailed (can't talk)
- `hardban` - Permanent bans that can't be undone

**Customization:**
- `prefixes` - Server custom prefixes
- `selfprefix` - User personal prefixes
- `invoke` - Custom commands
- `autoreact` - Auto-reactions to messages

**Levels & XP:**
- `levels` - User XP, level, and total XP
- `levelsetup` - Channel and destination for level-up messages
- `levelroles` - Roles awarded at specific levels

**Social:**
- `marry` - Marriage system
- `afk` - AFK status and reason
- `seen` - Last seen timestamp
- `oldusernames` - Username history

**Tickets:**
- `tickets` - Ticket system configuration
- `opened_tickets` - Currently open tickets
- `ticket_topics` - Available ticket categories
- `ticket_support` - Support roles

**Welcome/Leave:**
- `welcome` - Welcome message and channel
- `leave` - Leave message and channel
- `boost` - Boost message and channel
- `autorole` - Roles given on join

**Voice:**
- `voicemaster` - Voice master setup
- `vcs` - User temporary voice channels

**Music:**
- `lastfm` - Last.fm usernames
- `lastfmcc` - Last.fm custom commands
- `lfcrowns` - Artist crowns

**Giveaways:**
- `giveaway` - Active giveaways
- `gw_ended` - Ended giveaways

**And many more!** (80+ tables total)

---

## How Everything Works Together

### Bot Startup Sequence

1. `main.py` runs
2. Checks for DISCORD_TOKEN
3. Creates `Pride()` bot instance
4. `setup_hook()` runs:
   - Loads jishaku (debug extension)
   - Connects to database
   - Connects to Redis
   - Loads all cogs from `cogs/` folder
   - Loads all events from `events/` folder
   - Registers persistent views (buttons)
   - Creates database tables
5. Bot connects to Discord
6. `on_ready()` runs
7. Bot is now online and ready!

### Command Flow

1. User sends message: `;help`
2. `on_message` event fires
3. Bot checks rate limits
4. Bot processes command
5. Bot finds `help` command
6. Command checks permissions
7. Command runs
8. Response sent to user

### Cog System

Cogs are like plugins:
- Each cog file in `cogs/` folder
- Must have `async def setup(bot)` function
- Bot loads with `await bot.load_extension("cogs.filename")`
- Can be reloaded without restarting bot
- Organizes commands by category

### Persistent Views

Buttons/views that work after bot restart:
1. Create View class with `timeout=None`
2. Register in `setup_hook()` with `bot.add_view()`
3. For dynamic items, use `bot.add_dynamic_items()`
4. Custom IDs must be unique and persistent

### Database Flow

1. Bot starts → Connects to PostgreSQL
2. Creates tables if missing
3. Commands query database as needed
4. Data persists even after bot restarts
5. Graceful shutdown closes connection properly

### Redis Cache Flow

1. Bot starts → Connects to Redis
2. Commands store temporary data
3. Data expires automatically (set with `ex=` parameter)
4. Much faster than database for frequently accessed data
5. Good for rate limiting, temporary state

---

## Summary

**Key Takeaways:**

1. **bot/** = Core bot code (brain)
2. **cogs/** = Features (apps)
3. **events/** = Event handlers (reactions to Discord events)
4. **Embeds** = Pretty messages
5. **Views** = Buttons and dropdowns
6. **Database** = Permanent storage
7. **Redis** = Temporary fast storage
8. **Context helpers** = Easy response methods
9. **Pagination** = Multi-page navigation
10. **Cog system** = Modular features

Everything follows consistent patterns, uses the same colors and emojis, and is designed to be easy to extend and maintain!
