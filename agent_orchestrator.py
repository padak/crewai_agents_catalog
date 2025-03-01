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
        # For now, we'll just use the Telegram agent's processing
        # In a more complex implementation, we could analyze the message and route to specialized agents
        
        # Example of more complex routing:
        # if "search" in user_message.lower() or "find" in user_message.lower():
        #     search_result = self.search_agent.search(user_message)
        #     # Combine search result with telegram formatting
        #     return self.telegram_agent.format_response(search_result)
        
        # For now, just pass to the telegram agent
        return self.telegram_agent.process_message(chat_id, user_message)
    
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