"""Discord bot for TikTok video scraping with slash commands - Improved Version."""

import asyncio
import discord
from discord.ext import commands
from discord import app_commands
import logging
import sys
import os
from typing import List, Optional, Dict, Any, Tuple

# =============================================================================
# CONFIGURATION AND COMPONENT LOADING
# =============================================================================

def load_tiktok_components() -> Tuple[bool, Optional[Dict[str, Any]]]:
    """Load TikTok components with simplified error handling."""
    try:
        # Add src directory to Python path
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
        
        print("🔍 Loading TikTok components...")
        from TikTokApi import TikTokApi
        from src import config
        from src.utils import extract_video_data
        from src.search_strategies import (
            parallel_search_strategy, sequential_search_strategy,
            hashtag_only_strategy, personalized_search_strategy
        )
        from src.filters import passes_trend_filters, passes_content_filters, passes_personalized_filters
        from src.personalization import PreferenceAnalyzer, PersonalizedSearchEngine, build_preference_profile
        from src.database import video_db
        
        print("✅ All TikTok components loaded successfully!")
        return True, {
            'TikTokApi': TikTokApi,
            'video_db': video_db,
            'config': {
                'SESSIONID': config.SESSIONID,
                'SEARCH_STRATEGY': config.SEARCH_STRATEGY,
                'MAX_TOTAL_VIDEOS': config.MAX_TOTAL_VIDEOS,
                'ACTIVE_CATEGORIES': config.ACTIVE_CATEGORIES,
                'USE_PERSONALIZED_FILTERING': config.USE_PERSONALIZED_FILTERING,
                'HASHTAG_CATEGORIES': config.HASHTAG_CATEGORIES,
                'TREND_FILTERS': config.TREND_FILTERS,
                'ANALYZE_LIKED_VIDEOS': config.ANALYZE_LIKED_VIDEOS,
                'LIKED_VIDEOS_ANALYZE_COUNT': config.LIKED_VIDEOS_ANALYZE_COUNT,
                'MIN_PREFERENCE_SCORE': config.MIN_PREFERENCE_SCORE,
                'ENABLE_ALGORITHM_LEARNING': config.ENABLE_ALGORITHM_LEARNING,
                'DOWNLOAD_VIDEOS': config.DOWNLOAD_VIDEOS,
                'PREFERENCE_PROFILE_FILE': config.PREFERENCE_PROFILE_FILE
            },
            'strategies': {
                'parallel': parallel_search_strategy,
                'sequential': sequential_search_strategy,
                'hashtag_only': hashtag_only_strategy,
                'personalized': personalized_search_strategy
            },
            'filters': {
                'trend': passes_trend_filters,
                'content': passes_content_filters,
                'personalized': passes_personalized_filters
            },
            'utils': {
                'extract_video_data': extract_video_data,
                'PreferenceAnalyzer': PreferenceAnalyzer,
                'PersonalizedSearchEngine': PersonalizedSearchEngine,
                'build_preference_profile': build_preference_profile
            }
        }
    except ImportError as e:
        print(f"⚠️ TikTok components not available: {e}")
        return False, None

# Load components
TIKTOK_AVAILABLE, TIKTOK_COMPONENTS = load_tiktok_components()

# Load bot configuration
def load_bot_config() -> str:
    """Load Discord bot token."""
    try:
        from bot_config import BOT_TOKEN
        print("✅ Bot configuration loaded from bot_config.py")
        return BOT_TOKEN
    except ImportError:
        token = os.getenv('DISCORD_BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')
        if token == 'YOUR_BOT_TOKEN_HERE':
            print("⚠️ Bot token not configured. Please create bot_config.py or set DISCORD_BOT_TOKEN environment variable")
        return token

BOT_TOKEN = load_bot_config()

# =============================================================================
# DISCORD BOT SETUP
# =============================================================================

INTENTS = discord.Intents.default()
INTENTS.message_content = True

class TikTokBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!', intents=INTENTS)
        
    async def setup_hook(self):
        """Called when the bot is starting up."""
        try:
            print("🔄 Syncing slash commands...")
            
            # Get current commands for verification
            local_commands = [cmd.name for cmd in self.tree.get_commands()]
            print(f"📋 Local commands ({len(local_commands)}): {', '.join(local_commands)}")
            
            # Force sync with Discord (this ensures all commands are updated)
            synced = await asyncio.wait_for(self.tree.sync(), timeout=30.0)
            print(f"✅ Successfully synced {len(synced)} slash commands with Discord")
            
            # Verify all commands were synced
            synced_names = [cmd.name for cmd in synced]
            print(f"📤 Synced commands: {', '.join(synced_names)}")
            
            # Check for any missing commands
            missing = [cmd for cmd in local_commands if cmd not in synced_names]
            if missing:
                print(f"⚠️  Missing commands (will retry): {', '.join(missing)}")
            else:
                print("✅ All local commands successfully synced!")
                
        except asyncio.TimeoutError:
            print("⚠️ Command sync timed out (this is usually ok)")
        except Exception as e:
            print(f"⚠️ Error syncing commands: {e}")
            print("ℹ️ Commands may still work if they were previously synced")

    async def on_ready(self):
        """Called when the bot is ready."""
        print(f'🎉 {self.user} has landed! 🚀')
        print(f'📡 Connected to {len(self.guilds)} servers')
        print(f'👥 Serving {sum(guild.member_count for guild in self.guilds)} users')
        print("✅ Bot is ready to receive commands!")

bot = TikTokBot()

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def convert_to_tnktiktok(url: str) -> str:
    """Convert a regular TikTok URL to a tnkTok URL for better Discord previews."""
    if "tiktok.com" in url:
        return url.replace("tiktok.com", "tnktok.com")
    return url

def create_bot_detection_embed() -> discord.Embed:
    """Create an embed with bot detection troubleshooting info."""
    embed = discord.Embed(
        title="🤖 TikTok Bot Detection",
        description="TikTok is detecting automated requests. Here's how to fix it:",
        color=0xFF6B35
    )
    
    embed.add_field(
        name="🔧 Quick Fixes",
        value="1. **Wait 5-10 minutes** before trying again\n"
              "2. **Use `/tiktok_validate`** to check your session\n"
              "3. **Try the main `/tiktok` command** instead",
        inline=False
    )
    
    embed.add_field(
        name="🆔 Session Issues",
        value="• Your TikTok session ID might be expired\n"
              "• Get a fresh session from your browser\n"
              "• Update `src/config.py` with new session",
        inline=False
    )
    
    embed.add_field(
        name="💡 Alternative",
        value="Use **general search** with `/tiktok` command which has better anti-detection",
        inline=False
    )
    
    embed.set_footer(text="🔄 Bot detection is temporary - try again later")
    
    return embed

def create_error_embed(title: str, description: str, color: int = 0xff0000) -> discord.Embed:
    """Create an error embed."""
    return discord.Embed(title=f"❌ {title}", description=description, color=color)

def create_success_embed(title: str, description: str, color: int = 0x00ff00) -> discord.Embed:
    """Create a success embed."""
    return discord.Embed(title=f"✅ {title}", description=description, color=color)

