"""Script to deploy Discord slash commands."""

import asyncio
import discord
from discord.ext import commands
from discord import app_commands

# Import bot token
try:
    from bot_config import BOT_TOKEN
    print("✅ Bot configuration loaded from bot_config.py")
except ImportError:
    BOT_TOKEN = input("Enter your bot token: ")

class DeployBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents)
    
    async def setup_hook(self):
        """Called when the bot is starting up."""
        print("🔄 Deploying slash commands...")
        
        # Define the slash commands to deploy
        await self.define_commands()
        
        # Sync commands globally with retry logic
        max_retries = 3
        for attempt in range(max_retries):
            try:
                synced = await self.tree.sync()
                print(f"✅ Synced {len(synced)} global slash commands!")
                
                # List the commands that were synced
                for command in synced:
                    print(f"   • /{command.name} - {command.description}")
                
                print("🎉 All slash commands have been deployed!")
                break
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"⚠️ Sync attempt {attempt + 1} failed: {e}")
                    print(f"🔄 Retrying in 5 seconds... ({attempt + 2}/{max_retries})")
                    await asyncio.sleep(5)
                else:
                    print(f"❌ Failed to sync commands after {max_retries} attempts: {e}")
                    raise
        
        await self.close()
    
    async def define_commands(self):
        """Define all the slash commands."""
        
        # TikTok search command
        @self.tree.command(name="tiktok", description="Search for TikTok videos with various options")
        @app_commands.describe(
            strategy="Search strategy to use",
            max_videos="Maximum number of videos to find (1-25)",
            categories="Comma-separated categories (trending,entertainment,music_dance,etc.)"
        )
        @app_commands.choices(strategy=[
            app_commands.Choice(name="Parallel (All methods)", value="parallel"),
            app_commands.Choice(name="Sequential (Fallback)", value="sequential"), 
            app_commands.Choice(name="Hashtag Only", value="hashtag_only"),
            app_commands.Choice(name="Personalized (AI)", value="personalized")
        ])
        async def tiktok_search(
            interaction: discord.Interaction,
            strategy: str = "parallel",
            max_videos: int = 15,
            categories: str = None
        ):
            """Search for TikTok videos and display them with embeds."""
            await interaction.response.send_message(
                "✅ TikTok command deployed! Use this command in your main bot.",
                ephemeral=True
            )
        
        # TikTok validate command
        @self.tree.command(name="tiktok_validate", description="Validate your TikTok session ID configuration")
        async def tiktok_validate(interaction: discord.Interaction):
            """Validate TikTok session configuration."""
            await interaction.response.send_message(
                "✅ TikTok Validate command deployed! Use this command in your main bot.",
                ephemeral=True
            )
        
        # TikTok database command
        @self.tree.command(name="tiktok_database", description="View database statistics and manage sent videos")
        async def tiktok_database(interaction: discord.Interaction):
            """Display database statistics."""
            await interaction.response.send_message(
                "✅ TikTok Database command deployed! Use this command in your main bot.",
                ephemeral=True
            )
        
        # TikTok stats command
        @self.tree.command(name="tiktok_stats", description="View current TikTok scraper configuration and stats")
        async def tiktok_stats(interaction: discord.Interaction):
            """Display current bot configuration and statistics."""
            await interaction.response.send_message(
                "✅ TikTok Stats command deployed! Use this command in your main bot.",
                ephemeral=True
            )
        
        # TikTok help command
        @self.tree.command(name="tiktok_help", description="Get help with TikTok bot commands and features")
        async def tiktok_help(interaction: discord.Interaction):
            """Display help information for TikTok bot commands."""
            await interaction.response.send_message(
                "✅ TikTok Help command deployed! Use this command in your main bot.",
                ephemeral=True
            )
        
        # TikTok user command
        @self.tree.command(name="tiktok_user", description="Search videos from a specific TikTok user")
        @app_commands.describe(
            username="TikTok username (without @)",
            max_videos="Maximum number of videos to find (1-25)"
        )
        async def tiktok_user(
            interaction: discord.Interaction,
            username: str,
            max_videos: int = 10
        ):
            """Search videos from a specific user."""
            await interaction.response.send_message(
                "✅ TikTok User command deployed! Use this command in your main bot.",
                ephemeral=True
            )
        
        # TikTok hashtag command
        @self.tree.command(name="tiktok_hashtag", description="Search videos by specific hashtag")
        @app_commands.describe(
            hashtag="Hashtag to search for (without #)",
            max_videos="Maximum number of videos to find (1-25)"
        )
        async def tiktok_hashtag(
            interaction: discord.Interaction,
            hashtag: str,
            max_videos: int = 10
        ):
            """Search videos by hashtag."""
            await interaction.response.send_message(
                "✅ TikTok Hashtag command deployed! Use this command in your main bot.",
                ephemeral=True
            )
        
        # TikTok trending command
        @self.tree.command(name="tiktok_trending", description="Get current trending hashtags and topics")
        async def tiktok_trending(interaction: discord.Interaction):
            """Get trending hashtags and topics."""
            await interaction.response.send_message(
                "✅ TikTok Trending command deployed! Use this command in your main bot.",
                ephemeral=True
            )
          # TikTok info command
        @self.tree.command(name="tiktok_info", description="Get detailed info about a specific TikTok video")
        @app_commands.describe(
            url="TikTok video URL"
        )
        async def tiktok_info(
            interaction: discord.Interaction,
            url: str
        ):
            """Get detailed information about a TikTok video."""
            await interaction.response.send_message(
                "✅ TikTok Info command deployed! Use this command in your main bot.",
                ephemeral=True
            )

async def main():
    bot = DeployBot()
    
    try:
        # Set a timeout for the bot start operation
        await asyncio.wait_for(bot.start(BOT_TOKEN), timeout=30.0)
    except asyncio.TimeoutError:
        print("❌ Operation timed out! This might be due to network issues or Discord API rate limiting.")
        print("💡 Try running the script again in a few minutes.")
    except discord.LoginFailure:
        print("❌ Invalid bot token!")
        print("💡 Please check your BOT_TOKEN in bot_config.py")
    except discord.HTTPException as e:
        print(f"❌ Discord API error: {e}")
        print("💡 This might be a temporary Discord API issue. Try again later.")
    except KeyboardInterrupt:
        print("⚠️ Deployment cancelled by user (Ctrl+C)")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    finally:
        if not bot.is_closed():
            try:
                await bot.close()
            except:
                pass  # Ignore errors when closing

if __name__ == "__main__":
    print("🚀 Starting command deployment...")
    asyncio.run(main())
