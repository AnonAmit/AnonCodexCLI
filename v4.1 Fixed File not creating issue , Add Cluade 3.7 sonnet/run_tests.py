#!/usr/bin/env python
"""
Test runner for AnonCodexCli project
Executes all test files in the tests directory
"""
import os
import sys
import unittest
import importlib.util

def discover_and_load_tests():
    """Discover and load all test modules in the tests directory."""
    test_dir = os.path.join(os.path.dirname(__file__), "tests")
    
    # Create tests directory if it doesn't exist
    if not os.path.exists(test_dir):
        os.makedirs(test_dir)
        print(f"Created tests directory at {test_dir}")
        return unittest.TestSuite()
    
    # Load all test files
    test_suite = unittest.TestSuite()
    test_loader = unittest.TestLoader()
    
    for file in os.listdir(test_dir):
        if file.startswith("test_") and file.endswith(".py"):
            module_name = os.path.splitext(file)[0]
            module_path = os.path.join(test_dir, file)
            
            # Dynamically import the module
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Add tests to the suite
            for item in dir(module):
                if item.startswith("Test"):
                    test_class = getattr(module, item)
                    if isinstance(test_class, type) and issubclass(test_class, unittest.TestCase):
                        # Use TestLoader.loadTestsFromTestCase instead of makeSuite
                        test_suite.addTest(test_loader.loadTestsFromTestCase(test_class))
    
    return test_suite

def main():
    """Run all tests and report results."""
    print("=" * 70)
    print("Running tests for AnonCodexCli")
    print("=" * 70)
    
    test_suite = discover_and_load_tests()
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)
    
    print("\n" + "=" * 70)
    print(f"Test Results: {result.testsRun} tests run")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    print("=" * 70)
    
    # Return non-zero exit code if tests failed
    return 0 if result.wasSuccessful() else 1

if __name__ == "__main__":
    sys.exit(main()) 