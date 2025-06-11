"""
Example Configuration for TikTok Scraper
========================================

Copy the values below into src/config.py after getting your sessionid.
"""

# Example configuration - DO NOT USE THESE VALUES
EXAMPLE_CONFIG = {
    # Replace with your actual sessionid from browser cookies
    "SESSIONID": "your_actual_sessionid_goes_here_it_will_be_very_long",
    
    # Number of videos to scrape (start small for testing)
    "NUM_VIDEOS": 5,
    
    # Set to False if you only want metadata, not video files
    "DOWNLOAD_VIDEOS": True,
    
    # Directory name for downloaded videos
    "DOWNLOAD_DIR": "tiktok_videos"
}

# Steps to get your sessionid:
# 1. Go to tiktok.com in your browser
# 2. Log in to your account
# 3. Press F12 to open developer tools
# 4. Go to Application tab (Chrome) or Storage tab (Firefox)
# 5. Click on Cookies -> https://www.tiktok.com
# 6. Find the 'sessionid' cookie
# 7. Copy its value (it will be a long string)
# 8. Paste it in the SESSIONID variable in src/config.py
