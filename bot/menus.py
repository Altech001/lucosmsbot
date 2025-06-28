"""
Beautiful anime-style menus with inline keyboards
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from typing import List, Tuple

class AnimeMenus:
    """Creates beautiful anime-style menus and keyboards"""
    
    @staticmethod
    def main_menu() -> InlineKeyboardMarkup:
        """Main menu with anime styling"""
        keyboard = [
            [
                InlineKeyboardButton("🎬 YouTube", callback_data="youtube_menu"),
                InlineKeyboardButton("📺 Movies", callback_data="movies_menu")
            ],
            [
                InlineKeyboardButton("🎨 AI Art", callback_data="ai_menu"),
                InlineKeyboardButton("📁 Backup", callback_data="backup_menu")
            ],
            [
                InlineKeyboardButton("👤 Account", callback_data="account_menu"),
                InlineKeyboardButton("⚙️ Admin", callback_data="admin_menu")
            ],
            [
                InlineKeyboardButton("❓ Help", callback_data="help_menu"),
                InlineKeyboardButton("📊 Stats", callback_data="stats_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def youtube_menu() -> InlineKeyboardMarkup:
        """YouTube download menu"""
        keyboard = [
            [
                InlineKeyboardButton("🔍 Search", callback_data="youtube_search"),
                InlineKeyboardButton("📥 Download", callback_data="youtube_download")
            ],
            [
                InlineKeyboardButton("🎵 Audio Only", callback_data="youtube_audio"),
                InlineKeyboardButton("📹 Video HD", callback_data="youtube_hd")
            ],
            [
                InlineKeyboardButton("📱 Video SD", callback_data="youtube_sd"),
                InlineKeyboardButton("📋 Playlist", callback_data="youtube_playlist")
            ],
            [
                InlineKeyboardButton("🔙 Back", callback_data="main_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def movies_menu() -> InlineKeyboardMarkup:
        """Movies and TV shows menu"""
        keyboard = [
            [
                InlineKeyboardButton("🎬 Latest Movies", callback_data="movies_latest"),
                InlineKeyboardButton("🔥 Trending", callback_data="movies_trending")
            ],
            [
                InlineKeyboardButton("📺 TV Shows", callback_data="movies_tv"),
                InlineKeyboardButton("🌟 Anime", callback_data="movies_anime")
            ],
            [
                InlineKeyboardButton("🔍 Search Movies", callback_data="movies_search"),
                InlineKeyboardButton("💎 Premium", callback_data="movies_premium")
            ],
            [
                InlineKeyboardButton("📱 Telegram Groups", callback_data="movies_groups"),
                InlineKeyboardButton("🎯 Categories", callback_data="movies_categories")
            ],
            [
                InlineKeyboardButton("🔙 Back", callback_data="main_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def ai_menu() -> InlineKeyboardMarkup:
        """AI and image generation menu"""
        keyboard = [
            [
                InlineKeyboardButton("🎨 Generate Art", callback_data="ai_generate"),
                InlineKeyboardButton("🖼️ Analyze Image", callback_data="ai_analyze")
            ],
            [
                InlineKeyboardButton("😊 Make Sticker", callback_data="ai_sticker"),
                InlineKeyboardButton("✨ Text Sticker", callback_data="ai_text_sticker")
            ],
            [
                InlineKeyboardButton("🌸 Anime Style", callback_data="ai_anime"),
                InlineKeyboardButton("🎭 Cartoon Style", callback_data="ai_cartoon")
            ],
            [
                InlineKeyboardButton("🔮 Fantasy", callback_data="ai_fantasy"),
                InlineKeyboardButton("🤖 Cyberpunk", callback_data="ai_cyberpunk")
            ],
            [
                InlineKeyboardButton("🔙 Back", callback_data="main_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def backup_menu() -> InlineKeyboardMarkup:
        """File backup menu"""
        keyboard = [
            [
                InlineKeyboardButton("📤 Upload File", callback_data="backup_upload"),
                InlineKeyboardButton("💾 My Backups", callback_data="backup_list")
            ],
            [
                InlineKeyboardButton("🗂️ File Manager", callback_data="backup_manage"),
                InlineKeyboardButton("🔗 Get Links", callback_data="backup_links")
            ],
            [
                InlineKeyboardButton("⚡ Quick Upload", callback_data="backup_quick"),
                InlineKeyboardButton("📊 Storage Info", callback_data="backup_info")
            ],
            [
                InlineKeyboardButton("🔙 Back", callback_data="main_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def account_menu() -> InlineKeyboardMarkup:
        """Account management menu"""
        keyboard = [
            [
                InlineKeyboardButton("👤 My Profile", callback_data="account_profile"),
                InlineKeyboardButton("💰 Balance", callback_data="account_balance")
            ],
            [
                InlineKeyboardButton("📈 Usage Stats", callback_data="account_stats"),
                InlineKeyboardButton("⚙️ Settings", callback_data="account_settings")
            ],
            [
                InlineKeyboardButton("🔐 Security", callback_data="account_security"),
                InlineKeyboardButton("📱 Devices", callback_data="account_devices")
            ],
            [
                InlineKeyboardButton("🔙 Back", callback_data="main_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def admin_menu() -> InlineKeyboardMarkup:
        """Admin panel menu"""
        keyboard = [
            [
                InlineKeyboardButton("👥 User Management", callback_data="admin_users"),
                InlineKeyboardButton("💳 Recharge", callback_data="admin_recharge")
            ],
            [
                InlineKeyboardButton("📊 System Stats", callback_data="admin_stats"),
                InlineKeyboardButton("🔧 Bot Config", callback_data="admin_config")
            ],
            [
                InlineKeyboardButton("📝 Logs", callback_data="admin_logs"),
                InlineKeyboardButton("🔄 Restart", callback_data="admin_restart")
            ],
            [
                InlineKeyboardButton("🚨 Alerts", callback_data="admin_alerts"),
                InlineKeyboardButton("🛠️ Maintenance", callback_data="admin_maintenance")
            ],
            [
                InlineKeyboardButton("🔙 Back", callback_data="main_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def quality_menu() -> InlineKeyboardMarkup:
        """Video quality selection menu"""
        keyboard = [
            [
                InlineKeyboardButton("🎬 Best Quality", callback_data="quality_best"),
                InlineKeyboardButton("📺 HD (720p)", callback_data="quality_hd")
            ],
            [
                InlineKeyboardButton("📱 SD (480p)", callback_data="quality_sd"),
                InlineKeyboardButton("🎵 Audio Only", callback_data="quality_audio")
            ],
            [
                InlineKeyboardButton("🔙 Back", callback_data="youtube_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def movie_groups_menu() -> InlineKeyboardMarkup:
        """Movie Telegram groups menu"""
        keyboard = [
            [
                InlineKeyboardButton("🎬 VJ Junior", callback_data="group_vjjunior"),
                InlineKeyboardButton("🔥 Latest Movies", callback_data="group_latest")
            ],
            [
                InlineKeyboardButton("📺 TV Series", callback_data="group_tv"),
                InlineKeyboardButton("🌟 Anime Hub", callback_data="group_anime")
            ],
            [
                InlineKeyboardButton("💎 Premium Groups", callback_data="group_premium"),
                InlineKeyboardButton("🔍 Search Groups", callback_data="group_search")
            ],
            [
                InlineKeyboardButton("🔙 Back", callback_data="movies_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def anime_styles_menu() -> InlineKeyboardMarkup:
        """Anime art styles menu"""
        keyboard = [
            [
                InlineKeyboardButton("🌸 Kawaii", callback_data="style_kawaii"),
                InlineKeyboardButton("⚔️ Shounen", callback_data="style_shounen")
            ],
            [
                InlineKeyboardButton("💕 Shoujo", callback_data="style_shoujo"),
                InlineKeyboardButton("🌙 Magical Girl", callback_data="style_magical")
            ],
            [
                InlineKeyboardButton("🔥 Action", callback_data="style_action"),
                InlineKeyboardButton("🎭 Chibi", callback_data="style_chibi")
            ],
            [
                InlineKeyboardButton("🔙 Back", callback_data="ai_menu")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def confirmation_menu(action: str) -> InlineKeyboardMarkup:
        """Confirmation menu for important actions"""
        keyboard = [
            [
                InlineKeyboardButton("✅ Yes", callback_data=f"confirm_{action}"),
                InlineKeyboardButton("❌ No", callback_data=f"cancel_{action}")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def pagination_menu(current_page: int, total_pages: int, prefix: str) -> InlineKeyboardMarkup:
        """Pagination menu for long lists"""
        keyboard = []
        
        # Page navigation
        nav_row = []
        if current_page > 1:
            nav_row.append(InlineKeyboardButton("⬅️ Prev", callback_data=f"{prefix}_page_{current_page-1}"))
        
        nav_row.append(InlineKeyboardButton(f"📄 {current_page}/{total_pages}", callback_data="current_page"))
        
        if current_page < total_pages:
            nav_row.append(InlineKeyboardButton("Next ➡️", callback_data=f"{prefix}_page_{current_page+1}"))
        
        keyboard.append(nav_row)
        
        # Jump to page
        if total_pages > 3:
            keyboard.append([
                InlineKeyboardButton("🔢 Go to Page", callback_data=f"{prefix}_goto"),
                InlineKeyboardButton("🔄 Refresh", callback_data=f"{prefix}_refresh")
            ])
        
        keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="main_menu")])
        
        return InlineKeyboardMarkup(keyboard)

# Menu text templates with anime styling
MENU_TEXTS = {
    "welcome": """
