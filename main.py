import telegram
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    CallbackContext,
    ContextTypes,
    filters,
    Defaults,
)
import logging
import asyncio
import config
import pytz
from telegram.request import HTTPXRequest

# States for ConversationHandler
CONFIRMATION = 0

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configure HTTPX request with increased pool size and timeout
request = HTTPXRequest(
    connection_pool_size=16,  # Increased pool size
    read_timeout=60.0,       # Increased timeouts
    write_timeout=60.0,
    connect_timeout=60.0,
    pool_timeout=60.0
)

async def start(update: telegram.Update, context: CallbackContext) -> None:
    """Sends a welcome message when the /start command is issued."""
    await update.message.reply_text(
        "👋 Welcome! I'm a Telegram bot that can replicate and restore messages from a channel to a group.\n\n"
        "I can:\n"
        "• Forward new messages from the channel to the group automatically\n"
        "• Restore all existing messages from the channel to the group\n\n"
        "Use /help to see available commands."
    )

async def help_command(update: telegram.Update, context: CallbackContext) -> None:
    """Sends a help message when the /help command is issued."""
    await update.message.reply_text(
        "Available commands:\n\n"
        "/start - Start the bot and see welcome message\n"
        "/help - Show this help message\n"
        "/restore - Start the message restoration process\n"
        "/getids - Get IDs of channels and groups where bot is a member\n"
        "/cancel - Cancel any ongoing operation"
    )

async def getids_command(update: telegram.Update, context: CallbackContext) -> None:
    """Shows IDs and names of all channels and groups where the bot is a member."""
    user_id = update.message.from_user.id
    if user_id not in config.AUTHORIZED_USERS:
        await update.message.reply_text("You don't have permission to use this command.")
        return

    try:
        # Send initial message
        status_message = await update.message.reply_text("🔄 Getting chat information...")
        
        # Get current chat information
        current_chat = update.message.chat
        message = "📋 Chats where the bot is a member:\n\n"
        
        # Add current chat
        message += f"• Current Chat: {current_chat.title or current_chat.username or 'Private Chat'}\n"
        message += f"  ID: {current_chat.id}\n"
        message += f"  Type: {current_chat.type}\n\n"
        
        # Try to get channel info if configured
        if config.CHANNEL_ID:
            try:
                channel = await context.bot.get_chat(config.CHANNEL_ID)
                message += f"• Source Channel: {channel.title}\n"
                message += f"  ID: {channel.id}\n"
                message += f"  Type: {channel.type}\n\n"
            except Exception as e:
                logger.error(f"Error getting channel info: {e}")
                message += f"• Source Channel: Not accessible\n"
                message += f"  ID: {config.CHANNEL_ID}\n\n"
        
        # Try to get group info if configured
        if config.GROUP_ID:
            try:
                group = await context.bot.get_chat(config.GROUP_ID)
                message += f"• Target Group: {group.title}\n"
                message += f"  ID: {group.id}\n"
                message += f"  Type: {group.type}\n\n"
            except Exception as e:
                logger.error(f"Error getting group info: {e}")
                message += f"• Target Group: Not accessible\n"
                message += f"  ID: {config.GROUP_ID}\n\n"
        
        # Update the status message with the results
        await status_message.edit_text(message)

    except Exception as e:
        logger.error(f"Error in getids command: {e}")
        await update.message.reply_text(f"❌ An error occurred while getting chat IDs: {str(e)}")

async def restaurar_command(update: telegram.Update, context: CallbackContext) -> int:
    """Handles the /restore command."""
    user_id = update.message.from_user.id
    if user_id not in config.AUTHORIZED_USERS:
        await update.message.reply_text("You don't have permission to use this command.")
        return ConversationHandler.END

    await update.message.reply_text(
        "⚠️ This will restore ALL messages from the backup channel to the group.\n\n"
        "Type 'RESTORE' to confirm and start the process."
    )
    return CONFIRMATION

