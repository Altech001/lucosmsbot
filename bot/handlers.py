"""
Message handlers for the Telegram bot
"""

import logging
import aiofiles
import os
from telegram import Update
from telegram.ext import ContextTypes
from bot.api_client import CatboxClient
from bot.utils import is_file_size_valid, get_file_extension
from config import Config

logger = logging.getLogger(__name__)
config = Config()
catbox_client = CatboxClient()

async def handle_file_upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle file uploads for backup"""
    document = update.message.document
    
    if not document:
        await update.message.reply_text("❌ No file detected.")
        return
    
    # Check file size
    if not is_file_size_valid(document.file_size):
        await update.message.reply_text(
            f"❌ File too large. Maximum size: {config.MAX_FILE_SIZE_MB}MB"
        )
        return
    
    try:
        # Show upload status
        status_msg = await update.message.reply_text("📤 Uploading file for backup...")
        
        # Download file from Telegram
        file = await context.bot.get_file(document.file_id)
        file_path = f"temp_{document.file_name}"
        
        await file.download_to_drive(file_path)
        
        # Upload to Catbox
        await status_msg.edit_text("☁️ Uploading to backup service...")
        
        backup_url = await catbox_client.upload_file(file_path, document.file_name)
        
        if backup_url:
            success_text = f"""
✅ **File Backup Successful**

**File:** `{document.file_name}`
**Size:** {document.file_size / 1024 / 1024:.2f}MB
**Backup URL:** {backup_url}

Your file is now safely backed up and accessible via the link above.
            """
            await status_msg.edit_text(success_text, parse_mode='Markdown')
        else:
            await status_msg.edit_text("❌ Failed to upload file to backup service.")
        
        # Clean up temporary file
        if os.path.exists(file_path):
            os.remove(file_path)
    
    except Exception as e:
        logger.error(f"Error handling file upload: {str(e)}")
        await update.message.reply_text(f"❌ Error processing file: {str(e)}")
        
        # Clean up on error
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages (non-commands)"""
    text = update.message.text.lower()
    
    # Check for common queries
    if any(word in text for word in ['help', 'how', 'what', 'commands']):
        await update.message.reply_text(
            "Type /help to see all available commands!\n\n"
            "Or try:\n"
            "• /check <user_id> - Check user info\n"
            "• /backup - Upload a file\n"
            "• Send me a file directly for backup"
        )
    elif any(word in text for word in ['backup', 'upload', 'file']):
        await update.message.reply_text(
            "📁 To backup a file:\n"
            "1. Send me any file directly\n"
            "2. Or use /backup command for instructions\n\n"
            "I'll upload it to Catbox and give you a download link!"
        )
    else:
        await update.message.reply_text(
            "I'm here to help! Use /help to see what I can do.\n\n"
            "Main features:\n"
            "• User management and checking\n"
            "• Account recharge\n"
            "• File backup with Catbox\n"
            "• Admin tools"
        )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors that occur during bot operation"""
    logger.error(f"Update {update} caused error {context.error}")
    
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "❌ An error occurred while processing your request. "
            "Please try again or contact an administrator if the problem persists."
        )
