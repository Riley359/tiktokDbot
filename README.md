# TikTok "For You" Page Scraper

## ✅ Current Status: WORKING! 

**Last Updated:** June 9, 2025

✅ **Successfully bypassing TikTok bot detection**  
✅ **Scraping videos with full metadata**  
✅ **Downloading videos without watermarks**  
✅ **18/20 videos downloaded successfully in latest test**

---

A Python script that scrapes videos from TikTok's personalized "For You" page using the TikTok-Api library. The script can extract video metadata and optionally download videos without watermarks.

## Features

- 🔐 **Secure Authentication**: Uses sessionid cookie method (no username/password storage)
- 📱 **"For You" Page Scraping**: Fetches videos from your personalized feed
- 🧠 **AI-Powered Personalized Algorithm**: NEW! Analyzes your liked videos to build preference profiles
- 🎯 **Smart Search Strategies**: Multiple search modes including personalized, parallel, sequential, and hashtag-only
- 📊 **Comprehensive Data Extraction**: Gets video ID, URL, description, author, likes, comments, shares, and play counts
- 🤖 **Preference Learning**: Builds and updates user preference profiles for smarter content discovery
- 🔍 **Intelligent Filtering**: Preference-based scoring and content similarity matching
- 🤖 **Discord Bot Integration**: NEW! Full Discord bot with slash commands and rich embeds
- 💾 **Optional Video Downloading**: Downloads videos without watermarks
- 📈 **Advanced Analytics**: Engagement pattern analysis and content categorization
- 🛡️ **Error Handling**: Graceful error handling with clear error messages
- 🎨 **Clean Output**: Well-formatted console output with progress indicators

## 🤖 NEW: Discord Bot Features

### Interactive Discord Experience
- **Slash Commands**: Modern Discord slash command interface (`/tiktok`, `/tiktok_help`, `/tiktok_stats`)
- **Rich Embeds**: Beautiful TikTok video displays with stats, captions, and direct links
- **Pagination**: Navigate through results with interactive Previous/Next buttons
- **Real-time Search**: Live TikTok searching directly in Discord channels
- **Category Filtering**: Search specific content categories from Discord
- **Multi-Strategy Support**: Access all search strategies (parallel, personalized, etc.) via Discord

### Discord Bot Commands
- `/tiktok` - Search for TikTok videos with customizable parameters
- `/tiktok_help` - Get detailed help and usage examples
- `/tiktok_stats` - View current bot configuration and scraper settings

### Quick Discord Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Configure bot token in bot_config.py
BOT_TOKEN = "your_discord_bot_token"

# Run the bot
python discord_bot.py
```

**📖 For detailed Discord bot setup:** See [DISCORD_BOT_GUIDE.md](DISCORD_BOT_GUIDE.md)

## 🧠 NEW: Personalized Algorithm Features

### Liked Videos Analysis
- **Automatic Analysis**: Fetches and analyzes your liked videos to understand preferences
- **Pattern Recognition**: Identifies preferred hashtags, keywords, creators, and content types
- **Engagement Insights**: Analyzes your engagement patterns and content preferences
- **Preference Profiles**: Builds comprehensive user preference profiles saved to JSON

### Smart Search Strategy
- **AI-Driven Hashtags**: Automatically generates optimal search hashtags based on preferences
- **Creator Prioritization**: Prioritizes content from your preferred creators
- **Category Matching**: Focuses on content categories you engage with most
- **Adaptive Learning**: Improves recommendations over time based on your interactions

### Enhanced Filtering System
- **Preference Scoring**: Scores content based on similarity to your preferences (0.0-1.0)
- **Multi-Factor Analysis**: Considers hashtags, keywords, creators, categories, and engagement
- **Customizable Thresholds**: Configurable minimum preference scores for quality control
- **Smart Recommendations**: Returns only content that matches your interests

### Configuration Options
```python
# Paste your sessionid here
SESSIONID = "your_sessionid_here"

# Number of videos to scrape
NUM_VIDEOS = 10

# Enable/disable video downloading
DOWNLOAD_VIDEOS = True

# Directory to save videos
DOWNLOAD_DIR = "tiktok_videos"

