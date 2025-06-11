"""Video download functionality."""

import os
import aiohttp
from utils import sanitize_filename
from config import DOWNLOAD_DIR


async def download_video(video, video_data):
    """
    Download a video without watermark to the local directory.
    
    Args:
        video: TikTok video object from the API
        video_data: Dictionary containing video metadata
    
    Returns:
        bool: True if download successful, False otherwise
    """
    try:
        # Extract video information
        video_dict = video.as_dict
        
        # Try multiple methods to get the download URL
        download_url = None
        
        # Method 1: Try to get from video dict structure
        if 'video' in video_dict:
            video_info = video_dict['video']
            download_url = (video_info.get('downloadAddr') or 
                           video_info.get('playAddr'))
            
            # If URL is a list, get the first one
            if isinstance(download_url, list) and download_url:
                download_url = download_url[0]
        
        # Method 2: Try to get from bitrateInfo (higher quality)
        if not download_url and 'video' in video_dict:
            bitrate_info = video_dict['video'].get('bitrateInfo', [])
            if bitrate_info:
                # Get the highest quality version
                best_quality = max(bitrate_info, key=lambda x: x.get('Bitrate', 0))
                play_addr = best_quality.get('PlayAddr', {})
                url_list = play_addr.get('UrlList', [])
                if url_list:
                    download_url = url_list[0]
        
        # Method 3: Try direct video object attributes
        if not download_url:
            try:
                if hasattr(video, 'video'):
                    download_url = (getattr(video.video, 'downloadAddr', None) or 
                                   getattr(video.video, 'playAddr', None))
            except:
                pass
        
        # Method 4: Try the bytes method as fallback
        if not download_url:
            try:
                print(f"⚠️ Using fallback bytes method for video {video_data['id']}")
                video_bytes = await video.bytes()
                
                if video_bytes and len(video_bytes) > 1000:
                    # Create filename
                    author = video_data['author'].replace('@', '')
                    filename = f"{video_data['id']}_{sanitize_filename(author)}.mp4"
                    filepath = os.path.join(DOWNLOAD_DIR, filename)
                    
                    # Write directly
                    with open(filepath, 'wb') as f:
                        f.write(video_bytes)
                    
                    print(f"✓ Downloaded video {video_data['id']} from @{author} using bytes method ({len(video_bytes):,} bytes)")
                    return True
                else:
                    print(f"✗ Bytes method returned insufficient data for video {video_data['id']}")
            except Exception as bytes_error:
                print(f"⚠️ Bytes method failed for video {video_data['id']}: {str(bytes_error)}")
        
        if not download_url:
            print(f"✗ Could not find any download URL for video {video_data['id']}")
            print(f"   Available video keys: {list(video_dict.get('video', {}).keys()) if 'video' in video_dict else 'No video key'}")
            return False
        
        # Clean up the URL if needed
        if isinstance(download_url, str):
            download_url = download_url.replace('&amp;', '&')
        
        print(f"🔗 Found download URL for video {video_data['id']}: {download_url[:100]}...")
        
        # Create filename using video ID and author
        author = video_data['author'].replace('@', '')
        filename = f"{video_data['id']}_{sanitize_filename(author)}.mp4"
        filepath = os.path.join(DOWNLOAD_DIR, filename)
        
        # Download video using aiohttp
        async with aiohttp.ClientSession() as session:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Referer': 'https://www.tiktok.com/',
                'Accept': 'video/mp4,video/*,*/*;q=0.9',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'identity',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            timeout = aiohttp.ClientTimeout(total=60)  # 60 second timeout
            
            async with session.get(download_url, headers=headers, timeout=timeout) as response:
                if response.status == 200:
                    content = await response.read()
                    
                    # Basic validation - check if we got actual video content
                    if len(content) < 1000:  # Too small to be a video
                        print(f"✗ Downloaded content too small for video {video_data['id']} ({len(content)} bytes)")
                        return False
                    
                    # Check for common video file signatures (more comprehensive)
                    is_video = (
                        content.startswith(b'\x00\x00\x00') or  # MP4 signature
                        content[4:8] == b'ftyp' or              # MP4 ftyp box
                        b'moov' in content[:2000] or            # MP4 moov atom
                        b'mdat' in content[:2000] or            # MP4 mdat atom
                        content.startswith(b'ID3') or           # Sometimes MP4 with ID3
                        b'mp4' in content[:100].lower()         # MP4 identifier
                    )
                    
                    if not is_video:
                        print(f"✗ Downloaded content doesn't appear to be a valid video file for {video_data['id']}")
                        print(f"   Content starts with: {content[:20]}")
                        return False
                    
                    # Write video to file
                    with open(filepath, 'wb') as f:
                        f.write(content)
                    
                    print(f"✓ Downloaded video {video_data['id']} from @{author} ({len(content):,} bytes)")
                    return True
                else:
                    print(f"✗ Failed to download video {video_data['id']}: HTTP {response.status}")
                    if response.status == 403:
                        print("   This might be due to geographic restrictions or rate limiting")
                    return False
        
    except aiohttp.ClientError as e:
        print(f"✗ Network error downloading video {video_data['id']}: {str(e)}")
        return False
    except Exception as e:
        print(f"✗ Failed to download video {video_data['id']}: {str(e)}")
        return False
