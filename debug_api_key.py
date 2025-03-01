#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Debug API Key issues with CrewAI and LiteLLM

This script tests the OpenAI API key directly and through LiteLLM
to diagnose authentication issues.
"""

import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv
import requests

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Load environment variables
load_dotenv()

def test_openai_key_directly():
    """Test the OpenAI API key directly through the REST API."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY not found in environment variables.")
        return False
    
    print(f"Testing API key: {api_key[:10]}...{api_key[-5:]}")
    
    # Make a simple API call to OpenAI
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": "Hello"}],
        "max_tokens": 5
    }
    
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data
        )
        
        if response.status_code == 200:
            print("✅ OpenAI API key is valid when tested directly.")
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"❌ OpenAI API key failed with status {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing OpenAI API key directly: {str(e)}")
        return False

def test_litellm():
    """Test the LiteLLM library with the API key."""
    try:
        import litellm
        
        # Get API key from environment
        api_key = os.getenv("OPENAI_API_KEY")
        litellm_key = os.getenv("LITELLM_API_KEY")
        
        key_to_use = litellm_key or api_key
        
        if not key_to_use:
            print("Error: No API key found in environment variables.")
            return False
            
        print(f"Testing with LiteLLM using key: {key_to_use[:10]}...{key_to_use[-5:]}")
        
        # Configure LiteLLM
        litellm.api_key = key_to_use
        litellm.set_verbose = True
        
        # Try a completion
        try:
            response = litellm.completion(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5
            )
            print("✅ LiteLLM test successful.")
            print(f"Response: {response}")
            return True
            
        except Exception as e:
            print(f"❌ LiteLLM completion error: {str(e)}")
            return False
            
    except ImportError:
        print("❌ LiteLLM library not installed. Install with: pip install litellm")
        return False
        
def test_crewai_simple():
    """Test a minimal CrewAI setup."""
    try:
        from crewai import Agent
        
        print("Testing minimal CrewAI setup...")
        
        try:
            # Create a simple agent
            agent = Agent(
                role="Tester",
                goal="Test API key",
                backstory="I am a test agent",
                verbose=True
            )
            
            # Test the agent with a simple task
            result = agent.execute_task("Say hello")
            
            print("✅ CrewAI test successful.")
            print(f"Result: {result}")
            return True
            
        except Exception as e:
            print(f"❌ CrewAI test error: {str(e)}")
            return False
            
    except ImportError:
        print("❌ CrewAI library not installed. Install with: pip install crewai")
        return False

if __name__ == "__main__":
    print("API Key Debug Script")
    print("===================\n")
    
    print("1. Testing OpenAI API key directly...")
    direct_test = test_openai_key_directly()
    print()
    
    print("2. Testing with LiteLLM...")
    litellm_test = test_litellm()
    print()
    
    print("3. Testing minimal CrewAI setup...")
    crewai_test = test_crewai_simple()
    print()
    
    print("Summary:")
    print(f"- Direct API test: {'✅ Passed' if direct_test else '❌ Failed'}")
    print(f"- LiteLLM test: {'✅ Passed' if litellm_test else '❌ Failed'}")
    print(f"- CrewAI test: {'✅ Passed' if crewai_test else '❌ Failed'}")
    
    if not direct_test and not litellm_test and not crewai_test:
        print("\nSuggested fixes:")
        print("1. Check if your API key is valid and has sufficient credit.")
        print("2. Try a different API key format (standard OpenAI key starting with sk-, not sk-proj-).")
        print("3. Set OPENAI_API_BASE environment variable if using a custom endpoint.")
    elif not litellm_test or not crewai_test:
        print("\nSuggested fixes:")
        print("1. Your API key works directly but not with LiteLLM/CrewAI.")
        print("2. Try installing specific versions: pip install litellm==0.11.0 crewai==0.102.0")
        print("3. Check CrewAI documentation for API key format requirements.") 