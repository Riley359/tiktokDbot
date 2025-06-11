"""Different search strategy implementations."""

import asyncio
from config import MAX_TOTAL_VIDEOS, VIDEOS_PER_METHOD, MIN_VIDEOS_PER_HASHTAG
from utils import get_active_hashtags, get_diversified_hashtags
from personalization import build_preference_profile, PersonalizedSearchEngine
from filters import passes_personalized_filters


async def get_videos_by_hashtag(api, hashtag, count, max_retries=2):
    """Get videos from a specific hashtag with retry logic."""
    videos = []
    
    for attempt in range(max_retries + 1):
        try:
            print(f"🔍 Searching hashtag: #{hashtag}{' (retry attempt '+str(attempt)+')' if attempt > 0 else ''}")
            hashtag_obj = api.hashtag(name=hashtag)
            
            video_count = 0
            async for video in hashtag_obj.videos(count=count):
                videos.append(video)
                video_count += 1
                if video_count >= count:
                    break
            
            if videos:
                print(f"✓ Found {len(videos)} videos for #{hashtag}")
                return videos
            else:
                print(f"⚠️ No videos found for #{hashtag}, {'retrying...' if attempt < max_retries else 'giving up.'}")
                if attempt < max_retries:
                    # Wait a bit before retrying to avoid rate limits
                    await asyncio.sleep(1.5)
                    continue
                else:
                    return []
                
        except Exception as e:
            print(f"❌ Error fetching videos for #{hashtag}: {str(e)}")
            if attempt < max_retries:
                print(f"⏳ Retrying in 2 seconds... (attempt {attempt+1}/{max_retries})")
                await asyncio.sleep(2)
            else:
                print(f"❌ All retry attempts failed for #{hashtag}")
                return []
    
    return []


async def parallel_search_strategy(api, retry_attempt=0, used_hashtags=None):
    """Execute parallel search strategy - run all methods simultaneously with hashtag diversification."""
    print(f"🚀 Using PARALLEL search strategy (attempt {retry_attempt + 1})")
    print(f"🎯 Target: {MAX_TOTAL_VIDEOS} total videos")
    
    all_videos = []
    video_ids_seen = set()
    
    # Method 1: Trending videos
    try:
        print("📈 Fetching trending videos...")
        trending_count = 0
        async for video in api.trending.videos(count=VIDEOS_PER_METHOD):
            if video.id not in video_ids_seen:
                all_videos.append(video)
                video_ids_seen.add(video.id)
                trending_count += 1
            if len(all_videos) >= MAX_TOTAL_VIDEOS:
                break
        print(f"✓ Trending: {trending_count} unique videos")
    except Exception as e:
        print(f"⚠️ Trending failed: {str(e)}")
    
    # Method 2: For You videos as alternative to discover
    if len(all_videos) < MAX_TOTAL_VIDEOS:
        try:
            print("🔍 Fetching For You videos...")
            discover_count = 0
            async for video in api.for_you.videos(count=VIDEOS_PER_METHOD):
                if video.id not in video_ids_seen:
                    all_videos.append(video)
                    video_ids_seen.add(video.id)
                    discover_count += 1
                if len(all_videos) >= MAX_TOTAL_VIDEOS:
                    break
            print(f"✓ For You: {discover_count} unique videos")
        except Exception as e:
            print(f"⚠️ For You videos failed: {str(e)}")
      # Method 3: Hashtag-based videos with diversification
    if len(all_videos) < MAX_TOTAL_VIDEOS:
        # Get diversified hashtags for this attempt
        if retry_attempt > 0 and used_hashtags:
            active_hashtags = get_diversified_hashtags(used_hashtags=used_hashtags, retry_attempt=retry_attempt, max_hashtags=50)
            print(f"🔄 Using diversified hashtags for retry attempt {retry_attempt}")
        else:
            active_hashtags = get_active_hashtags()
        
        print(f"🏷️ Fetching from {len(active_hashtags)} hashtags...")
        hashtag_count = 0
        for hashtag in active_hashtags:
            if len(all_videos) >= MAX_TOTAL_VIDEOS:
                break
            
            # Track hashtag usage
            if used_hashtags is not None:
                used_hashtags.add(hashtag)
            
            print(f"🔍 Searching hashtag: #{hashtag}")
            hashtag_videos = await get_videos_by_hashtag(api, hashtag, MIN_VIDEOS_PER_HASHTAG)
            for video in hashtag_videos:
                if video.id not in video_ids_seen:
                    all_videos.append(video)
                    video_ids_seen.add(video.id)
                    hashtag_count += 1
                if len(all_videos) >= MAX_TOTAL_VIDEOS:
                    break
            
            print(f"✓ Found {len(hashtag_videos)} videos for #{hashtag}")
        
        print(f"✓ Hashtags: {hashtag_count} unique videos")
    
    return all_videos