def create_video_embed(video_data: dict) -> discord.Embed:
    """Create a rich embed for video information."""
    embed = discord.Embed(
        title=f"🎵 @{video_data.get('author', 'Unknown')}",  # Use get with default value
        description=video_data.get('caption', 'No caption available')[:300] + ("..." if len(video_data.get('caption', '')) > 300 else ""),
        color=0xFF0050,
        url=video_data.get('url', '')
    )
    
    # Add statistics
    likes = video_data.get('likes', 0)
    views = video_data.get('views', 0) 
    comments = video_data.get('comments', 0)
    
    embed.add_field(name="👍 Likes", value=f"{likes:,}", inline=True)
    embed.add_field(name="👁️ Views", value=f"{views:,}", inline=True)
    embed.add_field(name="💬 Comments", value=f"{comments:,}", inline=True)
    
    # Add duration if available
    duration = video_data.get('duration', 0)
    if duration:
        embed.add_field(name="⏱️ Duration", value=f"{duration}s", inline=True)
    
    # Add hashtags if available
    hashtags = video_data.get('hashtags', [])
    if hashtags:
        hashtag_text = " ".join([f"#{tag}" for tag in hashtags[:5]])  # Limit to 5 hashtags
        embed.add_field(name="🏷️ Tags", value=hashtag_text, inline=False)
    
    # Add thumbnail if available
    thumbnail = video_data.get('thumbnail') or video_data.get('cover_url')
    if thumbnail:
        embed.set_thumbnail(url=thumbnail)
    
    # Add created date if available
    created_time = video_data.get('created_time')
    if created_time:
        embed.set_footer(text=f"Created: {created_time}")
    else:
        embed.set_footer(text="🎵 TikTok Video")
    
    return embed

def create_info_embed(title: str, description: str, color: int = 0x0099ff) -> discord.Embed:
    """Create an informational embed."""
    return discord.Embed(title=f"ℹ️ {title}", description=description, color=color)

async def send_videos_in_batches(interaction_or_ctx, videos: List[dict], batch_size: int = 5):
    """Send videos in batches with proper error handling."""
    is_interaction = hasattr(interaction_or_ctx, 'followup')
    
    for batch_start in range(0, len(videos), batch_size):
        batch_end = min(batch_start + batch_size, len(videos))
        batch_videos = videos[batch_start:batch_end]
        
        # Create batch content
        batch_content = ""
        for i, video in enumerate(batch_videos):
            video_number = batch_start + i + 1
            video_url = convert_to_tnktiktok(video['url'])
            batch_content += f"**Video {video_number}:** {video_url}\n"
        
        # Send batch
        try:
            if is_interaction:
                await interaction_or_ctx.followup.send(batch_content.strip())
            else:
                await interaction_or_ctx.send(batch_content.strip())
        except discord.NotFound:
            print(f"⚠️ Message send failed - interaction expired")
            break
        except Exception as e:
            print(f"⚠️ Failed to send batch: {e}")
            break
        
        # Record in database
        for video in batch_videos:
            try:
                guild_id = getattr(interaction_or_ctx, 'guild_id', None) or (
                    interaction_or_ctx.guild.id if hasattr(interaction_or_ctx, 'guild') and interaction_or_ctx.guild else None
                )
                channel_id = getattr(interaction_or_ctx, 'channel_id', None) or interaction_or_ctx.channel.id
                
                TIKTOK_COMPONENTS['video_db'].add_sent_video(video, guild_id=guild_id, channel_id=channel_id)
            except Exception as e:
                print(f"Warning: Failed to record video: {e}")
        
        # Delay between batches
        if batch_end < len(videos):
            await asyncio.sleep(1)

async def send_videos_with_embeds(interaction_or_ctx, videos: List[dict], use_embeds: bool = False, batch_size: int = 3):
    """Send videos with optional rich embeds."""
    is_interaction = hasattr(interaction_or_ctx, 'followup')
    
    if use_embeds:
        # Send with rich embeds (smaller batches due to embed limits)
        for batch_start in range(0, len(videos), batch_size):
            batch_end = min(batch_start + batch_size, len(videos))
            batch_videos = videos[batch_start:batch_end]
            
            embeds = []
            for i, video in enumerate(batch_videos):
                video_number = batch_start + i + 1
                embed = create_video_embed(video)
                embed.title = f"🎵 Video {video_number}: @{video.get('author', 'Unknown')}"
                embeds.append(embed)
            
            try:
                if is_interaction:
                    await interaction_or_ctx.followup.send(embeds=embeds)
                else:
                    await interaction_or_ctx.send(embeds=embeds)
            except discord.NotFound:
                print(f"⚠️ Message send failed - interaction expired")
                break
            except Exception as e:
                print(f"⚠️ Failed to send embed batch: {e}")
                break
            
            # Record in database
            for video in batch_videos:
                try:
                    guild_id = getattr(interaction_or_ctx, 'guild_id', None) or (
                        interaction_or_ctx.guild.id if hasattr(interaction_or_ctx, 'guild') and interaction_or_ctx.guild else None
                    )
                    channel_id = getattr(interaction_or_ctx, 'channel_id', None) or interaction_or_ctx.channel.id
                    
                    TIKTOK_COMPONENTS['video_db'].add_sent_video(video, guild_id=guild_id, channel_id=channel_id)
                except Exception as e:
                    print(f"Warning: Failed to record video: {e}")
            
            # Delay between batches
            if batch_end < len(videos):
                await asyncio.sleep(2)
    else:
        # Use existing simple format
        await send_videos_in_batches(interaction_or_ctx, videos, batch_size=5)

# =============================================================================
# SHARED COMMAND HANDLERS
# =============================================================================

