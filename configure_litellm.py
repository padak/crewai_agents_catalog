#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
LiteLLM Configuration Script

This script configures LiteLLM to use a ProjectID format OpenAI API key.
Run this script before starting your agents.
"""

import os
import litellm
from dotenv import load_dotenv

def configure_litellm():
    """Configure LiteLLM with the correct API key and settings."""
    # Load environment variables
    load_dotenv()
    
    # Get API key from environment
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not found.")
        return False
    
    try:
        # Set LiteLLM configuration
        litellm.set_verbose = True  # Enable verbose logging
        
        # Configure LiteLLM to accept ProjectID keys
        litellm.api_key = api_key
        
        # Set additional configuration if needed
        # litellm.organization = os.getenv("OPENAI_ORG_ID")  # Uncomment if you have an org ID
        
        print("LiteLLM successfully configured.")
        return True
    except Exception as e:
        print(f"Error configuring LiteLLM: {str(e)}")
        return False

if __name__ == "__main__":
    print("Configuring LiteLLM for CrewAI...")
    success = configure_litellm()
    
    if success:
        print("Configuration successful. You can now run your CrewAI agents.")
    else:
        print("Configuration failed. Please check your API key and try again.") 