"""
Configuration settings for the Telegram bot
"""

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration class for bot settings"""
    
    # Telegram Bot Token
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
    
    # LucoSMS API Configuration
    LUCOSMS_API_BASE_URL = os.getenv('LUCOSMS_API_BASE_URL', 'https://lucosms-api.onrender.com/v1')
    LUCOSMS_API_KEY = os.getenv('LUCOSMS_API_KEY', '')
    
    # Catbox API Configuration
    CATBOX_API_URL = os.getenv('CATBOX_API_URL', 'https://catbox.moe/user/api.php')
    
    # Admin User IDs (comma-separated string)
    ADMIN_USER_IDS = [int(id.strip()) for id in os.getenv('ADMIN_USER_IDS', '').split(',') if id.strip()]
    
    # Rate limiting settings
    MAX_REQUESTS_PER_MINUTE = int(os.getenv('MAX_REQUESTS_PER_MINUTE', '10'))
    
    # File upload settings
    MAX_FILE_SIZE_MB = int(os.getenv('MAX_FILE_SIZE_MB', '50'))
    
    def __init__(self):
        """Validate configuration on initialization"""
        if not self.TELEGRAM_BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")
        
        if not self.LUCOSMS_API_KEY:
            raise ValueError("LUCOSMS_API_KEY environment variable is required")
