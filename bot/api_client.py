"""
API clients for external services
"""

import logging
import aiohttp
import asyncio
from typing import Optional, Dict, Any
from config import Config
from bot.utils import generate_random_curl_command

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
    
    async def initiate_payment(self, name: str, email: str, amount: float, telegram_id: str) -> Optional[Dict[str, Any]]:
        """Initiate payment with LucoPay"""
        try:
            session = await self._get_session()
            url = f"{config.LUCO_PAYMENT_SERVICE_URL}/lucopay/initiate-payment"
            # Correctly split name into first and last name
            name_parts = name.split(' ', 1)
            first_name = name_parts[0]
            last_name = name_parts[1] if len(name_parts) > 1 else ''

            payload = {
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'phone_number': '',  # Assuming phone is not collected
                'amount': amount,
                'telegram_id': telegram_id
            }
            headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}

            async with session.post(url, json=payload, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"Payment initiation failed: {response.status} - {await response.text()}")
                    return None
        except Exception as e:
            logger.error(f"Error in initiate_payment: {e}")
            return None

    async def get_payment_status(self, order_tracking_id: str) -> Optional[Dict[str, Any]]:
        """Get payment status from LucoPay"""
        try:
            session = await self._get_session()
            url = f"{config.LUCO_PAYMENT_SERVICE_URL}/lucopay/payment-callback?OrderTrackingId={order_tracking_id}"
            headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}

            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"Payment status check failed: {response.status} - {await response.text()}")
                    return None
        except Exception as e:
            logger.error(f"Error in get_payment_status: {e}")
            return None

    async def topup_wallet(self, user_id: str, amount: float) -> Optional[Dict[str, Any]]:
        """Top up user wallet after successful payment"""
        try:
            session = await self._get_session()
            url = f"{config.LUCOSMS_API_BASE_URL}/admin/userwallet/{user_id}/topup"
            payload = {'amount': amount}
            headers = {
                'Content-Type': 'application/json', 
                'Accept': 'application/json',
                'Authorization': f'Bearer {self.api_key}'
            }

            async with session.post(url, json=payload, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"Wallet top-up failed: {response.status} - {await response.text()}")
                    return None
        except Exception as e:
            logger.error(f"Error in topup_wallet: {e}")
            return None
    
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
