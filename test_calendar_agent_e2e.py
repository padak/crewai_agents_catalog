#!/usr/bin/env python
"""
End-to-end test for the Calendar Agent integration.

This script tests:
1. Calendar query detection
2. Calendar agent initialization
3. Calendar agent responses

Usage:
    ./test_calendar_agent_e2e.py [--debug]
"""

import os
import sys
import argparse
import logging
from datetime import datetime

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our custom environment loader
from env_loader import load_environment

# Setup logging
def setup_logging(debug=False):
    """Configure logging for the test script."""
    level = logging.DEBUG if debug else logging.INFO
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Setup console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    
    # Setup file handler
    file_handler = logging.FileHandler(f'calendar_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    
    # Set specific loggers
    logging.getLogger('calendar_test').setLevel(level)
    logging.getLogger('agent_orchestrator').setLevel(level)
    
    # Set other noisy loggers to WARNING
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('httpcore').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    
    return logging.getLogger('calendar_test')

def setup_environment():
    """Set up test environment and load environment variables."""
    logger = logging.getLogger('calendar_test')
    logger.info("Setting up test environment")
    
    # Load environment variables using our centralized loader
    if not load_environment(debug=True):
        logger.error("Failed to load environment variables")
        return False
        
    logger.info("Environment variables loaded successfully")
    
    # Check required environment variables for Calendar Agent
    required_vars = [
        'ANTHROPIC_API_KEY',
    ]
    
    # Optional Telegram-related variables
    optional_vars = [
        'OPENAI_API_KEY',
        'TELEGRAM_BOT_TOKEN',
        'TELEGRAM_CHAT_ID'
    ]
    
    # Check required vars
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        return False
        
    # Check optional vars
    missing_optional = [var for var in optional_vars if not os.getenv(var)]
    if missing_optional:
        logger.warning(f"Missing optional environment variables: {', '.join(missing_optional)}")
        logger.warning("Some features may be limited, but calendar testing can continue")
    
    # Check for calendar credentials in multiple possible locations
    possible_locations = [
        os.getcwd(),                          # Current directory
        os.path.join(os.getcwd(), 'config'),  # config subdirectory
        os.path.join(os.getcwd(), 'credentials'), # credentials subdirectory
        os.path.expanduser('~'),              # User's home directory
        os.path.join(os.getcwd(), 'tests')    # tests subdirectory
    ]
    
    token_found = False
    credentials_found = False
    token_path = None
    credentials_path = None
    
    for location in possible_locations:
        # Check for token.json
        token_file = os.path.join(location, 'token.json')
        if os.path.exists(token_file):
            token_found = True
            token_path = token_file
            logger.info(f"Found token.json at: {token_file}")
            
        # Check for credentials.json
        creds_file = os.path.join(location, 'credentials.json')
        if os.path.exists(creds_file):
            credentials_found = True
            credentials_path = creds_file
            logger.info(f"Found credentials.json at: {creds_file}")
            
        # If both found, break
        if token_found and credentials_found:
            break
    
    if not token_found:
        logger.error("Calendar token file (token.json) not found in any of the checked locations")
        return False
    
    if not credentials_found:
        logger.error("Calendar credentials file (credentials.json) not found in any of the checked locations")
        return False
    
    # Set environment variables for the found paths
    os.environ['GOOGLE_TOKEN_PATH'] = token_path
    os.environ['GOOGLE_CREDENTIALS_PATH'] = credentials_path
    
    logger.info("✓ Environment setup completed successfully")
    return True

def test_calendar_detection():
    """Test the calendar query detection function."""
    logger = logging.getLogger('calendar_test')
    logger.info("Testing calendar query detection")
    
    try:
        # Import agent orchestrator
        from agent_orchestrator import AgentOrchestrator
        
        # Create agent orchestrator
        orchestrator = AgentOrchestrator()
        
        # Test queries
        test_queries = [
            # English calendar queries (should be detected)
            "What meetings do I have today?",
            "When is my next meeting?",
            "Do I have any appointments tomorrow?",
            "What's on my calendar for Friday?",
            "Check my availability on Monday",
            
            # Czech calendar queries (should be detected)
            "Jaké schůzky mám dnes?",
            "Kdy je moje další jednání?",
            "Mám zítra nějaké schůzky?",
            "Co mám v kalendáři na pátek?",
            
            # Non-calendar queries (should not be detected)
            "What's the weather like in Prague?",
            "Tell me a joke",
            "What time is it?",
        ]
        
        results = {
            'detected': [],
            'not_detected': []
        }
        
        for query in test_queries:
            is_calendar = orchestrator._is_calendar_request(query)
            
            if is_calendar:
                results['detected'].append(query)
                logger.info(f"✓ Detected as calendar query: '{query}'")
            else:
                results['not_detected'].append(query)
                logger.info(f"✗ Not detected as calendar query: '{query}'")
        
        return results
        
    except Exception as e:
        logger.exception(f"Error testing calendar detection: {str(e)}")
        return None

def test_calendar_agent_responses():
    """Test actual calendar agent responses for various queries."""
    logger = logging.getLogger('calendar_test')
    logger.info("Testing calendar agent responses")
    
    try:
        # Import agent orchestrator
        from agent_orchestrator import AgentOrchestrator
        
        # Create agent orchestrator
        orchestrator = AgentOrchestrator()
        
        # Test calendar queries
        test_queries = [
            "What meetings do I have today?",
            "What meetings do I have tomorrow?",
            "What's on my calendar for next week?",
            "Am I available on Friday at 2pm?",
            "When is my next meeting?"
        ]
        
        results = {}
        
        for query in test_queries:
            logger.info(f"Testing query: '{query}'")
            
            try:
                # Time the response
                import time
                start_time = time.time()
                
                # Get response
                response = orchestrator.perform_calendar_query(query)
                
                # Calculate elapsed time
                elapsed_time = time.time() - start_time
                
                # Save response
                results[query] = {
                    'success': True,
                    'response': response,
                    'time': elapsed_time
                }
                
                # Format the response for logging (truncate if too long)
                log_response = response[:100] + "..." if len(response) > 100 else response
                logger.info(f"✓ Got response in {elapsed_time:.2f}s: '{log_response}'")
                
            except Exception as e:
                results[query] = {
                    'success': False,
                    'error': str(e)
                }
                logger.error(f"✗ Error processing query: '{query}' - {str(e)}")
        
        return results
        
    except Exception as e:
        logger.exception(f"Error testing calendar agent responses: {str(e)}")
        return None

def main():
    """Run the calendar agent end-to-end tests."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Test the Calendar Agent integration')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    args = parser.parse_args()
    
    # Setup logging
    logger = setup_logging(debug=args.debug)
    logger.info("Starting Calendar Agent E2E Test")
    
    # Setup environment
    if not setup_environment():
        logger.error("Environment setup failed, exiting")
        sys.exit(1)
    
    # Test calendar detection
    logger.info("=== Testing Calendar Query Detection ===")
    detection_results = test_calendar_detection()
    
    if detection_results:
        logger.info(f"Detection results: {len(detection_results['detected'])} detected, "
                   f"{len(detection_results['not_detected'])} not detected")
    else:
        logger.error("Calendar detection test failed")
    
    # Test calendar agent responses
    logger.info("=== Testing Calendar Agent Responses ===")
    response_results = test_calendar_agent_responses()
    
    if response_results:
        success_count = sum(1 for r in response_results.values() if r.get('success', False))
        logger.info(f"Response results: {success_count}/{len(response_results)} successful")
    else:
        logger.error("Calendar response test failed")
    
    logger.info("Calendar Agent E2E Test completed")

if __name__ == "__main__":
    main() 