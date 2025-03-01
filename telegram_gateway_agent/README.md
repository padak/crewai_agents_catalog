# CrewAI Telegram Gateway Agent

This project implements a Telegram bot that acts as a gateway to CrewAI agents. It allows users to interact with specialized AI agents through a Telegram chat interface.

## Features

- Conversational interface through Telegram
- Maintains conversation history for context
- Routes user requests to specialized AI agents
- Web search capability using Serper API

## Setup Instructions

### Prerequisites

- Python 3.9+
- A Telegram bot token (obtain from BotFather)
- OpenAI API key
- Serper API key for web search functionality

### Installation

1. Set up the virtual environment from the repository root:
   ```bash
   # Navigate to the repository root (parent directory)
   cd ..
   
   # Activate the virtual environment
   # On macOS/Linux:
   source venv/bin/activate
   # On Windows:
   # venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

2. Create a `.env` file based on `.env.example` and fill in your API keys:
   ```bash
   cp .env.example .env
   # Edit .env with your actual API keys
   ```

### Running the Bot

Make sure the virtual environment is activated, then run:

```bash
python bot.py
```

The bot will start and listen for messages on Telegram.

## Usage

1. Start a chat with your bot on Telegram
2. Use `/start` to get a welcome message
3. Use `/help` to see usage instructions
4. Send any message to interact with the AI agents

## Extending with Additional Agents

To add more specialized agents:

1. Add new agent definitions in `config/agents.yaml`
2. Create new task definitions in `config/tasks.yaml`
3. Update the `TelegramCrew` class in `src/telegram_crew.py` to include these new agents and tasks
4. Modify the message handling logic to route requests to the appropriate agents

## Project Structure

- `bot.py` - Main Telegram bot interface
- `src/telegram_crew.py` - CrewAI implementation
- `config/agents.yaml` - Agent definitions
- `config/tasks.yaml` - Task definitions
- `../requirements.txt` - Project dependencies (at repository root)
- `.env` - Environment variables (API keys, etc.)

## License

MIT 