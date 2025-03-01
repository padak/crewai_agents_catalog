from crewai import Agent, Task, Crew, Process
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import ephem  # For astronomical calculations
import pytz   # For timezone handling

class TimeCrew:
    """
    A CrewAI crew that handles time-related queries.
    This crew follows the Single Responsibility Principle by focusing solely on
    temporal information such as current time, dates, moon phases, etc.
    """
    
    def __init__(self):
        """Initialize the TimeCrew with configuration."""
        # Load agent and task configurations
        self.agents_config = self._load_agents_config()
        self.tasks_config = self._load_tasks_config()
    
    def _load_agents_config(self):
        """Load agent configurations"""
        return {
            'time_agent': {
                'name': 'Time and Date Agent',
                'description': 'Provides accurate time-related information including current dates, times, moon phases, and other astronomical data',
                'goal': 'Deliver precise temporal information based on real-time calculations',
                'backstory': 'I am a specialized agent focused on temporal data. I calculate current dates, times, moon phases, and other time-related information with precision.',
            }
        }
    
    def _load_tasks_config(self):
        """Load task configurations"""
        return {
            'process_time_query': {
                'description': 'Process a time-related query and generate accurate temporal information',
                'expected_output': 'A clear, accurate response with the requested time-related information'
            }
        }
        
    def time_agent(self) -> Agent:
        """
        Create and return the Time Agent.
        This agent is responsible for all time-related calculations and information.
        """
        return Agent(
            role=self.agents_config['time_agent']['name'],
            goal=self.agents_config['time_agent']['goal'],
            backstory=self.agents_config['time_agent']['backstory'],
            verbose=True,
            allow_delegation=False,
            tools=[
                self.get_current_time_tool(),
                self.get_moon_phase_tool(),
                self.get_sunrise_sunset_tool()
            ],
            memory=False  # Time data should always be fresh
        )
    
    def get_current_time_tool(self):
        """Tool for getting current time in different timezones"""
        def get_current_time(timezone: Optional[str] = None):
            """Get current time, optionally in a specific timezone"""
            if timezone:
                try:
                    tz = pytz.timezone(timezone)
                    current_time = datetime.now(tz)
                    return f"Current time in {timezone}: {current_time.strftime('%Y-%m-%d %H:%M:%S %Z')}"
                except pytz.exceptions.UnknownTimeZoneError:
                    return f"Unknown timezone: {timezone}. Please use a valid timezone name like 'America/New_York'."
            else:
                # Default to UTC
                current_time = datetime.now(pytz.UTC)
                return f"Current UTC time: {current_time.strftime('%Y-%m-%d %H:%M:%S %Z')}"
                
        # Wrap the function as a tool
        from langchain.tools import Tool
        return Tool(
            name="CurrentTime",
            func=get_current_time,
            description="Get the current date and time, optionally in a specific timezone. Parameter: timezone (optional) - e.g., 'America/New_York', 'Europe/London', 'Asia/Tokyo'."
        )
    
    def get_moon_phase_tool(self):
        """Tool for calculating moon phases"""
        def calculate_moon_phase(date_str: Optional[str] = None):
            """Calculate the moon phase for a given date or today"""
            try:
                if date_str:
                    target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                else:
                    target_date = datetime.now().date()
                
                # Calculate moon phase using ephem
                moon = ephem.Moon()
                moon.compute(target_date.strftime("%Y/%m/%d"))
                
                # Calculate next full moon
                next_full_moon = ephem.next_full_moon(target_date.strftime("%Y/%m/%d"))
                next_full_date = datetime.strptime(str(next_full_moon), "%Y/%m/%d %H:%M:%S").date()
                
                # Calculate previous full moon
                prev_full_moon = ephem.previous_full_moon(target_date.strftime("%Y/%m/%d"))
                prev_full_date = datetime.strptime(str(prev_full_moon), "%Y/%m/%d %H:%M:%S").date()
                
                # Calculate days until next full moon
                days_until_next = (next_full_date - target_date).days
                
                # Get moon phase percentage
                phase_percent = moon.phase
                
                # Determine moon phase name
                if phase_percent < 1:
                    phase_name = "New Moon"
                elif phase_percent < 49:
                    phase_name = "Waxing Crescent" if moon.phase < 25 else "Waxing Gibbous"
                elif phase_percent < 51:
                    phase_name = "Full Moon"
                else:
                    phase_name = "Waning Gibbous" if moon.phase < 75 else "Waning Crescent"
                
                result = {
                    "date": target_date.strftime("%Y-%m-%d"),
                    "moon_phase": phase_name,
                    "illumination_percent": round(phase_percent, 1),
                    "next_full_moon": next_full_date.strftime("%Y-%m-%d"),
                    "days_until_next_full_moon": days_until_next,
                    "previous_full_moon": prev_full_date.strftime("%Y-%m-%d")
                }
                
                return f"""Moon phase information for {result['date']}:
Phase: {result['moon_phase']}
Illumination: {result['illumination_percent']}%
Next full moon: {result['next_full_moon']} ({result['days_until_next_full_moon']} days from now)
Previous full moon: {result['previous_full_moon']}"""
                
            except Exception as e:
                return f"Error calculating moon phase: {str(e)}. Please use date format YYYY-MM-DD or leave blank for today."
                
        # Wrap the function as a tool
        from langchain.tools import Tool
        return Tool(
            name="MoonPhase",
            func=calculate_moon_phase,
            description="Calculate the moon phase for a given date or today. Parameter: date_str (optional) - date in format 'YYYY-MM-DD'. Provides phase name, illumination percentage, and next/previous full moon dates."
        )
    
    def get_sunrise_sunset_tool(self):
        """Tool for calculating sunrise and sunset times"""
        def calculate_sunrise_sunset(latitude: str, longitude: str, date_str: Optional[str] = None):
            """Calculate sunrise and sunset for a location on a specific date"""
            try:
                # Parse location
                lat = float(latitude)
                lon = float(longitude)
                
                # Parse date or use today
                if date_str:
                    target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                else:
                    target_date = datetime.now().date()
                
                # Create observer at location
                observer = ephem.Observer()
                observer.lat = str(lat)
                observer.lon = str(lon)
                observer.date = target_date.strftime("%Y/%m/%d")
                
                # Calculate sunrise and sunset
                sun = ephem.Sun()
                sunrise = observer.next_rising(sun)
                sunset = observer.next_setting(sun)
                
                # Format times
                sunrise_time = datetime.strptime(str(sunrise), "%Y/%m/%d %H:%M:%S").strftime("%H:%M:%S")
                sunset_time = datetime.strptime(str(sunset), "%Y/%m/%d %H:%M:%S").strftime("%H:%M:%S")
                
                return f"""Sunrise and sunset times for coordinates ({latitude}, {longitude}) on {target_date.strftime('%Y-%m-%d')}:
Sunrise: {sunrise_time} UTC
Sunset: {sunset_time} UTC"""
                
            except Exception as e:
                return f"Error calculating sunrise/sunset: {str(e)}. Please provide valid latitude, longitude (as decimal degrees) and optional date in YYYY-MM-DD format."
                
        # Wrap the function as a tool
        from langchain.tools import Tool
        return Tool(
            name="SunriseSunset",
            func=calculate_sunrise_sunset,
            description="Calculate sunrise and sunset times for a specific location and date. Parameters: latitude, longitude (decimal coordinates), date_str (optional, YYYY-MM-DD)."
        )
    
    def process_time_query(self, query: str) -> Task:
        """
        Create and return the task for processing time-related queries.
        """
        current_date = datetime.now().strftime("%B %d, %Y")
        
        return Task(
            description=f"{self.tasks_config['process_time_query']['description']}\nToday's date: {current_date}\nUser query: {query}",
            expected_output=self.tasks_config['process_time_query']['expected_output'],
            agent=self.time_agent()
        )
    
    def create_crew(self, query: str) -> Crew:
        """Create and return the Time crew."""
        return Crew(
            agents=[self.time_agent()],
            tasks=[self.process_time_query(query)],
            process=Process.sequential,
            verbose=True
        )
    
    def process_query(self, query: str) -> str:
        """
        Process a time-related query and return the response.
        
        Args:
            query: The time-related query from the user
            
        Returns:
            The response with accurate time information
        """
        crew = self.create_crew(query)
        result = crew.kickoff()
        
        # Ensure we return a string, not a CrewOutput object
        return str(result) 