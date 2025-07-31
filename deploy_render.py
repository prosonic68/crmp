#!/usr/bin/env python3
"""
Render Deployment Preparation Script
Checks and prepares your application for Render deployment
"""

import os
import sys
import subprocess
from pathlib import Path

def check_file_exists(filename, required=True):
    """Check if a file exists and print status"""
    exists = os.path.exists(filename)
    status = "✅" if exists else "❌"
    print(f"{status} {filename}")
    if not exists and required:
        print(f"   ⚠️  Required file missing: {filename}")
    return exists

def check_directory_exists(dirname, required=True):
    """Check if a directory exists and print status"""
    exists = os.path.exists(dirname)
    status = "✅" if exists else "❌"
    print(f"{status} {dirname}/")
    if not exists and required:
        print(f"   ⚠️  Required directory missing: {dirname}")
    return exists

def check_python_version():
    """Check Python version compatibility"""
    version = sys.version_info
    print(f"🐍 Python {version.major}.{version.minor}.{version.micro}")
    if version.major == 3 and version.minor >= 8:
        print("   ✅ Python version is compatible with Render")
        return True
    else:
        print("   ⚠️  Python version should be 3.8+ for Render")
        return False

def check_requirements():
    """Check if requirements.txt has necessary packages"""
    if not os.path.exists('requirements.txt'):
        print("❌ requirements.txt not found")
        return False
    
    with open('requirements.txt', 'r') as f:
        content = f.read()
    
    required_packages = ['Flask', 'gunicorn']
    missing = []
    
    for package in required_packages:
        if package not in content:
            missing.append(package)
    
    if missing:
        print(f"   ⚠️  Missing packages in requirements.txt: {', '.join(missing)}")
        return False
    else:
        print("   ✅ All required packages found in requirements.txt")
        return True

def check_wsgi():
    """Check wsgi.py configuration"""
    if not os.path.exists('wsgi.py'):
        print("❌ wsgi.py not found - required for Render")
        return False
    
    with open('wsgi.py', 'r') as f:
        content = f.read()
    
    if 'from app import app' in content:
        print("   ✅ wsgi.py correctly imports app")
        return True
    else:
        print("   ⚠️  wsgi.py should contain: from app import app")
        return False

def check_render_yaml():
    """Check render.yaml configuration"""
    if not os.path.exists('render.yaml'):
        print("❌ render.yaml not found - will use manual configuration")
        return False
    
    print("   ✅ render.yaml found - will use automatic configuration")
    return True

def check_environment_variables():
    """Check if .env file exists for local testing"""
    if os.path.exists('.env'):
        print("   ✅ .env file found for local testing")
        return True
    else:
        print("   ℹ️  No .env file - will use environment variables on Render")
        return True

def create_gitignore():
    """Create .gitignore if it doesn't exist"""
    if os.path.exists('.gitignore'):
        print("   ✅ .gitignore exists")
        return True
    
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
env/
ENV/

# Environment Variables
.env
.env.local
.env.production

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log

# Database
*.db
*.sqlite3

# Render
.render-buildlogs/
"""
    
    try:
        with open('.gitignore', 'w') as f:
            f.write(gitignore_content)
        print("   ✅ Created .gitignore")
        return True
    except Exception as e:
        print(f"   ⚠️  Could not create .gitignore: {e}")
        return False

def check_app_structure():
    """Check application structure"""
    print("\n📁 Checking Application Structure:")
    
    # Required files
    check_file_exists('app.py', required=True)
    check_file_exists('wsgi.py', required=True)
    check_file_exists('requirements.txt', required=True)
    check_file_exists('render.yaml', required=False)
    
    # Required directories
    check_directory_exists('templates', required=True)
    
    # Optional but recommended
    check_file_exists('.gitignore', required=False)
    check_directory_exists('static', required=False)

def check_configuration():
    """Check application configuration"""
    print("\n⚙️  Checking Configuration:")
    
    # Check Python version
    check_python_version()
    
    # Check requirements
    check_requirements()
    
    # Check WSGI
    check_wsgi()
    
    # Check render.yaml
    check_render_yaml()
    
    # Check environment
    check_environment_variables()

def generate_deployment_summary():
    """Generate deployment summary"""
    print("\n🚀 Render Deployment Summary:")
    print("=" * 50)
    
    print("\n📋 Required Steps:")
    print("1. Push your code to GitHub")
    print("2. Sign up at render.com")
    print("3. Connect your GitHub account")
    print("4. Create new Web Service")
    print("5. Configure environment variables")
    print("6. Deploy!")
    
    print("\n🔧 Environment Variables to Set:")
    print("- SECRET_KEY (Render will auto-generate)")
    print("- FLASK_DEBUG=false")
    print("- EMAIL_ENABLED=false (or true with credentials)")
    print("- GEMINI_API_KEY (optional)")
    
    print("\n📚 Documentation:")
    print("- Render Guide: RENDER_DEPLOYMENT_GUIDE.md")
    print("- Render Docs: https://docs.render.com")
    
    print("\n🎯 Next Steps:")
    print("1. Review RENDER_DEPLOYMENT_GUIDE.md")
    print("2. Push code to GitHub")
    print("3. Follow the deployment guide")
    print("4. Test your live application")

def main():
    """Main deployment preparation function"""
    print("🚀 Render Deployment Preparation")
    print("=" * 40)
    
    # Check application structure
    check_app_structure()
    
    # Check configuration
    check_configuration()
    
    # Create gitignore if needed
    create_gitignore()
    
    # Generate summary
    generate_deployment_summary()
    
    print("\n✅ Deployment preparation complete!")
    print("📖 Read RENDER_DEPLOYMENT_GUIDE.md for detailed instructions")

if __name__ == "__main__":
    main() 