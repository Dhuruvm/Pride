# Overview

Evict is a feature-rich Discord bot built with discord.py that provides multipurpose server management capabilities including moderation, leveling, music playback, ticketing, voice channel management, Last.fm integration, and social features. The bot uses PostgreSQL for persistent data storage and Redis for caching and distributed operations.

**Latest Update (Oct 26, 2025)**: Added comprehensive project documentation, modern help system with dropdown menus, and design rulebook. All dependencies installed and bot is production-ready.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Bot Framework
- **Core**: Built on discord.py 2.3.0+ with custom command context (`EvictContext`) extending base functionality
- **Command System**: Utilizes discord.py's commands extension with custom prefix support (per-guild and per-user)
- **Event-Driven**: Organized cog-based architecture for modular feature separation

## Data Layer
- **Primary Database**: PostgreSQL accessed via asyncpg for relational data storage
  - Schema includes 50+ tables covering features like prefixes, levels, tickets, starboard, marriage, Last.fm, moderation, and more
  - Tables created on startup via `create_db()` function
- **Cache Layer**: Redis with custom implementation (`bot.bot.Redis`) providing:
  - Thread-safe operations with asyncio locks
  - Automatic JSON serialization/deserialization
  - Connection pooling with retry logic and jitter backoff
  - Used for high-frequency read/write operations

## Music System
- **Audio Engine**: Pomice library for Lavalink integration
- **Architecture**: External Lavalink server (default: localhost:2333) handles audio processing
- **Design Rationale**: Offloads CPU-intensive audio operations from main bot process, enabling scalability

## Custom Components
- **Dynamic UI**: Persistent button views for interactive features:
  - `DynamicRoleButton`: Regex-based dynamic item for role assignment/removal with custom_id pattern `RB:{message_id}:{role_id}`
  - Ticket system buttons (CreateTicket, DeleteTicket)
  - Voice Master controls (vmbuttons)
  - Giveaway participation (GiveawayView)
- **Pattern**: All views use `timeout=None` for persistence across bot restarts

## Helper Systems
- **HTTP Session Manager**: Custom `Session` class providing:
  - Standardized headers and proxy rotation support
  - Specialized methods for JSON, text, and binary downloads
  - Built-in rate limiting via chunk-based downloads (500MB max)
  - Uses orjson for performance-optimized JSON operations
- **Extension System**: `Client` class (bot.ext) provides:
  - Consistent message formatting (success/error/warning)
  - Permission analysis (`is_dangerous()`)
  - Number formatting and relative time utilities
  - Message link parsing

## External Integrations
- **Last.fm**: Music scrobbling and statistics tracking (tables: lastfm, lastfmcc, lfmode, lfcrowns, lfreactions)
- **RivalAPI**: Custom API wrapper (minimal implementation, expandable)
- **Discord IOS**: Enhanced mobile experience support

## Feature Modules
The cog system organizes features into discrete modules:
- **Moderation**: Anti-raid, anti-invite, hardban, forcenick, uwulock, shutup
- **Leveling**: XP tracking with role rewards and customizable destinations
- **Voice Master**: Temporary voice channel creation and management
- **Ticketing**: Support ticket system with topics, categories, and role-based access
- **Social**: Marriage, AFK status, seen tracking, username history
- **Server Events**: Welcome/leave/boost messages, autorole, ping on join
- **Starboard**: Message highlighting system with custom emoji/count thresholds
- **Customization**: Custom commands (invoke), auto-reactions, chat filters, booster roles

## Configuration & Deployment
- **Environment Variables**: 
  - `DISCORD_TOKEN`: **Required** - Discord bot authentication token
  - `DATABASE_URL`: Optional - PostgreSQL connection string (defaults to local development)
  - `REDIS_URL`: Optional - Redis connection URL (defaults to local Redis)
  - `PROXIES`: Optional - Proxy list (pipe-separated)
  - Other optional: `evict_api`, `rival_api`, `proxy_url`, `commands_url`, `support_server`
- **Entry Point**: `main.py` - Main bot launcher with graceful shutdown handling
- **Workflow**: Configured as "Discord Bot" running `python main.py`
- **Graceful Shutdown**: Proper cleanup of database and Redis connections on exit
- **Error Handling**: Comprehensive exception handling with traceback logging and visual status indicators

