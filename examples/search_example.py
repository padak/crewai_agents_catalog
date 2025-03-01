#!/usr/bin/env python3
"""
Example script demonstrating web search with CrewAI
"""

import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from langchain.tools import BaseTool
import serpapi

# Load environment variables
load_dotenv()

# Define a custom search tool using LangChain's BaseTool
class WebSearchTool(BaseTool):
    name = "web_search"
    description = "Useful to search the web for information."
    
    def _run(self, query: str) -> str:
        """Execute the web search using SerpAPI."""
        try:
            client = serpapi.Client(api_key=os.getenv("SERPAPI_API_KEY"))
            results = client.search({
                "engine": "google",
                "q": query
            })
            
            # Extract and format the search results
            organic_results = results.get("organic_results", [])[:3]
            formatted_results = []
            
            for result in organic_results:
                title = result.get("title", "No title")
                link = result.get("link", "No link")
                snippet = result.get("snippet", "No snippet")
                formatted_results.append(f"Title: {title}\nURL: {link}\nSnippet: {snippet}\n")
            
            return "\n".join(formatted_results) if formatted_results else "No results found."
        except Exception as e:
            return f"Error performing web search: {str(e)}"
    
    async def _arun(self, query: str) -> str:
        """Async implementation simply calls the sync version."""
        return self._run(query)

def main():
    """Run the example crew with web search capability."""
    # Create the web search tool
    search_tool = WebSearchTool()
    
    # Create a researcher agent with the search tool
    researcher = Agent(
        role="Research Specialist",
        goal="Find accurate and up-to-date information on the web",
        backstory="You are an expert researcher with a talent for finding relevant information online.",
        tools=[search_tool],
        verbose=True
    )
    
    # Create a research task
    research_task = Task(
        description="Research the latest developments in artificial intelligence and summarize the findings.",
        expected_output="A concise summary of the latest developments in AI, including major breakthroughs and trends.",
        agent=researcher
    )
    
    # Create a crew with the researcher agent
    research_crew = Crew(
        agents=[researcher],
        tasks=[research_task],
        verbose=True,
        process=Process.sequential
    )
    
    # Execute the crew's task
    result = research_crew.kickoff()
    
    print("\n=== Research Results ===\n")
    print(result)
    
if __name__ == "__main__":
    main() 