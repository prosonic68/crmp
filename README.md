# Prosonic Task Management System

A comprehensive Flask-based task management system with role-based access, KRA scoring, reporting, and master data management.

## Features

- **Role-based Access Control**: Admin, Manager, and Team Member roles
- **Task Workflow Management**: Creation, acceptance, completion, validation, and reopening
- **KRA/KPI Scoring**: Automated performance evaluation
- **Comprehensive Reporting**: Monthly, employee, and stage-wise reports with charts
- **Master Data Management**: Departments, projects, categories, and user management
- **Extension Request System**: Task timeline management with approval workflow
- **Email Notifications**: Automated reminders and updates
- **Responsive UI**: Modern, mobile-friendly interface

## Demo Credentials

### Admin Access
- **Username:** `admin`
- **Password:** `admin`
- **Features:** Full system access, reports, master data management

### Manager Access
- **Username:** `manager1`
- **Password:** `manager123`
- **Features:** Team management, task creation, approvals

### Team Member Access
- **Username:** `user1`
- **Password:** `user123`
- **Features:** Task acceptance, completion, extension requests

## Quick Start (Local Development)

1. **Install Python 3.11+**
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the application:**
   ```bash
   python app.py
   ```
4. **Access the application:**
   - Open browser and go to: `http://localhost:5000`
   - Login with demo credentials above

## Email Configuration (Gmail Setup)

The system now uses **Gmail SMTP** as the default email provider for sending task reminders and notifications.

### Setting up Gmail for Email Reminders

1. **Enable 2-Factor Authentication** on your Gmail account
2. **Generate an App Password:**
   - Go to Google Account settings
   - Navigate to Security → 2-Step Verification → App passwords
   - Generate a new app password for "Mail"
3. **Configure Environment Variables:**
   ```bash
   # Copy the example file
   cp env_example.txt .env
   
   # Edit .env with your Gmail credentials
   EMAIL_ENABLED=true
   EMAIL_PROVIDER=gmail
   GMAIL_USERNAME=your-gmail@gmail.com
   GMAIL_PASSWORD=your-app-password
   GMAIL_FROM_EMAIL=your-gmail@gmail.com
   ```

### Email Features
- **Automatic Reminders**: Sent for overdue tasks, tasks due tomorrow, and tasks due soon
- **Manual Reminders**: Admin can send custom reminders for specific tasks
- **Reminder History**: Track all sent reminders with timestamps and messages
- **Anti-Spam Protection**: 24-hour cooldown between reminders for the same task

### Testing Email Configuration
Visit `/test_email` route to test your email setup before sending actual reminders.

## Deployment Options

### Option 1: Heroku (Recommended for Demo)

1. **Install Heroku CLI**
2. **Login to Heroku:**
   ```bash
   heroku login
   ```
3. **Create Heroku app:**
   ```bash
   heroku create your-task-manager-app
   ```
4. **Deploy:**
   ```bash
   git add .
   git commit -m "Initial deployment"
   git push heroku main
   ```
5. **Open the app:**
   ```bash
   heroku open
   ```

### Option 2: Railway

1. **Connect your GitHub repository to Railway**
2. **Railway will automatically detect Flask and deploy**
3. **Set environment variables if needed**
4. **Access your live URL**

### Option 3: Render

1. **Connect your GitHub repository to Render**
2. **Create a new Web Service**
3. **Set build command:** `pip install -r requirements.txt`
4. **Set start command:** `gunicorn wsgi:app`
5. **Deploy and get your live URL**

### Option 4: Python Anywhere

1. **Upload your files to PythonAnywhere**
2. **Create a new web app**
3. **Set up virtual environment and install requirements**
4. **Configure WSGI file**
5. **Deploy and access your live URL**

## Production Deployment

### Quick Production Setup

1. **Run the production deployment script:**
   ```bash
   python deploy_production.py
   ```

2. **Update environment variables:**
   ```bash
   cp .env.production .env
   # Edit .env with your actual credentials
   ```

3. **Choose deployment method:**

### Option 1: Docker Deployment (Recommended)
```bash
# Build and run with Docker
docker build -t prosonic-app .
docker run -p 8080:8080 --env-file .env prosonic-app

# Or use docker-compose
docker-compose up -d
```

### Option 2: Direct Server Deployment
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export FLASK_DEBUG=false
export SECRET_KEY=your-secret-key-here

# Run with gunicorn
gunicorn --bind 0.0.0.0:8080 --workers 4 wsgi:app
```

### Option 3: Cloud Platform Deployment
- **Heroku**: `git push heroku main`
- **Railway**: Connect GitHub repo
- **Render**: Deploy as Web Service
- **PythonAnywhere**: Upload and configure

### Production Security Checklist
- ✅ Debug mode disabled
- ✅ Test routes secured
- ✅ Environment variables configured
- ✅ Secret key changed
- ✅ Email credentials updated
- ✅ HTTPS enabled (recommended)
- ✅ Rate limiting configured
- ✅ Security headers added

### Environment Variables
```bash
# Required
SECRET_KEY=your-super-secret-key
FLASK_DEBUG=false

# Email Configuration (Gmail is now the default)
EMAIL_ENABLED=true
EMAIL_PROVIDER=gmail
SMTP_SERVER=smtp.gmail.com
SMTP_USERNAME=your-gmail@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=your-gmail@gmail.com

# Gmail SMTP Configuration (Default - Recommended)
GMAIL_SMTP_SERVER=smtp.gmail.com
GMAIL_SMTP_PORT=587
GMAIL_USERNAME=your-gmail@gmail.com
GMAIL_PASSWORD=your-app-password
GMAIL_FROM_EMAIL=your-gmail@gmail.com

# Prosonic SMTP (Optional - for company email)
PROSONIC_SMTP_SERVER=smtp.prosonic.in
PROSONIC_SMTP_PORT=587
PROSONIC_SMTP_USERNAME=your-email@prosonic.in
PROSONIC_SMTP_PASSWORD=your-email-password
PROSONIC_SMTP_FROM_EMAIL=your-email@prosonic.in

# AI Configuration (Optional)
GEMINI_API_KEY=your_api_key
```

## System Architecture

- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS, JavaScript with Chart.js
- **Data Storage**: In-memory (can be replaced with database)
- **Authentication**: Session-based with role management
- **Reporting**: Chart.js for interactive visualizations

## Support

For technical support or questions about the system, please refer to the code documentation or contact the development team.

## Created By

Abhishek A Tandalikar
