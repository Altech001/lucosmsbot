"""
Advanced command handlers for enhanced bot features
"""

import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from bot.youtube_downloader import YouTubeDownloader
from bot.gemini_ai import gemini_ai
from bot.menus import AnimeMenus, MENU_TEXTS
from bot.utils import is_admin_user
from bot.api_client import CatboxClient

logger = logging.getLogger(__name__)

# Initialize services
youtube_dl = YouTubeDownloader()
catbox_client = CatboxClient()

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show the beautiful main menu"""
    query = update.callback_query
    if query:
        await query.answer()
        await query.edit_message_text(
            text=MENU_TEXTS["welcome"],
            reply_markup=AnimeMenus.main_menu(),
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            text=MENU_TEXTS["welcome"],
            reply_markup=AnimeMenus.main_menu(),
            parse_mode='Markdown'
        )

async def youtube_search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle YouTube search"""
    if not context.args:
        await update.message.reply_text(
            "🔍 **YouTube Search**\n\n"
            "Please provide a search query!\n"
            "Example: `/ytsearch anime music video`",
            parse_mode='Markdown'
        )
        return
    
    query = " ".join(context.args)
    loading_msg = await update.message.reply_text("🔍 Searching YouTube...")
    
    try:
        results = await youtube_dl.search_youtube(query, max_results=5)
        
        if results:
            response = f"🎬 **Search Results for:** `{query}`\n\n"
            
            keyboard = []
            for i, video in enumerate(results, 1):
                duration = f"{video['duration']//60}:{video['duration']%60:02d}" if video['duration'] else "Live"
                response += f"**{i}.** {video['title'][:50]}...\n"
                response += f"👤 {video['uploader']} | ⏱️ {duration}\n\n"
                
                keyboard.append([
                    InlineKeyboardButton(
                        f"📥 Download {i}",
                        callback_data=f"download_{video['url']}"
                    )
                ])
            
            keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="youtube_menu")])
            
            await loading_msg.edit_text(
                response,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )
        else:
            await loading_msg.edit_text("❌ No results found. Try a different search term.")
    
    except Exception as e:
        logger.error(f"YouTube search error: {str(e)}")
        await loading_msg.edit_text(f"❌ Search failed: {str(e)}")

async def youtube_download_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle YouTube download"""
    if not context.args:
        await update.message.reply_text(
            "📥 **YouTube Download**\n\n"
            "Please provide a YouTube URL!\n"
            "Example: `/ytdl https://youtube.com/watch?v=example`",
            parse_mode='Markdown'
        )
        return
    
    url = context.args[0]
    
    # Show quality selection
    keyboard = [
        [
            InlineKeyboardButton("🎬 Best Quality", callback_data=f"dl_best_{url}"),
            InlineKeyboardButton("📺 HD (720p)", callback_data=f"dl_hd_{url}")
        ],
        [
            InlineKeyboardButton("📱 SD (480p)", callback_data=f"dl_sd_{url}"),
            InlineKeyboardButton("🎵 Audio Only", callback_data=f"dl_audio_{url}")
        ]
    ]
    
    await update.message.reply_text(
        "📥 **Choose Download Quality:**",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def generate_ai_art_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generate AI artwork"""
    if not context.args:
        await update.message.reply_text(
            "🎨 **AI Art Generator**\n\n"
            "Describe what you want me to create!\n"
            "Example: `/generate cute anime girl with blue hair`",
            parse_mode='Markdown'
        )
        return
    
    prompt = " ".join(context.args)
    loading_msg = await update.message.reply_text("🎨 Creating your artwork... ✨")
    
    try:
        image_path = await gemini_ai.generate_image(prompt, style="anime")
        
        if image_path and os.path.exists(image_path):
            # Upload to Catbox for sharing
            await loading_msg.edit_text("☁️ Uploading to cloud...")
            backup_url = await catbox_client.upload_file(image_path, f"ai_art_{hash(prompt)}.png")
            
            # Send the image
            with open(image_path, 'rb') as image_file:
                caption = f"🎨 **Your AI Artwork**\n\n📝 Prompt: `{prompt}`"
                if backup_url:
                    caption += f"\n🔗 Download: {backup_url}"
                
                await update.message.reply_photo(
                    photo=image_file,
                    caption=caption,
                    parse_mode='Markdown'
                )
            
            # Cleanup
            gemini_ai.cleanup_file(image_path)
            await loading_msg.delete()
        else:
            await loading_msg.edit_text("❌ Failed to generate image. Try a different prompt.")
    
    except Exception as e:
        logger.error(f"AI art generation error: {str(e)}")
        await loading_msg.edit_text(f"❌ Generation failed: {str(e)}")

