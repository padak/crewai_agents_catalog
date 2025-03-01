from crewai import Agent, Task, Crew, Process
from crewai.cli.crew_cli import CrewBase, agent, task, crew
import os
from typing import Dict, Any

class TelegramCrew(CrewBase):
    """
    A CrewAI crew that handles Telegram messages by routing them to appropriate agents.
    Following the Single Responsibility Principle, this crew ONLY handles Telegram communication
    and delegates to external agents for specific tasks.
    """
    
    def __init__(self):
        """Initialize the TelegramCrew with configuration."""
        super().__init__()
        
        # Dictionary to store conversation history for each chat_id
        self.conversation_histories = {}
    
    @agent
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
            config=self.agents_config['telegram_gateway_agent'],
            verbose=True,
            allow_delegation=True,
            tools=[],  # No tools - pure communication agent
            memory=True  # Enable memory for maintaining conversation context
        )
    
    @task
    def handle_telegram_message(self) -> Task:
        """
        Create and return the task for handling Telegram messages.
        This is the entry point for all Telegram interactions.
        """
        return Task(
            config=self.tasks_config['handle_telegram_message']
        )
    
    @crew
    def crew(self) -> Crew:
        """Create and return the Telegram crew focusing solely on communication."""
        return Crew(
            agents=[self.telegram_gateway_agent()],
            tasks=[self.handle_telegram_message()],
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
        result = self.crew().kickoff(
            inputs={
                'user_message': user_message,
                'conversation_history': conversation_history,
                'chat_id': chat_id  # Pass chat_id to allow agents to know which conversation this is
            }
        )
        
        # Update conversation history (simple approach - in production you might want to limit size)
        updated_history = f"{conversation_history}\nUser: {user_message}\nAgent: {result.raw}"
        # Only keep recent history to avoid exceeding token limits
        if len(updated_history.split('\n')) > 20:  # Limit of 10 conversation turns
            updated_history = '\n'.join(updated_history.split('\n')[-20:])
        self.conversation_histories[chat_id] = updated_history
        
        return result.raw 