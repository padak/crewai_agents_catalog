from crewai import Agent, Task, Crew, Process
import os
from typing import Dict, Any
from datetime import datetime

class TelegramCrew:
    """
    A CrewAI crew that handles Telegram messages by routing them to appropriate agents.
    Following the Single Responsibility Principle, this crew ONLY handles Telegram communication
    and delegates to external agents for specific tasks.
    """
    
    def __init__(self):
        """Initialize the TelegramCrew with configuration."""
        # Dictionary to store conversation histories for each chat_id
        self.conversation_histories = {}
        
        # Load agent and task configurations
        self.agents_config = self._load_agents_config()
        self.tasks_config = self._load_tasks_config()
    
    def _load_agents_config(self):
        """Load agent configurations"""
        return {
            'telegram_gateway_agent': {
                'name': 'Telegram Gateway Agent',
                'description': 'Manages Telegram communication, interprets user messages, and routes requests to specialized agents',
                'goal': 'Provide helpful, accurate responses to Telegram users',
                'backstory': 'I am a specialized communication agent who acts as the gateway between Telegram users and AI services.',
            }
        }
    
    def _load_tasks_config(self):
        """Load task configurations"""
        return {
            'handle_telegram_message': {
                'description': 'Process a message from a Telegram user and generate an appropriate response',
                'expected_output': 'A clear, helpful response that addresses the user message'
            }
        }
        
    def telegram_gateway_agent(self) -> Agent:
        """
        Create and return the Telegram Gateway agent.
        This agent is responsible for:
        - Interpreting user messages
        - Maintaining conversation context
        - Routing requests to external specialized agents
        - Formatting responses for Telegram
        """
        return Agent(
            role=self.agents_config['telegram_gateway_agent']['name'],
            goal=self.agents_config['telegram_gateway_agent']['goal'],
            backstory=self.agents_config['telegram_gateway_agent']['backstory'],
            verbose=True,
            allow_delegation=True,
            tools=[],  # No tools - pure communication agent
            memory=True  # Enable memory for maintaining conversation context
        )
    
    def handle_telegram_message(self, user_message: str, conversation_history: str, chat_id: str) -> Task:
        """
        Create and return the task for handling Telegram messages.
        This is the entry point for all Telegram interactions.
        """
        # Add current date information to the context
        current_date = datetime.now().strftime("%B %d, %Y")
        
        return Task(
            description=f"{self.tasks_config['handle_telegram_message']['description']}\nToday's date: {current_date}\nUser message: {user_message}\nConversation history: {conversation_history}\nChat ID: {chat_id}",
            expected_output=self.tasks_config['handle_telegram_message']['expected_output'],
            agent=self.telegram_gateway_agent()
        )
    
    def create_crew(self, user_message: str, conversation_history: str, chat_id: str) -> Crew:
        """Create and return the Telegram crew focusing solely on communication."""
        return Crew(
            agents=[self.telegram_gateway_agent()],
            tasks=[self.handle_telegram_message(user_message, conversation_history, chat_id)],
            process=Process.sequential,
            verbose=True
        )
    
    def process_message(self, chat_id: str, user_message: str) -> str:
        """
        Process a message from a Telegram user.
        
        Args:
            chat_id: The Telegram chat ID for tracking conversation history
            user_message: The message from the user
            
        Returns:
            The response to send back to the user
        """
        # Get or create conversation history for this chat
        conversation_history = self.conversation_histories.get(chat_id, "")
        
        # Run the crew with the user message and conversation history
        crew = self.create_crew(user_message, conversation_history, chat_id)
        result = crew.kickoff()
        
        # Ensure the result is a string
        result_str = str(result)
        
        # Update conversation history (simple approach - in production you might want to limit size)
        updated_history = f"{conversation_history}\nUser: {user_message}\nAgent: {result_str}"
        # Only keep recent history to avoid exceeding token limits
        if len(updated_history.split('\n')) > 20:  # Limit of 10 conversation turns
            updated_history = '\n'.join(updated_history.split('\n')[-20:])
        self.conversation_histories[chat_id] = updated_history
        
        return result_str 