class TikTokCommandHandler:
    """Shared logic for both slash and prefix commands."""
    
    @staticmethod
    def validate_search_params(strategy: str, max_videos: int, categories: str = None) -> Tuple[bool, str, Optional[List[str]]]:
        """Validate search parameters."""
        if not TIKTOK_AVAILABLE:
            return False, "❌ TikTok components not available. Install requirements: `pip install -r requirements.txt`", None
        
        if max_videos < 1 or max_videos > 50:
            return False, "❌ Maximum videos must be between 1 and 50.", None
        
        valid_strategies = ["parallel", "sequential", "hashtag_only", "personalized"]
        if strategy not in valid_strategies:
            return False, f"❌ Invalid strategy. Valid: {', '.join(valid_strategies)}", None
        
        category_list = None
        if categories:
            category_list = [cat.strip() for cat in categories.split(",")]
            valid_categories = list(TIKTOK_COMPONENTS['config']['HASHTAG_CATEGORIES'].keys())
            invalid_cats = [cat for cat in category_list if cat not in valid_categories]
            if invalid_cats:
                return False, f"❌ Invalid categories: {', '.join(invalid_cats)}\nValid: {', '.join(valid_categories)}", None
        
        return True, "✅ Parameters valid", category_list
    @staticmethod
    async def execute_search(strategy: str, max_videos: int, categories: List[str] = None) -> List[dict]:
        """Execute TikTok search with simplified logic."""
        if not TIKTOK_AVAILABLE or not TIKTOK_COMPONENTS:
            raise ValueError("TikTok components not available")
        
        config = TIKTOK_COMPONENTS['config']
        if not config['SESSIONID'] or config['SESSIONID'] == "":
            raise ValueError("TikTok sessionid not configured")
        
        return await scrape_tiktok_videos_simplified(strategy, max_videos, categories)
    
    @staticmethod
    async def search_user_videos(username: str, max_videos: int = 15) -> List[dict]:
        """Search videos from a specific user with enhanced anti-detection."""
        if not TIKTOK_AVAILABLE or not TIKTOK_COMPONENTS:
            raise ValueError("TikTok components not available")
        
        config = TIKTOK_COMPONENTS['config']
        TikTokApi = TIKTOK_COMPONENTS['TikTokApi']
        extract_video_data = TIKTOK_COMPONENTS['utils']['extract_video_data']
        passes_trend_filters = TIKTOK_COMPONENTS['filters']['trend']
        passes_content_filters = TIKTOK_COMPONENTS['filters']['content']
        video_db = TIKTOK_COMPONENTS['video_db']
        
        videos = []
        max_attempts = 3
        
        for attempt in range(max_attempts):
            try:
                async with TikTokApi() as api:
                    # Enhanced anti-detection settings
                    await api.create_sessions(
                        ms_tokens=[config['SESSIONID']],
                        num_sessions=1,
                        headless=False,  # Visible browser
                        browser="webkit",
                        sleep_after=5 + attempt * 2,  # Progressive delay
                        override_browser_args=[
                            "--no-sandbox",
                            "--disable-setuid-sandbox", 
                            "--disable-dev-shm-usage",
                            "--disable-accelerated-2d-canvas",
                            "--no-first-run",
                            "--no-zygote",
                            "--disable-gpu",
                            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                        ]
                    )
                    
                    # Add delay before making requests
                    await asyncio.sleep(2 + attempt)
                    
                    try:
                        user = api.user(username)
                        
                        # Add another delay before fetching videos
                        await asyncio.sleep(1)
                        
                        async for video in user.videos(count=max_videos * 3):  # Get more to compensate for filtering
                            if len(videos) >= max_videos:
                                break
                            
                            try:
                                video_data = extract_video_data(video)
                                if not video_data:
                                    continue
                                
                                # Apply filters
                                if not passes_trend_filters(video_data):
                                    continue
                                if not passes_content_filters(video_data):
                                    continue
                                
                                videos.append(video_data)
                                
                                # Small delay between video processing
                                await asyncio.sleep(0.1)
                                
                            except Exception as e:
                                print(f"Error processing user video: {e}")
                                continue
                        
                        # If we got videos, break out of retry loop
                        if videos:
                            break
                            
                    except Exception as e:
                        error_msg = str(e).lower()
                        if "empty response" in error_msg or "detecting" in error_msg:
                            if attempt < max_attempts - 1:
                                print(f"⚠️ Bot detection on user search attempt {attempt + 1}, retrying...")
                                await asyncio.sleep(10 + attempt * 5)  # Longer delay
                                continue
                            else:
                                raise ValueError(f"TikTok is consistently detecting bot behavior for user searches. User @{username} might not exist or have restricted content.")
                        else:
                            raise ValueError(f"Failed to fetch user videos: {str(e)}")
                            
            except Exception as e:
                if attempt == max_attempts - 1:
                    raise ValueError(f"Failed to fetch user videos after {max_attempts} attempts: {str(e)}")
                await asyncio.sleep(5)
        
        if not videos:
            raise ValueError(f"No videos found for user @{username}. User might not exist or have no public videos.")
        
        return videos[:max_videos]
    @staticmethod
    async def search_hashtag_videos(hashtag: str, max_videos: int = 15) -> List[dict]:
        """Search videos by specific hashtag with enhanced anti-detection."""
        if not TIKTOK_AVAILABLE or not TIKTOK_COMPONENTS:
            raise ValueError("TikTok components not available")
        
        config = TIKTOK_COMPONENTS['config']
        TikTokApi = TIKTOK_COMPONENTS['TikTokApi']
        extract_video_data = TIKTOK_COMPONENTS['utils']['extract_video_data']
        passes_trend_filters = TIKTOK_COMPONENTS['filters']['trend']
        passes_content_filters = TIKTOK_COMPONENTS['filters']['content']
        
        videos = []
        max_attempts = 3
        
        for attempt in range(max_attempts):
            try:
                async with TikTokApi() as api:
                    # Enhanced anti-detection settings
                    await api.create_sessions(
                        ms_tokens=[config['SESSIONID']],
                        num_sessions=1,
                        headless=False,
                        browser="webkit",
                        sleep_after=4 + attempt * 2,
                        override_browser_args=[
                            "--no-sandbox",
                            "--disable-setuid-sandbox", 
                            "--disable-dev-shm-usage",
                            "--disable-accelerated-2d-canvas",
                            "--no-first-run",
                            "--no-zygote",
                            "--disable-gpu",
                            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                        ]
                    )
                    
                    # Add delay before making requests
                    await asyncio.sleep(2 + attempt)
                    
                    try:
                        # Remove # if present
                        hashtag = hashtag.lstrip('#')
                        tag = api.hashtag(hashtag)
                        
                        # Add delay before fetching videos
                        await asyncio.sleep(1)
                        
                        async for video in tag.videos(count=max_videos * 3):  # Get more to filter
                            if len(videos) >= max_videos:
                                break
                            
                            try:
                                video_data = extract_video_data(video)
                                if not video_data:
                                    continue
                                
                                if passes_trend_filters(video_data) and passes_content_filters(video_data):
                                    videos.append(video_data)
                                    
                                # Small delay between video processing
                                await asyncio.sleep(0.1)
                                
                            except Exception as e:
                                print(f"Error processing hashtag video: {e}")
                                continue
                        
                        # If we got videos, break out of retry loop
                        if videos:
                            break
                            
                    except Exception as e:
                        error_msg = str(e).lower()
                        if "empty response" in error_msg or "detecting" in error_msg:
                            if attempt < max_attempts - 1:
                                print(f"⚠️ Bot detection on hashtag search attempt {attempt + 1}, retrying...")
                                await asyncio.sleep(8 + attempt * 3)  # Progressive delay
                                continue
                            else:
                                raise ValueError(f"TikTok is consistently detecting bot behavior for hashtag searches. Hashtag #{hashtag} might not exist or be restricted.")
                        else:
                            raise ValueError(f"Failed to fetch hashtag videos: {str(e)}")
                            
            except Exception as e:
                if attempt == max_attempts - 1:
                    raise ValueError(f"Failed to fetch hashtag videos after {max_attempts} attempts: {str(e)}")
                await asyncio.sleep(5)
        
        if not videos:
            raise ValueError(f"No videos found for hashtag #{hashtag}. Hashtag might not exist or have no recent videos.")
        
        return videos[:max_videos]
    
    @staticmethod
    async def get_trending_hashtags(count: int = 10) -> List[str]:
        """Get current trending hashtags."""
        if not TIKTOK_AVAILABLE or not TIKTOK_COMPONENTS:
            raise ValueError("TikTok components not available")
        
        # This is a simplified implementation - you'd want to implement actual trending detection
        config = TIKTOK_COMPONENTS['config']
        hashtag_categories = config['HASHTAG_CATEGORIES']
        
        # Return a mix of popular hashtags from different categories
        trending = []
        for category, hashtags in hashtag_categories.items():
            trending.extend(hashtags[:2])  # Take top 2 from each category
        
        return trending[:count]
    @staticmethod
    async def get_video_info(url: str) -> dict:
        """Get detailed information about a specific TikTok video with enhanced anti-detection."""
        if not TIKTOK_AVAILABLE or not TIKTOK_COMPONENTS:
            raise ValueError("TikTok components not available")
        
        config = TIKTOK_COMPONENTS['config']
        TikTokApi = TIKTOK_COMPONENTS['TikTokApi']
        extract_video_data = TIKTOK_COMPONENTS['utils']['extract_video_data']
        
        max_attempts = 2
        
        for attempt in range(max_attempts):
            try:
                async with TikTokApi() as api:
                    await api.create_sessions(
                        ms_tokens=[config['SESSIONID']],
                        num_sessions=1,
                        headless=False,
                        browser="webkit",
                        sleep_after=3 + attempt,
                        override_browser_args=[
                            "--no-sandbox",
                            "--disable-setuid-sandbox", 
                            "--disable-dev-shm-usage",
                            "--disable-accelerated-2d-canvas",
                            "--no-first-run",
                            "--no-zygote",
                            "--disable-gpu",
                            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                        ]
                    )
                    
                    # Add delay before making request
                    await asyncio.sleep(1 + attempt)
                    
                    try:
                        video = api.video(url=url)
                        video_data = extract_video_data(video)
                        
                        if not video_data:
                            raise ValueError("Could not extract video data")
                        
                        return video_data
                        
                    except Exception as e:
                        error_msg = str(e).lower()
                        if "empty response" in error_msg or "detecting" in error_msg:
                            if attempt < max_attempts - 1:
                                print(f"⚠️ Bot detection on video info attempt {attempt + 1}, retrying...")
                                await asyncio.sleep(5 + attempt * 3)
                                continue
                            else:
                                raise ValueError(f"TikTok is detecting bot behavior. Unable to analyze video: {url}")
                        else:
                            raise ValueError(f"Failed to get video info: {str(e)}")
                            
            except Exception as e:
                if attempt == max_attempts - 1:
                    raise ValueError(f"Failed to get video info after {max_attempts} attempts: {str(e)}")
                await asyncio.sleep(3)
        
        raise ValueError("Unable to get video information")

