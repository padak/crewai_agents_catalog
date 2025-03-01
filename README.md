# CrewAI Multi-Agent System

A modular multi-agent system built with CrewAI that follows the Single Responsibility Principle. Each agent focuses on a specific function, and an orchestration layer connects them.

## Architecture

This project demonstrates best practices for building CrewAI agent systems:

- **Separation of Concerns**: Each agent has a single responsibility
- **Modular Design**: Agents are in separate directories with their own configurations
- **Orchestration Layer**: Agents communicate through a dedicated orchestrator
- **Environment Isolation**: Uses Python virtual environment for dependency management
- **Centralized Configuration**: Single .env file at the root level for all environment variables

### Agents

1. **Telegram Gateway Agent**
   - Handles communication with Telegram users
   - Maintains conversation context
   - Routes requests to specialized agents

2. **Web Search Agent**
   - Performs web searches
   - Retrieves and synthesizes information
   - Returns factual data with sources

*More specialized agents can be added following the same pattern.*

## Setup

### Prerequisites

- Python 3.10-3.12 for latest CrewAI features (recommended: Python 3.11.x)
- Python 3.13.1 works with CrewAI 0.11.2 (limited feature set)
- Telegram Bot Token (from BotFather)
- SerpAPI API key for web search functionality
- OpenAI API key for CrewAI's underlying LLMs

### Installation

The project supports two environments:

#### Option 1: Latest CrewAI (0.102.0) with Python 3.11

1. Clone the repository:

```bash
git clone https://github.com/yourusername/tools.git
cd tools
```

2. Create and activate the environment for the latest CrewAI:

```bash
python3.11 -m venv venv_crewai_latest
source venv_crewai_latest/bin/activate  # On Windows: venv_crewai_latest\Scripts\activate
pip install -r requirements.txt
```

#### Option 2: Legacy Environment (CrewAI 0.11.2) with Python 3.13

```bash
python3.13 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
# Edit requirements.txt to use crewai==0.11.2 temporarily
pip install -r requirements.txt
```

### Environment Configuration

Set up environment variables:

```bash
cp .env.example .env
```

Then edit the `.env` file to include your API keys:

```bash
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
OPENAI_API_KEY=your_openai_api_key_here
SERPAPI_API_KEY=your_serpapi_api_key_here
```

## Additional Dependencies

### SerpAPI Dependencies

For web search functionality, you'll need to install the SerpAPI packages:

#### For CrewAI 0.11.2 (Original Environment)
```bash
source venv/bin/activate
pip install google-search-results>=2.4.2
```

#### For CrewAI 0.102.0 (Latest Environment)
```bash
source venv_crewai_latest/bin/activate
pip install google-search-results serpapi
```

