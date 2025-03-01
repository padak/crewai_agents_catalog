#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Telegram Bot Entry Point

This script sets up a Telegram bot that listens for messages and routes them
through the agent orchestrator to the appropriate specialized agents.
"""

import os
import logging
from typing import Dict, Any
from dotenv import load_dotenv
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# Import the agent orchestrator
from agent_orchestrator import AgentOrchestrator

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load environment variables from the root .env file
load_dotenv()

# Get Telegram bot token from environment
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN not found in environment variables!")

# Initialize orchestrator
orchestrator = AgentOrchestrator()

def start(update, context):
    """Handle /start command"""
    update.message.reply_text(
        "Hello! I'm your AI assistant powered by CrewAI agents. "
        "Each specialized function is handled by a dedicated agent. "
        "How can I help you today?"
    )

def help_command(update, context):
    """Handle /help command"""
    update.message.reply_text(
        "Here's how to use this bot:\n\n"
        "- Just send me any message or question\n"
        "- For web searches, try queries like 'search for latest AI news'\n"
        "- Use /start to see the welcome message\n"
        "- Use /help to see this help message\n\n"
        "Each type of request is handled by a specialized agent!"
    )

def handle_message(update, context):
    """Handle incoming messages"""
    user_text = update.message.text
    chat_id = update.message.chat_id
    
    logger.info(f"Received message from {chat_id}: {user_text}")
    
    # Show typing status while processing
    context.bot.send_chat_action(chat_id=chat_id, action='typing')
    
    try:
        # Process through orchestrator
        result = orchestrator.process_telegram_message(str(chat_id), user_text)
        
        # Send response back
        update.message.reply_text(result)
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        update.message.reply_text(
            "I'm sorry, I encountered an error while processing your request. "
            "Please try again or contact support if the issue persists."
        )

def main():
    """Start the bot"""
    # Create the Updater and pass it your bot's token
    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Register commands
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))

    # Register message handler
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    # Start the bot
    updater.start_polling()
    logger.info("Bot started, listening for messages...")
    
    # Run the bot until you press Ctrl-C
    updater.idle()

if __name__ == '__main__':
    main() 