async def sequential_search_strategy(api, retry_attempt=0, used_hashtags=None):
    """Execute sequential search strategy - fallback approach with hashtag diversification."""
    print(f"🔄 Using SEQUENTIAL search strategy (attempt {retry_attempt + 1})")
    print(f"🎯 Target: {MAX_TOTAL_VIDEOS} total videos")
    
    videos = []
    
    # Try trending videos first
    try:
        print("📈 Fetching trending videos...")
        trending_count = 0
        async for video in api.trending.videos(count=MAX_TOTAL_VIDEOS):
            videos.append(video)
            trending_count += 1
            if len(videos) >= MAX_TOTAL_VIDEOS:
                break
        print(f"✓ Trending: {trending_count} videos")
    except Exception as trending_error:
        print(f"⚠️ Trending failed: {str(trending_error)}")
        
        # Try For You videos if trending fails
        try:
            print("🔍 Trying For You approach...")
            discover_count = 0
            async for video in api.for_you.videos(count=MAX_TOTAL_VIDEOS):
                videos.append(video)
                discover_count += 1
                if len(videos) >= MAX_TOTAL_VIDEOS:
                    break
            print(f"✓ For You: {discover_count} videos")
        except Exception as discover_error:
            print(f"⚠️ For You failed: {str(discover_error)}")
            
            # Last resort: hashtags with diversification
            try:
                print("🏷️ Trying hashtag approach...")
                # Get diversified hashtags for this attempt
                if retry_attempt > 0 and used_hashtags:
                    active_hashtags = get_diversified_hashtags(used_hashtags, retry_attempt)
                    print(f"🔄 Using diversified hashtags for retry attempt {retry_attempt + 1}")
                else:
                    active_hashtags = get_active_hashtags()
                for hashtag in active_hashtags:
                    if len(videos) >= MAX_TOTAL_VIDEOS:
                        break
                    
                    # Track hashtag usage
                    if used_hashtags is not None:
                        used_hashtags.add(hashtag)
                        
                    hashtag_videos = await get_videos_by_hashtag(api, hashtag, MIN_VIDEOS_PER_HASHTAG)
                    videos.extend(hashtag_videos)
                print(f"✓ Hashtags: {len(videos)} videos")
            except Exception as hashtag_error:
                print(f"❌ All methods failed: {str(hashtag_error)}")
    
    return videos[:MAX_TOTAL_VIDEOS]


