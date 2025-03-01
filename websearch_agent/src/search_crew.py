from crewai import Agent, Task, Crew, Process
from crewai.tools import SerpAPITool
from crewai.cli.crew_cli import CrewBase, agent, task, crew
import os
from typing import Dict, Any

class SearchCrew(CrewBase):
    """
    A CrewAI crew that handles web search requests.
    Following the Single Responsibility Principle, this crew ONLY handles web search
    and information retrieval functionality.
    """
    
    def __init__(self):
        """Initialize the SearchCrew with configuration."""
        super().__init__()
    
    @agent
    def websearch_agent(self) -> Agent:
        """
        Create and return the Web Search agent.
        This agent is responsible for:
        - Performing web searches
        - Gathering and synthesizing information
        - Providing factual responses with sources
        """
        # Instantiate search tool
        search_tool = SerpAPITool()
        
        return Agent(
            config=self.agents_config['websearch_agent'],
            verbose=True,
            allow_delegation=False,
            tools=[search_tool],
            memory=False  # Search agent doesn't need persistent memory between searches
        )
    
    @task
    def perform_search(self) -> Task:
        """
        Create and return the task for performing web searches.
        """
        return Task(
            config=self.tasks_config['perform_search']
        )
    
    @crew
    def crew(self) -> Crew:
        """Create and return the Search crew focusing solely on web search functionality."""
        return Crew(
            agents=[self.websearch_agent()],
            tasks=[self.perform_search()],
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
        result = self.crew().kickoff(
            inputs={
                'search_query': query,
                'context': context
            }
        )
        
        return result.raw 