#!/usr/bin/env python3
"""
Telegram Bot for User Management, Account Recharge, and File Backup
"""

import logging
import os
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler, 
    ConversationHandler, filters
)
from aiohttp import web
from bot.commands import (
    start_command, help_command, check_user_command, 
    backup_file_command, admin_command, stats_command
)
from bot.payments import (
    start_recharge, ask_for_amount, generate_payment_link, verify_payment, cancel_recharge,
    EMAIL, AMOUNT, CONFIRMATION
)
from bot.handlers import handle_file_upload, handle_text_message, error_handler
from bot.advanced_commands import (
    show_main_menu, youtube_search_command, youtube_download_command,
    generate_ai_art_command, create_sticker_command, movie_search_command,
    handle_callback_query
)
from config import Config
from bot.keep_alive import keep_alive_task

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

async def health_check(request):
    """A simple health check endpoint for Render."""
    return web.Response(text="OK")

async def run_web_server():
    """Runs a simple aiohttp web server to satisfy Render's port binding."""
    port = int(os.environ.get('PORT', 8080))
    app = web.Application()
    app.router.add_get('/', health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    logger.info(f"Starting web server on port {port}...")
    await site.start()

async def main():
    """Initializes and runs the bot, keep-alive task, and web server."""
    config = Config()
    
    # Initialize the bot application
    application = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()

    # Conversation handler for the recharge command
    recharge_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('recharge', start_recharge)],
        states={
            EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_for_amount)],
            AMOUNT: [
                CallbackQueryHandler(generate_payment_link, pattern='^amount_'),
                MessageHandler(filters.TEXT & ~filters.COMMAND, generate_payment_link)
            ],
            CONFIRMATION: [CallbackQueryHandler(verify_payment, pattern='^confirm_payment_')]
        },
        fallbacks=[CommandHandler('cancel', cancel_recharge)],
        per_message=False
    )

    # Register handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("check", check_user_command))
    application.add_handler(CommandHandler("backup", backup_file_command))
    application.add_handler(CommandHandler("admin", admin_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(recharge_conv_handler)
    
    # Advanced command handlers
    application.add_handler(CommandHandler("menu", show_main_menu))
    application.add_handler(CommandHandler("ytsearch", youtube_search_command))
    application.add_handler(CommandHandler("ytdl", youtube_download_command))
    application.add_handler(CommandHandler("generate", generate_ai_art_command))
    application.add_handler(CommandHandler("sticker", create_sticker_command))
    application.add_handler(CommandHandler("movie", movie_search_command))
    application.add_handler(CallbackQueryHandler(handle_callback_query))

    # General message and file handlers
    application.add_handler(MessageHandler(filters.Document.ALL | filters.VIDEO | filters.PHOTO, handle_file_upload))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))

    # Error handler
    application.add_error_handler(error_handler)

    # Run the bot and other tasks concurrently
    async with application:
        await application.initialize()
        await application.start()
        await application.updater.start_polling(allowed_updates=["message", "callback_query"])
        logger.info("Telegram Bot started.")

        # Start the keep-alive task
        if config.KEEP_ALIVE_URL:
            asyncio.create_task(keep_alive_task(config.KEEP_ALIVE_URL))
        
        # Start the web server for Render
        asyncio.create_task(run_web_server())

        # Keep the application running
        while True:
            await asyncio.sleep(3600) # Keep the main coroutine alive

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped manually.")