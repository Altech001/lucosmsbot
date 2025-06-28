#!/usr/bin/env python3
"""
Telegram Bot for User Management, Account Recharge, and File Backup
"""

import logging
import asyncio
import os
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler, 
    ConversationHandler, filters
)
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
logger = logging.getLogger(__name__)

def main():
    """Start the bot."""
    # Create the Application
    config = Config()
    application = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", show_main_menu))
    application.add_handler(CommandHandler("menu", show_main_menu))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("check", check_user_command))
    recharge_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('recharge', start_recharge)],
        states={
            EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_for_amount)],
            AMOUNT: [
                CallbackQueryHandler(generate_payment_link, pattern='^recharge_'),
                MessageHandler(filters.TEXT & ~filters.COMMAND, generate_payment_link)
            ],
            CONFIRMATION: [CallbackQueryHandler(verify_payment, pattern='^verify_')]
        },
        fallbacks=[CommandHandler('cancel', cancel_recharge)],
        per_message=False
    )
    application.add_handler(recharge_conv_handler)
    application.add_handler(CommandHandler("backup", backup_file_command))
    application.add_handler(CommandHandler("admin", admin_command))
    application.add_handler(CommandHandler("stats", stats_command))
    
    # Add new enhanced commands
    application.add_handler(CommandHandler("ytsearch", youtube_search_command))
    application.add_handler(CommandHandler("ytdl", youtube_download_command))
    application.add_handler(CommandHandler("generate", generate_ai_art_command))
    application.add_handler(CommandHandler("sticker", create_sticker_command))
    application.add_handler(CommandHandler("movie", movie_search_command))

    # Add message handlers
    application.add_handler(MessageHandler(filters.Document.ALL, handle_file_upload))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
    
    # Add callback query handler for inline keyboards
    application.add_handler(CallbackQueryHandler(handle_callback_query))

    # Add error handler
    application.add_error_handler(error_handler)

    # Run the bot
    # Start the keep-alive task as a background process
    if config.KEEP_ALIVE_URL:
        loop = asyncio.get_event_loop()
        loop.create_task(keep_alive_task(config.KEEP_ALIVE_URL))

    # Run the bot
    logger.info("Starting Telegram Bot...")
    application.run_polling(allowed_updates=["message", "callback_query"])

if __name__ == '__main__':
    main()
