#!/usr/bin/env python3
"""
Deployment helper script for the Task Management System
"""

import os
import subprocess
import sys

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return None

def check_requirements():
    """Check if required tools are installed"""
    print("🔍 Checking deployment requirements...")
    
    # Check Python version
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print("❌ Python 3.8+ is required")
        return False
    
    print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Check if requirements.txt exists
    if not os.path.exists('requirements.txt'):
        print("❌ requirements.txt not found")
        return False
    
    print("✅ requirements.txt found")
    return True

def install_dependencies():
    """Install Python dependencies"""
    return run_command("pip install -r requirements.txt", "Installing dependencies")

def test_local():
    """Test the application locally"""
    print("\n🧪 Testing application locally...")
    print("Starting Flask development server...")
    print("Press Ctrl+C to stop the server")
    
    try:
        subprocess.run("python app.py", shell=True)
    except KeyboardInterrupt:
        print("\n✅ Local test completed")

def deploy_heroku():
    """Deploy to Heroku"""
    print("\n🚀 Deploying to Heroku...")
    
    # Check if Heroku CLI is installed
    if run_command("heroku --version", "Checking Heroku CLI") is None:
        print("❌ Heroku CLI not found. Please install it first:")
        print("   https://devcenter.heroku.com/articles/heroku-cli")
        return False
    
    # Login to Heroku
    if run_command("heroku login", "Logging into Heroku") is None:
        return False
    
    # Create Heroku app
    app_name = input("Enter Heroku app name (or press Enter for auto-generated): ").strip()
    if app_name:
        create_cmd = f"heroku create {app_name}"
    else:
        create_cmd = "heroku create"
    
    if run_command(create_cmd, "Creating Heroku app") is None:
        return False
    
    # Initialize git if not already done
    if not os.path.exists('.git'):
        run_command("git init", "Initializing git repository")
        run_command("git add .", "Adding files to git")
        run_command('git commit -m "Initial commit"', "Making initial commit")
    
    # Deploy to Heroku
    if run_command("git push heroku main", "Deploying to Heroku") is None:
        return False
    
    # Open the app
    run_command("heroku open", "Opening the deployed app")
    
    print("\n🎉 Deployment completed successfully!")
    print("Your app is now live on Heroku!")
    return True

def main():
    """Main deployment function"""
    print("🚀 Task Management System Deployment Helper")
    print("=" * 50)
    
    if not check_requirements():
        print("\n❌ Requirements check failed. Please fix the issues above.")
        return
    
    while True:
        print("\n📋 Choose an option:")
        print("1. Install dependencies")
        print("2. Test locally")
        print("3. Deploy to Heroku")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == '1':
            install_dependencies()
        elif choice == '2':
            test_local()
        elif choice == '3':
            deploy_heroku()
        elif choice == '4':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    main() 