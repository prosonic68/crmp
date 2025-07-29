#!/usr/bin/env python3
"""
Simple test script to verify AI assistant is working
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

def test_ai_setup():
    """Test if AI assistant is properly configured"""
    print("🧪 Testing AI Assistant Setup...")
    
    # Check if API key is loaded
    api_key = os.getenv('GEMINI_API_KEY')
    print(f"✅ API Key found: {'Yes' if api_key else 'No'}")
    
    if not api_key:
        print("❌ No API key found. Please check your .env file")
        return False
    
    print(f"✅ API Key length: {len(api_key)} characters")
    
    try:
        # Configure Gemini
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        
        # Test a simple response
        response = model.generate_content("Hello! Can you respond with 'AI is working!'?")
        
        print("✅ AI Response received:")
        print(f"📝 Response: {response.text}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing AI: {e}")
        return False

if __name__ == "__main__":
    success = test_ai_setup()
    if success:
        print("\n🎉 AI Assistant is working correctly!")
    else:
        print("\n❌ AI Assistant setup failed. Please check your configuration.") 