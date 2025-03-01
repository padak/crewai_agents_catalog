#!/usr/bin/env python3
"""
Test script to verify CrewAI installation and version.
"""

import sys
import crewai
from crewai import Agent, Task, Crew, Process

def main():
    """Run a basic test of CrewAI functionality."""
    try:
        print(f"Python version: {sys.version}")
        print(f"CrewAI version: {crewai.__version__}")
        
        # Create a simple agent
        researcher = Agent(
            role="Researcher",
            goal="Research and provide accurate information",
            backstory="You are an expert researcher with vast knowledge in various domains.",
            verbose=True
        )
        
        # Create a simple task
        research_task = Task(
            description="Research the benefits of AI in healthcare",
            expected_output="A short paragraph describing 3-5 key benefits of AI in healthcare",
            agent=researcher
        )
        
        # Create a simple crew
        research_crew = Crew(
            agents=[researcher],
            tasks=[research_task],
            verbose=True,
            process=Process.sequential
        )
        
        print("Successfully created Agent, Task, and Crew objects!")
        print("CrewAI installation test passed!")
        return 0
    except Exception as e:
        print(f"Error: {e}")
        print(f"CrewAI installation test failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 