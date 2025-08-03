#!/usr/bin/env python3
"""
Test script for Ollama AI setup
Run this to verify Ollama is working before using the main app
"""

import sys
import os

# Add the current directory to path
sys.path.append(os.path.dirname(__file__))

from my_agent.Nodes.Call_Api import call_openrouter

def test_ai():
    print("🤖 Testing Ollama Setup...")
    print("=" * 50)
    
    test_prompt = "Hello! Please respond briefly that you are working correctly."
    
    try:
        print("� Testing Ollama...")
        response = call_openrouter(test_prompt)
        print("✅ OLLAMA SUCCESS!")
        print(f"🤖 Response: {response}")
        print("\n🎉 Ollama is working! You can now use your application.")
        return True
        
    except Exception as e:
        print("❌ OLLAMA ERROR!")
        print(f"Error: {str(e)}")
        print("\n📋 Make sure:")
        print("1. Ollama is installed from https://ollama.ai")
        print("2. Model is downloaded: ollama run llama3.2:1b")
        print("3. Ollama is running (the download command should complete)")
        return False

if __name__ == "__main__":
    success = test_ai()
    if not success:
        sys.exit(1)