async def scrape_tiktok_videos_simplified(strategy: str, max_videos: int, categories: List[str] = None) -> List[dict]:
    """Simplified video scraping with basic retry logic."""
    
    if not TIKTOK_AVAILABLE or not TIKTOK_COMPONENTS:
        raise ValueError("TikTok components not available")
    
    config = TIKTOK_COMPONENTS['config']
    TikTokApi = TIKTOK_COMPONENTS['TikTokApi']
    extract_video_data = TIKTOK_COMPONENTS['utils']['extract_video_data']
    passes_trend_filters = TIKTOK_COMPONENTS['filters']['trend']
    passes_content_filters = TIKTOK_COMPONENTS['filters']['content']
    video_db = TIKTOK_COMPONENTS['video_db']
    all_videos = []
    max_attempts = 6
    used_hashtags = set()  # Track hashtags across all retry attempts
    
    async with TikTokApi() as api:
        # Create sessions with simplified settings
        await api.create_sessions(
            ms_tokens=[config['SESSIONID']],
            num_sessions=1,
            headless=False,
            browser="webkit",
            sleep_after=3
        )
        
        for attempt in range(max_attempts):
            try:
                print(f"🔍 Attempt {attempt + 1}: Searching for videos...")
                
                # Get strategy function
                strategy_func = TIKTOK_COMPONENTS['strategies'][strategy]
                
                # Execute search with retry information and persistent hashtag tracking
                videos = await strategy_func(api, retry_attempt=attempt, used_hashtags=used_hashtags)
                
                # Log hashtag tracking info for debugging
                if attempt > 0 and used_hashtags:
                    print(f"🔄 Retry attempt {attempt + 1}: {len(used_hashtags)} hashtags already tried")
                elif attempt == 0:
                    print(f"🎯 First attempt: Starting with fresh hashtag selection")
                
                if not videos:
                    print(f"❌ No videos returned on attempt {attempt + 1}")
                    continue
                
                # Process and filter videos
                processed_videos = []
                for video in videos:
                    if len(all_videos) + len(processed_videos) >= max_videos:
                        break
                        
                    try:
                        video_data = extract_video_data(video)
                        if not video_data:
                            continue
                        
                        # Apply filters
                        if not passes_trend_filters(video_data):
                            continue
                        if not passes_content_filters(video_data):
                            continue
                        
                        processed_videos.append(video_data)
                    except Exception as e:
                        print(f"Error processing video: {e}")
                        continue
                
                # Remove duplicates using database
                all_urls = [v['url'] for v in all_videos]
                unique_videos, duplicates = video_db.filter_duplicate_videos(
                    processed_videos, exclude_urls=all_urls
                )
                
                if duplicates:
                    print(f"🔄 Filtered out {len(duplicates)} duplicate videos")
                
                all_videos.extend(unique_videos)
                print(f"✅ Found {len(unique_videos)} new unique videos. Total: {len(all_videos)}/{max_videos}")
                
                # If we have enough videos or this is the last attempt, return
                if len(all_videos) >= max_videos or attempt == max_attempts - 1:
                    break
                
                # Brief delay between attempts
                await asyncio.sleep(2)
                
            except Exception as e:
                error_msg = str(e).lower()
                if "detecting" in error_msg or "empty response" in error_msg:
                    if attempt == max_attempts - 1:
                        raise ValueError("TikTok is consistently detecting bot behavior. Please check your session ID.")
                    print(f"⚠️ Bot detection on attempt {attempt + 1}, retrying...")
                    await asyncio.sleep(5)
                else:
                    if attempt == max_attempts - 1:
                        raise e
                    await asyncio.sleep(3)
    
    final_videos = all_videos[:max_videos]
    print(f"🎯 Returning {len(final_videos)} unique videos")
    return final_videos
# =============================================================================
# DATABASE MANAGEMENT
# =============================================================================

class DatabaseManager:
    """Shared database management logic."""
    
    @staticmethod
    async def handle_database_action(action: str, send_func, is_ephemeral: bool = False):
        """Handle database actions for both command types."""
        if not TIKTOK_AVAILABLE or not TIKTOK_COMPONENTS:
            await send_func("❌ TikTok components not available.", ephemeral=is_ephemeral)
            return
        
        db = TIKTOK_COMPONENTS['video_db']
        
        try:
            if action == "stats":
                stats = db.get_database_stats()
                embed = discord.Embed(
                    title="📊 TikTok Database Statistics",
                    description="Statistics about sent videos and duplicate prevention",
                    color=0x0099ff
                )
                
                embed.add_field(
                    name="📈 Video Counts",
                    value=f"• **Total Videos Sent:** {stats['total_videos']:,}\n"
                          f"• **Today:** {stats['today_videos']:,}\n"
                          f"• **This Week:** {stats['week_videos']:,}",
                    inline=True
                )
                
                if stats['top_authors']:
                    top_authors_text = "\n".join([f"• @{author}: {count}" for author, count in stats['top_authors'][:3]])
                    embed.add_field(name="👑 Top Authors", value=top_authors_text, inline=True)
                
                if stats['recent_videos']:
                    recent_text = "\n".join([f"• @{author} ({sent_at[:10]})" for author, sent_at in stats['recent_videos'][:3]])
                    embed.add_field(name="🕒 Recently Sent", value=recent_text, inline=False)
                
                embed.set_footer(text="Database prevents duplicate videos from being sent")
                await send_func(embed=embed, ephemeral=is_ephemeral)
                
            elif action == "clear":
                cleared = db.clear_database()
                await send_func(f"✅ **Database Cleared**\n\nRemoved {cleared:,} video records.", ephemeral=is_ephemeral)
                
            elif action == "cleanup":
                cleaned = db.cleanup_old_videos(30)
                await send_func(f"🧹 **Database Cleanup Complete**\n\nRemoved {cleaned:,} videos older than 30 days.", ephemeral=is_ephemeral)
                
            elif action == "recent":
                recent_videos = db.get_recent_videos(limit=10)
                
                if not recent_videos:
                    await send_func("📭 **No videos in database yet**\n\nSend some videos first using `/tiktok`!", ephemeral=is_ephemeral)
                    return
                
                embed = discord.Embed(
                    title="🕒 Recently Sent Videos",
                    description=f"Last {len(recent_videos)} videos sent by the bot",
                    color=0xff6b35
                )
                
                for i, video in enumerate(recent_videos[:5], 1):
                    sent_time = video['sent_at'][:16].replace('T', ' ')
                    caption = video['caption'][:50] + "..." if len(video['caption']) > 50 else video['caption']
                    
                    embed.add_field(
                        name=f"{i}. @{video['author']}",
                        value=f"**Caption:** {caption}\n**Sent:** {sent_time}",
                        inline=False
                    )
                
                await send_func(embed=embed, ephemeral=is_ephemeral)
                
        except Exception as e:
            await send_func(f"❌ **Database Error:** {str(e)}", ephemeral=is_ephemeral)

