#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test script for LLM-based query classification.

This script tests the new LLM-based intent classification in AgentOrchestrator
with various query types, especially focusing on edge cases.
"""

import os
import sys
import logging
from pathlib import Path

# Add the current directory to the path to ensure imports work
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

logger = logging.getLogger("test_llm_classification")

def setup_environment():
    """Set up the test environment"""
    logger.info("Setting up test environment")
    if load_environment(debug=True):
        logger.info("Environment variables loaded successfully")
        
        # Log API key status (without revealing the key)
        if os.getenv('ANTHROPIC_API_KEY'):
            logger.info("✓ Anthropic API key is set")
        else:
            logger.warning("✗ Anthropic API key is NOT set")
            
        return True
    else:
        logger.error("Failed to load environment variables")
        return False

def test_llm_classification():
    """Test the LLM-based query classification"""
    from agent_orchestrator import AgentOrchestrator
    
    # Create orchestrator
    logger.info("Creating AgentOrchestrator instance")
    orchestrator = AgentOrchestrator()
    
    # Define test queries
    test_queries = [
        # Calendar queries - should classify as "calendar"
        "What meetings do I have today?",
        "When is my next meeting?",
        "Do I have any appointments tomorrow?",
        "What's on my calendar for Friday?",
        "What is my first meeting on next Monday?",  # Problematic query
        "When is my next call with Sarah?",
        "Am I free this afternoon?",
        "Schedule a meeting with John tomorrow at 2 PM",
        "Move my 3 PM meeting to 4 PM",
        
        # Time queries - should classify as "time"
        "What time is it?",
        "What's the current time in Tokyo?",
        "What's the time difference between New York and London?",
        "Tell me the time in Paris",
        
        # Search queries - should classify as "search"
        "What is the weather in Prague now?",  # Problematic query
        "Who is the president of France?",
        "What's the population of Canada?",
        "Search for good restaurants near me",
        "Find information about electric cars",
        "What's the latest news about SpaceX?",
        
        # Ambiguous or other queries - classification may vary
        "Tell me a joke",
        "Translate hello to Spanish",
        "What's the meaning of life?",
        "How are you today?"
    ]
    
    logger.info(f"Testing {len(test_queries)} queries for LLM-based classification")
    
    results = {
        "calendar": [],
        "time": [],
        "search": [],
        "unknown": []
    }
    
    for query in test_queries:
        # Test both classification methods
        llm_result = orchestrator._classify_message_intent(query)
        regex_result = None
        
        if orchestrator._is_calendar_request(query):
            regex_result = "calendar"
        elif orchestrator._is_time_request(query):
            regex_result = "time"
        elif orchestrator._is_search_request(query):
            regex_result = "search"
        else:
            regex_result = "unknown"
        
        # Add to results
        results[llm_result].append(query)
        
        # Log result
        if llm_result == regex_result:
            agreement = "✅ AGREE"
        else:
            agreement = f"❌ DISAGREE (regex: {regex_result})"
            
        logger.info(f"Query: '{query}' → LLM: {llm_result} {agreement}")
    
    # Print summary
    logger.info("\n=== Classification Summary ===")
    logger.info(f"Calendar queries: {len(results['calendar'])}")
    logger.info(f"Time queries: {len(results['time'])}")
    logger.info(f"Search queries: {len(results['search'])}")
    logger.info(f"Unknown queries: {len(results['unknown'])}")
    
    return results

if __name__ == "__main__":
    if setup_environment():
        test_llm_classification()
    else:
        logger.error("Failed to set up test environment")
        sys.exit(1) 