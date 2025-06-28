# Telegram Bot for User Management, Account Recharge, and File Backup

## Overview

This is an advanced Python-based Telegram bot with anime-style menus that provides comprehensive entertainment and utility features. The bot includes YouTube downloading, AI-powered image generation, movie discovery, file backup, user management, and administrative controls with beautiful interactive menus.

## System Architecture

The application follows a modular architecture with clear separation of concerns:

- **Entry Point**: `main.py` - Bot initialization and handler registration
- **Configuration**: `config.py` - Centralized configuration management with environment variables
- **Commands**: `bot/commands.py` - Command handlers for user interactions
- **Handlers**: `bot/handlers.py` - Message and file upload handlers
- **API Clients**: `bot/api_client.py` - External service integrations
- **Utilities**: `bot/utils.py` - Helper functions and validation logic

## Key Components

### 1. Telegram Bot Framework
- **Technology**: Python Telegram Bot library (`python-telegram-bot`)
- **Purpose**: Provides the core bot functionality and webhook/polling mechanisms
- **Architecture**: Event-driven with command and message handlers

### 2. External API Integrations
- **LucoSMS API**: User management and account operations
- **Catbox API**: File upload and backup services
- **Authentication**: Bearer token-based authentication for APIs

### 3. Configuration Management
- **Environment Variables**: All sensitive data stored in environment variables
- **Validation**: Configuration validation on startup to ensure required variables are present
- **Settings**: Rate limiting, file size limits, and admin user management

### 4. Administrative Features
- **Role-based Access**: Admin-only commands and features
- **User Management**: Check user information and recharge accounts
- **Statistics**: Bot usage tracking and reporting

## Data Flow

### User Information Lookup
1. User sends `/check <user_id>` command
2. Bot validates user ID format
3. Makes API call to LucoSMS service
4. Returns formatted user information or error message

### File Backup Process
1. User uploads file or uses `/backup` command
2. Bot validates file size against configured limits
3. Downloads file from Telegram servers
4. Uploads file to Catbox storage service
5. Returns backup URL to user
6. Cleans up temporary files

### Account Recharge
1. Admin user sends `/recharge <user_id> <amount>` command
2. Bot validates admin permissions
3. Makes API call to LucoSMS for account recharge
4. Returns success/failure status

## External Dependencies

### Required Services
- **Telegram Bot API**: Core bot functionality
- **LucoSMS API**: User management backend
- **Catbox**: File storage and backup service

### Python Libraries
- `python-telegram-bot`: Telegram bot framework
- `aiohttp`: Async HTTP client for API calls
- `aiofiles`: Async file operations
- `python-dotenv`: Environment variable management

### Environment Variables
- `TELEGRAM_BOT_TOKEN`: Bot authentication token
- `LUCOSMS_API_KEY`: API key for LucoSMS service
- `LUCOSMS_API_BASE_URL`: Base URL for LucoSMS API
- `CATBOX_API_URL`: Catbox upload endpoint
- `ADMIN_USER_IDS`: Comma-separated list of admin user IDs
- `MAX_REQUESTS_PER_MINUTE`: Rate limiting configuration
- `MAX_FILE_SIZE_MB`: File upload size limit

## Deployment Strategy

### Architecture Decisions
- **Polling vs Webhooks**: Uses polling for simplicity and easier deployment
- **Async Operations**: Leverages asyncio for non-blocking API calls and file operations
- **Error Handling**: Comprehensive error handling with logging
- **Resource Management**: Automatic cleanup of temporary files

### Configuration
- Environment-based configuration for different deployment environments
- Validation of critical configuration parameters on startup
- Flexible API endpoint configuration

### Monitoring
- Structured logging with different log levels
- Error tracking through Telegram's error handler
- Admin statistics and usage tracking

## Changelog

- June 28, 2025: Initial setup and development completed
- June 28, 2025: Enhanced bot with advanced features deployed:
  - YouTube video/audio downloading with quality selection
  - AI-powered image generation with Gemini
  - Beautiful anime-style menus with inline keyboards
  - Movie discovery from Telegram groups
  - Image to sticker conversion
  - Text sticker creation
  - User lookup with LucoSMS API integration
  - Account recharge functionality for admins
  - File backup using Catbox service
  - Administrative commands and controls

## User Preferences

Preferred communication style: Simple, everyday language.