# Personalized Algorithm Settings
SEARCH_STRATEGY = "personalized"          # Use AI-powered personalized search
ANALYZE_LIKED_VIDEOS = True               # Analyze user's liked videos
LIKED_VIDEOS_ANALYZE_COUNT = 50           # Number of liked videos to analyze
USE_PERSONALIZED_FILTERING = True         # Apply preference-based filtering
MIN_PREFERENCE_SCORE = 0.3                # Minimum preference match score (0.0-1.0)
PREFERENCE_PROFILE_FILE = "user_preferences.json"  # Profile storage location

# Advanced personalization weights
PERSONALIZATION_WEIGHTS = {
    "hashtag_match": 0.3,        # Hashtag similarity importance
    "keyword_match": 0.25,       # Keyword similarity importance  
    "creator_match": 0.2,        # Creator preference importance
    "category_match": 0.15,      # Category preference importance
    "engagement_pattern": 0.1    # Engagement pattern importance
}
```

## Usage

Run the script:

```bash
python scraper.py
```

### Expected Output

```
🚀 Starting TikTok 'For You' page scraper...
📊 Target videos: 10
💾 Download videos: Yes
📁 Download directory: tiktok_videos
==================================================
✓ TikTok API initialized successfully
🔍 Fetching 10 videos from 'For You' page...
✓ Found 10 videos

--- Video 1 ---
ID: 7212345678901234567
Author: @coolcreator
Caption: This is my awesome new video! #fyp
URL: https://www.tiktok.com/@coolcreator/video/7212345678901234567
Likes: 150,321
Comments: 2,489
Shares: 5,432
Plays: 1,234,567
----------------------------------------
✓ Downloaded video 7212345678901234567 from coolcreator

--- Video 2 ---
...
```

## File Structure

```
tikTokDbot/
├── scraper.py             # Main entry point
├── src/                   # Source code modules
│   ├── __init__.py        # Package initialization
│   ├── config.py          # Configuration settings
│   ├── utils.py           # Utility functions
│   ├── filters.py         # Video filtering logic
│   ├── downloader.py      # Video download functionality
│   ├── personalization.py # AI personalization features
│   └── search_strategies.py # Search algorithm strategies
├── requirements.txt       # Python dependencies
├── README.md             # This file
└── tiktok_videos/        # Downloaded videos (created automatically)
    ├── .mp4
    └── ...
```

## Configuration Options

| Variable | Description | Default |
|----------|-------------|---------|
| `SESSIONID` | Your TikTok sessionid cookie | `""` (must be set) |
| `NUM_VIDEOS` | Number of videos to scrape | `10` |
| `DOWNLOAD_VIDEOS` | Enable/disable video downloading | `True` |
| `DOWNLOAD_DIR` | Directory for downloaded videos | `"tiktok_videos"` |

## Troubleshooting

### Common Issues

1. **"Please provide your TikTok sessionid!" Error**
   - Make sure you've copied your sessionid correctly
   - Ensure the sessionid is still valid (try logging out and back in)

2. **"No videos found" Error**
   - Your sessionid might be expired - get a fresh one
   - You might be rate-limited - wait a few minutes and try again
   - TikTok might have changed their API

3. **Download Failures**
   - Check your internet connection
   - Ensure you have write permissions in the script directory
   - Some videos might be region-restricted

4. **Rate Limiting**
   - The script includes delays between downloads
   - If you encounter rate limits, reduce `NUM_VIDEOS` or increase delays

### Getting a Fresh sessionid

If your sessionid stops working:
1. Log out of TikTok in your browser
2. Clear TikTok cookies
3. Log back in
4. Get a new sessionid following the setup instructions

## Legal and Ethical Considerations

- ⚖️ **Respect TikTok's Terms of Service**
- 🚫 **Don't use for commercial purposes without permission**
- 📊 **Use for research, backup, or personal use only**
- ⏱️ **Respect rate limits to avoid being blocked**
- 🔒 **Keep your sessionid secure and don't share it**

## Dependencies

- `TikTokApi>=5.2.0` - Main TikTok API library
- `requests>=2.28.0` - HTTP requests library
- `playwright>=1.40.0` - Browser automation library (required by TikTokApi)

**Note:** After installing the packages, you must also install playwright browsers:
```bash
python -m playwright install
```

## Limitations

- Only works with accounts that have a valid sessionid
- May break if TikTok changes their API
- Rate limiting may affect large scraping operations
- Some videos may not be downloadable due to privacy settings

## Contributing

Feel free to submit issues or pull requests to improve this script!

## Disclaimer

This tool is for educational and personal use only. Please respect TikTok's terms of service and content creators' rights. The authors are not responsible for any misuse of this tool.
