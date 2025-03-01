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
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    await update.message.reply_text(
        "Hello! I'm your AI assistant powered by CrewAI agents. "
        "Each specialized function is handled by a dedicated agent. "
        "How can I help you today?"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    await update.message.reply_text(
        "Here's how to use this bot:\n\n"
        "- Just send me any message or question\n"
        "- For web searches, try queries like 'search for latest AI news'\n"
        "- Use /start to see the welcome message\n"
        "- Use /help to see this help message\n\n"
        "Each type of request is handled by a specialized agent!"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming messages"""
    user_text = update.message.text
    chat_id = update.message.chat_id
    
    logger.info(f"Received message from {chat_id}: {user_text}")
    
    # Show typing status while processing
    await context.bot.send_chat_action(chat_id=chat_id, action='typing')
    
    try:
        # Process through orchestrator
        result = orchestrator.process_telegram_message(str(chat_id), user_text)
        
        # Send response back
        await update.message.reply_text(result)
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        await update.message.reply_text(
            "I'm sorry, I encountered an error while processing your request. "
            "Please try again or contact support if the issue persists."
        )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors in the dispatcher"""
    logger.error(f"Update {update} caused error {context.error}")

def main():
    """Start the bot"""
    # Create the Application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Register command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # Register message handler
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Register error handler
    application.add_error_handler(error_handler)

    # Start the bot
    logger.info("Bot started, listening for messages...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main() 