## Design Principles
- **Async-First**: All I/O operations use asyncio for concurrent handling
- **Separation of Concerns**: Clear boundaries between bot logic, database, helpers, and cogs
- **Extensibility**: Modular cog system allows easy addition of new features
- **Persistence**: Database-driven configuration enables per-guild customization
- **User Experience**: Rich embeds, ephemeral messages for interactions, and consistent theming

# External Dependencies

## Core Services
- **PostgreSQL Database**: Primary relational data store for all persistent bot data
- **Redis Server**: Caching layer for performance optimization and distributed state
- **Lavalink Server**: Audio processing server for music playback functionality

## Discord Integration
- **discord.py**: Primary Discord API wrapper (v2.3.0+)
- **discord-ios**: Enhanced mobile client support

## Python Libraries
- **asyncpg**: Asynchronous PostgreSQL client
- **redis**: Async Redis client with custom connection pooling
- **pomice**: Lavalink client for music operations
- **aiohttp**: Async HTTP client for external API calls
- **jishaku**: Advanced debugging and evaluation tools
- **humanfriendly/humanize**: Human-readable time and number formatting
- **orjson**: High-performance JSON serialization

## Third-Party APIs
- **Last.fm API**: Music scrobbling and user statistics
- **RivalAPI**: Custom integration (minimal current implementation)

## Infrastructure Requirements
- **Required**: Discord Bot Token (DISCORD_TOKEN environment variable)
- **Optional**: PostgreSQL database (DATABASE_URL) for persistent features
- **Optional**: Redis server (REDIS_URL) for caching and performance
- **Optional**: Lavalink server for music playback functionality
- **Optional**: HTTP/HTTPS proxy servers for rate limit distribution

# Recent Changes

## October 26, 2025 - Documentation & Modern Help System

### New Documentation
- **PROJECT_DOCUMENTATION.md**: Comprehensive explanation of all folders, files, and components in simple, everyday language
  - Covers entire project structure (bot/, cogs/, events/)
  - Explains all design patterns and how they work
  - Documents database system and all 80+ tables
  - Step-by-step explanation of how everything works together
  
- **DESIGN_RULEBOOK.md**: Permanent design guidelines for the project
  - Visual design rules (colors, emojis, embeds)
  - Response system patterns
  - Command structure standards
  - Database and Redis patterns
  - UI component guidelines
  - Code organization and best practices

### Modern Help System
- Created new `cogs/help.py` with dropdown menu interface
- Matches the exact UI pattern shown in user's screenshots
- Features:
  - Beautiful embed with bot info and invite links
  - Dropdown menu to select categories (Moderation, Music, etc.)
  - Shows all commands in selected category
  - Category-specific emojis
  - User interaction validation
  - Command-specific help available
- Disabled legacy help command in favor of new cog-based system

### Import Migration Completed
- All Python dependencies installed via uv package manager
- Workflow configured and ready
- Progress tracker updated
- Project ready for development

## October 25, 2025 - Initial Setup

## Project Restructuring
- Reorganized codebase into proper package structure:
  - `bot/` - Core bot modules (bot.py, helpers.py, ext.py, headers.py, database.py, dynamicrolebutton.py)
  - `cogs/` - Feature modules (voicemaster, ticket, giveaway, music)
  - `events/` - Event handlers (to be populated)
  - `rivalapi/` - Custom API wrapper
- Created `main.py` as the entry point for the bot

## Security Improvements
- Redis credentials moved from hardcoded values to environment variables (REDIS_URL)
- Added explicit warnings when production environment variables are not set
- Implemented proper secret management for Discord token

## Dependency Management
- Updated `pyproject.toml` with all required dependencies
- Added missing packages: `humanize`, `orjson`
- Properly configured setuptools for multi-package structure

## Error Handling & Observability
- Graceful shutdown with guaranteed cleanup of connections
- Visual status indicators (✓/✗) for startup process
- Improved logging for extension loading
- Defensive error handling for optional services (Redis, Database, Music)
- Proper exception tracking and traceback logging

## Production Readiness
- Bot validates required environment variables on startup
- Degrades gracefully when optional services are unavailable
- Proper connection pooling and cleanup
- Clear startup visibility with cog/extension load counts