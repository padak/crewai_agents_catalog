#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Agent Orchestrator - Connects independent specialized agents

This module provides orchestration between separate specialized agents,
following the principle of separation of concerns. Each agent handles
its specific functionality, and the orchestrator routes requests
between them.
"""

import os
import re
from typing import Dict, Optional
from dotenv import load_dotenv

# Import agent implementations
from telegram_gateway_agent.src.telegram_crew import TelegramCrew
from websearch_agent.src.search_crew import SearchCrew

# Load environment variables from the root .env file
load_dotenv()

class AgentOrchestrator:
    """
    Orchestrates communication between separate specialized agents.
    
    This class follows the Single Responsibility Principle by acting as
    a router between specialized agents rather than implementing any
    agent-specific functionality itself.
    """
    
    def __init__(self):
        """Initialize the agent orchestrator with available agents."""
        # Initialize available agents
        self.telegram_agent = TelegramCrew()
        self.search_agent = SearchCrew()
        
    def process_telegram_message(self, chat_id: str, user_message: str) -> str:
        """
        Process a message from Telegram and route to appropriate specialized agents if needed.
        
        Args:
            chat_id: The Telegram chat ID for tracking conversation history
            user_message: The message from the user
            
        Returns:
            The response to send back to the user
        """
        # Check if this is a search request
        if self._is_search_request(user_message):
            # Extract the search query
            search_query = self._extract_search_query(user_message)
            
            # Get search results from the search agent
            search_result = self.search_agent.search(search_query)
            
            # Update conversation history with both the question and answer
            self.telegram_agent.conversation_histories[chat_id] = self.telegram_agent.conversation_histories.get(chat_id, "") + \
                f"\nUser: {user_message}\nAgent: {search_result}"
            
            return search_result
        
        # For all other messages, use the Telegram agent's processing
        return self.telegram_agent.process_message(chat_id, user_message)
    
    def _is_search_request(self, message: str) -> bool:
        """
        Determine if a message is a search request.
        
        Args:
            message: The user message to analyze
            
        Returns:
            True if the message appears to be a search request, False otherwise
        """
        # Convert to lowercase for case-insensitive matching
        message_lower = message.lower()
        
        # Check for explicit search keywords
        search_keywords = ["search", "find", "look up", "lookup", "research", "google", 
                          "search for", "find information on", "what is", "who is",
                          "tell me about", "information about"]
        
        for keyword in search_keywords:
            if keyword in message_lower:
                return True
        
        # Check for question patterns
        question_patterns = [
            r"^what\s+is",
            r"^who\s+is",
            r"^where\s+is",
            r"^when\s+is",
            r"^why\s+is",
            r"^how\s+to",
            r"^how\s+do",
            r"\?$"
        ]
        
        for pattern in question_patterns:
            if re.search(pattern, message_lower):
                return True
        
        return False
    
    def _extract_search_query(self, message: str) -> str:
        """
        Extract the actual search query from a message.
        
        Args:
            message: The user message containing a search request
            
        Returns:
            The extracted search query
        """
        # Simple extraction for explicit search commands
        message_lower = message.lower()
        
        # Common prefixes to remove
        prefixes = [
            "search for", "search", "find", "look up", "lookup", 
            "research", "google", "find information on",
            "tell me about", "information about"
        ]
        
        for prefix in prefixes:
            if message_lower.startswith(prefix):
                return message[len(prefix):].strip()
        
        # If no prefix matched, return the original message
        return message
    
    def perform_search(self, query: str, context: str = "") -> str:
        """
        Perform a web search using the dedicated search agent.
        
        Args:
            query: The search query or question to research
            context: Optional additional context for the search
            
        Returns:
            The research results as a formatted string
        """
        return self.search_agent.search(query, context)

    # Additional orchestration methods can be added here as more agents are developed
    
# Example usage (commented out)
# if __name__ == "__main__":
#     orchestrator = AgentOrchestrator()
#     search_result = orchestrator.perform_search("What is the current weather in New York?")
#     print(search_result) 