# =============================================================================
# SESSION VALIDATION
# =============================================================================

async def validate_tiktok_session(sessionid: str) -> Tuple[bool, str]:
    """Validate if the TikTok session ID is working."""
    if not sessionid or sessionid == "":
        return False, "Session ID is empty or not configured"
    
    if not TIKTOK_AVAILABLE or not TIKTOK_COMPONENTS:
        return False, "TikTok components not available"
    
    try:
        TikTokApi = TIKTOK_COMPONENTS['TikTokApi']
        async with TikTokApi() as api:
            await api.create_sessions(
                ms_tokens=[sessionid],
                num_sessions=1,
                headless=False,
                browser="webkit",
                sleep_after=2
            )
            
            # Try a simple trending request
            try:
                async for video in api.trending.videos(count=1):
                    return True, "Session is working correctly"
                return False, "No videos returned - session may be invalid"
            except Exception:
                # If trending fails, try a search strategy
                try:
                    strategy_func = TIKTOK_COMPONENTS['strategies']['parallel']
                    test_videos = await strategy_func(api)
                    return (True, "Session is working correctly") if test_videos else (False, "Session appears invalid")
                except Exception as e:
                    return False, f"Session validation failed: {str(e)}"
                
    except Exception as e:
        error_msg = str(e).lower()
        if "detecting" in error_msg or "empty response" in error_msg:
            return False, "TikTok is detecting bot behavior. Session may be invalid."
        elif "session" in error_msg or "token" in error_msg:
            return False, "Session token is invalid or expired."
        else:
            return False, f"Session validation failed: {str(e)}"

# =============================================================================
# SLASH COMMANDS
# =============================================================================

@bot.tree.command(name="tiktok", description="Search for TikTok videos with various options")
@app_commands.describe(
    strategy="Search strategy to use",
    max_videos="Maximum number of videos to find (1-50)",
    categories="Comma-separated categories (trending,entertainment,music_dance,etc.)",
    use_embeds="Display videos with rich embeds (default: False for compatibility)"
)
@app_commands.choices(strategy=[
    app_commands.Choice(name="Parallel (All methods)", value="parallel"),
    app_commands.Choice(name="Sequential (Fallback)", value="sequential"), 
    app_commands.Choice(name="Hashtag Only", value="hashtag_only"),
    app_commands.Choice(name="Personalized (AI)", value="personalized")
])
async def tiktok_search(interaction: discord.Interaction, strategy: str = "parallel", max_videos: int = 15, categories: str = None, use_embeds: bool = False):
    """Search for TikTok videos and display them."""
    
    # Validate parameters
    is_valid, message, category_list = TikTokCommandHandler.validate_search_params(strategy, max_videos, categories)
    if not is_valid:
        await interaction.response.send_message(message, ephemeral=True)
        return
    
    # Defer response
    try:
        await interaction.response.defer()
    except Exception:
        return
    
    # Execute search
    try:
        await interaction.edit_original_response(content="🔍 **Searching TikTok...**\n\nPlease wait while I find the best videos for you!")
        
        videos = await TikTokCommandHandler.execute_search(strategy, max_videos, category_list)
        
        if not videos:
            await interaction.edit_original_response(content="❌ **No unique videos found** matching your criteria.")
            return
        
        # Update with results
        if len(videos) == max_videos:
            await interaction.edit_original_response(content=f"🎯 **Found exactly {max_videos} unique TikTok videos!**\n\n📤 Sending them now...")
        else:
            await interaction.edit_original_response(content=f"🎵 **Found {len(videos)} unique videos** (out of {max_videos} requested)\n\n📤 Sending all results...")
          # Send videos in batches
        if use_embeds:
            await send_videos_with_embeds(interaction, videos, use_embeds=True)
        else:
            await send_videos_in_batches(interaction, videos)
        
    except ValueError as e:
        error_msg = str(e)
        if "detecting bot behavior" in error_msg:
            await interaction.edit_original_response(
                content="❌ **TikTok Bot Detection**\n\nTikTok is blocking bot requests. Check your session ID with `/tiktok_validate`."
            )
        else:
            await interaction.edit_original_response(content=f"❌ **Configuration Error:** {error_msg}")
    except Exception as e:
        await interaction.edit_original_response(content=f"❌ **Search Failed:** {str(e)}")

@bot.tree.command(name="tiktok_validate", description="Validate your TikTok session ID configuration")
async def tiktok_validate(interaction: discord.Interaction):
    """Validate the TikTok session configuration."""
    
    if not TIKTOK_AVAILABLE:
        await interaction.response.send_message("❌ **TikTok Not Available**\n\nTikTok scraper components are not available.", ephemeral=True)
        return
    
    await interaction.response.send_message("🔍 **Validating TikTok Session...**\n\nThis may take a few seconds...")
    
    try:
        config = TIKTOK_COMPONENTS['config']
        is_valid, message = await validate_tiktok_session(config['SESSIONID'])
        
        if is_valid:
            embed = create_success_embed("Session Valid", "Your TikTok session ID is working correctly!")
            embed.add_field(name="Status", value="✅ Connection successful\n✅ Authentication working\n✅ Can fetch videos", inline=False)
        else:
            embed = create_error_embed("Session Invalid", f"**Error:** {message}")
            embed.add_field(
                name="🔧 How to Fix",
                value="1. Get a new session ID from TikTok\n2. Update your `src/config.py` file\n3. Restart the bot",
                inline=False
            )
            
        await interaction.edit_original_response(content=None, embed=embed)
        
    except Exception as e:
        await interaction.edit_original_response(content=f"❌ **Validation Failed:** {str(e)}")

