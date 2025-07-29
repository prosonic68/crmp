#!/usr/bin/env python3
"""
Simple test script to verify AI assistant is working
"""

import google.generativeai as genai

def test_ai_setup():
    """Test if AI assistant is properly configured"""
    print("🧪 Testing AI Assistant Setup...")
    
    # Use the API key directly
    api_key = "AIzaSyDigFJLH565HUg6OdqfgLHnU9Qh9KUnblQ"
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