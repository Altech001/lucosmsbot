"""
Command handlers for the Telegram bot
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes
from bot.api_client import LucoSMSClient
from bot.utils import is_admin_user, generate_random_curl_command
from config import Config

logger = logging.getLogger(__name__)
config = Config()
lucosms_client = LucoSMSClient()

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /start command"""
    user = update.effective_user
    welcome_message = f"""
🤖 Welcome to the User Management Bot, {user.first_name}!

Available commands:
• /help - Show this help message
• /check <user_id> - Check user information
• /recharge <user_id> <amount> - Recharge user account
• /backup - Upload a file for backup
• /admin - Admin panel (admins only)
• /stats - Show bot statistics

Send me a file to backup it automatically!
    """
    await update.message.reply_text(welcome_message)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /help command"""
    help_text = """
📋 **Bot Commands Help**

**User Management:**
• `/check <user_id>` - Look up user information from the API
• `/recharge <user_id> <amount>` - Add credits to user account

**File Management:**
• `/backup` - Upload a file for backup (or just send a file directly)
• Files are automatically uploaded to Catbox and you'll receive a download link

**Administrative:**
• `/admin` - Access admin panel (authorized users only)
• `/stats` - View bot usage statistics

**Examples:**
• `/check user123` - Check info for user with ID 'user123'
• `/recharge user123 100` - Add 100 credits to user123's account
• Send any file to backup it automatically

**Notes:**
• Maximum file size: {config.MAX_FILE_SIZE_MB}MB
• Rate limit: {config.MAX_REQUESTS_PER_MINUTE} requests per minute
• For support, contact an administrator
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def check_user_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /check command to look up user information"""
    if not context.args:
        await update.message.reply_text("❌ Please provide a user ID. Usage: /check <user_id>")
        return
    
    user_id = context.args[0]
    
    try:
        # Show loading message
        loading_msg = await update.message.reply_text("🔍 Looking up user information...")
        
        # Get user info from API
        user_info = await lucosms_client.get_user_info(user_id)
        
        if user_info:
            # Format user information
            # Generate random cURL command
            curl_command = generate_random_curl_command(user_id)
            
            info_text = f"""
👤 **User Information**

**User ID:** `{user_id}`
**Status:** {user_info.get('status', 'Unknown')}
**Balance:** ${user_info.get('balance', '0.00')}
**Created:** {user_info.get('created_at', 'Unknown')}
**Last Active:** {user_info.get('last_active', 'Unknown')}

**Random cURL Command:**
```bash
{curl_command}
```
            """
            
            await loading_msg.edit_text(info_text, parse_mode='Markdown')
        else:
            await loading_msg.edit_text(f"❌ User `{user_id}` not found in the system.")
    
    except Exception as e:
        logger.error(f"Error checking user: {str(e)}")
        await update.message.reply_text(f"❌ Error checking user: {str(e)}")

async def backup_file_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /backup command for file upload instructions"""
    backup_instructions = """
📁 **File Backup Instructions**

To backup a file, you can:

1. **Direct Upload**: Simply send me any file directly in the chat
2. **Use this command**: Send /backup followed by uploading a file

**Supported Features:**
• Maximum file size: {config.MAX_FILE_SIZE_MB}MB
• All file types supported
• Automatic upload to Catbox
• Secure backup links provided
• Automatic cleanup of temporary files

**How it works:**
1. Send me a file
2. I'll upload it to Catbox
3. You'll receive a secure download link
4. Your file is safely backed up!

Just send me a file to get started! 📤
    """
    await update.message.reply_text(backup_instructions.format(config=config))

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /admin command for administrative functions"""
    user_id = update.effective_user.id
    
    if not is_admin_user(user_id):
        await update.message.reply_text("❌ This command is only available to administrators.")
        return
    
    admin_panel = """
👑 **Administrator Panel**

**Available Admin Commands:**
• `/recharge <user_id> <amount>` - Recharge user account
• `/stats` - View bot statistics
• `/check <user_id>` - Check any user information

**Admin Features:**
• User account management
• Transaction processing
• System monitoring
• Rate limit bypass

**Current Settings:**
• Max file size: {config.MAX_FILE_SIZE_MB}MB
• Rate limit: {config.MAX_REQUESTS_PER_MINUTE} requests/min
• Admin users: {len(config.ADMIN_USER_IDS)} configured

Use these commands responsibly! 🛡️
    """
    await update.message.reply_text(admin_panel.format(config=config), parse_mode='Markdown')

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /stats command for bot statistics"""
    user_id = update.effective_user.id
    
    if not is_admin_user(user_id):
        await update.message.reply_text("❌ This command is only available to administrators.")
        return
    
    # Basic stats (you can extend this with actual metrics)
    stats_text = """
📊 **Bot Statistics**

**System Status:** ✅ Online
**Configuration:**
• Max file size: {config.MAX_FILE_SIZE_MB}MB
• Rate limit: {config.MAX_REQUESTS_PER_MINUTE} requests/min
• Admin users: {len(config.ADMIN_USER_IDS)}

**API Status:**
• LucoSMS API: {"✅ Connected" if config.LUCOSMS_API_KEY else "❌ No API key"}
• Catbox API: ✅ Available

**Features Active:**
• User management ✅
• Account recharge ✅
• File backup ✅
• Admin commands ✅

Bot is running normally! 🚀
    """
    await update.message.reply_text(stats_text.format(config=config), parse_mode='Markdown')
