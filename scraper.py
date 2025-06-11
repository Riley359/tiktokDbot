"""Main TikTok scraper entry point."""

import asyncio
import logging
import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from TikTokApi import TikTokApi

from config import *
from utils import create_download_directory, print_all_links, extract_video_data, print_video_info
from search_strategies import (
    parallel_search_strategy, sequential_search_strategy,
    hashtag_only_strategy, personalized_search_strategy
)
from filters import passes_trend_filters, passes_content_filters, passes_personalized_filters
from personalization import PreferenceAnalyzer, PersonalizedSearchEngine, build_preference_profile
from downloader import download_video


async def main():
    """Main function to run the enhanced TikTok scraper."""
    
    # Validate sessionid
    if not SESSIONID or SESSIONID == "":
        print("❌ Error: Please provide your TikTok sessionid!")
        print("\nHow to get your sessionid:")
        print("1. Open TikTok in your web browser and log in")
        print("2. Open Developer Tools (F12)")
        print("3. Go to Application/Storage tab -> Cookies -> https://www.tiktok.com")
        print("4. Find 'sessionid' cookie and copy its value")
        print("5. Paste it in the SESSIONID variable in src/config.py")
        return
    
    # Create download directory if needed
    if DOWNLOAD_VIDEOS:
        create_download_directory()
    
    print(f"🚀 Starting Enhanced TikTok Scraper...")
    print(f"🔍 Search Strategy: {SEARCH_STRATEGY.upper()}")
    print(f"📊 Target videos: {MAX_TOTAL_VIDEOS}")
    print(f"💾 Download videos: {'Yes' if DOWNLOAD_VIDEOS else 'No'}")
    print(f"🏷️ Active categories: {', '.join(ACTIVE_CATEGORIES) if ACTIVE_CATEGORIES else 'ALL'}")
    print(f"📈 Trend filters: Likes>{TREND_FILTERS['min_likes']}, Views>{TREND_FILTERS['min_views']}")
    
    # Show personalized settings if using personalized strategy
    if SEARCH_STRATEGY == "personalized":
        print(f"🧠 Personalized Settings:")
        print(f"   📱 Analyze liked videos: {'Yes' if ANALYZE_LIKED_VIDEOS else 'No'}")
        print(f"   📊 Liked videos to analyze: {LIKED_VIDEOS_ANALYZE_COUNT}")
        print(f"   🎯 Min preference score: {MIN_PREFERENCE_SCORE}")
        print(f"   💾 Preference profile: {PREFERENCE_PROFILE_FILE}")
    
    print("=" * 60)
    
    try:
        # Enhanced anti-detection configuration
        async with TikTokApi() as api:
            print("✓ TikTok API initialized successfully")
            
            # Create sessions
            await api.create_sessions(
                ms_tokens=[SESSIONID],
                num_sessions=1,
                headless=False
            )
            
            # Execute search strategy
            strategy_map = {
                "parallel": parallel_search_strategy,
                "sequential": sequential_search_strategy,
                "hashtag_only": hashtag_only_strategy,
                "personalized": personalized_search_strategy
            }
            
            if SEARCH_STRATEGY not in strategy_map:
                print(f"❌ Unknown search strategy: {SEARCH_STRATEGY}")
                return
            
            videos = await strategy_map[SEARCH_STRATEGY](api)
            
            if not videos:
                print("❌ No videos found with the current search strategy.")
                print("💡 Try:")
                print("   - Switching to a different search strategy")
                print("   - Lowering filter requirements")
                print("   - Checking your sessionid")
                return
            
            # Initialize search engine for personalized filtering if needed
            search_engine = None
            if USE_PERSONALIZED_FILTERING or SEARCH_STRATEGY == "personalized":
                if SEARCH_STRATEGY == "personalized":
                    # Reuse the analyzer from personalized search
                    analyzer = await build_preference_profile(api)
                    search_engine = PersonalizedSearchEngine(analyzer)
                else:
                    # Create new analyzer for filtering
                    analyzer = PreferenceAnalyzer()
                    if analyzer.load_preferences(PREFERENCE_PROFILE_FILE):
                        search_engine = PersonalizedSearchEngine(analyzer)
                    else:
                        print("⚠️ No preference profile found for personalized filtering, using basic filters only")
            
            # Process videos
            video_links = []
            trend_filtered_count = 0
            content_filtered_count = 0
            personalized_filtered_count = 0
            
            for i, video in enumerate(videos, 1):
                try:
                    video_data = extract_video_data(video)
                    if not video_data:
                        continue
                    
                    # Apply trend filters
                    if not passes_trend_filters(video_data):
                        trend_filtered_count += 1
                        continue
                    
                    # Apply content filters
                    if not passes_content_filters(video_data):
                        content_filtered_count += 1
                        continue
                    
                    # Apply personalized filters if enabled and not already done in search
                    if search_engine and USE_PERSONALIZED_FILTERING and SEARCH_STRATEGY != "personalized":
                        passes_filter, preference_score = passes_personalized_filters(video_data, search_engine)
                        if not passes_filter:
                            personalized_filtered_count += 1
                            continue
                    
                    # Video passed all filters
                    print_video_info(video_data, len(video_links) + 1)
                    video_links.append(video_data)
                    
                    # Download video if enabled
                    if DOWNLOAD_VIDEOS:
                        success = await download_video(video, video_data)
                        if success:
                            print(f"✓ Video {video_data['id']} downloaded successfully")
                        else:
                            print(f"⚠️ Failed to download video {video_data['id']}")
                    
                    # Rate limiting
                    await asyncio.sleep(0.3)
                    
                except Exception as e:
                    print(f"❌ Error processing video {i}: {str(e)}")
                    continue
            
            # Print summary statistics
            print("\n" + "=" * 60)
            print("📊 SCRAPING SUMMARY")
            print("=" * 60)
            print(f"📊 Videos found: {len(videos)}")
            print(f"✅ Videos passed all filters: {len(video_links)}")
            print(f"📈 Filtered by trend criteria: {trend_filtered_count}")
            print(f"📝 Filtered by content criteria: {content_filtered_count}")
            if USE_PERSONALIZED_FILTERING or SEARCH_STRATEGY == "personalized":
                print(f"🧠 Filtered by personalized criteria: {personalized_filtered_count}")
            print(f"🔍 Search strategy used: {SEARCH_STRATEGY.upper()}")
            
            if ACTIVE_CATEGORIES:
                print(f"🏷️ Categories searched: {', '.join(ACTIVE_CATEGORIES)}")
            
            # Show personalized insights if available
            if search_engine and (USE_PERSONALIZED_FILTERING or SEARCH_STRATEGY == "personalized"):
                top_prefs = search_engine.analyzer.get_top_preferences(3)
                if top_prefs['total_analyzed'] > 0:
                    print(f"\n🎯 Personalized Insights:")
                    print(f"   📊 Total liked videos analyzed: {top_prefs['total_analyzed']}")
                    if top_prefs['top_hashtags']:
                        print(f"   🏷️ Top hashtag preferences: {', '.join(['#' + k for k in list(top_prefs['top_hashtags'].keys())[:3]])}")
                    if top_prefs['top_authors']:
                        print(f"   👤 Preferred creators: {', '.join(['@' + k for k in list(top_prefs['top_authors'].keys())[:3]])}")
                    if top_prefs['top_categories']:
                        print(f"   📂 Preferred categories: {', '.join(list(top_prefs['top_categories'].keys())[:3])}")
            
            # Print all collected TikTok links
            if video_links:
                print_all_links(video_links)
            else:
                print("\n💡 No videos passed the filters. Consider:")
                print("   - Lowering trend filter requirements")
                print("   - Removing content filters")
                print("   - Adding more hashtag categories")
                if SEARCH_STRATEGY == "personalized":
                    print("   - Lowering the minimum preference score")
                    print("   - Analyzing more liked videos for better preferences")
        
    except Exception as e:
        print(f"❌ Fatal error: {str(e)}")
        print("\nPossible causes:")
        print("- Invalid sessionid")
        print("- Network connection issues")
        print("- TikTok API changes")
        print("- Rate limiting")
        print("- Missing playwright installation (run: python -m playwright install)")
        
        if "sessionid" in str(e).lower():
            print("\n💡 Try getting a fresh sessionid from your browser")


if __name__ == "__main__":
    # Configure logging to reduce noise
    logging.getLogger("TikTokApi").setLevel(logging.WARNING)
    
    # Run the async main function
    asyncio.run(main())
