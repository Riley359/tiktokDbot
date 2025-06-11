# Discord TikTok Bot Setup Guide

## 🎯 Overview
This Discord bot integrates with your TikTok scraper to search and display TikTok videos directly in Discord using slash commands with beautiful embeds and pagination.

## 🚀 Features
- **Slash Commands**: Modern Discord slash command interface
- **Multiple Search Strategies**: Parallel, Sequential, Hashtag-only, and Personalized AI-driven search
- **Rich Embeds**: Beautiful TikTok video displays with stats and direct links
- **Pagination**: Navigate through results with interactive buttons
- **Category Filtering**: Search specific content categories
- **Real-time Configuration**: View bot stats and current settings
- **Error Handling**: Comprehensive error messages and troubleshooting

## 📋 Prerequisites
1. **Python 3.8+** installed
2. **Discord Developer Account** and bot token
3. **TikTok Session ID** configured
4. **Required Python packages** installed

## 🔧 Installation Steps

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Create Discord Bot
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and give it a name
3. Go to "Bot" section in the left sidebar
4. Click "Reset Token" and copy the token
5. Under "Privileged Gateway Intents", enable:
   - Message Content Intent
   - Server Members Intent (optional)

### Step 3: Configure Bot Token
Edit `bot_config.py` and replace `YOUR_BOT_TOKEN_HERE` with your actual bot token:
```python
BOT_TOKEN = "your_actual_bot_token_here"
```

### Step 4: Configure TikTok Session
Make sure your TikTok sessionid is configured in `src/config.py`:
```python
SESSIONID = "your_tiktok_sessionid_here"
```

### Step 5: Invite Bot to Server
1. In Discord Developer Portal, go to "OAuth2" > "URL Generator"
2. Select scopes: `bot` and `applications.commands`
3. Select bot permissions: `Send Messages`, `Use Slash Commands`, `Embed Links`
4. Copy the generated URL and open it to invite the bot

### Step 6: Run the Bot
```bash
python discord_bot.py
```

## 🎮 Using the Bot

### Main Commands

#### `/tiktok` - Search for TikTok Videos
**Parameters:**
- `strategy` (optional): Search method
  - `Parallel (All methods)` - Uses all search methods simultaneously
  - `Sequential (Fallback)` - Tries methods one by one
  - `Hashtag Only` - Searches only by hashtags  
  - `Personalized (AI)` - AI-driven based on preferences
- `max_videos` (optional): Number of videos (1-25, default: 15)
- `categories` (optional): Comma-separated categories

**Examples:**
```
/tiktok
/tiktok strategy:parallel max_videos:10
/tiktok strategy:personalized categories:music_dance,trending
/tiktok strategy:hashtag_only max_videos:20 categories:entertainment,gaming
```

#### `/tiktok_help` - Get Help
Shows detailed information about commands and features.

#### `/tiktok_stats` - View Configuration
Displays current bot configuration and TikTok scraper settings.

### Available Categories
- `trending` - Viral and trending content
- `entertainment` - Comedy, memes, pranks
- `music_dance` - Music and dance videos
- `lifestyle` - Fashion, beauty, style
- `food` - Cooking, recipes, food content
- `tech` - Technology and gadgets
- `fitness` - Workout and health content
- `travel` - Travel and adventure
- `pets` - Animal and pet content
- `diy_crafts` - DIY and creative content
- `gaming` - Gaming content
- `education` - Educational content

## 🎨 Bot Features

### Interactive Embeds
- **Rich Video Information**: Author, caption, stats (likes, views, comments, shares)
- **Direct TikTok Links**: Click to watch videos on TikTok
- **Pagination**: Navigate through results with Previous/Next buttons
- **Refresh Option**: Re-run searches with refresh button

### Error Handling
The bot provides helpful error messages for:
- Invalid parameters
- Missing configuration
- Network issues
- API limitations
- Rate limiting

### Real-time Stats
View current configuration including:
- Search strategy settings
- Filter requirements
- Personalization settings
- API status

## ⚙️ Configuration

### Bot Settings (bot_config.py)
```python
BOT_TOKEN = "your_bot_token"
COMMAND_PREFIX = "!"
MAX_VIDEOS_PER_REQUEST = 25
DEFAULT_SEARCH_STRATEGY = "parallel"
DEFAULT_MAX_VIDEOS = 15
EMBED_COLOR = 0xff0050  # TikTok brand color
```

### TikTok Settings (src/config.py)
The bot uses your existing TikTok scraper configuration:
- Search strategies
- Filter settings
- Personalization options
- Category definitions

## 🔍 Troubleshooting

### Common Issues

#### "TikTok scraper components not available"
**Solution:** Install required packages
```bash
pip install -r requirements.txt
```

#### "TikTok sessionid not configured"
**Solution:** Add your sessionid to `src/config.py`
1. Open TikTok in browser and login
2. Open Developer Tools (F12)
3. Go to Application/Storage → Cookies → https://www.tiktok.com
4. Find 'sessionid' cookie and copy its value
5. Paste in `SESSIONID` variable

#### "No videos found"
**Solutions:**
- Try different search strategy
- Lower filter requirements in `src/config.py`
- Use different categories
- Check network connection

#### Bot not responding to commands
**Solutions:**
- Ensure bot has proper permissions
- Check if slash commands are synced
- Verify bot token is correct
- Make sure bot is online

### Permission Requirements
The bot needs these Discord permissions:
- Send Messages
- Use Slash Commands
- Embed Links
- Read Message History

## 🎯 Advanced Usage

### Personalized Search
For best results with personalized search:
1. Set `ANALYZE_LIKED_VIDEOS = True` in config
2. Increase `LIKED_VIDEOS_ANALYZE_COUNT` for better preferences
3. Adjust `MIN_PREFERENCE_SCORE` for filtering sensitivity

### Custom Categories
Add custom categories in `src/config.py`:
```python
HASHTAG_CATEGORIES = {
    "custom_category": ["hashtag1", "hashtag2", "hashtag3"]
}
```

### Rate Limiting
The bot includes built-in rate limiting to prevent API abuse:
- 0.3 second delay between video processing
- Configurable maximum videos per request
- Automatic retry logic for failed requests

## 📈 Performance Tips
- Use `parallel` strategy for fastest results
- Limit `max_videos` for quicker responses
- Use specific categories to narrow search scope
- Configure appropriate filter thresholds

## 🆘 Support
If you encounter issues:
1. Check the troubleshooting section above
2. Verify all configuration files are properly set up
3. Ensure all dependencies are installed
4. Check Discord bot permissions and server settings

## 🔄 Updates
To update the bot:
1. Pull latest changes
2. Update dependencies: `pip install -r requirements.txt --upgrade`
3. Restart the bot

Enjoy using your TikTok Discord bot! 🎉
