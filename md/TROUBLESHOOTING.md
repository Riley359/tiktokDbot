# TikTok Bot Troubleshooting Guide

## Common Issues and Solutions

### ❌ "TikTok returned an empty response. They are detecting you're a bot"

This is the most common issue. TikTok has sophisticated bot detection mechanisms.

**Solutions:**

1. **Check Your Session ID**
   ```
   Use /tiktok_validate in Discord to test your session
   ```

2. **Get a Fresh Session ID**
   - Open TikTok in your browser
   - Log in to your account
   - Open Developer Tools (F12)
   - Go to Application/Storage → Cookies → https://www.tiktok.com
   - Find `sessionid` cookie and copy its value
   - Update `src/config.py` with the new session ID

3. **Session ID Requirements**
   - Must be from a logged-in TikTok account
   - Should be 32+ characters long
   - Must be recent (expires after some time)
   - Account should have some activity (likes, follows)

4. **Additional Anti-Detection Measures**
   - The bot now tries multiple browser configurations
   - Uses realistic user agents
   - Adds delays between requests
   - Falls back to visible browser if needed

### ⚠️ "Session token is invalid or expired"

**Solutions:**
1. Get a new session ID following the steps above
2. Make sure you're copying the entire session ID
3. Ensure your TikTok account is active and not restricted

### 🔄 "Network issues" or "Connection failed"

**Solutions:**
1. Check your internet connection
2. Try again in a few minutes
3. Consider using a VPN or proxy
4. Restart the bot

### 🚫 "No unique videos found"

**Solutions:**
1. Use `/tiktok_database action:cleanup` to allow older videos
2. Try different search strategies
3. Change categories or remove category filters
4. Lower filter requirements in `src/config.py`

## Prevention Tips

1. **Keep Session Fresh**
   - Update session ID weekly
   - Use the account regularly in browser
   - Don't share session IDs

2. **Moderate Usage**
   - Don't make too many requests too quickly
   - Use reasonable video counts (≤25)
   - Space out searches

3. **Monitor Bot Health**
   - Use `/tiktok_validate` regularly
   - Check `/tiktok_stats` for configuration
   - Monitor error messages

## Configuration Tips

### For Better Success Rates:

1. **In `src/config.py`:**
   ```python
   # Use lower requirements to get more videos
   TREND_FILTERS = {
       "min_likes": 500,        # Lower than 1000
       "min_views": 5000,       # Lower than 10000
       "min_comments": 10,      # Lower than 20
       "max_age_days": 60       # Higher than 30
   }
   ```

2. **Try Different Strategies:**
   - `parallel` - Best for variety
   - `hashtag_only` - More reliable but limited
   - `sequential` - Good fallback
   - `personalized` - Requires setup but very effective

3. **Active Categories:**
   ```python
   # Try fewer categories for better results
   ACTIVE_CATEGORIES = ["trending", "entertainment"]  # Instead of many
   ```

## Advanced Solutions

### If Bot Detection Persists:

1. **Use Proxy Services:**
   - Residential proxies work best
   - Rotate proxies for different requests
   - Configure in TikTokApi settings

2. **Account Preparation:**
   - Use an older TikTok account
   - Have real activity (likes, comments, follows)
   - Use the account normally in browser

3. **Server Considerations:**
   - Some VPS providers are blocked by TikTok
   - Consider different hosting locations
   - Avoid shared hosting with other bots

## Getting Help

1. **Check Bot Logs:**
   - Look for specific error messages
   - Note when errors occur
   - Check patterns in failures

2. **Discord Commands:**
   - `/tiktok_validate` - Test session
   - `/tiktok_stats` - Check configuration
   - `/tiktok_help` - Command reference

3. **File Locations:**
   - `src/config.py` - Main configuration
   - `TIKTOK_SESSION_GUIDE.md` - Session setup guide
   - Bot logs in console/terminal

Remember: TikTok actively fights against bots, so some issues are expected. The key is maintaining fresh sessions and using the bot moderately.
