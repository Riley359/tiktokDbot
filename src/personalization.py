"""Personalized recommendation engine."""

import os
import json
import datetime
import re
from collections import Counter
from typing import Dict, List, Tuple
from config import (
    PREFERENCE_PROFILE_FILE, HASHTAG_CATEGORIES, 
    PERSONALIZATION_WEIGHTS, MIN_PREFERENCE_SCORE
)


class PreferenceAnalyzer:
    """Analyzes user's liked videos to build a comprehensive preference profile."""
    
    def __init__(self):
        self.preferences = {
            'hashtags': Counter(),
            'authors': Counter(), 
            'keywords': Counter(),
            'categories': Counter(),
            'engagement_patterns': {
                'avg_likes': 0,
                'avg_views': 0,
                'avg_shares': 0,
                'avg_comments': 0,
                'preferred_engagement_rate': 0
            },
            'video_ids_analyzed': set(),
            'last_updated': None,
            'total_videos_analyzed': 0
        }
    
    def extract_hashtags(self, caption: str) -> List[str]:
        """Extract hashtags from video caption."""
        hashtag_pattern = r'#(\w+)'
        hashtags = re.findall(hashtag_pattern, caption.lower())
        return hashtags
    
    def extract_keywords(self, caption: str) -> List[str]:
        """Extract meaningful keywords from caption, excluding common words."""
        # Remove hashtags and mentions
        clean_caption = re.sub(r'[#@]\w+', '', caption.lower())
        # Remove punctuation and split
        clean_caption = re.sub(r'[^\w\s]', ' ', clean_caption)
        words = clean_caption.split()
        
        # Common words to exclude
        stop_words = {
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
            'by', 'from', 'up', 'about', 'into', 'through', 'during', 'before',
            'after', 'above', 'below', 'between', 'among', 'through', 'during',
            'before', 'after', 'above', 'below', 'up', 'down', 'out', 'off', 'over',
            'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when',
            'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more',
            'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own',
            'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just',
            'don', 'should', 'now', 'this', 'that', 'these', 'those', 'is', 'are',
            'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does',
            'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'shall'
        }
        
        keywords = [word for word in words if len(word) > 2 and word not in stop_words]
        return keywords
    
    def categorize_content(self, caption: str, hashtags: List[str]) -> str:
        """Categorize content based on caption and hashtags."""
        text_to_check = (caption.lower() + ' ' + ' '.join(hashtags)).lower()
        
        category_scores = {}
        for category, category_hashtags in HASHTAG_CATEGORIES.items():
            score = sum(1 for tag in category_hashtags if tag in text_to_check)
            if score > 0:
                category_scores[category] = score
        
        if category_scores:
            return max(category_scores, key=category_scores.get)
        return "general"
    
    def analyze_video(self, video_data: Dict) -> None:
        """Analyze a single video and update preferences."""
        if video_data['id'] in self.preferences['video_ids_analyzed']:
            return  # Already analyzed
        
        # Extract hashtags
        hashtags = self.extract_hashtags(video_data['caption'])
        for hashtag in hashtags:
            self.preferences['hashtags'][hashtag] += 1
        
        # Track author preferences
        self.preferences['authors'][video_data['author']] += 1
        
        # Extract keywords
        keywords = self.extract_keywords(video_data['caption'])
        for keyword in keywords:
            self.preferences['keywords'][keyword] += 1
        
        # Categorize content
        category = self.categorize_content(video_data['caption'], hashtags)
        self.preferences['categories'][category] += 1
        
        # Update engagement patterns
        patterns = self.preferences['engagement_patterns']
        total_analyzed = self.preferences['total_videos_analyzed']
        
        # Calculate running averages
        patterns['avg_likes'] = ((patterns['avg_likes'] * total_analyzed) + video_data['likes']) / (total_analyzed + 1)
        patterns['avg_views'] = ((patterns['avg_views'] * total_analyzed) + video_data['plays']) / (total_analyzed + 1)
        patterns['avg_shares'] = ((patterns['avg_shares'] * total_analyzed) + video_data['shares']) / (total_analyzed + 1)
        patterns['avg_comments'] = ((patterns['avg_comments'] * total_analyzed) + video_data['comments']) / (total_analyzed + 1)
        
        # Calculate engagement rate
        if video_data['plays'] > 0:
            engagement_rate = video_data['likes'] / video_data['plays']
            patterns['preferred_engagement_rate'] = ((patterns['preferred_engagement_rate'] * total_analyzed) + engagement_rate) / (total_analyzed + 1)
        
        # Mark as analyzed
        self.preferences['video_ids_analyzed'].add(video_data['id'])
        self.preferences['total_videos_analyzed'] += 1
        self.preferences['last_updated'] = datetime.datetime.now().isoformat()
    
    def get_top_preferences(self, n: int = 10) -> Dict:
        """Get top N preferences for each category."""
        return {
            'top_hashtags': dict(self.preferences['hashtags'].most_common(n)),
            'top_authors': dict(self.preferences['authors'].most_common(n)),
            'top_keywords': dict(self.preferences['keywords'].most_common(n)),
            'top_categories': dict(self.preferences['categories'].most_common(n)),
            'engagement_patterns': self.preferences['engagement_patterns'],
            'total_analyzed': self.preferences['total_videos_analyzed']
        }
    
    def save_preferences(self, filepath: str) -> None:
        """Save preferences to JSON file."""
        # Convert sets to lists for JSON serialization
        serializable_prefs = self.preferences.copy()
        serializable_prefs['video_ids_analyzed'] = list(self.preferences['video_ids_analyzed'])
        serializable_prefs['hashtags'] = dict(self.preferences['hashtags'])
        serializable_prefs['authors'] = dict(self.preferences['authors'])
        serializable_prefs['keywords'] = dict(self.preferences['keywords'])
        serializable_prefs['categories'] = dict(self.preferences['categories'])
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(serializable_prefs, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Saved preference profile to {filepath}")
    
    def load_preferences(self, filepath: str) -> bool:
        """Load preferences from JSON file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                loaded_prefs = json.load(f)
            
            # Convert back to appropriate data structures
            self.preferences['video_ids_analyzed'] = set(loaded_prefs.get('video_ids_analyzed', []))
            self.preferences['hashtags'] = Counter(loaded_prefs.get('hashtags', {}))
            self.preferences['authors'] = Counter(loaded_prefs.get('authors', {}))
            self.preferences['keywords'] = Counter(loaded_prefs.get('keywords', {}))
            self.preferences['categories'] = Counter(loaded_prefs.get('categories', {}))
            self.preferences['engagement_patterns'] = loaded_prefs.get('engagement_patterns', self.preferences['engagement_patterns'])
            self.preferences['last_updated'] = loaded_prefs.get('last_updated')
            self.preferences['total_videos_analyzed'] = loaded_prefs.get('total_videos_analyzed', 0)
            
            print(f"📁 Loaded preference profile from {filepath}")
            print(f"   📊 Total videos analyzed: {self.preferences['total_videos_analyzed']}")
            return True
        except FileNotFoundError:
            print(f"📁 No existing preference profile found at {filepath}")
            return False
        except Exception as e:
            print(f"❌ Error loading preferences: {str(e)}")
            return False


class PersonalizedSearchEngine:
    """Handles personalized search based on user preferences."""
    
    def __init__(self, analyzer: PreferenceAnalyzer):
        self.analyzer = analyzer
        self.preferences = analyzer.get_top_preferences(20)  # Get top 20 for each category
    
    def calculate_preference_score(self, video_data: Dict) -> float:
        """Calculate how well a video matches user preferences (0.0-1.0)."""
        if not self.preferences['total_analyzed']:
            return 0.5  # Neutral score if no preferences yet
        
        score_components = {}
        
        # 1. Hashtag preference score
        video_hashtags = self.analyzer.extract_hashtags(video_data['caption'])
        hashtag_score = 0
        if video_hashtags and self.preferences['top_hashtags']:
            max_hashtag_count = max(self.preferences['top_hashtags'].values())
            for hashtag in video_hashtags:
                if hashtag in self.preferences['top_hashtags']:
                    hashtag_score += self.preferences['top_hashtags'][hashtag] / max_hashtag_count
            hashtag_score = min(hashtag_score / len(video_hashtags), 1.0)
        score_components['hashtag'] = hashtag_score
        
        # 2. Author preference score
        author_score = 0
        if self.preferences['top_authors']:
            max_author_count = max(self.preferences['top_authors'].values())
            if video_data['author'] in self.preferences['top_authors']:
                author_score = self.preferences['top_authors'][video_data['author']] / max_author_count
        score_components['author'] = author_score
        
        # 3. Keyword preference score
        video_keywords = self.analyzer.extract_keywords(video_data['caption'])
        keyword_score = 0
        if video_keywords and self.preferences['top_keywords']:
            max_keyword_count = max(self.preferences['top_keywords'].values())
            for keyword in video_keywords:
                if keyword in self.preferences['top_keywords']:
                    keyword_score += self.preferences['top_keywords'][keyword] / max_keyword_count
            keyword_score = min(keyword_score / len(video_keywords), 1.0)
        score_components['keyword'] = keyword_score
        
        # 4. Engagement pattern score
        engagement_score = 0
        patterns = self.preferences['engagement_patterns']
        if patterns['avg_likes'] > 0 and patterns['avg_views'] > 0:
            # Compare video engagement to user's preferred patterns
            like_ratio = min(video_data['likes'] / patterns['avg_likes'], 2.0) / 2.0
            view_ratio = min(video_data['plays'] / patterns['avg_views'], 2.0) / 2.0
            
            if video_data['plays'] > 0:
                video_engagement_rate = video_data['likes'] / video_data['plays']
                if patterns['preferred_engagement_rate'] > 0:
                    engagement_rate_ratio = min(video_engagement_rate / patterns['preferred_engagement_rate'], 2.0) / 2.0
                    engagement_score = (like_ratio + view_ratio + engagement_rate_ratio) / 3
                else:
                    engagement_score = (like_ratio + view_ratio) / 2
        score_components['engagement'] = engagement_score
        
        # 5. Category preference score
        video_hashtags = self.analyzer.extract_hashtags(video_data['caption'])
        category = self.analyzer.categorize_content(video_data['caption'], video_hashtags)
        category_score = 0
        if self.preferences['top_categories']:
            max_category_count = max(self.preferences['top_categories'].values())
            if category in self.preferences['top_categories']:
                category_score = self.preferences['top_categories'][category] / max_category_count
        score_components['category'] = category_score
        
        # Calculate weighted final score
        final_score = (
            score_components['hashtag'] * PERSONALIZATION_WEIGHTS['hashtag_preference'] +
            score_components['author'] * PERSONALIZATION_WEIGHTS['author_preference'] +
            score_components['keyword'] * PERSONALIZATION_WEIGHTS['keyword_preference'] +
            score_components['engagement'] * PERSONALIZATION_WEIGHTS['engagement_pattern'] +
            score_components['category'] * PERSONALIZATION_WEIGHTS['category_preference']
        )
        
        return min(final_score, 1.0)
    
    def generate_smart_hashtags(self, count: int = 10) -> List[str]:
        """Generate smart hashtag list based on preferences."""
        smart_hashtags = []
        
        # Get top preferred hashtags
        if self.preferences['top_hashtags']:
            preferred_hashtags = list(self.preferences['top_hashtags'].keys())[:count//2]
            smart_hashtags.extend(preferred_hashtags)
        
        # Add hashtags from preferred categories
        if self.preferences['top_categories']:
            for category in list(self.preferences['top_categories'].keys())[:3]:
                if category in HASHTAG_CATEGORIES:
                    category_hashtags = HASHTAG_CATEGORIES[category][:2]
                    smart_hashtags.extend(category_hashtags)
        
        # Fill remaining with trending hashtags if needed
        if len(smart_hashtags) < count:
            trending_hashtags = HASHTAG_CATEGORIES.get('trending', [])
            for hashtag in trending_hashtags:
                if hashtag not in smart_hashtags and len(smart_hashtags) < count:
                    smart_hashtags.append(hashtag)
        
        return smart_hashtags[:count]
    
    def get_preferred_authors(self, count: int = 10) -> List[str]:
        """Get list of preferred authors."""
        if self.preferences['top_authors']:
            return list(self.preferences['top_authors'].keys())[:count]
        return []


# ===== UTILITY FUNCTIONS =====

async def fetch_liked_videos(api, count: int = 100) -> List[Dict]:
    """
    Fetch user's liked videos for preference analysis.
    
    Args:
        api: TikTok API instance
        count: Number of liked videos to fetch
    
    Returns:
        List of video data dictionaries
    """
    from utils import extract_video_data
    
    liked_videos_data = []
    try:
        print(f"📱 Fetching your {count} most recent liked videos for analysis...")
        
        # Get current user's liked videos
        user = api.user()  # Current authenticated user
        
        video_count = 0
        async for video in user.liked(count=count):
            try:
                video_data = extract_video_data(video)
                if video_data:
                    liked_videos_data.append(video_data)
                    video_count += 1
                    if video_count % 10 == 0:
                        print(f"   📊 Analyzed {video_count}/{count} liked videos...")
                
                if video_count >= count:
                    break
                    
            except Exception as e:
                print(f"⚠️ Error processing liked video: {str(e)}")
                continue
        
        print(f"✓ Successfully fetched {len(liked_videos_data)} liked videos for analysis")
        return liked_videos_data
        
    except Exception as e:
        print(f"❌ Error fetching liked videos: {str(e)}")
        print("   This might be due to API limitations or authentication issues")
        return []


async def build_preference_profile(api) -> PreferenceAnalyzer:
    """
    Build or update user preference profile based on liked videos.
    
    Args:
        api: TikTok API instance
    
    Returns:
        PreferenceAnalyzer instance with user preferences
    """
    from config import ANALYZE_LIKED_VIDEOS, LIKED_VIDEOS_ANALYZE_COUNT
    
    analyzer = PreferenceAnalyzer()
    
    # Try to load existing preferences
    if os.path.exists(PREFERENCE_PROFILE_FILE):
        analyzer.load_preferences(PREFERENCE_PROFILE_FILE)
    
    if ANALYZE_LIKED_VIDEOS:
        print("🧠 Building personalized preference profile...")
        
        # Fetch liked videos
        liked_videos = await fetch_liked_videos(api, LIKED_VIDEOS_ANALYZE_COUNT)
        
        if liked_videos:
            new_videos_analyzed = 0
            for video_data in liked_videos:
                if video_data['id'] not in analyzer.preferences['video_ids_analyzed']:
                    analyzer.analyze_video(video_data)
                    new_videos_analyzed += 1
            
            if new_videos_analyzed > 0:
                print(f"✓ Analyzed {new_videos_analyzed} new liked videos")
                
                # Save updated preferences
                analyzer.save_preferences(PREFERENCE_PROFILE_FILE)
                
                # Display preference summary
                top_prefs = analyzer.get_top_preferences(5)
                print(f"\n🎯 Your Preference Profile Summary:")
                print(f"   📊 Total videos analyzed: {top_prefs['total_analyzed']}")
                print(f"   🏷️ Top hashtags: {', '.join(['#' + k for k in top_prefs['top_hashtags'].keys()])}")
                print(f"   👤 Top creators: {', '.join(['@' + k for k in top_prefs['top_authors'].keys()])}")
                print(f"   📝 Top keywords: {', '.join(top_prefs['top_keywords'].keys())}")
                print(f"   📂 Top categories: {', '.join(top_prefs['top_categories'].keys())}")
                print(f"   💯 Avg engagement: {top_prefs['engagement_patterns']['avg_likes']:.0f} likes, {top_prefs['engagement_patterns']['avg_views']:.0f} views")
            else:
                print("✓ Preference profile is up to date")
        else:
            print("⚠️ Could not fetch liked videos, using existing preferences or defaults")
    
    return analyzer


# ===== PREFERENCE PROFILE UTILITIES =====

def export_preference_profile(output_file: str = "exported_preferences.json"):
    """Export preference profile for backup or sharing."""
    if os.path.exists(PREFERENCE_PROFILE_FILE):
        try:
            with open(PREFERENCE_PROFILE_FILE, 'r', encoding='utf-8') as source:
                with open(output_file, 'w', encoding='utf-8') as dest:
                    dest.write(source.read())
            print(f"📤 Preference profile exported to {output_file}")
            return True
        except Exception as e:
            print(f"❌ Error exporting preferences: {str(e)}")
            return False
    else:
        print("❌ No preference profile found to export")
        return False


def import_preference_profile(input_file: str):
    """Import preference profile from backup or shared file."""
    if os.path.exists(input_file):
        try:
            with open(input_file, 'r', encoding='utf-8') as source:
                with open(PREFERENCE_PROFILE_FILE, 'w', encoding='utf-8') as dest:
                    dest.write(source.read())
            print(f"📥 Preference profile imported from {input_file}")
            return True
        except Exception as e:
            print(f"❌ Error importing preferences: {str(e)}")
            return False
    else:
        print(f"❌ Import file {input_file} not found")
        return False


def reset_preference_profile():
    """Reset preference profile by deleting the saved file."""
    if os.path.exists(PREFERENCE_PROFILE_FILE):
        try:
            os.remove(PREFERENCE_PROFILE_FILE)
            print(f"🗑️ Preference profile reset (deleted {PREFERENCE_PROFILE_FILE})")
            return True
        except Exception as e:
            print(f"❌ Error resetting preferences: {str(e)}")
            return False
    else:
        print("ℹ️ No preference profile found to reset")
        return True


def show_preference_summary():
    """Display a summary of the current preference profile."""
    if os.path.exists(PREFERENCE_PROFILE_FILE):
        try:
            analyzer = PreferenceAnalyzer()
            analyzer.load_preferences(PREFERENCE_PROFILE_FILE)
            top_prefs = analyzer.get_top_preferences(10)
            
            print("\n" + "=" * 60)
            print("🎯 CURRENT PREFERENCE PROFILE SUMMARY")
            print("=" * 60)
            print(f"📊 Total videos analyzed: {top_prefs['total_analyzed']}")
            print(f"📅 Last updated: {analyzer.preferences.get('last_updated', 'Unknown')}")
            
            print(f"\n🏷️ Top Hashtag Preferences:")
            for hashtag, count in list(top_prefs['top_hashtags'].items())[:10]:
                print(f"   #{hashtag}: {count} occurrences")
            
            print(f"\n👤 Top Creator Preferences:")
            for author, count in list(top_prefs['top_authors'].items())[:10]:
                print(f"   @{author}: {count} videos liked")
            
            print(f"\n📝 Top Keyword Preferences:")
            for keyword, count in list(top_prefs['top_keywords'].items())[:10]:
                print(f"   '{keyword}': {count} occurrences")
            
            print(f"\n📂 Category Preferences:")
            for category, count in list(top_prefs['top_categories'].items())[:10]:
                print(f"   {category}: {count} videos")
            
            patterns = top_prefs['engagement_patterns']
            print(f"\n💯 Engagement Patterns:")
            print(f"   Average likes: {patterns['avg_likes']:.0f}")
            print(f"   Average views: {patterns['avg_views']:.0f}")
            print(f"   Average shares: {patterns['avg_shares']:.0f}")
            print(f"   Average comments: {patterns['avg_comments']:.0f}")
            print(f"   Preferred engagement rate: {patterns['preferred_engagement_rate']:.3f}")
            
            print("=" * 60)
            return True
        except Exception as e:
            print(f"❌ Error reading preference profile: {str(e)}")
            return False
    else:
        print("ℹ️ No preference profile found. Run with personalized strategy to create one.")
        return False
