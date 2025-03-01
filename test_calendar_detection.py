#!/usr/bin/env python3
import logging
import os
import sys
from agent_orchestrator import AgentOrchestrator

# First, add the current directory to the path to ensure imports work
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our custom environment loader
from env_loader import load_environment

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("test_calendar_detection")

def setup_environment():
    # Load environment variables using our centralized loader
    logger.info("Setting up test environment")
    if load_environment(debug=True):
        logger.info("Environment variables loaded successfully")
        
        # Log Anthropic API key status (without revealing the key)
        if os.getenv('ANTHROPIC_API_KEY'):
            logger.info("✓ Anthropic API key is set")
        else:
            logger.warning("✗ Anthropic API key is NOT set")
            
        return True
    else:
        logger.error("Failed to load environment variables")
        return False

def test_calendar_detection():
    orchestrator = AgentOrchestrator()
    
    test_queries = [
        # English calendar queries - should be detected
        "What meetings do I have today?",
        "When is my next meeting?",
        "Do I have any appointments tomorrow?",
        "What's on my calendar for Friday?",
        "Check my availability on Monday",
        "Am I busy on March 15?",
        "What events do I have next week?",
        "When is my first meeting on Monday?",
        
        # Czech calendar queries - should be detected
        "Jaké schůzky mám dnes?",
        "Kdy je moje další jednání?",
        "Mám zítra nějaké schůzky?",
        "Co mám v kalendáři na pátek?",
        "Zkontroluj mou dostupnost v pondělí",
        "Jsem zaneprázdněný 15. března?",
        "Jaké události mám příští týden?",
        
        # Non-calendar queries - should NOT be detected
        "What's the weather like today?",
        "Send an email to John",
        "Translate 'hello' to French",
        "Tell me a joke",
        "What time is it?"
    ]
    
    logger.info(f"Testing {len(test_queries)} queries for calendar detection")
    
    for query in test_queries:
        is_calendar = orchestrator._is_calendar_request(query)
        result = "✅ CALENDAR" if is_calendar else "❌ NOT CALENDAR"
        logger.info(f"{result}: {query}")
    
    logger.info("Calendar detection test completed")

if __name__ == "__main__":
    if setup_environment():
        test_calendar_detection()
    else:
        logger.error("Failed to set up test environment") 