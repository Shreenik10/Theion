#!/usr/bin/env python3
"""
Test runner script for OSCE Simulator models.
Run this script to execute all tests for the models.
"""

import sys
import os
import subprocess
import pytest

def run_tests():
    """Run all tests for the OSCE Simulator models."""
    print("🧪 Running OSCE Simulator Model Tests...")
    print("=" * 50)
    
    # Add the app directory to Python path
    app_dir = os.path.join(os.path.dirname(__file__), 'app')
    sys.path.insert(0, app_dir)
    
    # Test files to run
    test_files = [
        "tests/test_student_model.py",
        "tests/test_models_integration.py"
    ]
    
    # Pytest arguments
    pytest_args = [
        "-v",  # Verbose output
        "--tb=short",  # Short traceback format
        "--color=yes",  # Colored output
        "--durations=10",  # Show 10 slowest tests
        "--cov=app.models",  # Coverage for models
        "--cov-report=term-missing",  # Show missing lines
        "--cov-report=html:htmlcov",  # Generate HTML coverage report
    ]
    
    # Add test files
    pytest_args.extend(test_files)
    
    try:
        # Run pytest
        result = pytest.main(pytest_args)
        
        if result == 0:
            print("\n✅ All tests passed!")
            print("\n📊 Coverage report generated in htmlcov/")
            return True
        else:
            print(f"\n❌ Tests failed with exit code {result}")
            return False
            
    except Exception as e:
        print(f"\n💥 Error running tests: {e}")
        return False

def run_specific_test(test_file):
    """Run a specific test file."""
    print(f"🧪 Running specific test: {test_file}")
    print("=" * 50)
    
    pytest_args = [
        "-v",
        "--tb=short",
        "--color=yes",
        test_file
    ]
    
    try:
        result = pytest.main(pytest_args)
        return result == 0
    except Exception as e:
        print(f"💥 Error running test: {e}")
        return False

def run_quick_tests():
    """Run tests without coverage for faster execution."""
    print("🧪 Running quick tests (no coverage)...")
    print("=" * 50)
    
    test_files = [
        "tests/test_student_model.py",
        "tests/test_models_integration.py"
    ]
    
    pytest_args = [
        "-v",
        "--tb=short",
        "--color=yes",
    ]
    
    pytest_args.extend(test_files)
    
    try:
        result = pytest.main(pytest_args)
        return result == 0
    except Exception as e:
        print(f"💥 Error running tests: {e}")
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run OSCE Simulator model tests")
    parser.add_argument("--quick", action="store_true", help="Run tests without coverage")
    parser.add_argument("--file", type=str, help="Run specific test file")
    
    args = parser.parse_args()
    
    if args.file:
        success = run_specific_test(args.file)
    elif args.quick:
        success = run_quick_tests()
    else:
        success = run_tests()
    
    sys.exit(0 if success else 1)
