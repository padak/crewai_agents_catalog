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

# Add the parent directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import our custom environment loader
from env_loader import load_environment

# Configure logging with more detailed format
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG  # Changed to DEBUG to capture all information
)
logger = logging.getLogger(__name__)

# Set up specific loggers for key components
calendar_logger = logging.getLogger('calendar_agent')
calendar_logger.setLevel(logging.DEBUG)

orchestrator_logger = logging.getLogger('agent_orchestrator')
orchestrator_logger.setLevel(logging.DEBUG)

telegram_logger = logging.getLogger('telegram_bot')
telegram_logger.setLevel(logging.DEBUG)

def setup_test_environment():
    """Setup test environment with test credentials"""
    logger.info("Setting up test environment...")
    
    # Try to load test environment variables
    if not load_environment(debug=True):
        logger.error("Failed to load environment variables")
        return False
    
    # Set TEST_MODE environment variable
    os.environ['TEST_MODE'] = 'True'
    logger.info("Set TEST_MODE=True in environment")
    
    # Enable detailed debugging for LiteLLM and CrewAI
    os.environ['LITELLM_LOG'] = 'DEBUG'
    os.environ['CREWAI_LOG_LEVEL'] = 'DEBUG'
    logger.info("Enabled detailed debugging for LiteLLM and CrewAI")
    
    # Log key environment variables for debugging (redacting sensitive info)
    logger.debug(f"LITELLM_PROVIDER: {os.getenv('LITELLM_PROVIDER')}")
    
    if os.getenv('ANTHROPIC_API_KEY'):
        logger.info("✓ Anthropic API key is set")
        # Log the model being used
        logger.debug(f"ANTHROPIC_MODEL: {os.getenv('ANTHROPIC_MODEL', 'Not set')}")
    
    if os.getenv('OPENAI_API_KEY'):
        logger.info("✓ OpenAI API key is set")
        # Log the model being used
        logger.debug(f"OPENAI_MODEL: {os.getenv('OPENAI_MODEL', 'Not set')}")
    
    # Verify required environment variables
    required_vars = ['TELEGRAM_BOT_TOKEN']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    # Check for admin chat ID
    if not os.getenv('ADMIN_CHAT_ID'):
        logger.warning("ADMIN_CHAT_ID not set in environment variables. Welcome message will not be sent.")
        logger.warning("Add your Telegram chat ID to .env.test or .env file as ADMIN_CHAT_ID=your_chat_id")
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.error("Please create a .env.test file with these variables")
        return False
    
    # Verify Calendar API credentials
    google_creds_exist = os.path.exists('calendar_agent/credentials.json')
    google_token_exists = os.path.exists('calendar_agent/token.json')
    google_env_vars = os.getenv('GOOGLE_CALENDAR_CLIENT_ID') and os.getenv('GOOGLE_CALENDAR_CLIENT_SECRET')
    
    if not (google_creds_exist or google_token_exists or google_env_vars):
        logger.warning("No Google Calendar credentials found. Calendar Agent may not function properly.")
    else:
        if google_creds_exist:
            logger.info("✓ Google Calendar credentials.json found")
        if google_token_exists:
            logger.info("✓ Google Calendar token.json found")
        if google_env_vars:
            logger.info("✓ Google Calendar API credentials found in environment variables")
    
    logger.info("Test environment setup complete")
    return True

def inject_test_message(bot_instance, message_text, chat_id=None):
    """
    Inject a test message directly to the agent orchestrator.
    This bypasses the Telegram interface for direct testing.
    """
    try:
        # Default to admin chat ID if none provided
        if not chat_id:
            chat_id = os.getenv('ADMIN_CHAT_ID')
            if not chat_id:
                logger.error("No chat_id provided and ADMIN_CHAT_ID not set")
                return False
        
        # Import orchestrator
        from agent_orchestrator import AgentOrchestrator
        orchestrator = AgentOrchestrator()
        
        logger.info(f"Injecting test message: '{message_text}'")
        
        # Process the message directly through orchestrator
        try:
            # Check if this is a calendar query first
            is_calendar = orchestrator._is_calendar_request(message_text)
            logger.debug(f"Message detected as calendar query: {is_calendar}")
            
            # Process the message
            response = orchestrator.process_telegram_message(message_text, chat_id)
            logger.info(f"Orchestrator response: {response}")
            return True
        except Exception as e:
            logger.error(f"Error processing message through orchestrator: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    except Exception as e:
        logger.error(f"Error injecting test message: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_test_bot():
    """Import and run the bot in test mode"""
    try:
        # Add the project root to the path if needed
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
        
        # First try direct testing of calendar queries if requested
        if os.getenv('TEST_CALENDAR_QUERY'):
            logger.info("Testing Calendar Agent directly...")
            test_query = os.getenv('TEST_CALENDAR_QUERY')
            inject_test_message(None, test_query)
            return True
        
        # Import the bot module
        import bot
        
        logger.info("Starting Telegram bot in test mode...")
        bot.main()
        
    except Exception as e:
        logger.error(f"Error running test bot: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    logger.info("=== TELEGRAM BOT TEST MODE ===")
    
    if setup_test_environment():
        run_test_bot()
    else:
        logger.error("Failed to setup test environment. Exiting.")
        sys.exit(1) 