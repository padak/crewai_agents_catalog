#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script for the Calendar Agent

This script allows for quick testing of the Calendar Agent functionality
without needing to go through the Telegram interface.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add the project root to the Python path for imports
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Load environment variables from .env file
load_dotenv()

def main():
    try:
        # Import the calendar crew after environment is set up
        from calendar_agent.src.calendar_crew import CalendarCrew
        
        # Print configuration information
        provider = os.getenv('LITELLM_PROVIDER', 'openai').lower()
        model = os.getenv('ANTHROPIC_MODEL', 'claude-3-opus-20240229') if provider == 'anthropic' else os.getenv('OPENAI_MODEL', 'gpt-4o')
        print(f"Using LLM Provider: {provider.upper()}")
        print(f"Using Model: {model}")
        
        # Create the calendar crew
        calendar_crew = CalendarCrew()
        
        # Interactive mode
        print("\n=== Calendar Agent Test ===")
        print("Enter 'exit' or 'quit' to end the session")
        
        while True:
            query = input("\nYour calendar query: ")
            if query.lower() in ['exit', 'quit']:
                break
                
            if not query.strip():
                continue
                
            print("\nProcessing query...")
            try:
                response = calendar_crew.process_message(query)
                print("\nCalendar Agent Response:")
                print(response)
            except Exception as e:
                print(f"Error: {e}")
                print("Something went wrong. Please check your environment setup.")
                
    except ImportError as e:
        print(f"Error: {e}")
        print("Could not import the Calendar Agent. Please check your installation.")
        return False
    except Exception as e:
        print(f"Error: {e}")
        print("An unexpected error occurred.")
        return False
        
    return True

if __name__ == "__main__":
    if not main():
        sys.exit(1) 