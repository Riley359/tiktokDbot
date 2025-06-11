#!/usr/bin/env python3
"""Force sync all Discord slash commands."""

import asyncio
import discord
from discord.ext import commands

# Import the main bot
import discord_bot

async def force_sync():
    """Force sync all commands with Discord."""
    try:
        # Use the main bot instance
        bot = discord_bot.bot
        
        print("🔄 Starting forced command sync...")
        print(f"📋 Bot has {len(bot.tree.get_commands())} commands registered locally:")
        
        for cmd in bot.tree.get_commands():
            print(f"   • /{cmd.name} - {cmd.description}")
        
        # Start the bot temporarily just to sync commands
        @bot.event
        async def on_ready():
            print(f"🤖 Bot logged in as {bot.user}")
            
            try:
                # Clear existing commands first
                print("🧹 Clearing old commands...")
                bot.tree.clear_commands(guild=None)
                
                # Force sync all commands
                print("📤 Syncing commands with Discord...")
                synced = await bot.tree.sync()
                
                print(f"✅ Successfully synced {len(synced)} commands with Discord!")
                for command in synced:
                    print(f"   ✓ /{command.name}")
                
                print("🎉 All commands are now available in Discord!")
                
            except Exception as e:
                print(f"❌ Error during sync: {e}")
            finally:
                print("🔚 Closing bot...")
                await bot.close()
        
        # Get token
        token = discord_bot.BOT_TOKEN
        if token == "YOUR_BOT_TOKEN_HERE":
            print("❌ Bot token not configured!")
            return
          # Start bot temporarily
        print("🔌 Connecting to Discord...")
        await asyncio.wait_for(bot.start(token), timeout=60.0)
        
    except discord.LoginFailure:
        print("❌ Invalid bot token!")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Force syncing Discord slash commands...")
    asyncio.run(force_sync())
