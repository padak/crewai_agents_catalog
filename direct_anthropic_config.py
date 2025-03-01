#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Configure CrewAI to use Anthropic Claude directly

This script sets up CrewAI to use Anthropic Claude directly, without relying on LiteLLM.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Load environment variables
load_dotenv()

def setup_direct_anthropic():
    """
    Configure the environment for using Anthropic Claude directly with CrewAI.
    """
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    
    if not anthropic_key:
        print("Error: ANTHROPIC_API_KEY not set in .env file")
        
        # Prompt for API key
        key = input("Enter your Anthropic API key: ").strip()
        if not key:
            print("No API key provided. Exiting.")
            return False
            
        # Update .env file with the key
        env_path = project_root / ".env"
        with open(env_path, "r") as f:
            env_content = f.read()
        
        if "ANTHROPIC_API_KEY=" in env_content:
            env_content = env_content.replace(
                f"ANTHROPIC_API_KEY={os.getenv('ANTHROPIC_API_KEY', '')}",
                f"ANTHROPIC_API_KEY={key}"
            )
        else:
            env_content += f"\nANTHROPIC_API_KEY={key}"
        
        with open(env_path, "w") as f:
            f.write(env_content)
            
        anthropic_key = key
        print("✅ Updated .env file with Anthropic API key")
    
    # Test the Anthropic API
    try:
        from anthropic import Anthropic
        
        print("\nTesting Anthropic configuration...")
        
        try:
            client = Anthropic(api_key=anthropic_key)
            message = client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=10,
                messages=[{"role": "user", "content": "Hello, Claude!"}]
            )
            print(f"✅ Anthropic test successful: {message.content[0].text}")
            return True
        except Exception as e:
            print(f"❌ Anthropic test failed: {str(e)}")
            return False
    
    except ImportError:
        print("Anthropic package not installed. Installing...")
        os.system(f"{sys.executable} -m pip install 'anthropic>=0.19.0'")
        print("Please run this script again.")
        return False

def update_all_agents():
    """Update all agent configurations to use Anthropic directly."""
    
    # Update the .env file to set Anthropic as the default provider
    env_path = project_root / ".env"
    with open(env_path, "r") as f:
        env_content = f.read()
    
    if "LITELLM_PROVIDER=" in env_content:
        env_content = env_content.replace(
            f"LITELLM_PROVIDER={os.getenv('LITELLM_PROVIDER', 'openai')}",
            "LITELLM_PROVIDER=anthropic"
        )
    else:
        env_content += "\nLITELLM_PROVIDER=anthropic"
    
    # Add other Anthropic configuration variables if needed
    if "ANTHROPIC_MODEL=" not in env_content:
        env_content += "\nANTHROPIC_MODEL=claude-3-opus-20240229"
    
    if "ANTHROPIC_TEMPERATURE=" not in env_content:
        env_content += "\nANTHROPIC_TEMPERATURE=0.7"
    
    if "ANTHROPIC_MAX_TOKENS=" not in env_content:
        env_content += "\nANTHROPIC_MAX_TOKENS=4000"
    
    with open(env_path, "w") as f:
        f.write(env_content)
    
    print("✅ Updated .env file with Anthropic configuration")
    print("✅ All agents will now use Anthropic Claude by default")
    
    return True

if __name__ == "__main__":
    print("Direct Anthropic Configuration for CrewAI")
    print("========================================\n")
    
    success = setup_direct_anthropic()
    
    if success:
        print("\nUpdating agent configurations for Anthropic...")
        update_all_agents()
        
        print("\nSetup complete! All agents will now use Anthropic Claude directly.")
        print("To test the Calendar Agent with Claude, run:")
        print("python calendar_agent/test_calendar_agent.py")
    else:
        print("\nAnthropic setup failed. Please check your API key and try again.") 