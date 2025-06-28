"""
YouTube downloader using yt-dlp
"""

import logging
import os
import yt_dlp
from typing import Optional, Dict, Any
import asyncio
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

class YouTubeDownloader:
    """YouTube video and audio downloader"""
    
    def __init__(self):
        self.download_path = "downloads"
        os.makedirs(self.download_path, exist_ok=True)
        self.executor = ThreadPoolExecutor(max_workers=2)
    
    def _get_ydl_opts(self, format_type: str = "video") -> Dict[str, Any]:
        """Get yt-dlp options based on format type"""
        base_opts = {
            'outtmpl': f'{self.download_path}/%(title)s.%(ext)s',
            'extractaudio': False,
            'audioformat': 'mp3',
            'noplaylist': True,
            'ignoreerrors': True,
        }
        
        if format_type == "audio":
            base_opts.update({
                'format': 'bestaudio/best',
                'extractaudio': True,
                'audioformat': 'mp3',
                'audioquality': '192',
            })
        elif format_type == "video_hd":
            base_opts['format'] = 'best[height<=720]'
        elif format_type == "video_sd":
            base_opts['format'] = 'best[height<=480]'
        else:  # default video
            base_opts['format'] = 'best[height<=1080]'
        
        return base_opts
    
    async def get_video_info(self, url: str) -> Optional[Dict[str, Any]]:
        """Get video information without downloading"""
        try:
            ydl_opts = {'quiet': True, 'no_warnings': True}
            
            def _extract_info():
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    return ydl.extract_info(url, download=False)
            
            loop = asyncio.get_event_loop()
            info = await loop.run_in_executor(self.executor, _extract_info)
            
            if info:
                return {
                    'title': info.get('title', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'uploader': info.get('uploader', 'Unknown'),
                    'view_count': info.get('view_count', 0),
                    'thumbnail': info.get('thumbnail', ''),
                    'description': info.get('description', '')[:200] + '...' if info.get('description') else '',
                }
            return None
        
        except Exception as e:
            logger.error(f"Error getting video info: {str(e)}")
            return None
    
    async def download_video(self, url: str, format_type: str = "video") -> Optional[str]:
        """Download video/audio and return file path"""
        try:
            ydl_opts = self._get_ydl_opts(format_type)
            
            def _download():
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    if info:
                        filename = ydl.prepare_filename(info)
                        return filename
                return None
            
            loop = asyncio.get_event_loop()
            filename = await loop.run_in_executor(self.executor, _download)
            
            return filename
        
        except Exception as e:
            logger.error(f"Error downloading video: {str(e)}")
            return None
    
    async def search_youtube(self, query: str, max_results: int = 5) -> list:
        """Search YouTube videos"""
        try:
            search_url = f"ytsearch{max_results}:{query}"
            ydl_opts = {'quiet': True, 'no_warnings': True}
            
            def _search():
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    return ydl.extract_info(search_url, download=False)
            
            loop = asyncio.get_event_loop()
            search_results = await loop.run_in_executor(self.executor, _search)
            
            results = []
            if search_results and 'entries' in search_results:
                for entry in search_results['entries']:
                    if entry:
                        results.append({
                            'title': entry.get('title', 'Unknown'),
                            'url': entry.get('webpage_url', ''),
                            'duration': entry.get('duration', 0),
                            'uploader': entry.get('uploader', 'Unknown'),
                            'thumbnail': entry.get('thumbnail', ''),
                        })
            
            return results
        
        except Exception as e:
            logger.error(f"Error searching YouTube: {str(e)}")
            return []
    
    def cleanup_file(self, filepath: str):
        """Clean up downloaded file"""
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                logger.info(f"Cleaned up file: {filepath}")
        except Exception as e:
            logger.error(f"Error cleaning up file: {str(e)}")