async def create_sticker_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Create sticker from text or image"""
    if update.message.reply_to_message and update.message.reply_to_message.photo:
        # Convert image to sticker
        loading_msg = await update.message.reply_text("😊 Converting to sticker...")
        
        try:
            # Download the image
            photo = update.message.reply_to_message.photo[-1]
            file = await context.bot.get_file(photo.file_id)
            image_path = f"temp_image_{photo.file_unique_id}.jpg"
            await file.download_to_drive(image_path)
            
            # Convert to sticker
            sticker_path = await gemini_ai.image_to_sticker(image_path)
            
            if sticker_path and os.path.exists(sticker_path):
                with open(sticker_path, 'rb') as sticker_file:
                    await update.message.reply_sticker(sticker=sticker_file)
                
                # Cleanup
                gemini_ai.cleanup_file(image_path)
                gemini_ai.cleanup_file(sticker_path)
                await loading_msg.delete()
            else:
                await loading_msg.edit_text("❌ Failed to create sticker")
        
        except Exception as e:
            logger.error(f"Sticker creation error: {str(e)}")
            await loading_msg.edit_text(f"❌ Sticker creation failed: {str(e)}")
    
    elif context.args:
        # Create text sticker
        text = " ".join(context.args)
        loading_msg = await update.message.reply_text("😊 Creating text sticker...")
        
        try:
            sticker_path = await gemini_ai.create_text_sticker(text, style="anime")
            
            if sticker_path and os.path.exists(sticker_path):
                with open(sticker_path, 'rb') as sticker_file:
                    await update.message.reply_sticker(sticker=sticker_file)
                
                gemini_ai.cleanup_file(sticker_path)
                await loading_msg.delete()
            else:
                await loading_msg.edit_text("❌ Failed to create text sticker")
        
        except Exception as e:
            logger.error(f"Text sticker creation error: {str(e)}")
            await loading_msg.edit_text(f"❌ Text sticker creation failed: {str(e)}")
    
    else:
        await update.message.reply_text(
            "😊 **Sticker Creator**\n\n"
            "**Options:**\n"
            "• Reply to an image with `/sticker` to convert it\n"
            "• Use `/sticker your text here` to create text sticker\n\n"
            "**Examples:**\n"
            "• `/sticker Hello World!`\n"
            "• Reply to a photo with `/sticker`",
            parse_mode='Markdown'
        )

async def movie_search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Search for movies in Telegram groups"""
    if not context.args:
        await update.message.reply_text(
            "🎬 **Movie Search**\n\n"
            "Search for movies in Telegram groups!\n"
            "Example: `/movie avengers endgame`",
            parse_mode='Markdown'
        )
        return
    
    query = " ".join(context.args)
    loading_msg = await update.message.reply_text(f"🔍 Searching for: `{query}`...")
    
    # For demo purposes, show popular movie groups
    keyboard = [
        [
            InlineKeyboardButton("🎬 VJ Junior Movies", url="https://t.me/vjjuniornewmovies"),
            InlineKeyboardButton("🔥 Latest Movies", url="https://t.me/latestmovies2024")
        ],
        [
            InlineKeyboardButton("📺 TV Series Hub", url="https://t.me/tvserieshub"),
            InlineKeyboardButton("🌟 Anime Collection", url="https://t.me/animecollection")
        ],
        [
            InlineKeyboardButton("💎 Premium Movies", url="https://t.me/premiummovies"),
            InlineKeyboardButton("🎯 Movie Requests", url="https://t.me/movierequests")
        ]
    ]
    
    await loading_msg.edit_text(
        f"🎬 **Movie Groups for:** `{query}`\n\n"
        "🌟 **Popular Telegram Movie Groups:**\n"
        "Click on any group to join and search for your movie!\n\n"
        "💡 **Tip:** Use group search after joining",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

# Callback query handlers
async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all callback queries from inline keyboards"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    # Menu navigation
    if data == "main_menu":
        await show_main_menu(update, context)
    
    elif data == "youtube_menu":
        await query.edit_message_text(
            text=MENU_TEXTS["youtube"],
            reply_markup=AnimeMenus.youtube_menu(),
            parse_mode='Markdown'
        )
    
    elif data == "movies_menu":
        await query.edit_message_text(
            text=MENU_TEXTS["movies"],
            reply_markup=AnimeMenus.movies_menu(),
            parse_mode='Markdown'
        )
    
    elif data == "ai_menu":
        await query.edit_message_text(
            text=MENU_TEXTS["ai_art"],
            reply_markup=AnimeMenus.ai_menu(),
            parse_mode='Markdown'
        )
    
    elif data == "backup_menu":
        await query.edit_message_text(
            text="📁 **File Backup Center**\n\n"
                 "Upload files securely and get permanent links!\n"
                 "Maximum file size: 50MB\n\n"
                 "Just send me any file to backup it automatically! 📤",
            reply_markup=AnimeMenus.backup_menu(),
            parse_mode='Markdown'
        )
    
    elif data == "account_menu":
        user_id = query.from_user.id
        await query.edit_message_text(
            text=f"👤 **Your Account**\n\n"
                 f"**User ID:** `{user_id}`\n"
                 f"**Username:** @{query.from_user.username or 'Not set'}\n"
                 f"**Name:** {query.from_user.first_name or 'Unknown'}\n\n"
                 f"**Status:** Active ✅\n"
                 f"**Joined:** Recently",
            reply_markup=AnimeMenus.account_menu(),
            parse_mode='Markdown'
        )
    
    elif data == "admin_menu":
        if is_admin_user(query.from_user.id):
            await query.edit_message_text(
                text="👑 **Admin Panel**\n\n"
                     "Welcome, Administrator!\n"
                     "Manage users, system settings, and bot configuration.\n\n"
                     "🛡️ Use these powers responsibly!",
                reply_markup=AnimeMenus.admin_menu(),
                parse_mode='Markdown'
            )
        else:
            await query.edit_message_text(
                text="❌ **Access Denied**\n\n"
                     "You don't have administrator privileges.\n"
                     "Contact an admin if you need access.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 Back", callback_data="main_menu")
                ]])
            )
    
    # YouTube download handlers
    elif data.startswith("dl_"):
        await handle_download_callback(update, context, data)
    
    # AI art style handlers
    elif data.startswith("ai_"):
        await handle_ai_callback(update, context, data)
    
    # Movie group handlers
    elif data.startswith("movies_"):
        await handle_movies_callback(update, context, data)