Both environments require a SerpAPI key, which you can obtain from [SerpAPI's website](https://serpapi.com/).

### Installing LangChain Tools (Latest Environment Only)

If you're using the latest CrewAI version (0.102.0), you'll need LangChain for custom tool creation:

```bash
source venv_crewai_latest/bin/activate
pip install langchain langchain-community
```

## Usage

Run the Telegram bot:

```bash
python bot.py
```

The bot will now listen for messages and route them to the appropriate specialized agents.

## Extending

To add a new specialized agent:

1. Create a new directory for the agent: `mkdir -p new_agent_name/src new_agent_name/config`
2. Define the agent in `new_agent_name/config/agents.yaml`
3. Define tasks in `new_agent_name/config/tasks.yaml`
4. Implement the CrewAI crew in `new_agent_name/src/your_agent_crew.py`
5. Update the orchestrator to include the new agent

## Project Structure

```
/
├── venv/                           # Virtual environment
├── venv_crewai_latest/             # Latest CrewAI virtual environment
├── requirements.txt                # Project dependencies
├── .env                            # Environment variables (not in repo)
├── .env.example                    # Environment variables template
├── .cursorrules                    # Project guidelines
├── bot.py                          # Telegram bot entry point
├── agent_orchestrator.py           # Orchestration layer
├── telegram_gateway_agent/         # Telegram interface agent
│   ├── src/
│   │   └── telegram_crew.py        # Telegram crew implementation
│   └── config/
│       ├── agents.yaml             # Telegram agent definition
│       └── tasks.yaml              # Telegram tasks
├── websearch_agent/                # Web search agent
│   ├── src/
│   │   └── search_crew.py          # Search crew implementation
│   └── config/
│       ├── agents.yaml             # Search agent definition
│       └── tasks.yaml              # Search tasks
├── examples/                       # Example scripts
│   ├── search_example_original.py  # Example for CrewAI 0.11.2
│   └── search_example_latest.py    # Example for CrewAI 0.102.0
├── tests/                          # Test scripts
│   └── test_crewai_version.py      # CrewAI installation verification
└── docs/                           # Documentation
    ├── crewai_version_notes.md     # Version compatibility notes
    ├── upgrade_summary.md          # Upgrade process summary
    └── how_to_agents.md            # CrewAI agent development guide
```

## License

[MIT License](LICENSE)

## Web Search Tool

The Telegram Gateway Agent project includes web search capabilities. Here's how to use the search functionality in different CrewAI versions:

### For CrewAI 0.11.2 (Original Environment)

In the original environment, the web search functionality uses the SerpAPITool:

```python
from crewai.tools import SerpAPITool

# Create a web search tool
search_tool = SerpAPITool()

# Add the tool to an agent
agent = Agent(
    role="Researcher",
    goal="Research information",
    backstory="You are a research expert",
    tools=[search_tool],
    verbose=True
)
```

### For CrewAI 0.102.0 (Latest Environment)

In the latest CrewAI version, you need to use the updated tool structure:

```python
from crewai import Agent
import os
import serpapi
from langchain.tools import BaseTool
from langchain.agents import tool

# Define a custom search tool
class CustomSearchTool(BaseTool):
    name = "web_search"
    description = "Useful to search the web for information."
    
    def _run(self, query: str) -> str:
        client = serpapi.Client(api_key=os.getenv("SERPAPI_API_KEY"))
        results = client.search({
            "engine": "google",
            "q": query
        })
        return str(results.get("organic_results", [])[:3])
        
    def _arun(self, query: str) -> str:
        return self._run(query)

# Create and use the custom search tool
search_tool = CustomSearchTool()

# Add the tool to an agent
agent = Agent(
    role="Researcher",
    goal="Research information",
    backstory="You are a research expert",
    tools=[search_tool],
    verbose=True
)
```

## Environment Variables

Make sure to set up your `.env` file with the appropriate API keys:

```
# OpenAI API Key for CrewAI to use GPT models
OPENAI_API_KEY=your_openai_api_key_here

# SerpAPI Key for web search functionality
SERPAPI_API_KEY=your_serpapi_api_key_here

# Telegram Bot Token for the Telegram Gateway Agent
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# Admin Chat ID for receiving test welcome messages
ADMIN_CHAT_ID=your_telegram_chat_id_here
```

## Testing

You can test the Telegram bot using the provided test scripts:

### Running Tests

```bash
# Activate your virtual environment first
source venv_crewai_latest/bin/activate  # For CrewAI 0.102.0
# OR
source venv/bin/activate  # For CrewAI 0.11.2

# Run all tests
./tests/run_tests.py

# Run a specific unit test
./tests/run_tests.py --test unit_test_telegram_bot

# Run the bot in manual test mode
./tests/run_tests.py --manual
```

The test suite will:
- Verify that CrewAI is installed correctly
- Test the creation of basic CrewAI components (Agent, Task, Crew)
- Report success or failure for each test

You can also run individual tests:
```bash
python tests/test_crewai_version.py
```

### Welcome Message Feature

When running the bot in manual test mode, it can send you a welcome message to help guide testing:

1. Add your Telegram chat ID to your `.env` file:
   ```
   ADMIN_CHAT_ID=your_telegram_chat_id_here
   ```
   
   To get your chat ID, start a conversation with [@userinfobot](https://t.me/userinfobot) on Telegram

2. Run the bot in manual test mode:
   ```bash
   ./tests/run_tests.py --manual
   ```

3. The bot will send you a welcome message with testing instructions, which you can respond to for immediate testing.

## Environment Variables

Make sure to set up your `.env` file with the appropriate API keys:

```
# OpenAI API Key for CrewAI to use GPT models
OPENAI_API_KEY=your_openai_api_key_here

# SerpAPI Key for web search functionality
SERPAPI_API_KEY=your_serpapi_api_key_here

# Telegram Bot Token for the Telegram Gateway Agent
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# Admin Chat ID for receiving test welcome messages
ADMIN_CHAT_ID=your_telegram_chat_id_here
``` 