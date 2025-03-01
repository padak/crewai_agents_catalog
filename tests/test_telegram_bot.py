#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test Script for Telegram Bot

This script sets up a test environment for the Telegram bot.
It loads test credentials and runs the bot in test mode.
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG  # Use DEBUG level for more verbose output during testing
)
logger = logging.getLogger(__name__)

def setup_test_environment():
    """Setup test environment with test credentials"""
    # Try to load test environment variables
    if os.path.exists('.env.test'):
        load_dotenv('.env.test')
        logger.info("Loaded test environment from .env.test")
    else:
        load_dotenv()
        logger.warning("No .env.test found, using regular .env file")
    
    # Verify required environment variables
    required_vars = ['TELEGRAM_BOT_TOKEN']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.error("Please create a .env.test file with these variables")
        return False
    
    logger.info("Test environment setup complete")
    return True

def run_test_bot():
    """Import and run the bot in test mode"""
    try:
        # Add the project root to the path if needed
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
        
        # Import the bot module
        import bot
        
        logger.info("Starting Telegram bot in test mode...")
        bot.main()
        
    except Exception as e:
        logger.error(f"Error running test bot: {e}")
        return False
    
    return True

if __name__ == "__main__":
    logger.info("=== TELEGRAM BOT TEST MODE ===")
    
    if setup_test_environment():
        run_test_bot()
    else:
        logger.error("Failed to setup test environment. Exiting.")
        sys.exit(1) 