async def confirmation_received(update: telegram.Update, context: CallbackContext) -> int:
    """Handles the 'RESTORE' confirmation."""
    if update.message.text == "RESTORE":
        await update.message.reply_text("Starting the restoration process. This may take a while...")
        
        try:
            # First, verify bot permissions
            try:
                channel = await context.bot.get_chat(config.CHANNEL_ID)
                group = await context.bot.get_chat(config.GROUP_ID)
                
                if not channel or not group:
                    await update.message.reply_text("Error: Could not access the channel or group. Please verify the IDs and bot permissions.")
                    return ConversationHandler.END
                
                logger.info(f"Channel title: {channel.title}, Group title: {group.title}")
            except Exception as e:
                await update.message.reply_text(f"Error verifying permissions: {str(e)}")
                return ConversationHandler.END

            # Start from message ID 1 and try to forward messages until we hit an error
            current_message_id = 1
            messages_forwarded = 0
            errors = 0
            max_errors = 5
            
            while errors < max_errors:
                try:
                    await context.bot.forward_message(
                        chat_id=config.GROUP_ID,
                        from_chat_id=config.CHANNEL_ID,
                        message_id=current_message_id
                    )
                    logger.info(f"Restored message {current_message_id}")
                    messages_forwarded += 1
                    errors = 0  # Reset error counter on success
                    current_message_id += 1
                    await asyncio.sleep(1)  # To avoid hitting rate limits
                except telegram.error.BadRequest as e:
                    error_msg = str(e).lower()
                    if "message to forward not found" in error_msg or \
                       "message_id_invalid" in error_msg:
                        logger.info(f"Reached end of messages at ID {current_message_id}")
                        break
                    elif "chat not found" in error_msg:
                        await update.message.reply_text("Error: Could not access the channel or group. Please verify the IDs.")
                        return ConversationHandler.END
                    elif "bot was blocked" in error_msg:
                        await update.message.reply_text("Error: The bot was blocked in the group or channel.")
                        return ConversationHandler.END
                    else:
                        logger.error(f"Error restoring message {current_message_id}: {e}")
                        errors += 1
                        current_message_id += 1
                except Exception as e:
                    logger.error(f"Unexpected error restoring message {current_message_id}: {e}")
                    errors += 1
                    current_message_id += 1
            
            if messages_forwarded > 0:
                await update.message.reply_text(f"✅ Restoration completed. Successfully restored {messages_forwarded} messages.")
            else:
                await update.message.reply_text("❌ No messages could be restored. Please verify bot permissions and channel/group IDs.")

        except Exception as e:
            logger.error(f"Error during restoration: {e}")
            await update.message.reply_text(f"An error occurred during restoration: {str(e)}")
        
        return ConversationHandler.END
    else:
        await update.message.reply_text("Restoration cancelled. You did not type 'RESTORE'.")
        return ConversationHandler.END

async def cancel(update: telegram.Update, context: CallbackContext) -> int:
    """Cancels and ends the conversation."""
    await update.message.reply_text('Operation cancelled.')
    return ConversationHandler.END

async def forward_channel_messages(update: telegram.Update, context: CallbackContext) -> None:
    """Forwards new messages from the channel to the group."""
    logger.info(f"Received update: {update}")
    logger.info(f"Channel post: {update.channel_post}")
    
    if update.channel_post and update.channel_post.chat.id == config.CHANNEL_ID:
        try:
            logger.info(f"Attempting to forward message {update.channel_post.message_id} from channel {config.CHANNEL_ID} to group {config.GROUP_ID}")
            await context.bot.forward_message(
                chat_id=config.GROUP_ID,
                from_chat_id=config.CHANNEL_ID,
                message_id=update.channel_post.message_id
            )
            logger.info(f"Successfully forwarded message {update.channel_post.message_id}")
        except Exception as e:
            logger.error(f"Error forwarding message: {e}")
            logger.error(f"Full error details: {str(e)}")
    else:
        if update.channel_post:
            logger.info(f"Received message from non-target channel: {update.channel_post.chat.id}")

async def main() -> None:
    """Start the bot."""
    # Initialize bot with custom request settings
    application = (
        Application.builder()
        .token(config.TOKEN)
        .request(request)
        .build()
    )

    # Add conversation handler for /restore command
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('restore', restaurar_command)],
        states={
            CONFIRMATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirmation_received)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("getids", getids_command))
    application.add_handler(conv_handler)
    
    # Handler for new channel messages
    application.add_handler(MessageHandler(
        filters.UpdateType.CHANNEL_POST & filters.Chat(chat_id=config.CHANNEL_ID), 
        forward_channel_messages
    ))

    logger.info("Bot starting...")
    await application.initialize()
    await application.start()
    await application.updater.start_polling()

    while True:
        await asyncio.sleep(3600)

if __name__ == '__main__':
    asyncio.run(main()) 