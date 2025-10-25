import discord
import asyncio
import os
import sys
from bot import Evict

async def main():
    discord_token = os.environ.get("DISCORD_TOKEN")
    if not discord_token:
        print("ERROR: DISCORD_TOKEN environment variable not set!")
        sys.exit(1)
    
    bot = Evict()
    
    try:
        await bot.start(discord_token)
    except KeyboardInterrupt:
        print("\nReceived interrupt signal, shutting down...")
    except Exception as e:
        print(f"Error starting bot: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if bot:
            if bot.db:
                await bot.db.close()
                print("Database connection closed")
            if hasattr(bot, 'redis') and bot.redis:
                await bot.redis.close()
                print("Redis connection closed")
            await bot.close()
            print("Bot shut down successfully")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except SystemExit:
        pass
