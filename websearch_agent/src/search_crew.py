from crewai import Agent, Task, Crew, Process
from langchain_community.utilities.serpapi import SerpAPIWrapper
import os
from typing import Dict, Any, Optional
from langchain.tools import Tool
import json
import re
from pydantic import BaseModel, Field

# Define a Pydantic model for the Search tool arguments
class SearchSchema(BaseModel):
    """Schema for Search tool arguments"""
    query: str = Field(description="The search query to look up")
    kwargs: Optional[Dict[str, Any]] = Field(
        default={},
        description="Additional parameters for the search"
    )

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
    
    def _search_tool_wrapper(self, query: str, **kwargs) -> str:
        """
        Wrapper for the SerpAPI search tool to handle the required kwargs parameter.
        
        Args:
            query: The search query
            kwargs: Additional parameters for the search
            
        Returns:
            Search results as string
        """
        search = SerpAPIWrapper()
        try:
            # Ensure kwargs has at least an empty dict
            if not kwargs:
                kwargs = {}
            return search.run(query, **kwargs)
        except Exception as e:
            return f"Error performing search: {str(e)}"
    
    def websearch_agent(self) -> Agent:
        """
        Create and return the Web Search agent.
        This agent is responsible for:
        - Performing web searches
        - Gathering and synthesizing information
        - Providing factual responses with sources
        """
        try:
            # Create a search tool that properly handles the kwargs parameter
            search_tool = Tool(
                name="Search",
                func=self._search_tool_wrapper,
                description="Useful for when you need to answer questions about current events or search for specific information on the web.",
                args_schema=SearchSchema
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
        except Exception as e:
            print(f"Error creating web search agent: {str(e)}")
            # Create fallback agent without tools if there's an error
            return Agent(
                role=self.agents_config['websearch_agent']['name'],
                goal=self.agents_config['websearch_agent']['goal'],
                backstory=self.agents_config['websearch_agent']['backstory'],
                verbose=True,
                allow_delegation=False,
                tools=[],
                memory=False
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
        Perform a web search for the given query and return the results.
        
        Args:
            query: The search query or question to research
            context: Optional additional context for the search
            
        Returns:
            The research results as a formatted string
        """
        crew = self.create_crew(query, context)
        result = crew.kickoff()
        
        # Ensure we return a string, not a CrewOutput object
        return str(result)

    def process_message(self, query: str) -> str:
        """
        Process a message by performing a web search.
        This method is for compatibility with the agent orchestrator.
        
        Args:
            query: The query to search for
            
        Returns:
            str: The search results
        """
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"SearchCrew processing message: '{query}'")
        
        try:
            # Strip any "search for" prefix to clean up the query
            cleaned_query = re.sub(r'^(?i)(search for|search|find|look up)\s+', '', query).strip()
            logger.debug(f"Cleaned query: '{cleaned_query}'")
            
            # Call the search method
            return self.search(cleaned_query)
        except Exception as e:
            logger.error(f"Error in SearchCrew.process_message: {str(e)}")
            return f"I encountered an error while searching: {str(e)}" 