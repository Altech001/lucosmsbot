"""
Keep-alive mechanism to prevent the bot from being spun down by hosting services.
"""

import asyncio
import logging
import aiohttp

logger = logging.getLogger(__name__)

async def ping_url(url: str):
    """Sends an HTTP GET request to the specified URL."""
    if not url:
        logger.warning("Keep-alive URL is not configured. Skipping ping.")
        return

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    logger.info(f"Successfully pinged keep-alive URL: {url}")
                else:
                    logger.warning(
                        f"Keep-alive ping to {url} failed with status: {response.status}"
                    )
    except aiohttp.ClientError as e:
        logger.error(f"Error pinging keep-alive URL {url}: {e}")

async def keep_alive_task(url: str, interval_minutes: int = 14):
    """Periodically pings a URL to keep the service alive."""
    interval_seconds = interval_minutes * 60
    logger.info(f"Keep-alive task started. Pinging {url} every {interval_minutes} minutes.")
    while True:
        await ping_url(url)
        await asyncio.sleep(interval_seconds)
