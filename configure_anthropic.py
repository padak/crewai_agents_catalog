#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Configure Anthropic for use with CrewAI

This script sets up the environment variables and configuration files needed
to use Anthropic's Claude models with CrewAI. It validates the API key and
creates a configuration file if needed.
"""

import os
import yaml
from pathlib import Path
import sys
from dotenv import load_dotenv

def main():
    # Load environment variables from .env file
    load_dotenv()
    
    # Check if ANTHROPIC_API_KEY is set
    anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
    if not anthropic_api_key:
        print("❌ ANTHROPIC_API_KEY not found in environment variables.")
        print("Please add it to your .env file or set it in your environment.")
        return False
    
    # Set environment variables for the session
    os.environ['ANTHROPIC_API_KEY'] = anthropic_api_key
    os.environ['LITELLM_PROVIDER'] = 'anthropic'
    
    print("✓ Environment variable ANTHROPIC_API_KEY is set")
    print("✓ Environment variable LITELLM_PROVIDER=anthropic is set")
    
    # Test Anthropic API key
    try:
        from anthropic import Anthropic
        client = Anthropic(api_key=anthropic_api_key)
        message = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=100,
            messages=[{"role": "user", "content": "Hello, please respond with a simple greeting."}]
        )
        print(f"✓ Anthropic API key works! Response: {message.content[0].text}")
    except ImportError:
        print("❌ Could not import Anthropic. Please install it with: pip install anthropic>=0.19.0")
        return False
    except Exception as e:
        print(f"❌ Error testing Anthropic API key: {e}")
        return False
    
    # Create crew_config.yaml file
    config_path = Path('crew_config.yaml')
    config = {
        'llm': {
            'config': {
                'model': os.getenv('ANTHROPIC_MODEL', 'claude-3-opus-20240229'),
                'temperature': float(os.getenv('ANTHROPIC_TEMPERATURE', '0.7')),
                'max_tokens': int(os.getenv('ANTHROPIC_MAX_TOKENS', '4000')),
                'anthropic_api_key': anthropic_api_key,
            }
        }
    }
    
    with open(config_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)
    
    print(f"✓ Created configuration file: {config_path}")
    
    # Check if Calendar Agent is configured
    calendar_agent_path = Path('calendar_agent/src/calendar_crew.py')
    if calendar_agent_path.exists():
        print("✓ Calendar Agent found. It's already configured to support Anthropic Claude.")
    else:
        print("⚠️ Calendar Agent not found or has non-standard format.")
        print("Please follow the instructions in calendar_agent/README.md to set it up.")
    
    print("\n✅ Setup complete! You can now use Anthropic Claude with CrewAI.")
    print("Test your Calendar Agent with: python calendar_agent/test_calendar_agent.py")
    return True

if __name__ == "__main__":
    if not main():
        sys.exit(1) 