@bot.tree.command(name="tiktok_database", description="View database statistics and manage sent videos")
@app_commands.describe(action="Database action to perform")
@app_commands.choices(action=[
    app_commands.Choice(name="View Stats", value="stats"),
    app_commands.Choice(name="Clear All", value="clear"),
    app_commands.Choice(name="Cleanup Old (30+ days)", value="cleanup"),
    app_commands.Choice(name="Recent Videos", value="recent")
])
async def tiktok_database(interaction: discord.Interaction, action: str = "stats"):
    """Manage the TikTok video database."""
    
    try:
        await interaction.response.defer(ephemeral=True)
        await DatabaseManager.handle_database_action(action, interaction.followup.send, is_ephemeral=True)
    except Exception as e:
        try:
            await interaction.response.send_message(f"❌ **Error:** {str(e)}", ephemeral=True)
        except:
            pass

@bot.tree.command(name="tiktok_stats", description="View current TikTok scraper configuration and stats")
async def tiktok_stats(interaction: discord.Interaction):
    """Display current configuration and statistics."""
    
    embed = discord.Embed(
        title="📊 TikTok Bot Statistics",
        description="Current configuration and status",
        color=0x00ff00
    )
    
    if TIKTOK_AVAILABLE:
        config = TIKTOK_COMPONENTS['config']
        
        embed.add_field(
            name="⚙️ Configuration",
            value=f"• **Default Strategy:** {config['SEARCH_STRATEGY'].title()}\n"
                  f"• **Max Videos:** {config['MAX_TOTAL_VIDEOS']}\n"
                  f"• **Active Categories:** {', '.join(config['ACTIVE_CATEGORIES']) if config['ACTIVE_CATEGORIES'] else 'All'}\n"
                  f"• **Personalized Filtering:** {'Enabled' if config['USE_PERSONALIZED_FILTERING'] else 'Disabled'}",
            inline=False
        )
        
        session_status = "❌ Not configured" if not config['SESSIONID'] else "✅ Configured"
        embed.add_field(
            name="🔐 Authentication",
            value=f"• **Session ID:** {session_status}\n• **Use `/tiktok_validate`** to test",
            inline=False
        )
        
        embed.add_field(
            name="📈 Filter Settings",
            value=f"• **Min Likes:** {config['TREND_FILTERS']['min_likes']:,}\n"
                  f"• **Min Views:** {config['TREND_FILTERS']['min_views']:,}\n"
                  f"• **Min Comments:** {config['TREND_FILTERS']['min_comments']:,}\n"
                  f"• **Max Age:** {config['TREND_FILTERS']['max_age_days']} days",
            inline=True
        )
    else:
        embed.add_field(
            name="❌ TikTok Components",
            value="TikTok scraper components are not available.\nPlease install requirements: `pip install -r requirements.txt`",
            inline=False
        )
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="tiktok_help", description="Get help with TikTok bot commands and features")
async def tiktok_help(interaction: discord.Interaction):
    """Display help information for the TikTok bot."""
    
    embed = discord.Embed(
        title="🎵 TikTok Bot Help",
        description="Search and discover TikTok videos directly in Discord!",
        color=0xff0050
    )
    
    embed.add_field(
        name="📋 Main Commands",
        value="`/tiktok` - Search for TikTok videos\n"
              "`/tiktok_user` - Search videos from a user\n"
              "`/tiktok_hashtag` - Search by hashtag\n"
              "`/tiktok_trending` - Get trending hashtags\n"
              "`/tiktok_info` - Analyze a video URL\n"
              "`/tiktok_validate` - Validate session\n"
              "`/tiktok_database` - Manage database\n"
              "`/tiktok_stats` - View bot status",
        inline=False
    )
    
    embed.add_field(
        name="🎯 Search Strategies",
        value="• **Parallel** - All methods simultaneously\n"
              "• **Sequential** - Fallback methods\n"
              "• **Hashtag Only** - Only hashtag search\n"
              "• **Personalized** - AI-driven preferences",
        inline=False
    )
    
    embed.add_field(
        name="💡 Examples",
        value="`/tiktok strategy:parallel max_videos:10 use_embeds:True`\n"
              "`/tiktok_user username:charlidamelio max_videos:5`\n"
              "`/tiktok_hashtag hashtag:funny max_videos:10`\n"
              "`/tiktok_database action:stats`",
        inline=False
    )
    
    await interaction.response.send_message(embed=embed)

# =============================================================================
# ENHANCED SLASH COMMANDS
# =============================================================================

@bot.tree.command(name="tiktok_user", description="Search videos from a specific TikTok user")
@app_commands.describe(
    username="TikTok username (without @)",
    max_videos="Number of videos to get (1-25)",
    use_embeds="Display videos with rich embeds"
)
async def tiktok_user(interaction: discord.Interaction, username: str, max_videos: int = 10, use_embeds: bool = True):
    """Search videos from a specific TikTok user."""
    
    if max_videos < 1 or max_videos > 25:
        await interaction.response.send_message("❌ Maximum videos must be between 1 and 25.", ephemeral=True)
        return
    
    if not TIKTOK_AVAILABLE:
        await interaction.response.send_message("❌ TikTok components not available.", ephemeral=True)
        return
    
    # Clean username
    username = username.lstrip('@').strip()
    if not username:
        await interaction.response.send_message("❌ Please provide a valid username.", ephemeral=True)
        return
    
    try:
        await interaction.response.defer()
        await interaction.edit_original_response(content=f"🔍 **Searching @{username}'s videos...**\n\nPlease wait while I find their latest content!")
        
        videos = await TikTokCommandHandler.search_user_videos(username, max_videos)
        
        if not videos:
            await interaction.edit_original_response(content=f"❌ **No videos found** from @{username}\n\nUser might not exist or have no public videos.")
            return
        await interaction.edit_original_response(content=f"🎯 **Found {len(videos)} videos from @{username}!**\n\n📤 Sending them now...")
        
        if use_embeds:
            await send_videos_with_embeds(interaction, videos, use_embeds=True)
        else:
            await send_videos_in_batches(interaction, videos)
        
    except ValueError as e:
        error_msg = str(e)
        if "detecting bot behavior" in error_msg or "detecting" in error_msg.lower():
            embed = create_bot_detection_embed()
            embed.title = f"🤖 User Search Blocked (@{username})"
            await interaction.edit_original_response(content=None, embed=embed)
        else:
            await interaction.edit_original_response(content=f"❌ **Error:** {str(e)}")
    except Exception as e:
        await interaction.edit_original_response(content=f"❌ **Search Failed:** {str(e)}")

@bot.tree.command(name="tiktok_hashtag", description="Search videos by specific hashtag")
@app_commands.describe(
    hashtag="Hashtag to search (without #)",
    max_videos="Number of videos to get (1-25)",
    use_embeds="Display videos with rich embeds"
)
async def tiktok_hashtag(interaction: discord.Interaction, hashtag: str, max_videos: int = 15, use_embeds: bool = True):
    """Search videos by specific hashtag."""
    
    if max_videos < 1 or max_videos > 25:
        await interaction.response.send_message("❌ Maximum videos must be between 1 and 25.", ephemeral=True)
        return
    
    if not TIKTOK_AVAILABLE:
        await interaction.response.send_message("❌ TikTok components not available.", ephemeral=True)
        return
    
    # Clean hashtag
    hashtag = hashtag.lstrip('#').strip()
    if not hashtag:
        await interaction.response.send_message("❌ Please provide a valid hashtag.", ephemeral=True)
        return
    
    try:
        await interaction.response.defer()
        await interaction.edit_original_response(content=f"🔍 **Searching #{hashtag} videos...**\n\nPlease wait while I find trending content!")
        
        videos = await TikTokCommandHandler.search_hashtag_videos(hashtag, max_videos)
        
        if not videos:
            await interaction.edit_original_response(content=f"❌ **No videos found** for #{hashtag}\n\nHashtag might not exist or have no recent videos.")
            return
        
        await interaction.edit_original_response(content=f"🎯 **Found {len(videos)} videos for #{hashtag}!**\n\n📤 Sending them now...")
        
        if use_embeds:
            await send_videos_with_embeds(interaction, videos, use_embeds=True)
        else:
            await send_videos_in_batches(interaction, videos)
        
    except ValueError as e:
        await interaction.edit_original_response(content=f"❌ **Error:** {str(e)}")
    except Exception as e:
        await interaction.edit_original_response(content=f"❌ **Search Failed:** {str(e)}")