🌟 **Welcome to Luco Bot!** 🌟

✨ Your magical assistant for Recharge, downloads, AI art, and more!

**🎯 What can I do?**
• 🎬 Download YouTube videos & music
• 📺 Find movies from Telegram groups  
• 🎨 Generate beautiful AI artwork
• 😊 Create custom stickers
• 📁 Backup your files securely
• 👤 Manage your account

**Choose an option below to get started!** ⭐
    """,
    
    "youtube": """
🎬 **YouTube Downloader** 📥

**Available Options:**
• 🔍 Search for videos
• 📥 Download by URL
• 🎵 Audio-only downloads
• 📹 HD/SD video options
• 📋 Playlist support

**Just send me a YouTube URL or search for content!** ✨
    """,
    
    "ai_art": """
🎨 **AI Art Studio** ✨

**Create amazing artwork with AI:**
• 🌸 Anime-style illustrations
• 🎭 Cartoon characters
• 🔮 Fantasy scenes
• 🤖 Cyberpunk art
• 😊 Convert images to stickers

**Send me a description and watch the magic happen!** 🌟
    """,
    
    "movies": """
🎬 **Movie & TV Hub** 📺

**Find the latest content:**
• 🔥 Trending movies
• 📺 TV series & anime
• 🌟 Premium content
• 📱 Telegram movie groups
• 🎯 Search by category

**Your entertainment center awaits!** ✨
    """
}