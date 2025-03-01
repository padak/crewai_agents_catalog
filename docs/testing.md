# Testing the Telegram Bot

This document explains how to test the Telegram bot in the CrewAI project.

## Prerequisites

Before testing the Telegram bot, ensure you have:

1. Set up your Python environment and installed dependencies:
   ```bash
   source venv_crewai_latest/bin/activate
   pip install -r requirements.txt
   ```

2. Created a test bot on Telegram:
   - Contact [@BotFather](https://t.me/botfather) on Telegram
   - Send `/newbot` command and follow the instructions
   - Keep the API token provided by BotFather

3. Created a `.env.test` file with your test credentials:
   ```
   TELEGRAM_BOT_TOKEN=your_test_bot_token
   OPENAI_API_KEY=your_openai_api_key
   # Add other required variables
   ```

## Testing Options

### 1. Manual Testing

For manual testing with a real Telegram bot:

```bash
# Activate your virtual environment first
source venv_crewai_latest/bin/activate

# Run the manual test script
python tests/run_tests.py --manual
```

This will:
- Load your test credentials from `.env.test`
- Start the bot in test mode
- Connect to the Telegram API
- Allow you to interact with your bot via Telegram

### 2. Running Unit Tests

To run automated unit tests (which use mocks and don't require a real Telegram connection):

```bash
# Activate your virtual environment first
source venv_crewai_latest/bin/activate

# Run all tests
python tests/run_tests.py

# Run only the Telegram bot tests
python tests/run_tests.py --test unit_test_telegram_bot
```

## Test Structure

- `tests/test_telegram_bot.py`: Manual testing script that runs the bot with test credentials
- `tests/unit_test_telegram_bot.py`: Unit tests for bot functionality using mocks
- `tests/run_tests.py`: Test runner script that can run individual tests or all tests

## Common Testing Issues

1. **Authentication Errors**: Ensure your bot token in `.env.test` is correct
2. **Module Not Found**: Make sure you've activated the virtual environment with all dependencies
3. **Telegram API Rate Limits**: If you receive rate limit errors, wait before retrying

## Adding New Tests

When adding new functionality to the bot:

1. Add unit tests in `tests/unit_test_telegram_bot.py`
2. Test new commands manually with the test bot
3. Document any new testing procedures in this file 