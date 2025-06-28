#!/usr/bin/env python3
"""
Telegram Bot for User Management, Account Recharge, and File Backup
"""

import logging
import asyncio
import os
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from bot.commands import (
    start_command, help_command, check_user_command, recharge_command,
    backup_file_command, admin_command, stats_command
)
from bot.handlers import handle_file_upload, handle_text_message, error_handler
from bot.advanced_commands import (
    show_main_menu, youtube_search_command, youtube_download_command,
    generate_ai_art_command, create_sticker_command, movie_search_command,
    handle_callback_query
)
from config import Config

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
    application.add_handler(CommandHandler("recharge", recharge_command))
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
    logger.info("Starting Telegram Bot...")
    application.run_polling(allowed_updates=["message", "callback_query"])

if __name__ == '__main__':
    main()
