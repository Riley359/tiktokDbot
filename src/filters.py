"""Video filtering functions."""

from typing import Dict, Tuple
from config import TREND_FILTERS, CONTENT_FILTERS


def passes_trend_filters(video_data):
    """Check if video passes trend-based filters."""
    if not video_data:
        return False
    
    # Check minimum engagement metrics
    if video_data['likes'] < TREND_FILTERS['min_likes']:
        return False
    
    if video_data['plays'] < TREND_FILTERS['min_views']:
        return False
    
    if video_data['shares'] < TREND_FILTERS['min_shares']:
        return False
    
    if video_data['comments'] < TREND_FILTERS['min_comments']:
        return False
    
    # Check engagement rate (likes/views)
    if video_data['plays'] > 0:
        engagement_rate = video_data['likes'] / video_data['plays']
        if engagement_rate < TREND_FILTERS['min_engagement_rate']:
            return False
    
    return True


def passes_content_filters(video_data):
    """Check if video passes content-based filters."""
    if not video_data:
        return False
    
    # Check caption length
    if len(video_data['caption']) < CONTENT_FILTERS['min_caption_length']:
        return False
    
    # Check for excluded keywords
    caption_lower = video_data['caption'].lower()
    for keyword in CONTENT_FILTERS['exclude_keywords']:
        if keyword.lower() in caption_lower:
            return False
    
    return True


def passes_personalized_filters(video_data: Dict, search_engine) -> Tuple[bool, float]:
    """
    Check if video passes personalized filters based on user preferences.
    
    Args:
        video_data: Dictionary containing video metadata
        search_engine: PersonalizedSearchEngine instance
    
    Returns:
        Tuple of (passes_filter: bool, preference_score: float)
    """
    from config import MIN_PREFERENCE_SCORE
    
    # Calculate preference score
    preference_score = search_engine.calculate_preference_score(video_data)
    
    # Check if meets minimum preference threshold
    if preference_score < MIN_PREFERENCE_SCORE:
        return False, preference_score
    
    # Apply secondary filters (existing trend and content filters as backup)
    if not passes_trend_filters(video_data):
        return False, preference_score
    
    if not passes_content_filters(video_data):
        return False, preference_score
    
    return True, preference_score


def rank_videos_by_preference(videos_data, search_engine=None):
    """Rank videos by preference score, highest first."""
    if not search_engine:
        return videos_data
    
    scored_videos = []
    for video_data in videos_data:
        passes_filter, score = passes_personalized_filters(video_data, search_engine)
        if passes_filter:
            scored_videos.append((video_data, score))
    
    # Sort by score descending
    scored_videos.sort(key=lambda x: x[1], reverse=True)
    
    return [video_data for video_data, score in scored_videos]
