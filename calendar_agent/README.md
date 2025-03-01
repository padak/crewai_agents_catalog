# Calendar Agent

This agent integrates with Google Calendar to allow querying and managing calendar events.

## Setup Instructions

### 1. Set up Google Calendar API credentials

1. Visit the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Calendar API
4. Create OAuth 2.0 credentials
   - Application type: Desktop application
   - Download the credentials.json file

### 2. Prepare the credential files

You have several options for storing your Google Calendar credentials:

#### Option 1: Use the secrets folder (Recommended)
1. Place your `credentials.json` file in `secrets/calendar/`
2. The first time you run the agent, it will authenticate and generate a `token.json` file in the same location

#### Option 2: Use environment variables
Set the following environment variables in your `.env` file:
```
GOOGLE_CALENDAR_CLIENT_ID=your_client_id
GOOGLE_CALENDAR_PROJECT_ID=your_project_id
GOOGLE_CALENDAR_CLIENT_SECRET=your_client_secret
```

#### Option 3: Use the calendar_agent directory (Legacy)
1. Copy `credentials.template.json` to `credentials.json` within the calendar_agent directory
2. Replace the placeholder values with your actual Google API credentials

IMPORTANT: Regardless of which method you choose, NEVER commit credential files to version control.

### 3. Environment Variables

Set the following environment variables:
- `GOOGLE_CREDENTIALS_PATH`: Path to your credentials.json file (optional, defaults to looking in the current directory)
- `GOOGLE_TOKEN_PATH`: Path to your token.json file (optional, defaults to looking in the current directory)
- `ANTHROPIC_API_KEY`: Your Anthropic API key for Claude

## Usage

The calendar agent can handle various calendar-related queries in both English and Czech:

- "What meetings do I have today?"
- "When is my next meeting?"
- "Am I free tomorrow afternoon?"
- "Jaké schůzky mám dnes?"
- "Kdy je moje další jednání?"

## Note on Security

- **IMPORTANT**: Never commit your actual `credentials.json` and `token.json` files to version control
- These files contain sensitive Google OAuth credentials that should be kept private
- Use the template files as references only and keep your actual credential files secure

## Features

- Query upcoming events
- Check availability for specific times
- Find events by keywords or participants
- Works with both Anthropic Claude and OpenAI GPT models

## Setup Instructions

### Prerequisites

1. Python 3.8 or later
2. Google account with Calendar enabled
3. A CrewAI-compatible LLM (Claude or GPT)

### Installation

1. The agent is included in the main project. Make sure you've installed all dependencies:
   ```
   pip install -r requirements.txt
   ```

### First-time Authentication

When you first run the Calendar Agent, it will prompt you to authenticate:

1. A browser window will open asking you to log in to your Google account
2. Grant permissions for the application to access your calendar (read-only)
3. After authentication, the token will be saved to `calendar_agent/token.json` for future use

## Testing the Calendar Agent

You can test the Calendar Agent using the provided test script:

```
python calendar_agent/test_calendar_agent.py
```

This will start an interactive session where you can enter calendar queries directly.

## Example Queries

You can ask the Calendar Agent questions like:

- "What meetings do I have today?"
- "Am I free tomorrow afternoon?"
- "Do I have any events about project planning this week?"
- "When is my next meeting with Alex?"
- "What's on my calendar for next Monday?"

## Integration with Other Agents

The Calendar Agent is integrated into the main orchestrator and can be accessed through the Telegram interface. The orchestrator will automatically route calendar-related queries to this agent.

## Using with Anthropic Claude

The Calendar Agent supports both OpenAI GPT and Anthropic Claude models. To use Claude:

1. Make sure you have an Anthropic API key
2. Add it to your `.env` file: `ANTHROPIC_API_KEY=your_api_key_here`
3. Set `LITELLM_PROVIDER=anthropic` in your `.env` file
4. (Optional) Set `ANTHROPIC_MODEL=claude-3-opus-20240229` to choose a specific model

## Troubleshooting

- **Authentication Issues**: If you encounter authentication problems, delete the `token.json` file and try again.
- **API Limits**: The Google Calendar API has usage limits. If you receive errors about quota limits, you may need to wait or adjust your usage patterns.
- **Model Selection**: If you're having issues with a specific LLM, try switching between Anthropic and OpenAI by changing the `LITELLM_PROVIDER` environment variable. 