# Secrets Folder

This folder contains credential files and other secrets required by the agents. 
**The contents of this folder are excluded from version control by .gitignore.**

## Structure

The secrets folder is organized by agent type:

```
secrets/
├── README.md
├── calendar/        # Google Calendar credentials and tokens
├── telegram/        # Telegram bot credentials
└── ... other agents
```

## Setting Up Credentials

### Calendar Agent

1. Place your `credentials.json` file in `secrets/calendar/`
2. Place your `token.json` file in `secrets/calendar/` (or it will be generated there)

### Telegram Agent

1. Place any Telegram-specific credential files in `secrets/telegram/`

## Environment Variables

For maximum flexibility, the system will check for credentials in this order:

1. Environment variables defined in .env file
2. Files in this secrets directory
3. Files in the agent's own directory (legacy support)

## Security Notes

- NEVER commit the contents of this folder to version control
- Be careful when sharing your codebase not to include this folder
- For deployments, consider using environment variables or secure secret management services 