"""
Utility functions for the Telegram bot
"""

import random
import string
from typing import List
from config import Config

config = Config()

def is_admin_user(user_id: int) -> bool:
    """Check if user is an administrator"""
    return user_id in config.ADMIN_USER_IDS

def is_file_size_valid(file_size: int) -> bool:
    """Check if file size is within limits"""
    max_size_bytes = config.MAX_FILE_SIZE_MB * 1024 * 1024
    return file_size <= max_size_bytes

def get_file_extension(filename: str) -> str:
    """Get file extension from filename"""
    return filename.split('.')[-1].lower() if '.' in filename else ''

def generate_random_curl_command(user_id: str) -> str:
    """Generate a random cURL command for the user"""
    # Generate random parameters
    random_params = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    
    curl_command = f"""curl -X 'GET' \\
  '{config.LUCOSMS_API_BASE_URL}/admin/users/{user_id}%2C{random_params}' \\
  -H 'accept: application/json' \\
  -H 'Authorization: Bearer {config.LUCOSMS_API_KEY[:8]}...'"""
    
    return curl_command

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

def validate_user_id(user_id: str) -> bool:
    """Validate user ID format"""
    # Basic validation - adjust according to your API requirements
    if not user_id:
        return False
    
    # Check length (adjust as needed)
    if len(user_id) < 3 or len(user_id) > 50:
        return False
    
    # Check for valid characters (alphanumeric and underscore)
    return user_id.replace('_', '').replace('-', '').isalnum()

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage"""
    # Remove potentially dangerous characters
    safe_chars = string.ascii_letters + string.digits + '-_.'
    sanitized = ''.join(c for c in filename if c in safe_chars)
    
    # Ensure filename is not empty and has reasonable length
    if not sanitized:
        sanitized = 'unnamed_file'
    
    return sanitized[:100]  # Limit length

class RateLimiter:
    """Simple rate limiter for API calls"""
    
    def __init__(self, max_requests: int = 10, time_window: int = 60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = {}
    
    def is_allowed(self, user_id: int) -> bool:
        """Check if user is allowed to make a request"""
        import time
        current_time = time.time()
        
        # Clean old requests
        if user_id in self.requests:
            self.requests[user_id] = [
                req_time for req_time in self.requests[user_id]
                if current_time - req_time < self.time_window
            ]
        else:
            self.requests[user_id] = []
        
        # Check if under limit
        if len(self.requests[user_id]) < self.max_requests:
            self.requests[user_id].append(current_time)
            return True
        
        return False

# Global rate limiter instance
rate_limiter = RateLimiter(max_requests=config.MAX_REQUESTS_PER_MINUTE)