@bot.tree.command(name="tiktok_trending", description="Get current trending hashtags and topics")
@app_commands.describe(count="Number of trending hashtags to get (1-20)")
async def tiktok_trending(interaction: discord.Interaction, count: int = 10):
    """Get current trending hashtags."""
    
    if count < 1 or count > 20:
        await interaction.response.send_message("❌ Count must be between 1 and 20.", ephemeral=True)
        return
    
    if not TIKTOK_AVAILABLE:
        await interaction.response.send_message("❌ TikTok components not available.", ephemeral=True)
        return
    
    try:
        await interaction.response.defer()
        
        trending_hashtags = await TikTokCommandHandler.get_trending_hashtags(count)
        
        if not trending_hashtags:
            await interaction.edit_original_response(content="❌ **No trending hashtags available**")
            return
        
        embed = discord.Embed(
            title="🔥 Trending TikTok Hashtags",
            description="Popular hashtags you can use with `/tiktok_hashtag`",
            color=0xFF6B35
        )
        
        # Split into two columns
        mid_point = len(trending_hashtags) // 2
        left_column = trending_hashtags[:mid_point]
        right_column = trending_hashtags[mid_point:]
        
        left_text = "\n".join([f"#{tag}" for tag in left_column])
        right_text = "\n".join([f"#{tag}" for tag in right_column])
        
        embed.add_field(name="🏷️ Popular Tags", value=left_text, inline=True)
        if right_text:
            embed.add_field(name="🏷️ More Tags", value=right_text, inline=True)
        
        embed.add_field(
            name="💡 Usage Tip",
            value="Use `/tiktok_hashtag hashtag:funny` to search specific hashtags!",
            inline=False
        )
        
        embed.set_footer(text="🎵 TikTok Trending")
        
        await interaction.edit_original_response(content=None, embed=embed)
        
    except Exception as e:
        await interaction.edit_original_response(content=f"❌ **Error:** {str(e)}")

@bot.tree.command(name="tiktok_info", description="Get detailed info about a specific TikTok video")
@app_commands.describe(url="TikTok video URL")
async def tiktok_info(interaction: discord.Interaction, url: str):
    """Get detailed information about a specific TikTok video."""
    
    if not TIKTOK_AVAILABLE:
        await interaction.response.send_message("❌ TikTok components not available.", ephemeral=True)
        return
    
    # Validate URL
    if "tiktok.com" not in url:
        await interaction.response.send_message("❌ Please provide a valid TikTok URL.", ephemeral=True)
        return
    
    try:
        await interaction.response.defer()
        await interaction.edit_original_response(content="🔍 **Analyzing TikTok video...**\n\nPlease wait while I get detailed information!")
        
        video_data = await TikTokCommandHandler.get_video_info(url)
        
        # Create rich embed with all video details
        embed = create_video_embed(video_data)
        embed.title = f"📊 Video Analysis: @{video_data.get('author', 'Unknown')}"
        
        # Add additional analysis fields
        engagement_rate = 0
        if video_data.get('views', 0) > 0:
            engagement_rate = ((video_data.get('likes', 0) + video_data.get('comments', 0)) / video_data.get('views', 1)) * 100
        
        embed.add_field(
            name="📈 Engagement Rate",
            value=f"{engagement_rate:.2f}%",
            inline=True
        )
        
        # Add converted URL for easy sharing
        tnk_url = convert_to_tnktiktok(url)
        embed.add_field(
            name="🔗 Enhanced URL",
            value=f"[Better Discord Preview]({tnk_url})",
            inline=False
        )
        
        await interaction.edit_original_response(content=None, embed=embed)
        
    except ValueError as e:
        await interaction.edit_original_response(content=f"❌ **Error:** {str(e)}")
    except Exception as e:
        await interaction.edit_original_response(content=f"❌ **Analysis Failed:** {str(e)}")

# =============================================================================
# PREFIX COMMANDS (Simplified)
# =============================================================================

@bot.command(name="user")
async def user_prefix(ctx, username: str, max_videos: int = 10):
    """Search TikTok videos from a specific user using prefix command."""
    
    if max_videos < 1 or max_videos > 25:
        await ctx.send("❌ Maximum videos must be between 1 and 25.")
        return
    
    if not TIKTOK_AVAILABLE:
        await ctx.send("❌ TikTok components not available.")
        return
    
    # Clean username
    username = username.lstrip('@').strip()
    if not username:
        await ctx.send("❌ Please provide a valid username.")
        return
    
    loading_msg = await ctx.send(f"🔍 **Searching @{username}'s videos...**")
    
    try:
        videos = await TikTokCommandHandler.search_user_videos(username, max_videos)
        
        if not videos:
            await loading_msg.edit(content=f"❌ **No videos found** from @{username}")
            return
        
        await loading_msg.edit(content=f"🎯 **Found {len(videos)} videos from @{username}!** Sending now...")
        await send_videos_in_batches(ctx, videos)
        
    except Exception as e:
        await loading_msg.edit(content=f"❌ **Search Failed:** {str(e)}")

@bot.command(name="hashtag")
async def hashtag_prefix(ctx, hashtag: str, max_videos: int = 15):
    """Search TikTok videos by hashtag using prefix command."""
    
    if max_videos < 1 or max_videos > 25:
        await ctx.send("❌ Maximum videos must be between 1 and 25.")
        return
    
    if not TIKTOK_AVAILABLE:
        await ctx.send("❌ TikTok components not available.")
        return
    
    # Clean hashtag
    hashtag = hashtag.lstrip('#').strip()
    if not hashtag:
        await ctx.send("❌ Please provide a valid hashtag.")
        return
    
    loading_msg = await ctx.send(f"🔍 **Searching #{hashtag} videos...**")
    
    try:
        videos = await TikTokCommandHandler.search_hashtag_videos(hashtag, max_videos)
        
        if not videos:
            await loading_msg.edit(content=f"❌ **No videos found** for #{hashtag}")
            return
        
        await loading_msg.edit(content=f"🎯 **Found {len(videos)} videos for #{hashtag}!** Sending now...")
        await send_videos_in_batches(ctx, videos)
        
    except Exception as e:
        await loading_msg.edit(content=f"❌ **Search Failed:** {str(e)}")

