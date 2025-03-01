#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Agent Orchestrator - Connects independent specialized agents

This module provides orchestration between separate specialized agents,
following the principle of separation of concerns. Each agent handles
its specific functionality, and the orchestrator routes requests
between them.
"""

import re
import os
from typing import Dict, Optional, Any
import logging
import time
import sys
from pathlib import Path

# Add parent directory to path for module imports if needed
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

# Import the environment loader
from env_loader import load_environment

# Import agent implementations
from telegram_gateway_agent.src.telegram_crew import TelegramCrew
from websearch_agent.src.search_crew import SearchCrew
from time_agent.src.time_crew import TimeCrew
from calendar_agent.src.calendar_crew import CalendarCrew

# Load environment variables
load_environment(debug=True)

# Configure LLM provider based on environment
LLM_PROVIDER = os.getenv("LITELLM_PROVIDER", "openai")

# Default LLM configuration
if LLM_PROVIDER == "anthropic":
    DEFAULT_LLM_CONFIG = {
        "model": f"anthropic/{os.getenv('ANTHROPIC_MODEL', 'claude-3-opus-20240229')}",
        "api_key": os.getenv("ANTHROPIC_API_KEY"),
        "temperature": float(os.getenv("ANTHROPIC_TEMPERATURE", "0.7")),
        "max_tokens": int(os.getenv("ANTHROPIC_MAX_TOKENS", "4000"))
    }
else:
    DEFAULT_LLM_CONFIG = {
        "model": os.getenv("OPENAI_MODEL", "gpt-4o"),
        "api_key": os.getenv("OPENAI_API_KEY"),
        "temperature": float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
    }

class AgentOrchestrator:
    """
    Orchestrates communication between separate specialized agents.
    
    This class follows the Single Responsibility Principle by acting as
    a router between specialized agents rather than implementing any
    agent-specific functionality itself.
    """
    
    def __init__(self):
        """Initialize the agent orchestrator with available agents."""
        # Initialize specialized agents
        self.telegram_crew = TelegramCrew()
        self.search_crew = SearchCrew()
        self.time_crew = TimeCrew()
        
        # Ensure proper environment variables are set for different LLM providers
        if LLM_PROVIDER == "anthropic":
            # Ensure ANTHROPIC_API_KEY is set - this is what CalendarCrew looks for directly
            if not os.getenv("ANTHROPIC_API_KEY") and os.getenv("ANTHROPIC_API_KEY_LIT"):
                # Use the key from LiteLLM if available
                os.environ["ANTHROPIC_API_KEY"] = os.getenv("ANTHROPIC_API_KEY_LIT")
                
        # Initialize the calendar crew last after environment setup
        self.calendar_crew = CalendarCrew()
        
    def _classify_message_intent(self, message: str) -> str:
        """
        Use the LLM to classify the intent of a message.
        
        Args:
            message: The message to classify
            
        Returns:
            str: The classified intent (calendar, search, time, or unknown)
        """
        logger = logging.getLogger(__name__)
        logger.debug(f"Classifying intent for message: '{message}'")
        
        # First try the faster regex-based classification
        if self._is_calendar_request(message):
            logger.debug("Message classified as calendar request using regex patterns")
            return "calendar"
        elif self._is_time_request(message):
            logger.debug("Message classified as time request using regex patterns")
            return "time"
        elif self._is_search_request(message):
            logger.debug("Message classified as search request using regex patterns")
            return "search"
        
        # If regex didn't match, use LLM for more nuanced classification
        try:
            from litellm import completion
            
            # Define the classification prompt
            prompt = f"""You are an AI assistant that classifies user messages into specific categories.
            Please classify the following user message into one of these categories:
            - calendar: For anything related to meetings, appointments, schedules, or calendar events
            - time: For queries about current time, time in a location, or time zones
            - search: For general knowledge questions, web searches, or information retrieval
            - unknown: If it doesn't clearly fit any of the categories above

            User message: "{message}"
            
            Output only one word: either "calendar", "time", "search", or "unknown".
            """
            
            # Select model based on provider
            if LLM_PROVIDER == "anthropic":
                model = f"anthropic/{os.getenv('ANTHROPIC_MODEL', 'claude-3-haiku-20240307')}"
            else:
                model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
            
            # Use a small, fast model for classification
            response = completion(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a message classifier that categorizes messages."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=10,  # Keep it short, we only need one word
                temperature=0.1  # Low temperature for more predictable outputs
            )
            
            # Extract the category from the response
            category = response.choices[0].message.content.strip().lower()
            logger.debug(f"LLM classified message as: {category}")
            
            # Validate the response
            valid_categories = ["calendar", "time", "search", "unknown"]
            if category in valid_categories:
                return category
            else:
                logger.warning(f"LLM returned invalid category: {category}")
                return "unknown"
            
        except Exception as e:
            logger.error(f"Error using LLM for intent classification: {str(e)}")
            # Fall back to default
            return "unknown"

    def process_telegram_message(self, user_message: str, chat_id: int) -> str:
        """
        Process a message from Telegram and route it to the appropriate agent.
        
        Args:
            user_message: The message from the user
            chat_id: The Telegram chat ID
            
        Returns:
            str: The response to send back to the user
        """
        # Log the incoming message
        logger = logging.getLogger(__name__)
        logger.info(f"Processing message: {user_message}")
        
        try:
            # Use LLM-based classification to determine message intent
            intent = self._classify_message_intent(user_message)
            logger.info(f"Message intent classified as: {intent}")
            
            if intent == "calendar":
                # Route to the calendar agent
                return self.perform_calendar_query(user_message)
            elif intent == "time":
                # Route to the time agent
                return self.perform_time_query(user_message)
            elif intent == "search":
                # Route to the search agent
                return self.perform_web_search(user_message)
            else:
                # Default to a simple response for unrecognized commands
                return "I'm not sure how to help with that. You can ask me about your calendar, check the time, or search for information."
        
        except Exception as e:
            # Handle any errors that occur during processing
            error_msg = f"Error processing your request: {str(e)}"
            logger.error(f"ERROR: {error_msg}")
            return error_msg
    
    def _is_search_request(self, message: str) -> bool:
        """
        Determine if a message is requesting a web search.
        
        Args:
            message: The message to analyze
            
        Returns:
            bool: True if the message is a search request, False otherwise
        """
        search_patterns = [
            r"(?i)^search for\s+",
            r"(?i)^search\s+",
            r"(?i)^find information (on|about)\s+",
            r"(?i)^look up\s+",
            r"(?i)^what is\s+",
            r"(?i)^who is\s+",
            r"(?i)^tell me about\s+",
            r"(?i)^find\s+",
            r"(?i)^research\s+"
        ]
        
        return any(re.search(pattern, message) for pattern in search_patterns)
    
    def _is_time_request(self, message: str) -> bool:
        """
        Determine if a message is requesting time information.
        
        Args:
            message: The message to analyze
            
        Returns:
            bool: True if the message is a time request, False otherwise
        """
        time_patterns = [
            r"(?i)what time",
            r"(?i)current time",
            r"(?i)time now",
            r"(?i)time in",
            r"(?i)time zone",
            r"(?i)time difference",
            r"(?i)time of day"
        ]
        
        return any(re.search(pattern, message) for pattern in time_patterns)
    
    def _is_calendar_request(self, text: str) -> bool:
        """
        Check if the message is related to calendar/meetings.
        
        Args:
            text: The message text to check
            
        Returns:
            bool: True if the message is related to calendar/meetings, False otherwise
        """
        logger = logging.getLogger(__name__)
        logger.debug(f"Checking if message is a calendar request: '{text}'")
        
        # English calendar patterns
        calendar_patterns_en = [
            r"(?i)\bcalendar\b",
            r"(?i)\bmeeting\b",
            r"(?i)\bappointment\b",
            r"(?i)\bschedule\b",
            r"(?i)\bevent\b",
            r"(?i)\bavailab\w+\b",
            r"(?i)\bbook\s+a\b",
            r"(?i)\bbusy\b",
            r"(?i)what.*meeting",
            r"(?i)do I have.*tomorrow",
        ]
        
        # Czech calendar patterns
        calendar_patterns_cs = [
            r"(?i)\bkalendář\b",
            r"(?i)\bjednání\b",
            r"(?i)\bschůzk\w+\b",  # Updated to match schůzky, schůzka, etc.
            r"(?i)\bdostupn\w+\b",
            r"(?i)\bzaneprázdněn\w+\b",
            r"(?i)\bpátek\b",
            r"(?i)\bpondělí\b",
            r"(?i)\búterý\b",
            r"(?i)\bstředa\b",
            r"(?i)\bčtvrtek\b",
            r"(?i)\bsobota\b",
            r"(?i)\bneděle\b",
            r"(?i)\budálost\w+\b",  # Updated to match události, událost, etc.
            r"(?i)\bmám\s+.*(schůzk|jednání|událost)",  # Added pattern for "mám ... schůzky"
            r"(?i)\bzítra\b",  # Added zítra (tomorrow)
            r"(?i)\bdnes\b",   # Added dnes (today)
            r"(?i)\bpříští\s+týden\b",  # Added příští týden (next week)
        ]
        
        # Date-related patterns that might indicate calendar requests
        date_patterns = [
            r"(?i)\btoday\b",
            r"(?i)\btomorrow\b",
            r"(?i)\bnext\s+week\b",
            r"(?i)\blast\s+week\b",
            r"(?i)\bnext\s+month\b",
            r"(?i)\blast\s+month\b",
            r"(?i)\b\d{1,2}\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\b",
            r"(?i)\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2}\b",
            r"(?i)\b\d{1,2}/\d{1,2}(/\d{2,4})?\b",
            r"(?i)\b\d{4}-\d{2}-\d{2}\b",
        ]
        
        # Check calendar patterns first
        for pattern in calendar_patterns_en + calendar_patterns_cs:
            if re.search(pattern, text):
                logger.debug(f"Calendar pattern matched: {pattern}")
                return True
        
        # Then check date patterns
        for pattern in date_patterns:
            if re.search(pattern, text):
                logger.debug(f"Date pattern matched: {pattern}")
                return True
        
        logger.debug("No calendar or date patterns matched")
        return False
    
    def perform_web_search(self, query: str) -> str:
        """
        Perform a web search using the search agent.
        
        Args:
            query: The search query
            
        Returns:
            str: The search results
        """
        logger = logging.getLogger(__name__)
        logger.info(f"Performing web search for: '{query}'")
        
        try:
            # Check if search_crew has the expected method
            if hasattr(self.search_crew, 'process_message'):
                logger.debug("Using process_message method of SearchCrew")
                return self.search_crew.process_message(query)
            elif hasattr(self.search_crew, 'search'):
                logger.debug("Using search method of SearchCrew")
                return self.search_crew.search(query)
            else:
                logger.error("SearchCrew doesn't have process_message or search methods")
                return f"I'm sorry, the search functionality is currently unavailable. Please try again later."
        except Exception as e:
            logger.error(f"Error performing web search: {str(e)}")
            return f"I encountered an error while searching for information: {str(e)}"
    
    def perform_time_query(self, query: str) -> str:
        """
        Perform a time query using the time agent.
        
        Args:
            query: The time query
            
        Returns:
            str: The time information
        """
        return self.time_crew.process_message(query)
    
    def perform_calendar_query(self, query: str) -> str:
        """
        Process a calendar-related query using the calendar agent.
        
        Args:
            query: The calendar query to process
            
        Returns:
            str: The response from the calendar agent, or an error message if processing fails
        """
        logger = logging.getLogger(__name__)
        logger.info(f"Processing calendar query: '{query}'")
        
        try:
            # Check if calendar crew is available
            if not hasattr(self, 'calendar_crew') or self.calendar_crew is None:
                logger.error("Calendar crew not initialized")
                # Try to initialize calendar agent
                try:
                    logger.debug("Attempting to initialize calendar crew")
                    self._setup_calendar_agent()
                    if not hasattr(self, 'calendar_crew') or self.calendar_crew is None:
                        return "The Calendar Assistant is not available. Please check your configuration and try again."
                except Exception as e:
                    logger.error(f"Failed to initialize calendar crew: {str(e)}")
                    return f"Unable to set up Calendar Assistant: {str(e)}"
            
            # Process the query with the calendar agent
            logger.debug(f"Sending query to calendar agent: {query}")
            start_time = time.time()
            response = self.calendar_crew.process_message(query)
            elapsed_time = time.time() - start_time
            logger.debug(f"Calendar query processed in {elapsed_time:.2f} seconds")
            
            # Log response summary (truncated if too long)
            if response:
                log_response = response[:100] + "..." if len(response) > 100 else response
                logger.debug(f"Calendar response: {log_response}")
            
            return response or "I couldn't get information from your calendar. Please try again later."
            
        except Exception as e:
            logger.exception(f"Error processing calendar query: {str(e)}")
            return f"I encountered an error while processing your calendar query: {str(e)}"

    def _setup_calendar_agent(self):
        """
        Initialize the calendar agent if not already initialized.
        
        This method is called when a calendar query is detected but the calendar agent
        is not yet initialized.
        """
        logger = logging.getLogger(__name__)
        logger.info("Setting up calendar agent")
        
        # Check if credentials are available
        # First check environment variables for paths
        token_path = os.getenv('GOOGLE_TOKEN_PATH')
        credentials_path = os.getenv('GOOGLE_CREDENTIALS_PATH')
        
        # If not set in environment, use default paths
        if not token_path:
            token_path = os.path.join(os.getcwd(), 'token.json')
            logger.debug(f"Using default token path: {token_path}")
        else:
            logger.debug(f"Using token path from environment: {token_path}")
            
        if not credentials_path:
            credentials_path = os.path.join(os.getcwd(), 'credentials.json')
            logger.debug(f"Using default credentials path: {credentials_path}")
        else:
            logger.debug(f"Using credentials path from environment: {credentials_path}")
        
        if not os.path.exists(token_path):
            logger.error(f"Token file not found at: {token_path}")
            raise FileNotFoundError(f"Could not find token.json file at {token_path}")
            
        if not os.path.exists(credentials_path):
            logger.error(f"Credentials file not found at: {credentials_path}")
            raise FileNotFoundError(f"Could not find credentials.json file at {credentials_path}")
        
        logger.debug("Calendar credentials found, initializing calendar crew")
        
        # Import here to avoid circular imports
        from agents.calendar_agent import CalendarCrew
        
        # Check if required environment variables are set
        anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        if not anthropic_api_key:
            logger.error("ANTHROPIC_API_KEY environment variable not set")
            raise ValueError("ANTHROPIC_API_KEY environment variable is required for calendar agent")
        
        try:
            # Create the calendar crew
            self.calendar_crew = CalendarCrew()
            logger.info("Calendar crew initialized successfully")
        except Exception as e:
            logger.exception(f"Failed to create calendar crew: {str(e)}")
            raise Exception(f"Failed to initialize calendar agent: {str(e)}")

    # Additional orchestration methods can be added here as more agents are developed
    
# Example usage (commented out)
# if __name__ == "__main__":
#     orchestrator = AgentOrchestrator()
#     search_result = orchestrator.perform_web_search("What is the current weather in New York?")
#     print(search_result) 