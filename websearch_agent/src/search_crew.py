from crewai import Agent, Task, Crew, Process
from langchain_community.utilities.serpapi import SerpAPIWrapper
import os
from typing import Dict, Any
from langchain.tools import Tool

class SearchCrew:
    """
    A CrewAI crew that handles web search requests.
    Following the Single Responsibility Principle, this crew ONLY handles web search
    and information retrieval functionality.
    """
    
    def __init__(self):
        """Initialize the SearchCrew with configuration."""
        # Load agent and task configurations
        self.agents_config = self._load_agents_config()
        self.tasks_config = self._load_tasks_config()
    
    def _load_agents_config(self):
        """Load agent configurations"""
        return {
            'websearch_agent': {
                'name': 'Web Search Agent',
                'description': 'Performs web searches and synthesizes information from multiple sources',
                'goal': 'Provide accurate, up-to-date information based on web searches',
                'backstory': 'I am a specialized research agent who searches the web to find the most relevant and accurate information.'
            }
        }
    
    def _load_tasks_config(self):
        """Load task configurations"""
        return {
            'perform_search': {
                'description': 'Perform a web search on the given query and synthesize the results',
                'expected_output': 'A comprehensive and accurate response that answers the query with relevant information from the web'
            }
        }
    
    def websearch_agent(self) -> Agent:
        """
        Create and return the Web Search agent.
        This agent is responsible for:
        - Performing web searches
        - Gathering and synthesizing information
        - Providing factual responses with sources
        """
        # Instantiate search tool
        search = SerpAPIWrapper()
        search_tool = Tool(
            name="Search",
            func=search.run,
            description="Useful for when you need to answer questions about current events or search for specific information on the web."
        )
        
        return Agent(
            role=self.agents_config['websearch_agent']['name'],
            goal=self.agents_config['websearch_agent']['goal'],
            backstory=self.agents_config['websearch_agent']['backstory'],
            verbose=True,
            allow_delegation=False,
            tools=[search_tool],
            memory=False  # Search agent doesn't need persistent memory between searches
        )
    
    def perform_search(self, query: str, context: str = "") -> Task:
        """
        Create and return the task for performing web searches.
        """
        return Task(
            description=f"{self.tasks_config['perform_search']['description']}\nSearch Query: {query}\nContext: {context}",
            expected_output=self.tasks_config['perform_search']['expected_output'],
            agent=self.websearch_agent()
        )
    
    def create_crew(self, query: str, context: str = "") -> Crew:
        """Create and return the Search crew focusing solely on web search functionality."""
        return Crew(
            agents=[self.websearch_agent()],
            tasks=[self.perform_search(query, context)],
            process=Process.sequential,
            verbose=True
        )
    
    def search(self, query: str, context: str = "") -> str:
        """
        Perform a web search for the given query.
        
        Args:
            query: The search query or question to research
            context: Optional additional context for the search
            
        Returns:
            The research results as a formatted string
        """
        # Run the crew with the search query and optional context
        crew = self.create_crew(query, context)
        result = crew.kickoff()
        
        return result 