"""
API clients for external services
"""

import logging
import aiohttp
import asyncio
from typing import Optional, Dict, Any
from config import Config

logger = logging.getLogger(__name__)
config = Config()

class LucoSMSClient:
    """Client for LucoSMS API integration"""
    
    def __init__(self):
        self.base_url = config.LUCOSMS_API_BASE_URL
        self.api_key = config.LUCOSMS_API_KEY
        self.session = None
    
    async def _get_session(self):
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def get_user_info(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user information from LucoSMS API"""
        try:
            session = await self._get_session()
            url = f"{self.base_url}/admin/users/{user_id}"
            headers = {
                'accept': 'application/json',
                'Authorization': f'Bearer {self.api_key}'
            }
            
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                elif response.status == 404:
                    return None
                else:
                    logger.error(f"API error: {response.status} - {await response.text()}")
                    return None
        
        except Exception as e:
            logger.error(f"Error fetching user info: {str(e)}")
            return None
    
    async def recharge_user(self, user_id: str, amount: float) -> Dict[str, Any]:
        """Recharge user account"""
        try:
            session = await self._get_session()
            url = f"{self.base_url}/admin/users/{user_id}/recharge"
            headers = {
                'accept': 'application/json',
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.api_key}'
            }
            data = {
                'amount': amount,
                'currency': 'USD'
            }
            
            async with session.post(url, headers=headers, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    return {
                        'success': True,
                        'new_balance': result.get('new_balance'),
                        'transaction_id': result.get('transaction_id')
                    }
                else:
                    error_text = await response.text()
                    logger.error(f"Recharge API error: {response.status} - {error_text}")
                    return {
                        'success': False,
                        'error': f'API error: {response.status}'
                    }
        
        except Exception as e:
            logger.error(f"Error processing recharge: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def close(self):
        """Close the HTTP session"""
        if self.session and not self.session.closed:
            await self.session.close()

class CatboxClient:
    """Client for Catbox file hosting service"""
    
    def __init__(self):
        self.upload_url = config.CATBOX_API_URL
        self.session = None
    
    async def _get_session(self):
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def upload_file(self, file_path: str, filename: str) -> Optional[str]:
        """Upload file to Catbox and return download URL"""
        try:
            session = await self._get_session()
            
            with open(file_path, 'rb') as file:
                data = aiohttp.FormData()
                data.add_field('reqtype', 'fileupload')
                data.add_field('fileToUpload', file, filename=filename)
                
                async with session.post(self.upload_url, data=data) as response:
                    if response.status == 200:
                        result = await response.text()
                        # Catbox returns the direct URL as plain text
                        if result.startswith('https://files.catbox.moe/'):
                            return result.strip()
                        else:
                            logger.error(f"Unexpected Catbox response: {result}")
                            return None
                    else:
                        logger.error(f"Catbox upload error: {response.status}")
                        return None
        
        except Exception as e:
            logger.error(f"Error uploading to Catbox: {str(e)}")
            return None
    
    async def close(self):
        """Close the HTTP session"""
        if self.session and not self.session.closed:
            await self.session.close()
