#!/usr/bin/env python3
"""Check GPT API functionality for the recipe finder.

This script verifies that the GPT API is working correctly and
provides helpful error messages if there are any issues.

Usage:
    python check_gpt_api.py
"""

import os
import sys
from pathlib import Path

from openai import OpenAI

def check_api_key() -> bool:
    """Verify that the OpenAI API key is set and valid."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable is not set")
        print("Please set it in your .env file or environment")
        return False

    try:
        client = OpenAI(api_key=api_key)
        # Make a minimal API call to verify the key
        client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": "test"}],
            max_tokens=5,
        )
        print("✓ API key is valid")
        return True
    except Exception as exc:
        print(f"Error: API key validation failed: {exc}")
        return False

def check_model_access() -> bool:
    """Verify that we can access the required GPT model."""
    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        # Try to get model info
        models = client.models.list()
        available_models = [model.id for model in models.data]
        
        if "gpt-4" not in available_models:
            print("Error: GPT-4 model is not available with your API key")
            print("Available models:", ", ".join(available_models))
            return False
            
        print("✓ GPT-4 model is available")
        return True
    except Exception as exc:
        print(f"Error: Failed to check model access: {exc}")
        return False

def check_file_permissions() -> bool:
    """Verify that we have proper permissions for file operations."""
    output_dir = Path("/srv/homeassistant/ai")
    recipes_dir = output_dir / "recipes"
    
    try:
        # Check if directories exist or can be created
        output_dir.mkdir(parents=True, exist_ok=True)
        recipes_dir.mkdir(parents=True, exist_ok=True)
        
        # Check if we can write to the directories
        test_file = recipes_dir / "test.txt"
        test_file.write_text("test")
        test_file.unlink()
        
        print("✓ File permissions are correct")
        return True
    except Exception as exc:
        print(f"Error: File permission check failed: {exc}")
        return False

def main() -> None:
    """Run all checks and provide a summary."""
    print("Checking GPT API functionality...\n")
    
    checks = [
        ("API Key", check_api_key),
        ("Model Access", check_model_access),
        ("File Permissions", check_file_permissions),
    ]
    
    all_passed = True
    for name, check_func in checks:
        print(f"\nChecking {name}...")
        if not check_func():
            all_passed = False
    
    print("\nSummary:")
    if all_passed:
        print("✓ All checks passed! The recipe finder should work correctly.")
    else:
        print("✗ Some checks failed. Please fix the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 