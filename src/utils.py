"""Utility functions for TikTok scraper."""

import os
import re
from typing import Dict, List
from config import DOWNLOAD_VIDEOS, DOWNLOAD_DIR


def create_download_directory():
    """Create the download directory if it doesn't exist."""
    if DOWNLOAD_VIDEOS and not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)
        print(f"Created download directory: {DOWNLOAD_DIR}")


def sanitize_filename(filename):
    """Remove or replace characters that are invalid in filenames."""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename[:100]  # Limit filename length


def extract_video_data(video):
    """
    Extract relevant data from a TikTok video object.
    
    Args:
        video: TikTok video object from the API
    
    Returns:
        dict: Dictionary containing extracted video data
    """
    try:
        # Extract basic video information
        video_dict = video.as_dict
        stats = video_dict.get('stats', {})
        
        video_data = {
            'id': video.id,
            'author': video.author.username,
            'caption': video_dict.get('desc', 'No caption'),
            'url': f"https://www.tiktok.com/@{video.author.username}/video/{video.id}",
            'likes': stats.get('diggCount', 0),
            'comments': stats.get('commentCount', 0), 
            'shares': stats.get('shareCount', 0),
            'plays': stats.get('playCount', 0)
        }
        return video_data
        
    except Exception as e:
        print(f"Error extracting video data: {str(e)}")
        return None


def print_video_info(video_data, video_number):
    """
    Print video information in a formatted way.
    
    Args:
        video_data: Dictionary containing video metadata
        video_number: Sequential number of the video
    """
    print(f"\n--- Video {video_number} ---")
    print(f"ID: {video_data['id']}")
    print(f"Author: @{video_data['author']}")
    print(f"Caption: {video_data['caption']}")
    print(f"🔗 TikTok URL: {video_data['url']}")
    print(f"Likes: {video_data['likes']:,}")
    print(f"Comments: {video_data['comments']:,}")
    print(f"Shares: {video_data['shares']:,}")
    print(f"Plays: {video_data['plays']:,}")
    print("-" * 40)


def print_all_links(video_links):
    """
    Print all collected TikTok links in an easy-to-copy format.
    
    Args:
        video_links: List of dictionaries containing video URLs and authors
    """
    print("\n" + "=" * 60)
    print("📋 ALL TIKTOK LINKS - COPY & PASTE READY")
    print("=" * 60)
    
    for i, link_data in enumerate(video_links, 1):
        print(f"{i}. {link_data['url']}")
        print(f"   👤 @{link_data['author']} - {link_data['caption'][:50]}{'...' if len(link_data['caption']) > 50 else ''}")
        print()
    
    print("📋 LINKS ONLY (one per line):")
    print("-" * 40)
    for link_data in video_links:
        print(link_data['url'])
    
    print("\n" + "=" * 60)


def get_active_hashtags():
    """Get hashtags based on active categories."""
    from config import ACTIVE_CATEGORIES, HASHTAG_CATEGORIES
    
    if not ACTIVE_CATEGORIES:
        # If no categories specified, use all
        all_hashtags = []
        for category_hashtags in HASHTAG_CATEGORIES.values():
            all_hashtags.extend(category_hashtags)
        return all_hashtags
    
    active_hashtags = []
    for category in ACTIVE_CATEGORIES:
        if category in HASHTAG_CATEGORIES:
            active_hashtags.extend(HASHTAG_CATEGORIES[category])
    
    return active_hashtags


def enhanced_print_video_info(video_data, video_number, show_advanced=False):
    """
    Enhanced video information display with optional advanced metrics.
    
    Args:
        video_data: Dictionary containing video metadata
        video_number: Sequential number of the video
        show_advanced: Whether to show advanced metrics (engagement rate, etc.)
    """
    print(f"\n--- Video {video_number} ---")
    print(f"ID: {video_data['id']}")
    print(f"Author: @{video_data['author']}")
    print(f"Caption: {video_data['caption']}")
    print(f"🔗 TikTok URL: {video_data['url']}")
    print(f"Likes: {video_data['likes']:,}")
    print(f"Comments: {video_data['comments']:,}")
    print(f"Shares: {video_data['shares']:,}")
    print(f"Plays: {video_data['plays']:,}")
    
    if show_advanced:
        # Calculate engagement rate
        engagement_rate = (video_data['likes'] + video_data['shares'] + video_data['comments']) / video_data['plays'] if video_data['plays'] > 0 else 0
        print(f"Engagement Rate: {engagement_rate:.2%}")
    
    print("-" * 40)


