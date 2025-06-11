"""Database module for tracking sent TikTok videos to prevent duplicates."""

import sqlite3
import os
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from urllib.parse import urlparse, parse_qs

class VideoDatabase:
    """Handle database operations for tracking sent TikTok videos."""
    
    def __init__(self, db_path: str = "tiktok_videos.db"):
        """Initialize the database connection and create tables if needed."""
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Create the database tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sent_videos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT NOT NULL,
                    normalized_url TEXT NOT NULL UNIQUE,
                    author TEXT,
                    caption TEXT,
                    likes INTEGER DEFAULT 0,
                    views INTEGER DEFAULT 0,
                    comments INTEGER DEFAULT 0,
                    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    guild_id INTEGER,
                    channel_id INTEGER
                )
            """)
            
            # Create index for faster lookups
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_normalized_url 
                ON sent_videos(normalized_url)
            """)
            
            # Create index for cleanup operations
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_sent_at 
                ON sent_videos(sent_at)
            """)
            
            conn.commit()
    
    def normalize_tiktok_url(self, url: str) -> str:
        """
        Normalize TikTok URL to extract the core video identifier.
        This helps detect duplicates even with different URL formats.
        """
        try:
            # Extract video ID from different TikTok URL formats
            
            # Standard format: https://www.tiktok.com/@username/video/1234567890
            standard_match = re.search(r'tiktok\.com/@[^/]+/video/(\d+)', url)
            if standard_match:
                return f"tiktok_video_{standard_match.group(1)}"
            
            # Short format: https://vm.tiktok.com/ZMxxx/
            short_match = re.search(r'vm\.tiktok\.com/([^/?]+)', url)
            if short_match:
                return f"tiktok_short_{short_match.group(1)}"
            
            # Mobile format: https://m.tiktok.com/v/1234567890
            mobile_match = re.search(r'm\.tiktok\.com/v/(\d+)', url)
            if mobile_match:
                return f"tiktok_mobile_{mobile_match.group(1)}"
            
            # vxTikTok format (used by the bot)
            vx_match = re.search(r'vxtiktok\.com/@[^/]+/video/(\d+)', url)
            if vx_match:
                return f"tiktok_video_{vx_match.group(1)}"
            
            # Fallback: use the full URL without parameters
            parsed = urlparse(url)
            return f"tiktok_url_{parsed.netloc}{parsed.path}".replace('/', '_')
            
        except Exception:
            # If normalization fails, use the original URL
            return url.replace('/', '_').replace(':', '_')
    
    def is_video_sent(self, url: str) -> Tuple[bool, Optional[Dict]]:
        """
        Check if a video URL has been sent before.
        
        Returns:
            Tuple of (is_sent, video_info_dict or None)
        """
        normalized_url = self.normalize_tiktok_url(url)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM sent_videos 
                WHERE normalized_url = ? 
                ORDER BY sent_at DESC 
                LIMIT 1
            """, (normalized_url,))
            
            row = cursor.fetchone()
            if row:
                return True, dict(row)
            else:
                return False, None
    def add_sent_video(self, video_data: Dict, guild_id: int = None, channel_id: int = None) -> bool:
        """
        Add a video to the sent videos database.
        
        Args:
            video_data: Dictionary containing video information
            guild_id: Discord guild ID where video was sent
            channel_id: Discord channel ID where video was sent
            
        Returns:
            True if successfully added, False if already exists
        """
        try:
            url = video_data.get('url', '')
            normalized_url = self.normalize_tiktok_url(url)
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO sent_videos 
                    (url, normalized_url, author, caption, likes, views, comments, guild_id, channel_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    url,
                    normalized_url,
                    video_data.get('author', ''),
                    video_data.get('caption', ''),
                    video_data.get('likes', 0),
                    video_data.get('plays', 0),  # 'plays' maps to views
                    video_data.get('comments', 0),
                    guild_id,
                    channel_id
                ))
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            # Video already exists
            return False
        except Exception as e:
            print(f"Error adding video to database: {e}")
            return False
    
    def filter_duplicate_videos(self, videos: List[Dict], allow_stale_days: int = 7, exclude_urls: List[str] = None) -> Tuple[List[Dict], List[Dict]]:
        """
        Filter out videos that have already been sent.
        
        Args:
            videos: List of video data dictionaries
            allow_stale_days: Allow videos to be sent again if sent more than this many days ago
            exclude_urls: Additional URLs to exclude (e.g., from current session)
            
        Returns:
            Tuple of (new_videos, duplicate_videos)
        """
        new_videos = []
        duplicate_videos = []
        exclude_urls = exclude_urls or []
        
        # Normalize exclude URLs for comparison
        normalized_exclude_urls = {self.normalize_tiktok_url(url) for url in exclude_urls}
        
        from datetime import datetime, timedelta
        stale_cutoff = datetime.now() - timedelta(days=allow_stale_days)
        
        for video in videos:
            video_url = video.get('url', '')
            normalized_video_url = self.normalize_tiktok_url(video_url)
            
            # Check if this video is in our exclude list
            if normalized_video_url in normalized_exclude_urls:
                duplicate_videos.append(video)
                continue
            
            is_sent, video_info = self.is_video_sent(video_url)
            
            if is_sent and video_info:
                # Check if the video is "stale" (old enough to be sent again)
                sent_time = datetime.fromisoformat(video_info['sent_at'].replace('Z', '+00:00'))
                if sent_time < stale_cutoff:
                    # Video is old enough to be considered "new" again
                    new_videos.append(video)
                else:
                    # Video is still considered a duplicate
                    duplicate_videos.append(video)
            else:
                # Video hasn't been sent before
                new_videos.append(video)
        
        return new_videos, duplicate_videos
    
    def filter_duplicate_videos_strict(self, videos: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
        """
        Filter out videos that have already been sent (strict - never allow duplicates).
        This is the original method behavior.
        
        Args:
            videos: List of video data dictionaries
            
        Returns:
            Tuple of (new_videos, duplicate_videos)
        """
        new_videos = []
        duplicate_videos = []
        
        for video in videos:
            is_sent, _ = self.is_video_sent(video.get('url', ''))
            if is_sent:
                duplicate_videos.append(video)
            else:
                new_videos.append(video)
        
        return new_videos, duplicate_videos
    
    def get_database_stats(self) -> Dict:
        """Get statistics about the database."""
        with sqlite3.connect(self.db_path) as conn:
            # Total videos
            total_cursor = conn.execute("SELECT COUNT(*) FROM sent_videos")
            total_videos = total_cursor.fetchone()[0]
            
            # Videos sent today
            today = datetime.now().date()
            today_cursor = conn.execute("""
                SELECT COUNT(*) FROM sent_videos 
                WHERE DATE(sent_at) = ?
            """, (today,))
            today_videos = today_cursor.fetchone()[0]
            
            # Videos sent this week
            week_ago = datetime.now() - timedelta(days=7)
            week_cursor = conn.execute("""
                SELECT COUNT(*) FROM sent_videos 
                WHERE sent_at >= ?
            """, (week_ago,))
            week_videos = week_cursor.fetchone()[0]
            
            # Top authors
            authors_cursor = conn.execute("""
                SELECT author, COUNT(*) as count 
                FROM sent_videos 
                WHERE author != '' 
                GROUP BY author 
                ORDER BY count DESC 
                LIMIT 5
            """)
            top_authors = authors_cursor.fetchall()
            
            # Most recent videos
            recent_cursor = conn.execute("""
                SELECT author, sent_at 
                FROM sent_videos 
                ORDER BY sent_at DESC 
                LIMIT 5
            """)
            recent_videos = recent_cursor.fetchall()
            
            return {
                'total_videos': total_videos,
                'today_videos': today_videos,
                'week_videos': week_videos,
                'top_authors': top_authors,
                'recent_videos': recent_videos
            }
    
    def cleanup_old_videos(self, days_old: int = 30) -> int:
        """
        Remove videos older than specified days to prevent database bloat.
        
        Args:
            days_old: Remove videos older than this many days
            
        Returns:
            Number of videos removed
        """
        cutoff_date = datetime.now() - timedelta(days=days_old)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                DELETE FROM sent_videos 
                WHERE sent_at < ?
            """, (cutoff_date,))
            conn.commit()
            return cursor.rowcount
    
    def clear_database(self) -> int:
        """Clear all videos from the database. Returns number of videos removed."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("DELETE FROM sent_videos")
            conn.commit()
            return cursor.rowcount
    
    def get_recent_videos(self, limit: int = 10) -> List[Dict]:
        """Get recently sent videos."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM sent_videos 
                ORDER BY sent_at DESC 
                LIMIT ?
            """, (limit,))
            
            return [dict(row) for row in cursor.fetchall()]

# Global database instance
video_db = VideoDatabase()
