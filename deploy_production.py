#!/usr/bin/env python3
"""
Production Deployment Script for Prosonic Task Management System
This script helps prepare the application for production deployment.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_requirements():
    """Check if all required files exist"""
    required_files = [
        'app.py',
        'wsgi.py',
        'requirements.txt',
        'Procfile',
        'runtime.txt'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing required files: {missing_files}")
        return False
    
    print("✅ All required files found")
    return True

def check_environment():
    """Check environment variables"""
    print("\n🔧 Environment Configuration:")
    
    # Check if .env file exists
    if os.path.exists('.env'):
        print("✅ .env file found")
    else:
        print("⚠️  .env file not found - using env_example.txt as template")
        if os.path.exists('env_example.txt'):
            shutil.copy('env_example.txt', '.env')
            print("✅ Created .env from env_example.txt")
    
    # Check critical environment variables
    critical_vars = ['SECRET_KEY', 'FLASK_DEBUG']
    for var in critical_vars:
        value = os.environ.get(var)
        if value:
            if var == 'SECRET_KEY' and value == 'your-secret-key-here-change-in-production':
                print(f"⚠️  {var}: Using default value - CHANGE IN PRODUCTION!")
            else:
                print(f"✅ {var}: Set")
        else:
            print(f"❌ {var}: Not set")

def install_dependencies():
    """Install Python dependencies"""
    print("\n📦 Installing dependencies...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                      check=True, capture_output=True)
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False
    return True

def test_application():
    """Test the application"""
    print("\n🧪 Testing application...")
    try:
        # Test import
        import app
        print("✅ Application imports successfully")
        
        # Test basic functionality
        from app import users, tasks, departments, projects
        print(f"✅ Data loaded: {len(users)} users, {len(tasks)} tasks")
        
        return True
    except Exception as e:
        print(f"❌ Application test failed: {e}")
        return False

def create_production_config():
    """Create production configuration"""
    print("\n⚙️  Creating production configuration...")
    
    # Create production .env template
    prod_env_content = """# Production Environment Variables
# Copy this to .env and update with your actual values

# Security
SECRET_KEY=your-super-secret-key-change-this-in-production
FLASK_DEBUG=false

# Email Configuration
EMAIL_ENABLED=true
EMAIL_PROVIDER=prosonic

# Prosonic Email (Update with actual credentials)
SMTP_SERVER=smtp.prosonic.in
SMTP_PORT=587
SMTP_USERNAME=sm@prosonic.in
SMTP_PASSWORD=your_actual_password_here
SMTP_FROM_EMAIL=sm@prosonic.in

# Gmail Configuration (Alternative)
# EMAIL_PROVIDER=gmail
# GMAIL_SMTP_SERVER=smtp.gmail.com
# GMAIL_SMTP_PORT=587
# GMAIL_USERNAME=your-gmail@gmail.com
# GMAIL_PASSWORD=your-app-password
# GMAIL_FROM_EMAIL=your-gmail@gmail.com

# AI Configuration
GEMINI_API_KEY=your_gemini_api_key_here
"""
    
    with open('.env.production', 'w', encoding='utf-8') as f:
        f.write(prod_env_content)
    
    print("✅ Created .env.production template")
    print("📝 Please update .env.production with your actual credentials")

def generate_deployment_instructions():
    """Generate deployment instructions"""
    instructions = """
🚀 PRODUCTION DEPLOYMENT INSTRUCTIONS
=====================================

1. ENVIRONMENT SETUP:
   - Copy .env.production to .env
   - Update SECRET_KEY with a strong random key
   - Update email credentials
   - Set FLASK_DEBUG=false

2. DEPLOYMENT OPTIONS:

   Option A - Heroku:
   - Install Heroku CLI
   - Run: heroku create your-app-name
   - Run: git push heroku main
   - Set environment variables in Heroku dashboard

   Option B - VPS/Server:
   - Install Python 3.8+, nginx, gunicorn
   - Copy files to server
   - Run: pip install -r requirements.txt
   - Run: gunicorn wsgi:app
   - Configure nginx as reverse proxy

   Option C - Docker:
   - Create Dockerfile
   - Build: docker build -t prosonic-app .
   - Run: docker run -p 8080:8080 prosonic-app

3. SECURITY CHECKLIST:
   ✅ Debug mode disabled
   ✅ Test routes secured
   ✅ Environment variables configured
   ✅ Secret key changed
   ✅ Email credentials updated

4. MONITORING:
   - Check application logs
   - Monitor email functionality
   - Test user authentication
   - Verify task management features

5. BACKUP:
   - Backup user data
   - Backup configuration files
   - Document deployment steps

For detailed deployment guides, see the README.md file.
"""
    
    with open('DEPLOYMENT_INSTRUCTIONS.txt', 'w', encoding='utf-8') as f:
        f.write(instructions)
    
    print("✅ Created DEPLOYMENT_INSTRUCTIONS.txt")

def main():
    """Main deployment script"""
    print("🚀 Prosonic Task Management System - Production Deployment")
    print("=" * 60)
    
    # Check requirements
    if not check_requirements():
        print("❌ Deployment failed - missing requirements")
        return False
    
    # Check environment
    check_environment()
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Deployment failed - dependency installation failed")
        return False
    
    # Test application
    if not test_application():
        print("❌ Deployment failed - application test failed")
        return False
    
    # Create production config
    create_production_config()
    
    # Generate instructions
    generate_deployment_instructions()
    
    print("\n🎉 Production deployment preparation completed!")
    print("📋 Next steps:")
    print("   1. Review DEPLOYMENT_INSTRUCTIONS.txt")
    print("   2. Update .env.production with your credentials")
    print("   3. Choose your deployment platform")
    print("   4. Deploy and test thoroughly")
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1) 