async def hashtag_only_strategy(api, retry_attempt=0, used_hashtags=None):
    """Execute hashtag-only search strategy with hashtag diversification on retries."""
    print(f"🏷️ Using HASHTAG-ONLY search strategy (attempt {retry_attempt + 1})")
    print(f"🎯 Target: {MAX_TOTAL_VIDEOS} total videos")
    
    # Get diversified hashtags for this attempt
    if retry_attempt > 0 and used_hashtags:
        active_hashtags = get_diversified_hashtags(used_hashtags, retry_attempt)
        print(f"🔄 Using diversified hashtags for retry attempt {retry_attempt + 1}")
    else:
        active_hashtags = get_active_hashtags()
    
    print(f"📋 Searching {len(active_hashtags)} hashtags: {', '.join(['#' + tag for tag in active_hashtags[:5]])}{'...' if len(active_hashtags) > 5 else ''}")
    
    all_videos = []
    video_ids_seen = set()
    videos_per_hashtag = max(MIN_VIDEOS_PER_HASHTAG, MAX_TOTAL_VIDEOS // len(active_hashtags))
    for hashtag in active_hashtags:
        if len(all_videos) >= MAX_TOTAL_VIDEOS:
            break
            
        # Track hashtag usage
        if used_hashtags is not None:
            used_hashtags.add(hashtag)
            
        hashtag_videos = await get_videos_by_hashtag(api, hashtag, videos_per_hashtag)
        
        hashtag_count = 0
        for video in hashtag_videos:
            if video.id not in video_ids_seen:
                all_videos.append(video)
                video_ids_seen.add(video.id)
                hashtag_count += 1
            
            if len(all_videos) >= MAX_TOTAL_VIDEOS:
                break
                
        print(f"  #{hashtag}: added {hashtag_count} videos, total now: {len(all_videos)}/{MAX_TOTAL_VIDEOS}")
        await asyncio.sleep(0.5)  # Rate limiting
    
    print(f"✓ Hashtags: {len(all_videos)} unique videos")
    
    return all_videos


async def personalized_search_strategy(api, retry_attempt=0, used_hashtags=None):
    """Execute personalized search strategy using AI-driven preference analysis."""
    if retry_attempt > 0:
        print(f"🧠 Using PERSONALIZED search strategy (Retry #{retry_attempt})")
    else:
        print(f"🧠 Using PERSONALIZED search strategy")
    print(f"🎯 Target: {MAX_TOTAL_VIDEOS} total videos")
    
    # Initialize used hashtags set
    if used_hashtags is None:
        used_hashtags = set()
    
    # Build or load preference profile
    analyzer = await build_preference_profile(api)
    search_engine = PersonalizedSearchEngine(analyzer)
    
    all_videos = []
    video_ids_seen = set()
    scored_videos = []    # Method 1: Smart hashtag-based search using preferences
    smart_hashtags = search_engine.generate_smart_hashtags(15)
    if smart_hashtags:
        # On retry attempts, filter out already used hashtags
        if retry_attempt > 0:
            print(f"🔄 Retry #{retry_attempt}: Filtering out used hashtags to avoid duplicates...")
            original_count = len(smart_hashtags)
            smart_hashtags = [h for h in smart_hashtags if h not in used_hashtags]
            print(f"   Filtered from {original_count} to {len(smart_hashtags)} hashtags")
        
        print(f"🧠 Using {len(smart_hashtags)} AI-generated smart hashtags...")
        for hashtag in smart_hashtags:
            if len(all_videos) >= MAX_TOTAL_VIDEOS:
                break
                
            # Track hashtag usage
            used_hashtags.add(hashtag)
                
            try:
                hashtag_videos = await get_videos_by_hashtag(api, hashtag, MIN_VIDEOS_PER_HASHTAG)
                for video in hashtag_videos:
                    if video.id not in video_ids_seen:
                        # Score the video based on user preferences
                        score = search_engine.score_video_relevance(video)
                        scored_videos.append((video, score))
                        video_ids_seen.add(video.id)
            except Exception as e:
                print(f"⚠️ Error with smart hashtag #{hashtag}: {str(e)}")
    
    # Method 2: Search by preferred authors
    preferred_authors = search_engine.get_preferred_authors(5)
    if preferred_authors and len(all_videos) < MAX_TOTAL_VIDEOS:
        print(f"👤 Searching videos from {len(preferred_authors)} preferred creators...")
        for username in preferred_authors:
            if len(all_videos) >= MAX_TOTAL_VIDEOS:
                break
                
            try:
                user = await api.user(username=username)
                videos = await user.videos(count=3)
                for video in videos:
                    if video.id not in video_ids_seen:
                        score = search_engine.score_video_relevance(video)
                        scored_videos.append((video, score))
                        video_ids_seen.add(video.id)
            except Exception as e:
                print(f"⚠️ Error with preferred author @{username}: {str(e)}")
    
    # Sort videos by relevance score and take the top ones
    sorted_videos = sorted(scored_videos, key=lambda x: x[1], reverse=True)
    for video, score in sorted_videos:
        if len(all_videos) >= MAX_TOTAL_VIDEOS:
            break
        # Only add videos that pass the minimum preference score
        try:
            from utils import extract_video_data
            video_data = extract_video_data(video)
            if video_data:
                passes_filter, preference_score = passes_personalized_filters(video_data, search_engine)
                if passes_filter:
                    all_videos.append(video)
                    print(f"✓ Added video with score {score:.2f}: {video.desc[:30]}...")
        except Exception as e:
            print(f"⚠️ Error filtering video: {str(e)}")
    
    # Fill remaining slots with trending if needed
    if len(all_videos) < MAX_TOTAL_VIDEOS:
        try:
            print(f"📈 Filling remaining {MAX_TOTAL_VIDEOS - len(all_videos)} slots with trending videos...")
            async for video in api.trending.videos(count=MAX_TOTAL_VIDEOS - len(all_videos)):
                if video.id not in video_ids_seen:
                    all_videos.append(video)
                    video_ids_seen.add(video.id)
                if len(all_videos) >= MAX_TOTAL_VIDEOS:
                    break
        except Exception as e:
            print(f"⚠️ Error filling with trending: {str(e)}")
    
    print(f"✓ Personalized search: {len(all_videos)} videos")
    return all_videos