def enhanced_print_all_links(video_links, include_advanced=False):
    """
    Print all collected TikTok links with optional advanced metrics.
    
    Args:
        video_links: List of dictionaries containing video URLs and authors
        include_advanced: Whether to include advanced metrics (engagement rate, etc.)
    """
    print("\n" + "=" * 60)
    print("📋 ALL TIKTOK LINKS - COPY & PASTE READY")
    print("=" * 60)
    
    for i, link_data in enumerate(video_links, 1):
        print(f"{i}. {link_data['url']}")
        print(f"   👤 @{link_data['author']} - {link_data['caption'][:50]}{'...' if len(link_data['caption']) > 50 else ''}")
        
        if include_advanced:
            # Calculate engagement rate
            engagement_rate = (link_data['likes'] + link_data['shares'] + link_data['comments']) / link_data['plays'] if link_data['plays'] > 0 else 0
            print(f"   Engagement Rate: {engagement_rate:.2%}")
        
        print()
    
    print("📋 LINKS ONLY (one per line):")
    print("-" * 40)
    for link_data in video_links:
        print(link_data['url'])
    
    print("\n" + "=" * 60)


def get_diversified_hashtags(used_hashtags=None, retry_attempt=0, max_hashtags=None):
    """
    Get hashtags for search, diversifying on retry attempts to avoid duplicates.
    
    Args:
        used_hashtags: Set of hashtags already used in previous attempts
        retry_attempt: Current retry attempt number (0 = first attempt)
        max_hashtags: Maximum number of hashtags to return
    
    Returns:
        List of hashtag strings to use for this search attempt
    """
    from config import ACTIVE_CATEGORIES, HASHTAG_CATEGORIES
    
    if used_hashtags is None:
        used_hashtags = set()
    
    # Get base hashtags from active categories or all categories
    if ACTIVE_CATEGORIES:
        base_hashtags = []
        for category in ACTIVE_CATEGORIES:
            if category in HASHTAG_CATEGORIES:
                base_hashtags.extend(HASHTAG_CATEGORIES[category])
    else:
        base_hashtags = []
        for category_hashtags in HASHTAG_CATEGORIES.values():
            base_hashtags.extend(category_hashtags)
    
    # Remove duplicates while preserving order
    all_available_hashtags = []
    seen = set()
    for hashtag in base_hashtags:
        if hashtag not in seen:
            all_available_hashtags.append(hashtag)
            seen.add(hashtag)
      # On retry attempts, prioritize unused hashtags
    if retry_attempt > 0:
        # Get unused hashtags
        unused_hashtags = [h for h in all_available_hashtags if h not in used_hashtags]
        
        if unused_hashtags:
            # On retry attempts, AVOID popular hashtags and use more diverse ones
            # Popular hashtags tend to return similar content
            popular_hashtags = [
                "fyp", "foryou", "viral", "trending", "xyzbca", "explore", "recommended"
            ]
            
            # Prioritize less common hashtags for better diversification
            diverse_hashtags = [h for h in unused_hashtags if h not in popular_hashtags]
            fallback_hashtags = [h for h in unused_hashtags if h in popular_hashtags]
              # Use diverse hashtags first, then popular ones as fallback if needed
            diversified_hashtags = diverse_hashtags + fallback_hashtags
            
            # Add randomization to break patterns and avoid algorithmic clustering
            import random
            random.shuffle(diversified_hashtags)
            
            print(f"🔄 Retry attempt {retry_attempt}: Using {len(diverse_hashtags)} diverse hashtags, {len(fallback_hashtags)} popular fallbacks")
            
            # Return a subset for this retry, or all if max_hashtags not specified
            if max_hashtags:
                return diversified_hashtags[:max_hashtags]
            return diversified_hashtags
    
    # For first attempt or when no diversification needed
    if max_hashtags:
        return all_available_hashtags[:max_hashtags]
    return all_available_hashtags


def get_hashtag_categories_for_retry(used_categories=None, retry_attempt=0, max_categories=3):
    """
    Get categories to search for retry attempts, focusing on unused categories.
    
    Args:
        used_categories: Set of categories already used
        retry_attempt: Current retry attempt number
        max_categories: Maximum number of new categories to add
    
    Returns:
        List of category names to search
    """
    from config import HASHTAG_CATEGORIES
    
    if used_categories is None:
        used_categories = set()
    
    all_categories = list(HASHTAG_CATEGORIES.keys())
    
    # High-engagement categories to prioritize
    priority_categories = [
        "trending", "entertainment", "music_dance", "comedy_skits", 
        "memes_trends", "viral", "hip_hop", "pop_music"
    ]
    
    # Get unused categories
    unused_categories = [cat for cat in all_categories if cat not in used_categories]
    
    if not unused_categories:
        # All categories used, return high-priority ones
        return priority_categories[:max_categories]
    
    # Prioritize unused high-engagement categories
    priority_unused = [cat for cat in priority_categories if cat in unused_categories]
    other_unused = [cat for cat in unused_categories if cat not in priority_categories]
    
    # Combine and limit
    new_categories = (priority_unused + other_unused)[:max_categories]
    
    return new_categories
