#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test Runner Script

Executes all tests in the tests directory.
"""

import os
import sys
import unittest
import argparse

def run_all_tests():
    """Run all test cases in the tests directory"""
    # Add the parent directory to the path
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    
    # Discover and run all tests
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(os.path.abspath(__file__))
    suite = loader.discover(start_dir, pattern="*test*.py")
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

def run_specific_test(test_name):
    """Run a specific test by name"""
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    
    if not test_name.endswith('.py'):
        test_name += '.py'
    
    # Check if the test file exists
    test_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), test_name)
    if not os.path.exists(test_path):
        print(f"Error: Test file '{test_name}' not found")
        return False
    
    # Run the specific test
    test_module = test_name[:-3]  # Remove .py extension
    suite = unittest.defaultTestLoader.loadTestsFromName(test_module)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

def main():
    parser = argparse.ArgumentParser(description='Run tests for the CrewAI project')
    parser.add_argument('--test', '-t', help='Specific test to run (e.g., unit_test_telegram_bot)')
    parser.add_argument('--manual', '-m', action='store_true', 
                       help='Run manual test for Telegram bot (starts the bot)')
    
    args = parser.parse_args()
    
    if args.manual:
        # Import and run the manual test for the Telegram bot
        print("=== Running Manual Telegram Bot Test ===")
        import test_telegram_bot
        sys.exit(0)
    
    if args.test:
        success = run_specific_test(args.test)
    else:
        success = run_all_tests()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main()) 