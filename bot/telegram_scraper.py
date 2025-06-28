"""
Telegram group scraper using Telethon
"""

import logging
import asyncio
from typing import List, Dict, Any, Optional
from telethon import TelegramClient, events
from telethon.tl.types import MessageMediaDocument, MessageMediaPhoto
import os
from config import Config

logger = logging.getLogger(__name__)
config = Config()

class TelegramScraper:
    """Scraper for Telegram groups and channels"""
    
    def __init__(self):
        self.client = None
        self.session_name = 'telegram_scraper'
        
    async def initialize_client(self, api_id: str, api_hash: str, phone: str = None):
        """Initialize Telegram client"""
        try:
            self.client = TelegramClient(self.session_name, api_id, api_hash)
            await self.client.start(phone=phone)
            logger.info("Telegram client initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Error initializing Telegram client: {str(e)}")
            return False
    
    async def get_channel_messages(self, channel_username: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent messages from a channel"""
        if not self.client:
            return []
        
        try:
            messages = []
            async for message in self.client.iter_messages(channel_username, limit=limit):
                if message.text or message.media:
                    message_data = {
                        'id': message.id,
                        'text': message.text or '',
                        'date': message.date.isoformat() if message.date else '',
                        'views': getattr(message, 'views', 0),
                        'forwards': getattr(message, 'forwards', 0),
                        'has_media': bool(message.media),
                        'media_type': self._get_media_type(message.media),
                        'file_size': self._get_file_size(message.media),
                    }
                    messages.append(message_data)
            
            return messages
        
        except Exception as e:
            logger.error(f"Error getting channel messages: {str(e)}")
            return []
    
    async def search_movies_in_channel(self, channel_username: str, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search for movies in a channel"""
        if not self.client:
            return []
        
        try:
            movies = []
            search_terms = query.lower().split()
            
            async for message in self.client.iter_messages(channel_username, limit=100):
                if message.text:
                    text_lower = message.text.lower()
                    # Check if message contains movie-related keywords and search terms
                    if any(term in text_lower for term in search_terms) and \
                       any(keyword in text_lower for keyword in ['movie', 'film', 'download', 'quality', 'mkv', 'mp4']):
                        
                        movie_data = {
                            'id': message.id,
                            'text': message.text[:200] + '...' if len(message.text) > 200 else message.text,
                            'full_text': message.text,
                            'date': message.date.isoformat() if message.date else '',
                            'has_media': bool(message.media),
                            'media_type': self._get_media_type(message.media),
                            'file_size': self._get_file_size(message.media),
                            'message_link': f'https://t.me/{channel_username.replace("@", "")}/{message.id}'
                        }
                        movies.append(movie_data)
                        
                        if len(movies) >= limit:
                            break
            
            return movies
        
        except Exception as e:
            logger.error(f"Error searching movies in channel: {str(e)}")
            return []
    
    async def download_media_from_message(self, channel_username: str, message_id: int, download_path: str = "downloads") -> Optional[str]:
        """Download media from a specific message"""
        if not self.client:
            return None
        
        try:
            os.makedirs(download_path, exist_ok=True)
            
            message = await self.client.get_messages(channel_username, ids=message_id)
            if message and message.media:
                file_path = await self.client.download_media(message, file=download_path)
                return file_path
            
            return None
        
        except Exception as e:
            logger.error(f"Error downloading media: {str(e)}")
            return None
    
    def _get_media_type(self, media) -> str:
        """Get media type from message media"""
        if not media:
            return 'none'
        
        if isinstance(media, MessageMediaDocument):
            if media.document:
                mime_type = media.document.mime_type or ''
                if 'video' in mime_type:
                    return 'video'
                elif 'audio' in mime_type:
                    return 'audio'
                elif 'image' in mime_type:
                    return 'image'
                else:
                    return 'document'
        elif isinstance(media, MessageMediaPhoto):
            return 'photo'
        
        return 'other'
    
    def _get_file_size(self, media) -> int:
        """Get file size from message media"""
        if not media:
            return 0
        
        if isinstance(media, MessageMediaDocument) and media.document:
            return media.document.size or 0
        
        return 0
    
    async def close(self):
        """Close the Telegram client"""
        if self.client:
            await self.client.disconnect()
            logger.info("Telegram client disconnected")

# Global scraper instance
telegram_scraper = TelegramScraper()