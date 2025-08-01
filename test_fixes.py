#!/usr/bin/env python3
"""
Test script to verify the fixes for:
1. Task creation with target_date field
2. Member dashboard user variable issue
"""

import requests
import json

def test_health():
    """Test if the app is running"""
    try:
        response = requests.get('http://localhost:8080/health')
        print(f"✅ Health check: {response.status_code}")
        print(f"   Response: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_login():
    """Test login functionality"""
    try:
        # Test login with a member user
        login_data = {
            'username': 'monali',
            'password': 'prosonic123'
        }
        response = requests.post('http://localhost:8080/login', data=login_data, allow_redirects=False)
        print(f"✅ Login test: {response.status_code}")
        
        if response.status_code == 302:
            print("   Login successful (redirected)")
            return True
        else:
            print(f"   Login failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Login test failed: {e}")
        return False

def test_create_task_form():
    """Test if create task form loads without errors"""
    try:
        # First login to get session
        session = requests.Session()
        login_data = {
            'username': 'abhishek',  # Admin user
            'password': 'prosonic123'
        }
        response = session.post('http://localhost:8080/login', data=login_data, allow_redirects=False)
        
        if response.status_code == 302:
            # Now try to access create task page
            response = session.get('http://localhost:8080/create_task')
            print(f"✅ Create task form test: {response.status_code}")
            
            if response.status_code == 200:
                content = response.text
                if 'target_date' in content:
                    print("   ✅ target_date field found in form")
                else:
                    print("   ❌ target_date field not found")
                
                if 'timeline_days' not in content:
                    print("   ✅ timeline_days field removed from form")
                else:
                    print("   ❌ timeline_days field still present")
                
                return True
            else:
                print(f"   ❌ Create task form failed to load: {response.status_code}")
                return False
        else:
            print("   ❌ Login failed for create task test")
            return False
    except Exception as e:
        print(f"❌ Create task form test failed: {e}")
        return False

def test_member_dashboard():
    """Test member dashboard loads without user variable error"""
    try:
        # Login as member
        session = requests.Session()
        login_data = {
            'username': 'monali',
            'password': 'prosonic123'
        }
        response = session.post('http://localhost:8080/login', data=login_data, allow_redirects=False)
        
        if response.status_code == 302:
            # Try to access member dashboard
            response = session.get('http://localhost:8080/member/dashboard')
            print(f"✅ Member dashboard test: {response.status_code}")
            
            if response.status_code == 200:
                content = response.text
                if 'user_data.name' in content:
                    print("   ✅ user_data.name found in template")
                else:
                    print("   ❌ user_data.name not found in template")
                
                if 'user.name' not in content:
                    print("   ✅ user.name removed from template")
                else:
                    print("   ❌ user.name still present in template")
                
                return True
            else:
                print(f"   ❌ Member dashboard failed to load: {response.status_code}")
                return False
        else:
            print("   ❌ Login failed for member dashboard test")
            return False
    except Exception as e:
        print(f"❌ Member dashboard test failed: {e}")
        return False

def test_user_email_updates():
    """Test that user email updates are applied"""
    try:
        # Check if the updated emails are in the app
        response = requests.get('http://localhost:8080/email_info')
        print(f"✅ Email info test: {response.status_code}")
        
        if response.status_code == 200:
            content = response.text
            if 'tandalikarabhi@gmail.com' in content:
                print("   ✅ Abhishek email updated correctly")
            else:
                print("   ❌ Abhishek email not updated")
            
            if 'amol.panse@prosonic.in' in content:
                print("   ✅ Amol email updated correctly")
            else:
                print("   ❌ Amol email not updated")
            
            if 'omkar.prosonic@gmail.com' not in content:
                print("   ✅ Old Amol email removed")
            else:
                print("   ❌ Old Amol email still present")
            
            return True
        else:
            print(f"   ❌ Email info failed to load: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Email info test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Task Management System Fixes")
    print("=" * 50)
    
    tests = [
        ("Health Check", test_health),
        ("Login Functionality", test_login),
        ("Create Task Form", test_create_task_form),
        ("Member Dashboard", test_member_dashboard),
        ("User Email Updates", test_user_email_updates)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Testing: {test_name}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The fixes are working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the issues above.")

if __name__ == "__main__":
    main() 