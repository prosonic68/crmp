#!/usr/bin/env python3
"""
Check users data directly from the app module
"""

import app

def check_users():
    """Check the users data"""
    print("🔍 Checking Users Data")
    print("=" * 30)
    
    for username, user_data in app.users.items():
        print(f"Username: {username}")
        print(f"  Name: {user_data['name']}")
        print(f"  Email: {user_data['email']}")
        print(f"  Role: {user_data['role']}")
        print()
    
    # Check specific users
    print("🔍 Checking Specific Users:")
    if 'abhishek' in app.users:
        print(f"Abhishek email: {app.users['abhishek']['email']}")
    else:
        print("❌ Abhishek not found")
    
    if 'amol' in app.users:
        print(f"Amol email: {app.users['amol']['email']}")
    else:
        print("❌ Amol not found")

if __name__ == "__main__":
    check_users() 