async def handle_download_callback(update: Update, context: ContextTypes.DEFAULT_TYPE, data: str):
    """Handle download callbacks"""
    query = update.callback_query
    
    parts = data.split("_", 2)
    if len(parts) < 3:
        await query.edit_message_text("❌ Invalid download request")
        return
    
    quality = parts[1]
    url = parts[2]
    
    quality_map = {
        "best": "video",
        "hd": "video_hd", 
        "sd": "video_sd",
        "audio": "audio"
    }
    
    format_type = quality_map.get(quality, "video")
    
    await query.edit_message_text(f"📥 Starting download in {quality.upper()} quality...")
    
    try:
        file_path = await youtube_dl.download_video(url, format_type)
        
        if file_path and os.path.exists(file_path):
            # Upload to Catbox
            await query.edit_message_text("☁️ Uploading to cloud storage...")
            filename = os.path.basename(file_path)
            backup_url = await catbox_client.upload_file(file_path, filename)
            
            if backup_url:
                await query.edit_message_text(
                    f"✅ **Download Complete!**\n\n"
                    f"📁 **File:** {filename}\n"
                    f"🔗 **Download Link:** {backup_url}\n\n"
                    f"💡 Your file will be available at this link permanently!",
                    parse_mode='Markdown'
                )
            else:
                await query.edit_message_text("❌ Upload to cloud storage failed")
            
            # Cleanup local file
            youtube_dl.cleanup_file(file_path)
        else:
            await query.edit_message_text("❌ Download failed")
    
    except Exception as e:
        logger.error(f"Download error: {str(e)}")
        await query.edit_message_text(f"❌ Download failed: {str(e)}")

async def handle_ai_callback(update: Update, context: ContextTypes.DEFAULT_TYPE, data: str):
    """Handle AI-related callbacks"""
    query = update.callback_query
    
    if data == "ai_generate":
        await query.edit_message_text(
            "🎨 **AI Art Generator**\n\n"
            "Send me a description of what you want to create!\n\n"
            "**Examples:**\n"
            "• `cute anime girl with blue hair and magical powers`\n"
            "• `cyberpunk city at night with neon lights`\n"
            "• `fantasy dragon flying over mountains`\n\n"
            "Just type your description and I'll create it! ✨"
        )
    
    elif data == "ai_sticker":
        await query.edit_message_text(
            "😊 **Sticker Creator**\n\n"
            "**How to create stickers:**\n"
            "• Send me an image to convert it to a sticker\n"
            "• Type text to create a text-based sticker\n\n"
            "**Example:** Just type `Hello World!` and I'll make it into a sticker!"
        )
    
    elif data in ["ai_anime", "ai_cartoon", "ai_fantasy", "ai_cyberpunk"]:
        style = data.replace("ai_", "")
        await query.edit_message_text(
            f"🎨 **{style.title()} Style Generator**\n\n"
            f"Perfect! Send me a description and I'll create it in {style} style.\n\n"
            f"**Example:** `warrior princess with magical sword`"
        )

async def handle_movies_callback(update: Update, context: ContextTypes.DEFAULT_TYPE, data: str):
    """Handle movie-related callbacks"""
    query = update.callback_query
    
    if data == "movies_groups":
        await query.edit_message_text(
            text="📱 **Telegram Movie Groups**\n\n"
                 "🌟 Best groups for movies and TV shows:",
            reply_markup=AnimeMenus.movie_groups_menu(),
            parse_mode='Markdown'
        )
    
    elif data == "group_vjjunior":
        keyboard = [[
            InlineKeyboardButton("🎬 Join VJ Junior", url="https://t.me/vjjuniornewmovies"),
            InlineKeyboardButton("🔙 Back", callback_data="movies_groups")
        ]]
        
        await query.edit_message_text(
            "🎬 **VJ Junior New Movies**\n\n"
            "✨ Latest movies and TV shows\n"
            "🔥 High quality content\n"
            "📱 Mobile-friendly formats\n"
            "🌟 Active community\n\n"
            "Click to join the channel!",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )