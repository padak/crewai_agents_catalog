#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Calendar Agent Example

This example demonstrates how to use the Calendar Agent directly,
without going through the Telegram interface.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Load environment variables
load_dotenv()

# Import the Calendar Agent
from calendar_agent.src.calendar_crew import CalendarCrew

def main():
    """Run a simple Calendar Agent example."""
    print("Calendar Agent Example")
    print("=====================\n")
    
    # Create a CalendarCrew instance
    calendar_crew = CalendarCrew()
    
    # Check if credentials are set up
    if not calendar_crew.creds:
        print("\nWARNING: Calendar authentication required.")
        print("To use the Calendar Agent, you need to provide credentials.json file.")
        print(f"Place Google API credentials in {os.path.abspath('calendar_agent/credentials.json')}")
        print("See calendar_agent/README.md for instructions.")
        return
    
    # Example queries to demonstrate functionality
    example_queries = [
        "What events do I have this week?",
        "Am I free tomorrow afternoon?",
        "Find events related to work",
        "Check my availability on Friday"
    ]
    
    # Process each example query
    for i, query in enumerate(example_queries, 1):
        print(f"\nExample {i}: '{query}'")
        print("-" * (len(f"Example {i}: '{query}'") + 2))
        
        try:
            # Get response from Calendar Agent
            result = calendar_crew.process_query(query)
            print(f"Response:\n{result}\n")
        except Exception as e:
            print(f"Error: {str(e)}")
    
    print("\nCalendar Agent Example Complete!")
    print("You can now implement similar functionality in your own applications.")

if __name__ == "__main__":
    main() 