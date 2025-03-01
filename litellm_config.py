#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
LiteLLM Configuration for ProjectID Keys

This script sets up LiteLLM to work with ProjectID format OpenAI keys.
Run this script before using CrewAI.
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

# Set the LITELLM_API_KEY environment variable
api_key = os.getenv("OPENAI_API_KEY")
if api_key:
    os.environ["LITELLM_API_KEY"] = api_key
    print(f"✅ Set LITELLM_API_KEY environment variable")

# Set the OPENAI_API_TYPE environment variable
os.environ["OPENAI_API_TYPE"] = "open_ai"
print(f"✅ Set OPENAI_API_TYPE environment variable")

# Import and configure litellm
try:
    import litellm
    
    # Configure LiteLLM
    litellm.api_key = api_key
    
    # Set verbose mode for debugging
    os.environ["LITELLM_LOG"] = "DEBUG"
    
    # Test LiteLLM configuration
    try:
        print("Testing LiteLLM with ProjectID key...")
        response = litellm.completion(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=5
        )
        print(f"✅ LiteLLM test successful: {response.choices[0].message.content}")
    except Exception as e:
        print(f"❌ LiteLLM test failed: {str(e)}")
        
    print("\nLiteLLM configuration complete. You can now use CrewAI.")
    print("To use this configuration, run the following command before starting your agents:")
    print(f"python {__file__}")
    
except ImportError:
    print("LiteLLM not installed. Installing...")
    os.system(f"{sys.executable} -m pip install litellm")
    print("Please run this script again to configure LiteLLM.")
    
if __name__ == "__main__":
    print("LiteLLM Configuration")
    print("====================")
    print("This script configures LiteLLM to work with ProjectID format OpenAI keys.") 