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

## Production Considerations

- **Database**: Replace in-memory storage with PostgreSQL or MySQL
- **Email**: Configure real SMTP settings for email notifications
- **Security**: Change default passwords and use environment variables
- **SSL**: Enable HTTPS for production deployments
- **Monitoring**: Add logging and monitoring tools

## System Architecture

- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS, JavaScript with Chart.js
- **Data Storage**: In-memory (can be replaced with database)
- **Authentication**: Session-based with role management
- **Reporting**: Chart.js for interactive visualizations

## Support

For technical support or questions about the system, please refer to the code documentation or contact the development team


## Crerated By 
Abhishek A Tandalikar
