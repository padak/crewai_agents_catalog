#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Direct Test Script for Calendar Agent

This script tests the Calendar Agent directly without going through the Telegram interface.
It helps isolate and debug issues with the Calendar Agent integration.
"""

import os
import sys
import logging
import traceback
from pathlib import Path

# Add parent directory to path for module imports
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

# Import our custom environment loader
from env_loader import load_environment

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)

def setup_environment():
    """Set up the environment for testing the Calendar Agent"""
    logger.info("Setting up test environment for Calendar Agent...")
    
    # Load environment variables
    if not load_environment(debug=True):
        logger.error("Failed to load environment variables")
        return False
    
    # Set debug flags
    os.environ['LITELLM_LOG'] = 'DEBUG'
    os.environ['CREWAI_LOG_LEVEL'] = 'DEBUG'
    
    # Log provider information
    provider = os.getenv('LITELLM_PROVIDER', 'openai').lower()
    logger.info(f"LLM Provider: {provider.upper()}")
    
    # Log API key status
    if provider == 'anthropic':
        anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        if anthropic_key:
            logger.info("✓ Anthropic API key is set")
            # Log part of the key for debugging (safely)
            key_start = anthropic_key[:10]
            logger.debug(f"API key starts with: {key_start}...")
            
            # Log model information
            model = os.getenv('ANTHROPIC_MODEL', 'claude-3-opus-20240229')
            logger.info(f"Using Anthropic model: {model}")
        else:
            logger.error("✗ Anthropic API key is NOT set")
            return False
    else:
        openai_key = os.getenv('OPENAI_API_KEY')
        if openai_key:
            logger.info("✓ OpenAI API key is set")
            # Log model information
            model = os.getenv('OPENAI_MODEL', 'gpt-4o')
            logger.info(f"Using OpenAI model: {model}")
        else:
            logger.error("✗ OpenAI API key is NOT set")
            return False
    
    # Check for crew_config.yaml
    config_path = Path('crew_config.yaml')
    if config_path.exists():
        logger.info(f"✓ Found crew_config.yaml: {config_path}")
    else:
        logger.warning("No crew_config.yaml found")
    
    # Check Google Calendar credentials
    token_path = Path('calendar_agent/token.json')
    creds_path = Path('calendar_agent/credentials.json')
    
    if token_path.exists():
        logger.info(f"✓ Found token.json: {token_path}")
    else:
        logger.warning(f"No token.json found at {token_path}")
    
    if creds_path.exists():
        logger.info(f"✓ Found credentials.json: {creds_path}")
    else:
        logger.warning(f"No credentials.json found at {creds_path}")
        
    # Check environment variables for Google Calendar
    google_creds = all([
        os.getenv('GOOGLE_CALENDAR_CLIENT_ID'),
        os.getenv('GOOGLE_CALENDAR_CLIENT_SECRET'),
        os.getenv('GOOGLE_CALENDAR_PROJECT_ID')
    ])
    
    if google_creds:
        logger.info("✓ Google Calendar API environment variables are set")
    else:
        logger.warning("Google Calendar API environment variables are incomplete")
    
    return True

def test_calendar_agent_directly():
    """Test the Calendar Agent directly"""
    try:
        logger.info("Importing Calendar Agent...")
        from calendar_agent.src.calendar_crew import CalendarCrew
        
        logger.info("Creating Calendar Crew instance...")
        calendar_crew = CalendarCrew()
        
        # Test the agent with a simple query
        test_query = "What meetings do I have today?"
        logger.info(f"Testing Calendar Agent with query: '{test_query}'")
        
        try:
            # Try processing the query
            response = calendar_crew.process_message(test_query)
            logger.info(f"Response: {response}")
            return True
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            traceback.print_exc()
            return False
            
    except Exception as e:
        logger.error(f"Error importing or initializing Calendar Agent: {e}")
        traceback.print_exc()
        return False

def test_calendar_agent_via_orchestrator():
    """Test the Calendar Agent through the orchestrator"""
    try:
        logger.info("Importing Agent Orchestrator...")
        from agent_orchestrator import AgentOrchestrator
        
        logger.info("Creating Agent Orchestrator instance...")
        orchestrator = AgentOrchestrator()
        
        # Test with a calendar query
        test_query = "What meetings do I have today?"
        logger.info(f"Testing query via orchestrator: '{test_query}'")
        
        # Check if the query is detected as a calendar request
        is_calendar = orchestrator._is_calendar_request(test_query)
        logger.info(f"Detected as calendar query: {is_calendar}")
        
        if is_calendar:
            try:
                # Try processing via the calendar-specific method
                logger.info("Processing via perform_calendar_query...")
                response = orchestrator.perform_calendar_query(test_query)
                logger.info(f"Calendar response: {response}")
            except Exception as e:
                logger.error(f"Error in perform_calendar_query: {e}")
                traceback.print_exc()
        
        # Process through the main interface regardless
        try:
            logger.info("Processing via process_telegram_message...")
            # Using a dummy chat_id
            dummy_chat_id = "12345"
            response = orchestrator.process_telegram_message(test_query, int(dummy_chat_id))
            logger.info(f"Orchestrator response: {response}")
            return True
        except Exception as e:
            logger.error(f"Error in process_telegram_message: {e}")
            traceback.print_exc()
            return False
            
    except Exception as e:
        logger.error(f"Error importing or initializing Agent Orchestrator: {e}")
        traceback.print_exc()
        return False

def run_tests():
    """Run all tests for the Calendar Agent"""
    if not setup_environment():
        logger.error("Environment setup failed")
        return False
    
    # First test the Calendar Agent directly
    logger.info("\n=== Testing Calendar Agent Directly ===\n")
    direct_test_result = test_calendar_agent_directly()
    
    if direct_test_result:
        logger.info("✓ Direct Calendar Agent test succeeded")
    else:
        logger.error("✗ Direct Calendar Agent test failed")
    
    # Then test via the orchestrator
    logger.info("\n=== Testing Calendar Agent via Orchestrator ===\n")
    orchestrator_test_result = test_calendar_agent_via_orchestrator()
    
    if orchestrator_test_result:
        logger.info("✓ Orchestrator Calendar Agent test succeeded")
    else:
        logger.error("✗ Orchestrator Calendar Agent test failed")
    
    return direct_test_result and orchestrator_test_result

if __name__ == "__main__":
    logger.info("=== CALENDAR AGENT DIRECT TEST ===")
    success = run_tests()
    sys.exit(0 if success else 1) 