@bot.command(name="trending")
async def trending_prefix(ctx, count: int = 10):
    """Get trending hashtags using prefix command."""
    
    if count < 1 or count > 20:
        await ctx.send("❌ Count must be between 1 and 20.")
        return
    
    if not TIKTOK_AVAILABLE:
        await ctx.send("❌ TikTok components not available.")
        return
    
    try:
        trending_hashtags = await TikTokCommandHandler.get_trending_hashtags(count)
        
        if not trending_hashtags:
            await ctx.send("❌ **No trending hashtags available**")
            return
        
        embed = discord.Embed(
            title="🔥 Trending TikTok Hashtags",
            description="Popular hashtags you can use with `!hashtag`",
            color=0xFF6B35
        )
        
        # Split into two columns
        mid_point = len(trending_hashtags) // 2
        left_column = trending_hashtags[:mid_point]
        right_column = trending_hashtags[mid_point:]
        
        left_text = "\n".join([f"#{tag}" for tag in left_column])
        right_text = "\n".join([f"#{tag}" for tag in right_column])
        
        embed.add_field(name="🏷️ Popular Tags", value=left_text, inline=True)
        if right_text:
            embed.add_field(name="🏷️ More Tags", value=right_text, inline=True)
        
        embed.add_field(
            name="💡 Usage Tip",
            value="Use `!hashtag funny` to search specific hashtags!",
            inline=False
        )
        
        embed.set_footer(text="🎵 TikTok Trending")
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send(f"❌ **Error:** {str(e)}")

@bot.command(name="info")
async def info_prefix(ctx, url: str):
    """Get detailed info about a TikTok video using prefix command."""
    
    if not TIKTOK_AVAILABLE:
        await ctx.send("❌ TikTok components not available.")
        return
    
    # Validate URL
    if "tiktok.com" not in url:
        await ctx.send("❌ Please provide a valid TikTok URL.")
        return
    
    loading_msg = await ctx.send("🔍 **Analyzing TikTok video...**")
    
    try:
        video_data = await TikTokCommandHandler.get_video_info(url)
        
        # Create rich embed with all video details
        embed = create_video_embed(video_data)
        embed.title = f"📊 Video Analysis: @{video_data.get('author', 'Unknown')}"
        
        # Add additional analysis fields
        engagement_rate = 0
        if video_data.get('views', 0) > 0:
            engagement_rate = ((video_data.get('likes', 0) + video_data.get('comments', 0)) / video_data.get('views', 1)) * 100
        
        embed.add_field(
            name="📈 Engagement Rate",
            value=f"{engagement_rate:.2f}%",
            inline=True
        )
        
        # Add converted URL for easy sharing
        tnk_url = convert_to_tnktiktok(url)
        embed.add_field(
            name="🔗 Enhanced URL",
            value=f"[Better Discord Preview]({tnk_url})",
            inline=False
        )
        
        await loading_msg.edit(content=None, embed=embed)
        
    except Exception as e:
        await loading_msg.edit(content=f"❌ **Analysis Failed:** {str(e)}")

# =============================================================================
# PREFIX COMMANDS (Simplified)
# =============================================================================

@bot.command(name="tiktok")
async def tiktok_prefix(ctx, strategy: str = "parallel", max_videos: int = 15, *, categories: str = None):
    """Search for TikTok videos using prefix command."""
    
    # Validate
    is_valid, message, category_list = TikTokCommandHandler.validate_search_params(strategy, max_videos, categories)
    if not is_valid:
        await ctx.send(message)
        return
    
    # Execute
    loading_msg = await ctx.send("🔍 **Searching TikTok...**\n\nPlease wait while I find videos for you!")
    
    try:
        videos = await TikTokCommandHandler.execute_search(strategy, max_videos, category_list)
        
        if not videos:
            await loading_msg.edit(content="❌ **No unique videos found** matching your criteria.")
            return
        
        await loading_msg.edit(content=f"🎯 **Found {len(videos)} unique videos!** Sending now...")
        await send_videos_in_batches(ctx, videos)
        
    except Exception as e:
        await loading_msg.edit(content=f"❌ **Search Failed:** {str(e)}")

@bot.command(name="validate")
async def validate_prefix(ctx):
    """Validate TikTok session using prefix command."""
    if not TIKTOK_AVAILABLE:
        await ctx.send("❌ **TikTok Not Available**")
        return
    
    loading_msg = await ctx.send("🔍 **Validating TikTok Session...**")
    
    try:
        config = TIKTOK_COMPONENTS['config']
        is_valid, message = await validate_tiktok_session(config['SESSIONID'])
        
        if is_valid:
            embed = create_success_embed("Session Valid", "Your TikTok session ID is working!")
        else:
            embed = create_error_embed("Session Invalid", f"Error: {message}")
            
        await loading_msg.edit(content=None, embed=embed)
        
    except Exception as e:
        await loading_msg.edit(content=f"❌ **Validation Failed:** {str(e)}")

@bot.command(name="database")
async def database_prefix(ctx, action: str = "stats"):
    """Manage database using prefix command."""
    valid_actions = ["stats", "clear", "cleanup", "recent"]
    
    if action not in valid_actions:
        await ctx.send(f"❌ **Invalid Action**\n\nValid actions: {', '.join(valid_actions)}")
        return
    
    await DatabaseManager.handle_database_action(action, ctx.send)

@bot.command(name="stats")
async def stats_prefix(ctx):
    """View bot stats using prefix command."""
    embed = discord.Embed(title="📊 TikTok Bot Statistics", color=0x00ff00)
    
    if TIKTOK_AVAILABLE:
        config = TIKTOK_COMPONENTS['config']
        embed.add_field(
            name="⚙️ Configuration",
            value=f"• **Strategy:** {config['SEARCH_STRATEGY'].title()}\n"
                  f"• **Max Videos:** {config['MAX_TOTAL_VIDEOS']}\n"
                  f"• **Session:** {'✅ Configured' if config['SESSIONID'] else '❌ Not configured'}",
            inline=False
        )
    else:
        embed.add_field(name="❌ Status", value="TikTok components not available", inline=False)
    
    await ctx.send(embed=embed)

@bot.command(name="help_tiktok")
async def help_tiktok_prefix(ctx):
    """Show TikTok bot help using prefix command."""
    embed = discord.Embed(
        title="🎵 TikTok Bot Help (Prefix Commands)",
        description="Available prefix commands:",
        color=0xff0050
    )
    
    embed.add_field(
        name="📋 Commands",
        value="`!tiktok [strategy] [max_videos] [categories]`\n"
              "`!user <username> [max_videos]` - Search user videos\n"
              "`!hashtag <hashtag> [max_videos]` - Search by hashtag\n"
              "`!trending [count]` - Get trending hashtags\n"
              "`!info <url>` - Analyze video URL\n"
              "`!validate` - Check session\n"
              "`!database [action]` - Manage database\n"
              "`!stats` - View configuration",
        inline=False
    )
    
    await ctx.send(embed=embed)

# =============================================================================
# MAIN FUNCTION
# =============================================================================

async def main():
    """Main async function to start the bot."""
    try:
        print("🔍 Checking bot configuration...")
        
        if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
            print("❌ Error: Please set your Discord bot token in bot_config.py")
            return
        
        if TIKTOK_AVAILABLE and not TIKTOK_COMPONENTS['config']['SESSIONID']:
            print("⚠️ Warning: TikTok sessionid not configured")
        
        print("🚀 Starting TikTok Discord Bot...")
        await bot.start(BOT_TOKEN)
        
    except discord.LoginFailure:
        print("❌ Login failed! Invalid bot token.")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    finally:
        if not bot.is_closed():
            await bot.close()

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    logging.getLogger("TikTokApi").setLevel(logging.WARNING)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Failed to start bot: {e}")
