#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Calendar Agent - Provides read-only access to calendar data

This agent follows the Single Responsibility Principle by focusing solely on
calendar-related operations and queries.
"""

from crewai import Agent, Task, Crew, Process
from langchain.tools import Tool
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import os
import os.path
import pytz
import json
import yaml
from pydantic import BaseModel, Field
from pathlib import Path

# Initialize Anthropic or OpenAI based on environment configuration
provider = os.getenv('LITELLM_PROVIDER', 'openai').lower()
if provider == 'anthropic':
    try:
        from anthropic import Anthropic
        # Ensure API key is set
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if api_key:
            print("✓ Anthropic API key is set")
            # Validate the key by creating a client (but not making a request)
            anthropic_client = Anthropic(api_key=api_key)
    except ImportError:
        print("Warning: Anthropic package not installed. Run 'pip install anthropic>=0.19.0'")
else:
    # For OpenAI, there's less setup needed as CrewAI handles it well by default
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key:
        print("✓ OpenAI API key is set")

# Google Calendar API imports
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Constants
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']  # Readonly scope
TOKEN_PATH = Path('calendar_agent/token.json')
CREDENTIALS_PATH = Path('calendar_agent/credentials.json')


class CalendarCrew:
    """
    A CrewAI crew that handles calendar-related queries.
    This crew follows the Single Responsibility Principle by focusing solely on
    calendar operations like event listing, schedule checking, etc.
    """
    
    def __init__(self):
        """Initialize the Calendar Crew with necessary tools and agents"""
        # Load agent and task configurations
        self.agents_config = self._load_agents_config()
        self.tasks_config = self._load_tasks_config()
        # Get calendar credentials
        self.creds = self._get_calendar_credentials()
        # Create the calendar agent
        self.calendar_agent = self._create_calendar_agent()
        
    def _create_calendar_agent(self):
        """Create the Calendar Agent with appropriate tools"""
        calendar_tools = self._create_calendar_tools()
        
        # Load LLM configuration
        llm_config = self._load_llm_config()
        
        # Get the current provider for better agent description
        provider = os.getenv('LITELLM_PROVIDER', 'openai').lower()
        model_name = "Claude" if provider == "anthropic" else "GPT"
        
        # Create the calendar agent
        return Agent(
            role="Calendar Assistant",
            goal=f"Provide accurate and helpful information about calendar events using {model_name}",
            backstory=(
                f"You are an AI assistant specialized in retrieving and understanding calendar data. "
                f"You have read-only access to the user's calendar and can provide information about "
                f"upcoming events, schedule conflicts, and availability."
            ),
            verbose=True,
            allow_delegation=False,
            tools=calendar_tools,
            llm_config=llm_config
        )
    
    def _load_agents_config(self):
        """Load agent configurations"""
        return {
            'calendar_agent': {
                'name': 'Calendar Agent',
                'description': 'Provides read-only access to calendar information',
                'goal': 'Help users stay organized by providing accurate information about their schedule',
                'backstory': 'I am a specialized agent focused on calendar management. I can view your upcoming meetings, events, and help you plan your day based on your schedule.',
            }
        }
    
    def _load_tasks_config(self):
        """Load task configurations"""
        return {
            'process_calendar_query': {
                'description': 'Process a calendar-related query and provide accurate information',
                'expected_output': 'A clear, accurate response about the user\'s calendar or schedule'
            }
        }
    
    def _load_llm_config(self) -> Dict[str, Any]:
        """
        Load the LLM configuration from environment or config file
        
        Returns:
            Dict[str, Any]: LLM configuration dictionary
        """
        # Check for config file first
        config_file = Path('crew_config.yaml')
        
        if config_file.exists():
            with open(config_file, 'r') as file:
                config = yaml.safe_load(file)
                if config and 'llm' in config:
                    return config['llm']
        
        # If no config file or it doesn't have LLM section, use environment variables
        provider = os.getenv('LITELLM_PROVIDER', 'openai').lower()
        
        # Default values
        llm_config = {
            'temperature': 0.7,
            'verbose': True,
        }
        
        if provider == 'anthropic':
            # Direct Anthropic configuration
            api_key = os.getenv('ANTHROPIC_API_KEY')
            model = os.getenv('ANTHROPIC_MODEL', 'claude-3-opus-20240229')
            
            if not api_key:
                print("Warning: ANTHROPIC_API_KEY not set in environment")
                return llm_config  # Return default config, will likely fail later
                
            try:
                from anthropic import Anthropic
                
                # For CrewAI using direct Anthropic integration
                llm_config = {
                    'model': f"anthropic/{model}",  # Include provider prefix for CrewAI
                    'api_key': api_key,  # Simple format that CrewAI understands
                    'temperature': float(os.getenv('ANTHROPIC_TEMPERATURE', '0.7')),
                    'max_tokens': int(os.getenv('ANTHROPIC_MAX_TOKENS', '4000'))
                }
                
                print(f"Using Anthropic model: {model} with direct API configuration")
                return llm_config
            except ImportError:
                print("Warning: Anthropic package not installed. Run 'pip install anthropic>=0.19.0'")
                # Fall back to CrewAI default (likely OpenAI)
                return {}
                
        else:
            # OpenAI configuration
            api_key = os.getenv('OPENAI_API_KEY')
            model = os.getenv('OPENAI_MODEL', 'gpt-4o')
            
            if not api_key:
                print("Warning: OPENAI_API_KEY not set in environment")
                return llm_config  # Return default config, will likely fail later
                
            llm_config = {
                'model': model,
                'api_key': api_key,
                'temperature': float(os.getenv('OPENAI_TEMPERATURE', '0.7'))
            }
                
        return llm_config
    
    def _get_calendar_credentials(self):
        """Get or refresh Google Calendar credentials."""
        creds = None
        
        # Check if token file exists
        if TOKEN_PATH.exists():
            try:
                creds = Credentials.from_authorized_user_info(
                    json.loads(TOKEN_PATH.read_text()), SCOPES)
            except Exception as e:
                print(f"Error loading credentials: {str(e)}")
                
        # If no valid credentials, need to authenticate
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception:
                    print("Credentials could not be refreshed. Need to authenticate again.")
                    creds = None
            
            # If still no valid credentials, try different authentication methods
            if not creds:
                # First try to use environment variables
                client_id = os.getenv('GOOGLE_CALENDAR_CLIENT_ID')
                client_secret = os.getenv('GOOGLE_CALENDAR_CLIENT_SECRET')
                
                if client_id and client_secret:
                    print("Using Google Calendar credentials from environment variables.")
                    try:
                        # Create a client config dict from environment variables
                        client_config = {
                            "installed": {
                                "client_id": client_id,
                                "project_id": os.getenv('GOOGLE_CALENDAR_PROJECT_ID', ''),
                                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                                "token_uri": "https://oauth2.googleapis.com/token",
                                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                                "client_secret": client_secret,
                                "redirect_uris": ["http://localhost"]
                            }
                        }
                        
                        # Run the OAuth flow with the constructed config
                        flow = InstalledAppFlow.from_client_config(
                            client_config, SCOPES)
                        creds = flow.run_local_server(port=0)
                        
                        # Save credentials to token file for future use
                        TOKEN_PATH.parent.mkdir(exist_ok=True)
                        TOKEN_PATH.write_text(creds.to_json())
                        print(f"Successfully authenticated. Token saved to {TOKEN_PATH}")
                    except Exception as e:
                        print(f"Error during authentication with environment variables: {str(e)}")
                        print("Falling back to credentials.json file if available.")
                
                # If environment variable method failed, fall back to credentials.json file
                if not creds and CREDENTIALS_PATH.exists():
                    print("\nWARNING: Calendar authentication required")
                    print(f"Using credentials from {CREDENTIALS_PATH}")
                    print("See README for instructions on how to obtain Google Calendar API credentials.")
                    
                    try:
                        flow = InstalledAppFlow.from_client_secrets_file(
                            str(CREDENTIALS_PATH), SCOPES)
                        creds = flow.run_local_server(port=0)
                        
                        # Save credentials
                        TOKEN_PATH.parent.mkdir(exist_ok=True)
                        TOKEN_PATH.write_text(creds.to_json())
                        print(f"Successfully authenticated. Token saved to {TOKEN_PATH}")
                    except Exception as e:
                        print(f"Error during authentication with credentials file: {str(e)}")
                
                # If all attempts failed, show instructions
                if not creds:
                    print("\nERROR: Could not authenticate with Google Calendar API.")
                    print("Please either:")
                    print("1. Set GOOGLE_CALENDAR_CLIENT_ID and GOOGLE_CALENDAR_CLIENT_SECRET in .env file, or")
                    print(f"2. Place valid credentials.json file in {CREDENTIALS_PATH}")
        
        return creds
    
    def get_events_tool(self):
        """Tool for listing calendar events"""
        def get_upcoming_events(days: int = 7, max_results: int = 10) -> str:
            """Get upcoming calendar events for a specified number of days"""
            if not self.creds:
                return "Calendar access not authenticated. Please set up Google Calendar API credentials."
            
            try:
                # Build Google Calendar service
                service = build('calendar', 'v3', credentials=self.creds)
                
                # Calculate time range
                now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
                end_date = (datetime.utcnow() + timedelta(days=int(days))).isoformat() + 'Z'
                
                # Call the Calendar API
                events_result = service.events().list(
                    calendarId='primary',
                    timeMin=now,
                    timeMax=end_date,
                    maxResults=int(max_results),
                    singleEvents=True,
                    orderBy='startTime'
                ).execute()
                events = events_result.get('items', [])
                
                if not events:
                    return f"No upcoming events found in the next {days} days."
                
                # Format events data
                formatted_events = []
                for event in events:
                    start = event.get('start', {})
                    
                    # Handle all-day events vs. time-specific events
                    if 'dateTime' in start:
                        start_time = datetime.fromisoformat(start['dateTime'].replace('Z', '+00:00'))
                        time_str = start_time.strftime('%Y-%m-%d %H:%M:%S (%Z)')
                    else:
                        # All-day event
                        time_str = f"{start.get('date')} (All day)"
                    
                    formatted_events.append(f"- {event.get('summary', 'Unnamed event')} at {time_str}")
                
                return "Upcoming events:\n" + "\n".join(formatted_events)
                
            except Exception as e:
                return f"Error retrieving calendar events: {str(e)}"
                
        # Wrap the function as a tool
        return Tool(
            name="UpcomingEvents",
            func=get_upcoming_events,
            description="Get upcoming calendar events for a specified number of days. Parameters: days (optional, default=7) - number of days to look ahead, max_results (optional, default=10) - maximum number of events to return."
        )
    
    def check_availability_tool(self):
        """Tool for checking availability in calendar"""
        def check_availability(date_str: str, start_time: Optional[str] = None, end_time: Optional[str] = None) -> str:
            """Check if there are any events scheduled for a specific date and time range"""
            if not self.creds:
                return "Calendar access not authenticated. Please set up Google Calendar API credentials."
            
            try:
                # Parse date and times
                try:
                    date = datetime.strptime(date_str, "%Y-%m-%d").date()
                    
                    # Default to entire day if no times provided
                    if not start_time:
                        start_datetime = datetime.combine(date, datetime.min.time())
                        start_datetime = start_datetime.replace(tzinfo=pytz.UTC)
                    else:
                        start_time_parsed = datetime.strptime(start_time, "%H:%M").time()
                        start_datetime = datetime.combine(date, start_time_parsed)
                        start_datetime = start_datetime.replace(tzinfo=pytz.UTC)
                    
                    if not end_time:
                        end_datetime = datetime.combine(date, datetime.max.time())
                        end_datetime = end_datetime.replace(tzinfo=pytz.UTC)
                    else:
                        end_time_parsed = datetime.strptime(end_time, "%H:%M").time()
                        end_datetime = datetime.combine(date, end_time_parsed)
                        end_datetime = end_datetime.replace(tzinfo=pytz.UTC)
                        
                except ValueError:
                    return "Invalid date or time format. Use YYYY-MM-DD for date and HH:MM for time."
                
                # Build Google Calendar service
                service = build('calendar', 'v3', credentials=self.creds)
                
                # Call the Calendar API
                events_result = service.events().list(
                    calendarId='primary',
                    timeMin=start_datetime.isoformat(),
                    timeMax=end_datetime.isoformat(),
                    singleEvents=True,
                    orderBy='startTime'
                ).execute()
                events = events_result.get('items', [])
                
                if not events:
                    time_range = f"on {date_str}"
                    if start_time and end_time:
                        time_range = f"between {start_time} and {end_time} on {date_str}"
                    elif start_time:
                        time_range = f"after {start_time} on {date_str}"
                    elif end_time:
                        time_range = f"before {end_time} on {date_str}"
                        
                    return f"You are available {time_range}. No events scheduled."
                
                # Format events data
                formatted_events = []
                for event in events:
                    start = event.get('start', {})
                    end = event.get('end', {})
                    
                    # Handle all-day events vs. time-specific events
                    if 'dateTime' in start:
                        start_time = datetime.fromisoformat(start['dateTime'].replace('Z', '+00:00'))
                        end_time = datetime.fromisoformat(end['dateTime'].replace('Z', '+00:00'))
                        time_str = f"{start_time.strftime('%H:%M')} to {end_time.strftime('%H:%M')}"
                    else:
                        # All-day event
                        time_str = "All day"
                    
                    formatted_events.append(f"- {event.get('summary', 'Unnamed event')} ({time_str})")
                
                time_range = f"on {date_str}"
                if start_time and end_time:
                    time_range = f"between {start_time} and {end_time} on {date_str}"
                elif start_time:
                    time_range = f"after {start_time} on {date_str}"
                elif end_time:
                    time_range = f"before {end_time} on {date_str}"
                
                return f"You have the following events {time_range}:\n" + "\n".join(formatted_events)
                
            except Exception as e:
                return f"Error checking availability: {str(e)}"
                
        # Wrap the function as a tool
        return Tool(
            name="CheckAvailability",
            func=check_availability,
            description="Check availability for a specific date and optional time range. Parameters: date_str (required, format: YYYY-MM-DD), start_time (optional, format: HH:MM), end_time (optional, format: HH:MM)."
        )
    
    def find_event_tool(self):
        """Tool for finding specific events"""
        def find_events(query: str, days: int = 30, max_results: int = 5) -> str:
            """Search for events matching a query in the calendar"""
            if not self.creds:
                return "Calendar access not authenticated. Please set up Google Calendar API credentials."
            
            try:
                # Build Google Calendar service
                service = build('calendar', 'v3', credentials=self.creds)
                
                # Calculate time range
                now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
                end_date = (datetime.utcnow() + timedelta(days=int(days))).isoformat() + 'Z'
                
                # Call the Calendar API
                events_result = service.events().list(
                    calendarId='primary',
                    timeMin=now,
                    timeMax=end_date,
                    maxResults=50,  # Get more events to filter
                    singleEvents=True,
                    orderBy='startTime'
                ).execute()
                events = events_result.get('items', [])
                
                if not events:
                    return f"No events found in the next {days} days."
                
                # Filter events by query
                query = query.lower()
                matching_events = []
                
                for event in events:
                    event_summary = event.get('summary', '').lower()
                    event_description = event.get('description', '').lower()
                    event_location = event.get('location', '').lower()
                    
                    if (query in event_summary or 
                        query in event_description or 
                        query in event_location):
                        matching_events.append(event)
                        
                        # Limit to max_results
                        if len(matching_events) >= max_results:
                            break
                
                if not matching_events:
                    return f"No events matching '{query}' found in the next {days} days."
                
                # Format events data
                formatted_events = []
                for event in matching_events:
                    start = event.get('start', {})
                    
                    # Handle all-day events vs. time-specific events
                    if 'dateTime' in start:
                        start_time = datetime.fromisoformat(start['dateTime'].replace('Z', '+00:00'))
                        time_str = start_time.strftime('%Y-%m-%d %H:%M:%S')
                    else:
                        # All-day event
                        time_str = f"{start.get('date')} (All day)"
                    
                    formatted_events.append(f"- {event.get('summary', 'Unnamed event')} at {time_str}")
                
                return f"Events matching '{query}':\n" + "\n".join(formatted_events)
                
            except Exception as e:
                return f"Error finding events: {str(e)}"
                
        # Wrap the function as a tool
        return Tool(
            name="FindEvents",
            func=find_events,
            description="Search for calendar events matching a specific query. Parameters: query (required) - search term, days (optional, default=30) - number of days to look ahead, max_results (optional, default=5) - maximum number of events to return."
        )
    
    def process_calendar_query(self, query: str) -> Task:
        """
        Create and return the task for processing calendar-related queries.
        """
        current_date = datetime.now().strftime("%B %d, %Y")
        
        return Task(
            description=f"{self.tasks_config['process_calendar_query']['description']}\nToday's date: {current_date}\nUser query: {query}",
            expected_output=self.tasks_config['process_calendar_query']['expected_output'],
            agent=self.calendar_agent
        )
    
    def create_crew(self, query: str) -> Crew:
        """Create and return the Calendar crew."""
        return Crew(
            agents=[self.calendar_agent],
            tasks=[self.process_calendar_query(query)],
            process=Process.sequential,
            verbose=True
        )
    
    def process_query(self, query: str) -> str:
        """
        Process a calendar-related query and return the response.
        
        Args:
            query: The calendar-related query from the user
            
        Returns:
            The response with accurate calendar information
        """
        # Check if we have valid credentials
        if not self.creds:
            return "Calendar access is not set up. Please follow the instructions to authorize Google Calendar access."
        
        crew = self.create_crew(query)
        result = crew.kickoff()
        
        # Ensure we return a string, not a CrewOutput object
        return str(result)
    
    def process_message(self, query: str) -> str:
        """
        Process a calendar-related message and return the response.
        This method provides a consistent interface for the agent orchestrator.
        
        Args:
            query: The calendar-related query from the user
            
        Returns:
            str: The response with accurate calendar information
        """
        return self.process_query(query)
    
    def _create_calendar_tools(self):
        """Create and return the calendar tools for the agent to use"""
        return [
            self.get_events_tool(),
            self.check_availability_tool(),
            self.find_event_tool()
        ] 