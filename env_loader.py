#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Environment Variable Loader

This module provides centralized loading of environment variables from .env files.
It handles locating and loading the .env file regardless of the script's execution directory.
"""

import os
import logging
from pathlib import Path
from dotenv import load_dotenv, find_dotenv

logger = logging.getLogger(__name__)

def load_environment(debug=False):
    """
    Load environment variables from .env file.
    
    This function searches for .env files in multiple potential locations
    to ensure environment variables are properly loaded regardless of the
    script's execution directory.
    
    Args:
        debug (bool): Whether to log debug information during loading
        
    Returns:
        bool: True if environment variables were successfully loaded, False otherwise
    """
    # Possible locations for .env file
    possible_locations = [
        os.getcwd(),                          # Current directory
        str(Path(os.getcwd()).parent),        # Parent directory
        str(Path(__file__).parent),           # Directory of this script
        str(Path(__file__).parent.parent),    # Parent of this script's directory
        os.path.expanduser('~'),              # User's home directory
    ]
    
    # Try to find .env.test first (for test environment)
    for location in possible_locations:
        env_test_path = os.path.join(location, '.env.test')
        if os.path.exists(env_test_path):
            if debug:
                logger.info(f"Loading test environment from: {env_test_path}")
            load_dotenv(env_test_path)
            os.environ['TEST_MODE'] = 'True'
            return True
    
    # Try automatic detection first
    dotenv_path = find_dotenv(usecwd=True)
    if dotenv_path:
        if debug:
            logger.info(f"Loading environment from auto-detected path: {dotenv_path}")
        load_dotenv(dotenv_path)
        return True
    
    # If auto-detection fails, try explicit locations
    for location in possible_locations:
        env_path = os.path.join(location, '.env')
        if os.path.exists(env_path):
            if debug:
                logger.info(f"Loading environment from: {env_path}")
            load_dotenv(env_path)
            return True
    
    # If we got here, we couldn't find a .env file
    if debug:
        logger.warning("No .env file found in any of the searched locations")
        logger.warning(f"Searched locations: {possible_locations}")
    
    return False

if __name__ == "__main__":
    # Configure logging for testing
    logging.basicConfig(level=logging.DEBUG)
    
    # Try to load environment variables
    success = load_environment(debug=True)
    
    if success:
        print("Environment variables loaded successfully")
        # Print some non-sensitive environment variables as a test
        print(f"LITELLM_PROVIDER: {os.getenv('LITELLM_PROVIDER', 'not set')}")
        print(f"TEST_MODE: {os.getenv('TEST_MODE', 'not set')}")
    else:
        print("Failed to load environment variables") 