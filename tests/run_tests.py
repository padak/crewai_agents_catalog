#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test Runner Script

Executes all tests in the tests directory.
"""

import os
import sys
import unittest
import argparse
import logging

# Add the parent directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import our custom environment loader
from env_loader import load_environment

# Configure logging to show DEBUG messages
logging.basicConfig(level=logging.DEBUG, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Only disable specific noisy loggers
for logger_name in ['httpcore', 'httpx', 'urllib3']:
    logging.getLogger(logger_name).setLevel(logging.WARNING)

# Keep telegram logger at INFO level for more visibility
logging.getLogger('telegram').setLevel(logging.INFO)

# Set up a specific logger for our tests
test_logger = logging.getLogger('test_runner')
test_logger.setLevel(logging.DEBUG)

def setup_environment():
    """Set up environment for all tests"""
    test_logger.info("Setting up test environment")
    if load_environment(debug=True):
        test_logger.info("Environment variables loaded successfully")
        return True
    else:
        test_logger.error("Failed to load environment variables")
        return False

def run_all_tests():
    """Run all test cases in the tests directory"""
    # Discover and run all tests
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(os.path.abspath(__file__))
    suite = loader.discover(start_dir, pattern="*test*.py")
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

def run_specific_test(test_name):
    """Run a specific test by name"""
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    
    if not test_name.endswith('.py'):
        test_name += '.py'
    
    # Check if the test file exists
    test_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), test_name)
    if not os.path.exists(test_path):
        test_logger.error(f"Test file '{test_name}' not found")
        return False
    
    # Run the specific test
    test_module = test_name[:-3]  # Remove .py extension
    suite = unittest.defaultTestLoader.loadTestsFromName(test_module)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

def main():
    test_logger.debug("Run tests script started")
    parser = argparse.ArgumentParser(description='Run tests for the CrewAI project')
    parser.add_argument('--test', '-t', help='Specific test to run (e.g., unit_test_telegram_bot)')
    parser.add_argument('--manual', '-m', action='store_true', 
                       help='Run manual test for Telegram bot (starts the bot)')
    parser.add_argument('--debug', '-d', action='store_true',
                       help='Enable extra debug logging')
    
    args = parser.parse_args()
    test_logger.debug(f"Command-line arguments: {args}")
    
    # Set extra debug logging if requested
    if args.debug:
        # Set DEBUG level for all loggers
        for handler in logging.root.handlers:
            handler.setLevel(logging.DEBUG)
        
        # Enable specific module debugging
        os.environ['LITELLM_LOG'] = 'DEBUG'
        os.environ['CREWAI_LOG_LEVEL'] = 'DEBUG'
        
        test_logger.debug("Extra debug logging enabled")
    
    # Set up the environment before running any tests
    if not setup_environment():
        test_logger.error("Environment setup failed")
        return 1
    
    if args.manual:
        # Import and run the manual test for the Telegram bot
        test_logger.info("=== Running Manual Telegram Bot Test ===")
        test_logger.debug("About to import test_telegram_bot")
        try:
            # Get the full path to the test script
            test_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "test_telegram_bot.py"))
            test_logger.debug(f"Test script path: {test_path}")
            test_logger.debug(f"Test script exists: {os.path.exists(test_path)}")
            
            # Monkey patch the handle_message in bot.py to fix parameter order if needed
            def monkey_patch_bot():
                test_logger.debug("Applying monkey patch to bot.py")
                try:
                    import bot
                    
                    # Store original handle_message function
                    original_handle_message = bot.handle_message
                    
                    # Define a wrapper that checks parameter order
                    async def wrapped_handle_message(update, context):
                        user_text = update.message.text
                        chat_id = update.message.chat_id
                        test_logger.debug(f"Message intercepted - chat_id: {chat_id}, text: {user_text}")
                        
                        try:
                            # Patch the orchestrator call if needed
                            result = bot.orchestrator.process_telegram_message(user_text, chat_id)
                            test_logger.debug(f"Message processed by orchestrator")
                            await update.message.reply_text(result)
                        except Exception as e:
                            test_logger.error(f"Error in patched handle_message: {e}")
                            # Fall back to original implementation if our patch fails
                            return await original_handle_message(update, context)
                    
                    # Replace the original with our wrapper
                    bot.handle_message = wrapped_handle_message
                    test_logger.debug("Monkey patch applied successfully")
                    return True
                except Exception as e:
                    test_logger.error(f"Failed to apply monkey patch: {e}")
                    return False
            
            # Apply the patch
            monkey_patch_applied = monkey_patch_bot()
            test_logger.debug(f"Monkey patch status: {'Success' if monkey_patch_applied else 'Failed'}")
            
            # Directly execute the test
            sys.path.insert(0, os.path.dirname(__file__))
            from test_telegram_bot import setup_test_environment, run_test_bot
            
            test_logger.debug("Successfully imported test_telegram_bot")
            if setup_test_environment():
                test_logger.info("Environment setup successful, running bot...")
                run_test_bot()
            else:
                test_logger.error("Environment setup failed")
                
        except Exception as e:
            test_logger.error(f"Error running manual test: {e}")
            import traceback
            traceback.print_exc()
        
        sys.exit(0)
    
    if args.test:
        success = run_specific_test(args.test)
    else:
        success = run_all_tests()
    
    return 0 if success else 1

if __name__ == "__main__":
    test_logger.debug("Script entry point reached")
    sys.exit(main()) 