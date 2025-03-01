#!/usr/bin/env python3
"""
Test runner script for the CrewAI project.
Executes all test scripts in the tests directory.
"""

import os
import sys
import importlib.util
import subprocess

def run_test(test_file):
    """Run a single test file and report the result."""
    print(f"Running {test_file}...")
    result = subprocess.run(
        [sys.executable, test_file],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print(f"✅ {test_file} passed")
        print(result.stdout)
        return True
    else:
        print(f"❌ {test_file} failed")
        print(result.stdout)
        print(result.stderr)
        return False

def main():
    """Run all test files in the tests directory."""
    # Get the directory of this script
    tests_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Find all Python files in the tests directory
    test_files = [
        os.path.join(tests_dir, f) 
        for f in os.listdir(tests_dir) 
        if f.endswith('.py') and f != os.path.basename(__file__)
    ]
    
    if not test_files:
        print("No test files found.")
        return 0
    
    print(f"Found {len(test_files)} test files.")
    
    # Run each test file
    successes = 0
    failures = 0
    
    for test_file in test_files:
        if run_test(test_file):
            successes += 1
        else:
            failures += 1
    
    # Print summary
    print("\n=== Test Summary ===")
    print(f"Total tests: {len(test_files)}")
    print(f"Successes: {successes}")
    print(f"Failures: {failures}")
    
    return 0 if failures == 0 else 1

if __name__ == "__main__":
    sys.exit(main()) 