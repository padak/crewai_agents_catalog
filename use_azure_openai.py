#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Configure CrewAI to use Azure OpenAI

This script configures CrewAI to use Azure OpenAI services as a fallback.
Many users find that Azure OpenAI works better with CrewAI.
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

def setup_azure_openai():
    """
    Setup environment variables for Azure OpenAI.
    
    This function will:
    1. Prompt the user for Azure OpenAI credentials
    2. Add them to the .env file
    3. Configure CrewAI to use Azure OpenAI
    """
    print("Setting up Azure OpenAI Configuration")
    print("====================================")
    print("\nYou'll need the following information from your Azure OpenAI resource:")
    print("1. API key")
    print("2. Endpoint URL")
    print("3. Deployment name (for chat models)")
    print("\nYou can find this information in the Azure portal under your OpenAI resource.\n")
    
    # Get user input
    azure_api_key = input("Enter your Azure OpenAI API key: ").strip()
    azure_endpoint = input("Enter your Azure OpenAI endpoint URL: ").strip()
    azure_deployment = input("Enter your Azure OpenAI deployment name for chat models: ").strip()
    
    if not azure_api_key or not azure_endpoint or not azure_deployment:
        print("Error: All fields are required.")
        return False
    
    # Update .env file
    env_path = project_root / ".env"
    
    if not env_path.exists():
        print(f"Error: .env file not found at {env_path}")
        return False
    
    try:
        # Read existing .env content
        env_content = env_path.read_text()
        
        # Check if Azure variables already exist
        has_azure_api = "AZURE_OPENAI_API_KEY" in env_content
        has_azure_endpoint = "AZURE_OPENAI_API_BASE" in env_content
        has_azure_deployment = "AZURE_OPENAI_DEPLOYMENT_NAME" in env_content
        
        # Prepare new content
        new_content = env_content
        
        # Add lines as needed
        if not has_azure_api:
            new_content += f"\n# Azure OpenAI credentials\nAZURE_OPENAI_API_KEY={azure_api_key}\n"
        if not has_azure_endpoint:
            new_content += f"AZURE_OPENAI_API_BASE={azure_endpoint}\n"
        if not has_azure_deployment:
            new_content += f"AZURE_OPENAI_DEPLOYMENT_NAME={azure_deployment}\n"
        
        # Add the litellm_provider variable if it doesn't exist
        if "LITELLM_PROVIDER" not in new_content:
            new_content += f"LITELLM_PROVIDER=azure\n"
        
        # Write back to .env
        env_path.write_text(new_content)
        
        print("\n✅ Azure OpenAI configuration added to .env file.")
        
        # Create a minimal litellm_config.yaml file
        create_litellm_config()
        
        return True
    
    except Exception as e:
        print(f"Error updating .env file: {str(e)}")
        return False

def create_litellm_config():
    """Create a litellm_config.yaml file to map model names."""
    config_path = project_root / "litellm_config.yaml"
    
    config_content = """# LiteLLM configuration file
model_list:
  - model_name: gpt-4
    litellm_params:
      model: azure/deployment-name
      api_base: ${AZURE_OPENAI_API_BASE}
      api_key: ${AZURE_OPENAI_API_KEY}
      
  - model_name: gpt-3.5-turbo
    litellm_params:
      model: azure/deployment-name
      api_base: ${AZURE_OPENAI_API_BASE}
      api_key: ${AZURE_OPENAI_API_KEY}
"""
    
    try:
        config_path.write_text(config_content)
        print("✅ Created litellm_config.yaml file.")
        print("NOTE: You need to edit this file to replace 'deployment-name' with your actual deployment names.")
        return True
    except Exception as e:
        print(f"Error creating litellm_config.yaml: {str(e)}")
        return False

def configure_crewai_for_azure():
    """
    Configure CrewAI to use Azure OpenAI.
    """
    try:
        # Check if litellm is installed
        try:
            import litellm
        except ImportError:
            print("Installing litellm...")
            os.system(f"{sys.executable} -m pip install litellm")
        
        # Set environment variables to ensure they're available in the current process
        os.environ["LITELLM_PROVIDER"] = "azure"
        
        print("\n✅ Environment configured for Azure OpenAI.")
        print("You can now run your CrewAI agents with Azure OpenAI.")
        
        return True
    except Exception as e:
        print(f"Error configuring environment: {str(e)}")
        return False

if __name__ == "__main__":
    print("Azure OpenAI Configuration for CrewAI")
    print("=====================================\n")
    
    # Setup Azure OpenAI
    if setup_azure_openai():
        # Configure CrewAI for Azure
        if configure_crewai_for_azure():
            print("\nSetup complete! You can now run your CrewAI agents with Azure OpenAI.")
            print("To test, run: python debug_api_key.py")
    else:
        print("\nSetup failed. Please try again or continue with standard OpenAI API.") 