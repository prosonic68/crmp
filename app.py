from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from datetime import datetime, timedelta
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import calendar
from collections import defaultdict
try:
    from ai_assistant import ai_assistant
    AI_AVAILABLE = True
except Exception as e:
    print(f"⚠️ AI Assistant not available: {e}")
    AI_AVAILABLE = False
    ai_assistant = None

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here-change-in-production')
app.debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'

@app.errorhandler(500)
def internal_error(error):
    print(f"500 Error occurred: {error}")
    return "Internal Server Error - Check console for details", 500

@app.errorhandler(404)
def not_found_error(error):
    print(f"404 Error occurred: {error}")
    return "Page not found", 404

# --- Email Configuration ---
EMAIL_CONFIG = {
    'enabled': os.environ.get('EMAIL_ENABLED', 'False').lower() == 'true',
    'provider': os.environ.get('EMAIL_PROVIDER', 'prosonic'),  # 'gmail' or 'prosonic'
    'smtp_server': os.environ.get('SMTP_SERVER', 'smtp.prosonic.in'),
    'smtp_port': int(os.environ.get('SMTP_PORT', '587')),
    'username': os.environ.get('SMTP_USERNAME', ''),
    'password': os.environ.get('SMTP_PASSWORD', ''),
    'from_email': os.environ.get('SMTP_FROM_EMAIL', '')
}

# Prosonic SMTP Configuration (strictly for company email)
PROSONIC_EMAIL_CONFIG = {
    'smtp_server': os.environ.get('PROSONIC_SMTP_SERVER', 'smtp.prosonic.in'),
    'smtp_port': int(os.environ.get('PROSONIC_SMTP_PORT', '587')),
    'username': os.environ.get('PROSONIC_SMTP_USERNAME', 'sm@prosonic.in'),
    'password': os.environ.get('PROSONIC_SMTP_PASSWORD', ''),
    'from_email': os.environ.get('PROSONIC_SMTP_FROM_EMAIL', 'sm@prosonic.in')
}

# Gmail SMTP Configuration (for Gmail users)
GMAIL_EMAIL_CONFIG = {
    'smtp_server': os.environ.get('GMAIL_SMTP_SERVER', 'smtp.gmail.com'),
    'smtp_port': int(os.environ.get('GMAIL_SMTP_PORT', '587')),
    'username': os.environ.get('GMAIL_USERNAME', 'your-gmail@gmail.com'),
    'password': os.environ.get('GMAIL_PASSWORD', 'your-app-password'),
    'from_email': os.environ.get('GMAIL_FROM_EMAIL', 'your-gmail@gmail.com')
}

# --- Task class must be defined before use ---
class Task:
    def __init__(self, id, title, description, assigned_by, assigned_to, timeline_days, priority='medium', 
                 category='DEV', project_id=None, department=None):
        self.id = id
        self.title = title
        self.description = description
        self.assigned_by = assigned_by
        self.assigned_to = assigned_to
        self.created_date = datetime.now()
        self.target_date = datetime.now() + timedelta(days=timeline_days)
        self.review_date = self.target_date - timedelta(days=1)
        self.status = 'pending'  # pending, accepted, in_progress, completed, validated, reopened
        self.priority = priority
        self.category = category
        self.project_id = project_id
        self.department = department
        self.accepted_date = None
        self.completion_date = None
        self.validation_date = None
        self.roadmap = []
        self.reminders = []  # Track all reminders sent
        self.extension_requests = []
        self.kra_score = 0
        self.quality_score = 0
        self.collaboration_score = 0
        self.last_reminder_date = None  # Track when last reminder was sent
        self.reminder_count = 0  # Count of reminders sent

# --- In-memory users dictionary (no database) ---
users = {
    'monali':   {'password': 'prosonic123', 'role': 'member',  'name': 'Monali Joshi',          'email': 'acc.prosonic@gmail.com',   'department': 'Accounts', 'manager': 'jaywant'},
    'jaywant':  {'password': 'prosonic123', 'role': 'manager', 'name': 'Jaywant Khese',         'email': 'trc@prosonic.in',          'department': 'Repair', 'team': ['monali']},
    'mandar':   {'password': 'prosonic123', 'role': 'manager', 'name': 'Mandar Tembe',          'email': 'mandar.tembe64@gmail.com', 'department': 'Purchase & Logistics', 'team': ['divya']},
    'abhishek': {'password': 'prosonic123', 'role': 'admin',   'name': 'Abhishek Tandanlikar',  'email': 'tandalikarabhi@gmail.com', 'department': 'IT', 'team': ['nayan']},
    'divya':    {'password': 'prosonic123', 'role': 'member',  'name': 'Divya Jori',            'email': 'divyajori.prosonic@gmail.com', 'department': 'HR', 'manager': 'mandar'},
    'nayan':    {'password': 'prosonic123', 'role': 'member',  'name': 'Nayan Ahir',            'email': 'nayanaahir50@gmail.com',   'department': 'Design', 'manager': 'abhishek'},
    'archana':  {'password': 'prosonic123', 'role': 'manager', 'name': 'Archana Tatooskar',     'email': 'coo@prosonic.in',          'department': 'Operations', 'team': ['monali']},
    'amol':     {'password': 'prosonic123', 'role': 'manager', 'name': 'Amol Panse',            'email': 'amol.panse@prosonic.in', 'department': 'Management', 'team': ['monali', 'divya']},
    'admin':    {'password': 'admin',        'role': 'admin',   'name': 'System Administrator',  'email': 'admin@prosonic.in',        'department': 'IT', 'team': ['nayan', 'divya', 'monali']},
}

# Enhanced Data storage with master data
departments = {
    'IT': {'name': 'Information Technology', 'manager': 'abhishek'},
    'HR': {'name': 'Human Resources', 'manager': 'archana'},
    'FIN': {'name': 'Finance', 'manager': 'amol'},
    'MKT': {'name': 'Marketing', 'manager': 'amol'},
    'Accounts': {'name': 'Accounts', 'manager': 'jaywant'},
    'Repair': {'name': 'Repair', 'manager': 'jaywant'},
    'Purchase & Logistics': {'name': 'Purchase & Logistics', 'manager': 'mandar'},
    'Design': {'name': 'Design', 'manager': 'abhishek'},
    'Operations': {'name': 'Operations', 'manager': 'archana'},
    'Management': {'name': 'Management', 'manager': 'amol'}
}

projects = {
    'PROJ001': {'name': 'Website Redesign', 'department': 'IT', 'start_date': '2024-01-01', 'end_date': '2024-06-30'},
    'PROJ002': {'name': 'Employee Portal', 'department': 'IT', 'start_date': '2024-02-01', 'end_date': '2024-08-31'},
    'PROJ003': {'name': 'Recruitment Drive', 'department': 'HR', 'start_date': '2024-03-01', 'end_date': '2024-05-31'},
    'PROJ004': {'name': 'Budget Planning', 'department': 'FIN', 'start_date': '2024-01-15', 'end_date': '2024-04-30'}
}

task_categories = {
    'DEV': 'Development',
    'TEST': 'Testing',
    'DOC': 'Documentation',
    'DESIGN': 'Design',
    'ANALYSIS': 'Analysis',
    'PLANNING': 'Planning',
    'REVIEW': 'Review',
    'DEPLOY': 'Deployment'
}

kra_kpi = {
    'TASK_COMPLETION': {'name': 'Task Completion Rate', 'target': 90, 'weight': 30},
    'TIMELINE_ADHERENCE': {'name': 'Timeline Adherence', 'target': 85, 'weight': 25},
    'QUALITY_SCORE': {'name': 'Quality Score', 'target': 95, 'weight': 25},
    'COLLABORATION': {'name': 'Collaboration Score', 'target': 80, 'weight': 20}
}

# Sample tasks for demonstration
tasks = [
    Task(1, "Website Homepage Redesign", "Redesign the company homepage with modern UI/UX", "abhishek", "nayan", 7, "high", "DESIGN", "PROJ001", "IT"),
    Task(2, "Database Optimization", "Optimize database queries for better performance", "abhishek", "nayan", 5, "medium", "DEV", "PROJ002", "IT"),
    Task(3, "Employee Handbook Update", "Update employee handbook with new policies", "mandar", "divya", 10, "medium", "DOC", "PROJ003", "HR"),
    Task(4, "Recruitment Portal Testing", "Test the new recruitment portal functionality", "mandar", "divya", 3, "high", "TEST", "PROJ003", "HR"),
    Task(5, "Budget Report Generation", "Generate monthly budget reports for Q1", "amol", "monali", 8, "high", "ANALYSIS", "PROJ004", "FIN"),
    Task(6, "Financial Data Analysis", "Analyze financial data for quarterly review", "amol", "monali", 6, "medium", "ANALYSIS", "PROJ004", "FIN"),
    Task(7, "Marketing Campaign Design", "Design new marketing campaign materials", "archana", "nayan", 12, "high", "DESIGN", None, "MKT"),
    Task(8, "Social Media Content", "Create social media content for the month", "archana", "divya", 4, "medium", "PLANNING", None, "MKT")
]

# Set some tasks to different statuses for demonstration
tasks[0].status = 'validated'
tasks[0].accepted_date = datetime.now() - timedelta(days=5)
tasks[0].completion_date = datetime.now() - timedelta(days=2)
tasks[0].validation_date = datetime.now() - timedelta(days=1)
tasks[0].kra_score = 92.5

tasks[1].status = 'validated'
tasks[1].accepted_date = datetime.now() - timedelta(days=3)
tasks[1].completion_date = datetime.now() - timedelta(days=1)
tasks[1].validation_date = datetime.now()
tasks[1].kra_score = 87.3

tasks[2].status = 'validated'
tasks[2].accepted_date = datetime.now() - timedelta(days=2)
tasks[2].completion_date = datetime.now()
tasks[2].validation_date = datetime.now()
tasks[2].kra_score = 89.1

tasks[3].status = 'validated'
tasks[3].accepted_date = datetime.now() - timedelta(days=4)
tasks[3].completion_date = datetime.now() - timedelta(days=1)
tasks[3].validation_date = datetime.now()
tasks[3].kra_score = 88.0

tasks[4].status = 'validated'
tasks[4].accepted_date = datetime.now() - timedelta(days=6)
tasks[4].completion_date = datetime.now() - timedelta(days=2)
tasks[4].validation_date = datetime.now() - timedelta(days=1)
tasks[4].kra_score = 95.2

tasks[5].status = 'validated'
tasks[5].accepted_date = datetime.now() - timedelta(days=4)
tasks[5].completion_date = datetime.now() - timedelta(days=1)
tasks[5].validation_date = datetime.now()
tasks[5].kra_score = 91.8

task_requests = []
kra_scores = {}

def send_email(to_email, subject, body, reminder_type='general'):
    """Send email notification using Prosonic SMTP strictly"""
    try:
        msg = MIMEMultipart()
        
        # Use Prosonic SMTP configuration
        if EMAIL_CONFIG['provider'] == 'prosonic':
            msg['From'] = PROSONIC_EMAIL_CONFIG['from_email']
            smtp_config = PROSONIC_EMAIL_CONFIG
        else:
            msg['From'] = EMAIL_CONFIG['from_email']
            smtp_config = EMAIL_CONFIG
            
        msg['To'] = to_email
        msg['Subject'] = f"[Prosonic Task Manager] {subject}"
        
        # Create HTML email template with reminder-specific styling
        priority_color = '#dc3545' if 'URGENT' in subject else '#667eea'
        reminder_icon = '🚨' if reminder_type == 'urgent' else '📧' if reminder_type == 'manual' else '⏰'
        
        html_body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .header {{ background: linear-gradient(135deg, {priority_color} 0%, #764ba2 100%); color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; }}
                .footer {{ background: #f8f9fa; padding: 15px; text-align: center; color: #666; font-size: 12px; }}
                .btn {{ display: inline-block; padding: 10px 20px; background: {priority_color}; color: white; text-decoration: none; border-radius: 5px; }}
                .prosonic {{ color: #dc3545; font-weight: bold; }}
                .reminder-badge {{ background: {priority_color}; color: white; padding: 5px 10px; border-radius: 15px; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{reminder_icon} <span class="prosonic">Prosonic</span> Task Manager</h1>
                <div class="reminder-badge">{reminder_type.upper()} REMINDER</div>
            </div>
            <div class="content">
                {body.replace(chr(10), '<br>')}
            </div>
            <div class="footer">
                <p>This is an automated notification from <span class="prosonic">Prosonic</span> Task Management System</p>
                <p>Please do not reply to this email</p>
            </div>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(html_body, 'html'))
        
        if EMAIL_CONFIG['enabled']:
            # Send real email using Prosonic SMTP
            server = smtplib.SMTP(smtp_config['smtp_server'], smtp_config['smtp_port'])
            server.starttls()
            server.login(smtp_config['username'], smtp_config['password'])
            server.send_message(msg)
            server.quit()
            print(f"✅ Email sent via Prosonic SMTP to {to_email}: {subject}")
        else:
            # Just print for testing
            print(f"📧 Email would be sent via Prosonic SMTP to {to_email}: {subject}")
            print(f"📧 Email body: {body}")
            
    except Exception as e:
        print(f"❌ Email sending failed: {e}")
        return False
    
    return True

def calculate_kra_score(task):
    """Calculate comprehensive KRA score"""
    if task.status != 'validated':
        return 0
    
    # Timeline adherence (40%)
    days_taken = (task.completion_date - task.accepted_date).days
    original_timeline = (task.target_date - task.created_date).days
    
    if days_taken <= original_timeline:
        timeline_score = 100
    elif days_taken <= original_timeline + 1:
        timeline_score = 80
    elif days_taken <= original_timeline + 2:
        timeline_score = 60
    elif days_taken <= original_timeline + 3:
        timeline_score = 40
    else:
        timeline_score = 20
    
    # Quality score (30%) - based on validation and reopens
    quality_score = task.quality_score if task.quality_score > 0 else 85
    
    # Collaboration score (30%) - based on extension requests and communication
    collaboration_score = task.collaboration_score if task.collaboration_score > 0 else 80
    
    # Weighted average
    final_score = (timeline_score * 0.4) + (quality_score * 0.3) + (collaboration_score * 0.3)
    return round(final_score, 1)

def get_monthly_stats(year, month):
    """Get monthly task statistics"""
    start_date = datetime(year, month, 1)
    if month == 12:
        end_date = datetime(year + 1, 1, 1)
    else:
        end_date = datetime(year, month + 1, 1)
    
    monthly_tasks = [task for task in tasks if start_date <= task.created_date < end_date]
    
    stats = {
        'total_tasks': len(monthly_tasks),
        'completed_tasks': len([t for t in monthly_tasks if t.status == 'validated']),
        'pending_tasks': len([t for t in monthly_tasks if t.status == 'pending']),
        'in_progress_tasks': len([t for t in monthly_tasks if t.status in ['accepted', 'completed']]),
        'completion_rate': 0
    }
    
    if stats['total_tasks'] > 0:
        stats['completion_rate'] = round((stats['completed_tasks'] / stats['total_tasks']) * 100, 1)
    
    return stats

def get_employee_stats(employee_id):
    """Get employee-specific statistics"""
    employee_tasks = [task for task in tasks if task.assigned_to == employee_id]
    
    stats = {
        'total_assigned': len(employee_tasks),
        'completed': len([t for t in employee_tasks if t.status == 'validated']),
        'pending': len([t for t in employee_tasks if t.status == 'pending']),
        'in_progress': len([t for t in employee_tasks if t.status in ['accepted', 'completed']]),
        'average_kra': 0,
        'completion_rate': 0
    }
    
    if stats['total_assigned'] > 0:
        stats['completion_rate'] = round((stats['completed'] / stats['total_assigned']) * 100, 1)
    
    # Calculate average KRA
    employee_kra_scores = [task.kra_score for task in employee_tasks if task.kra_score > 0]
    if employee_kra_scores:
        stats['average_kra'] = round(sum(employee_kra_scores) / len(employee_kra_scores), 1)
    
    return stats

@app.route('/')
def home():
    try:
        if 'user' not in session:
            return redirect(url_for('login'))
        
        user = session['user']
        if user in users:
            if users[user]['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif users[user]['role'] == 'manager':
                return redirect(url_for('manager_dashboard'))
            else:
                return redirect(url_for('member_dashboard'))
        return redirect(url_for('login'))
    except Exception as e:
        print(f"Error in home route: {e}")
        return redirect(url_for('login'))

@app.route('/health')
def health_check():
    """Health check endpoint for deployment verification"""
    return jsonify({
        'status': 'healthy', 
        'message': 'Task Management System is running',
        'ai_available': AI_AVAILABLE if 'AI_AVAILABLE' in globals() else False
    })

@app.route('/simple')
def simple_test():
    """Simple test route to check basic functionality"""
    return "Hello! Flask is working correctly."

@app.route('/minimal')
def minimal_test():
    """Minimal test route without any dependencies"""
    try:
        return "Minimal test successful!"
    except Exception as e:
        print(f"Error in minimal test: {e}")
        return f"Error: {str(e)}"

@app.route('/ping')
def ping():
    """Simple ping route to test if Flask is responding"""
    return "PONG - Flask is working!"

@app.route('/test')
def test():
    """Simple test route to check if Flask is working - DISABLED IN PRODUCTION"""
    if not app.debug:
        return jsonify({'error': 'Test route disabled in production'}), 403
    return jsonify({
        'status': 'ok',
        'users_count': len(users),
        'tasks_count': len(tasks),
        'departments_count': len(departments),
        'available_users': list(users.keys())
    })

@app.route('/login_test')
def login_test():
    """Debug page for login testing - DISABLED IN PRODUCTION"""
    if not app.debug:
        return "Test page disabled in production", 403
    return render_template('login_test.html',
                         users_count=len(users),
                         tasks_count=len(tasks),
                         departments_count=len(departments))

@app.route('/simple_login')
def simple_login():
    """Simple login page for testing - DISABLED IN PRODUCTION"""
    if not app.debug:
        return "Test page disabled in production", 403
    try:
        return render_template('simple_login.html')
    except Exception as e:
        print(f"Error rendering simple login: {e}")
        return f"Template error: {str(e)}"

@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            print(f"Login attempt - Username: {username}, Password: {password}")
            print(f"Available users: {list(users.keys())}")
            
            if username in users:
                print(f"User found: {username}")
                if users[username]['password'] == password:
                    print(f"Password match for user: {username}")
                    session['user'] = username
                    if users[username]['role'] == 'admin':
                        return redirect(url_for('admin_dashboard'))
                    elif users[username]['role'] == 'manager':
                        return redirect(url_for('manager_dashboard'))
                    else:
                        return redirect(url_for('member_dashboard'))
                else:
                    print(f"Password mismatch for user: {username}")
                    flash('Invalid credentials. Please try again.')
            else:
                print(f"User not found: {username}")
                flash('Invalid credentials. Please try again.')
        return render_template('login.html')
    except Exception as e:
        print(f"Error in login route: {e}")
        flash('An error occurred. Please try again.')
        return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    user = session['user']
    if user not in users:
        return redirect(url_for('login'))

    if users[user]['role'] != 'admin':
        return redirect(url_for('login'))
    
    # Get current month stats
    now = datetime.now()
    monthly_stats = get_monthly_stats(now.year, now.month)
    
    # Department-wise stats
    dept_stats = {}
    for dept_id, dept_data in departments.items():
        dept_tasks = [task for task in tasks if task.department == dept_id]
        dept_stats[dept_id] = {
            'name': dept_data['name'],
            'total': len(dept_tasks),
            'completed': len([t for t in dept_tasks if t.status == 'validated']),
            'pending': len([t for t in dept_tasks if t.status == 'pending'])
        }
    
    return render_template('admin_dashboard.html', 
                         users=users, 
                         tasks=tasks,
                         kra_scores=kra_scores,
                         departments=departments,
                         projects=projects,
                         task_categories=task_categories,
                         monthly_stats=monthly_stats,
                         dept_stats=dept_stats)

@app.route('/manager/dashboard')
def manager_dashboard():
    try:
        if 'user' not in session:
            return redirect(url_for('login'))
        
        user = session['user']
        if user not in users:
            return redirect(url_for('login'))

        if users[user]['role'] != 'manager':
            return redirect(url_for('login'))
        
        manager = user
        team_tasks = [task for task in tasks if task.assigned_to in users[manager]['team']]
        
        # Employee-wise stats
        employee_stats = {}
        for member in users[manager]['team']:
            employee_stats[member] = get_employee_stats(member)
        
        # Project-wise stats
        project_stats = {}
        for project_id, project_data in projects.items():
            if project_data['department'] == users[manager]['department']:
                project_tasks = [task for task in team_tasks if task.project_id == project_id]
                project_stats[project_id] = {
                    'name': project_data['name'],
                    'total': len(project_tasks),
                    'completed': len([t for t in project_tasks if t.status == 'validated']),
                    'pending': len([t for t in project_tasks if t.status == 'pending'])
                }
        
        return render_template('manager_dashboard.html',
                             tasks=team_tasks,
                             team_members=users[manager]['team'],
                             users=users,
                             employee_stats=employee_stats,
                             project_stats=project_stats,
                             task_categories=task_categories)
    except Exception as e:
        print(f"Error in manager dashboard: {e}")
        return f"Error in manager dashboard: {str(e)}", 500

@app.route('/member/dashboard')
def member_dashboard():
    try:
        if 'user' not in session:
            return redirect(url_for('login'))
        
        user = session['user']
        if user not in users:
            return redirect(url_for('login'))

        if users[user]['role'] != 'member':
            return redirect(url_for('login'))
        
        member = user
        my_tasks = [task for task in tasks if task.assigned_to == member]
        
        # Date-wise task breakdown
        date_wise_tasks = defaultdict(list)
        for task in my_tasks:
            date_key = task.created_date.strftime('%Y-%m-%d')
            date_wise_tasks[date_key].append(task)
        
        # Personal stats
        personal_stats = get_employee_stats(member)
        
        return render_template('member_dashboard.html',
                             tasks=my_tasks,
                             user_data=users[member],
                             date_wise_tasks=dict(date_wise_tasks),
                             personal_stats=personal_stats,
                             now=datetime.now())
    except Exception as e:
        print(f"Error in member dashboard: {e}")
        return f"Error in member dashboard: {str(e)}", 500

@app.route('/create_task', methods=['GET', 'POST'])
def create_task():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    user = session['user']
    if user not in users:
        return redirect(url_for('login'))

    # Only admins and managers can create tasks
    if users[user]['role'] not in ['admin', 'manager']:
        flash('You do not have permission to create tasks', 'error')
        return redirect(url_for('member_dashboard'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        assigned_to = request.form.get('assigned_to')
        priority = request.form.get('priority')
        target_date = request.form.get('target_date')
        target_time = request.form.get('target_time')
        category = request.form.get('category')
        department = request.form.get('department')
        project = request.form.get('project')
        
        if not all([title, description, assigned_to, priority, target_date, target_time]):
            flash('All required fields must be filled', 'error')
            return render_template('create_task.html', users=users, departments=departments, projects=projects, today_date=datetime.now().strftime('%Y-%m-%d'))
        
        # Validate assigned_to based on user role
        if users[user]['role'] == 'manager':
            # Managers can only assign to their team members
            if assigned_to not in users[user].get('team', []):
                flash('You can only assign tasks to your team members', 'error')
                return render_template('create_task.html', users=users, departments=departments, projects=projects)
        elif users[user]['role'] == 'admin':
            # Admins can assign to any member
            if assigned_to not in users or users[assigned_to]['role'] != 'member':
                flash('Invalid team member selected', 'error')
                return render_template('create_task.html', users=users, departments=departments, projects=projects)
        
        try:
            # Combine date and time
            datetime_str = f"{target_date} {target_time}"
            target_datetime = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M')
            target_date = target_datetime.date()
        except ValueError:
            flash('Invalid date or time format', 'error')
            return render_template('create_task.html', users=users, departments=departments, projects=projects, today_date=datetime.now().strftime('%Y-%m-%d'))
        
        # Calculate timeline_days from target_date
        timeline_days = (target_date - datetime.now().date()).days
        
        # Create new task
        new_task = Task(
            id=len(tasks) + 1,
            title=title,
            description=description,
            assigned_by=user,
            assigned_to=assigned_to,
            timeline_days=timeline_days,
            priority=priority,
            category=category,
            department=department,
            project_id=project
        )
        
        tasks.append(new_task)
        flash('Task created successfully!', 'success')
        return redirect(url_for('admin_dashboard' if users[user]['role'] == 'admin' else 'manager_dashboard'))
    
    # Get pre-filled assigned_to from query parameter
    pre_filled_assigned_to = request.args.get('assigned_to', '')
    
    return render_template('create_task.html', 
                         users=users, 
                         departments=departments, 
                         projects=projects,
                         pre_filled_assigned_to=pre_filled_assigned_to,
                         today_date=datetime.now().strftime('%Y-%m-%d'))

@app.route('/accept_task/<int:task_id>')
def accept_task(task_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    
    user = session['user']
    if user not in users:
        return redirect(url_for('login'))

    task = next((t for t in tasks if t.id == task_id), None)
    if task and task.assigned_to == user:
        task.status = 'accepted'
        task.accepted_date = datetime.now()
        
        # Send notification to manager
        manager = users[task.assigned_to]['manager']
        manager_email = users[manager]['email']
        send_email(manager_email,
                  f'Task Accepted: {task.title}',
                  f'Task "{task.title}" has been accepted by {users[user]["name"]}')
        
        flash('Task accepted successfully!')
    
    return redirect(url_for('member_dashboard'))

@app.route('/request_extension/<int:task_id>', methods=['POST'])
def request_extension(task_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    
    user = session['user']
    if user not in users:
        return redirect(url_for('login'))

    task = next((t for t in tasks if t.id == task_id), None)
    if task and task.assigned_to == user:
        extra_days = int(request.form['extra_days'])
        reason = request.form['reason']
        
        extension_request = {
            'task_id': task_id,
            'requested_by': user,
            'extra_days': extra_days,
            'reason': reason,
            'request_date': datetime.now(),
            'status': 'pending'
        }
        
        task.extension_requests.append(extension_request)
        
        # Send notification to manager
        manager = users[task.assigned_to]['manager']
        manager_email = users[manager]['email']
        send_email(manager_email,
                  f'Extension Request: {task.title}',
                  f'Extension request for task "{task.title}": {extra_days} extra days\nReason: {reason}')
        
        flash('Extension request submitted!')
    
    return redirect(url_for('member_dashboard'))

@app.route('/approve_extension/<int:task_id>/<int:request_index>')
def approve_extension(task_id, request_index):
    if 'user' not in session:
        return redirect(url_for('login'))
    
    user = session['user']
    if user not in users:
        return redirect(url_for('login'))

    task = next((t for t in tasks if t.id == task_id), None)
    if task and request_index < len(task.extension_requests):
        request = task.extension_requests[request_index]
        request['status'] = 'approved'
        task.target_date += timedelta(days=request['extra_days'])
        
        # Send notification to team member
        member_email = users[request['requested_by']]['email']
        send_email(member_email,
                  f'Extension Approved: {task.title}',
                  f'Your extension request for task "{task.title}" has been approved.')
        
        flash('Extension request approved!')
    
    return redirect(url_for('manager_dashboard'))

@app.route('/reject_extension/<int:task_id>/<int:request_index>')
def reject_extension(task_id, request_index):
    if 'user' not in session:
        return redirect(url_for('login'))
    
    user = session['user']
    if user not in users:
        return redirect(url_for('login'))

    task = next((t for t in tasks if t.id == task_id), None)
    if task and request_index < len(task.extension_requests):
        request = task.extension_requests[request_index]
        request['status'] = 'rejected'
        
        # Send notification to team member
        member_email = users[request['requested_by']]['email']
        send_email(member_email,
                  f'Extension Rejected: {task.title}',
                  f'Your extension request for task "{task.title}" has been rejected.')
        
        flash('Extension request rejected!')
    
    return redirect(url_for('manager_dashboard'))

@app.route('/complete_task/<int:task_id>')
def complete_task(task_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    
    user = session['user']
    if user not in users:
        return redirect(url_for('login'))

    task = next((t for t in tasks if t.id == task_id), None)
    if task and task.assigned_to == user:
        task.status = 'completed'
        task.completion_date = datetime.now()
        
        # Send notification to manager
        manager = users[task.assigned_to]['manager']
        manager_email = users[manager]['email']
        send_email(manager_email,
                  f'Task Completed: {task.title}',
                  f'Task "{task.title}" has been completed by {users[user]["name"]}. Please review and validate.')
        
        flash('Task marked as completed!')
    
    return redirect(url_for('member_dashboard'))

@app.route('/validate_task/<int:task_id>')
def validate_task(task_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    
    user = session['user']
    if user not in users:
        return redirect(url_for('login'))

    task = next((t for t in tasks if t.id == task_id), None)
    if task:
        task.status = 'validated'
        task.validation_date = datetime.now()
        task.kra_score = calculate_kra_score(task)
        
        # Update KRA scores
        member = task.assigned_to
        if member not in kra_scores:
            kra_scores[member] = []
        kra_scores[member].append({
            'task_id': task.id,
            'score': task.kra_score,
            'date': datetime.now().strftime('%Y-%m-%d')
        })
        
        flash('Task validated successfully!')
    
    return redirect(url_for('manager_dashboard'))

@app.route('/reopen_task/<int:task_id>')
def reopen_task(task_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    
    user = session['user']
    if user not in users:
        return redirect(url_for('login'))

    task = next((t for t in tasks if t.id == task_id), None)
    if task:
        task.status = 'reopened'
        
        # Send notification to team member
        member_email = users[task.assigned_to]['email']
        send_email(member_email,
                  f'Task Reopened: {task.title}',
                  f'Task "{task.title}" has been reopened by your manager. Please review and complete any remaining work.')
        
        flash('Task reopened!')
    
    return redirect(url_for('manager_dashboard'))

@app.route('/send_daily_kra')
def send_daily_kra():
    if 'user' not in session or users[session['user']]['role'] != 'admin':
        return redirect(url_for('login'))
    
    # Calculate daily KRA scores
    today = datetime.now().strftime('%Y-%m-%d')
    daily_scores = {}
    
    for member, scores in kra_scores.items():
        today_scores = [s for s in scores if s['date'] == today]
        if today_scores:
            avg_score = sum(s['score'] for s in today_scores) / len(today_scores)
            daily_scores[member] = avg_score
    
    # Send email to all team members
    for member, score in daily_scores.items():
        member_email = users[member]['email']
        send_email(member_email,
                  f'Daily KRA Score - {today}',
                  f'Your daily KRA score for {today}: {score:.2f}%')
    
    flash('Daily KRA scores sent to all team members!')
    return redirect(url_for('admin_dashboard'))

def send_manual_reminder(task_id, reminder_message='', reminder_type='manual'):
    """Send manual reminder for a specific task"""
    task = next((t for t in tasks if t.id == task_id), None)
    if not task:
        return False, "Task not found"
    
    # Check if reminder was sent recently (within 24 hours)
    if task.last_reminder_date and (datetime.now() - task.last_reminder_date).days < 1:
        return False, "Reminder already sent recently"
    
    assigned_user = users[task.assigned_to]
    assigned_user_email = assigned_user['email']
    
    # Create reminder message
    if not reminder_message:
        reminder_message = f"Please update the status of task '{task.title}'"
    
    subject = f'Manual Reminder: {task.title}'
    body = f'''{reminder_message}

Task Details:
- Title: {task.title}
- Status: {task.status.upper()}
- Priority: {task.priority.upper()}
- Due Date: {task.target_date.strftime('%Y-%m-%d')}
- Assigned To: {assigned_user['name']}

Task Description: {task.description}

Please update the task status or contact your manager if you need assistance.'''
    
    # Send email
    success = send_email(assigned_user_email, subject, body, reminder_type)
    
    if success:
        # Update task reminder tracking
        task.reminders.append({
            'date': datetime.now(),
            'type': reminder_type,
            'message': reminder_message,
            'sent_by': session.get('user', 'system')
        })
        task.last_reminder_date = datetime.now()
        task.reminder_count += 1
        
        # Also notify manager
        if task.assigned_to in users and 'manager' in users[task.assigned_to]:
            manager = users[task.assigned_to]['manager']
            if manager in users:
                manager_email = users[manager]['email']
                manager_subject = f'Manual Reminder Sent: {task.title}'
                manager_body = f'''A manual reminder was sent to {assigned_user['name']} for task "{task.title}".

Reminder Message: {reminder_message}

Task Status: {task.status.upper()}
Due Date: {task.target_date.strftime('%Y-%m-%d')}'''
                
                send_email(manager_email, manager_subject, manager_body, 'manual')
    
    return success, "Reminder sent successfully" if success else "Failed to send reminder"

def send_automatic_reminders():
    """Send automatic reminders based on task status and due dates"""
    today = datetime.now()
    reminders_sent = 0
    reminder_details = []
    
    for task in tasks:
        if task.status in ['pending', 'accepted', 'in_progress']:
            days_until_due = (task.target_date - today).days
            
            # Determine reminder type and frequency
            reminder_needed = False
            reminder_type = 'automatic'
            
            if days_until_due <= 0:  # Overdue
                reminder_needed = True
                reminder_type = 'urgent'
                subject = f'URGENT: Overdue Task - {task.title}'
                body = f'''Task "{task.title}" is OVERDUE!

Due Date: {task.target_date.strftime('%Y-%m-%d')}
Days Overdue: {abs(days_until_due)}
Priority: {task.priority.upper()}

Please complete this task immediately.

Task Description: {task.description}'''
                
            elif days_until_due <= 1:  # Due tomorrow
                reminder_needed = True
                reminder_type = 'urgent'
                subject = f'URGENT: Task Due Tomorrow - {task.title}'
                body = f'''Task "{task.title}" is due TOMORROW!

Due Date: {task.target_date.strftime('%Y-%m-%d')}
Priority: {task.priority.upper()}

Please complete this task today.

Task Description: {task.description}'''
                
            elif days_until_due <= 3:  # Due soon
                reminder_needed = True
                reminder_type = 'automatic'
                subject = f'Reminder: Task Due Soon - {task.title}'
                body = f'''Task "{task.title}" is due in {days_until_due} day(s).

Due Date: {task.target_date.strftime('%Y-%m-%d')}
Priority: {task.priority.upper()}

Please ensure timely completion.

Task Description: {task.description}'''
            
            # Check if reminder was sent recently (avoid spam)
            if reminder_needed:
                last_reminder_days = 0
                if task.last_reminder_date:
                    last_reminder_days = (today - task.last_reminder_date).days
                
                # Send reminder if not sent recently
                if last_reminder_days >= 1 or task.reminder_count == 0:
                    assigned_user_email = users[task.assigned_to]['email']
                    success = send_email(assigned_user_email, subject, body, reminder_type)
                    
                    if success:
                        # Update task reminder tracking
                        task.reminders.append({
                            'date': datetime.now(),
                            'type': reminder_type,
                            'message': f'Automatic reminder for task due in {days_until_due} days',
                            'sent_by': 'system'
                        })
                        task.last_reminder_date = datetime.now()
                        task.reminder_count += 1
                        reminders_sent += 1
                        
                        reminder_details.append({
                            'task': task.title,
                            'user': users[task.assigned_to]['name'],
                            'type': reminder_type,
                            'days_until_due': days_until_due
                        })
    
    return reminders_sent, reminder_details

@app.route('/send_task_reminders')
def send_task_reminders():
    """Send automatic reminders for pending and overdue tasks"""
    if 'user' not in session or users[session['user']]['role'] != 'admin':
        return redirect(url_for('login'))
    
    reminders_sent, reminder_details = send_automatic_reminders()
    
    if reminders_sent > 0:
        details_text = "\n".join([f"- {r['task']} ({r['user']}) - {r['type']}" for r in reminder_details])
        flash(f'✅ Automatic reminders sent: {reminders_sent} emails\n\nDetails:\n{details_text}')
    else:
        flash('ℹ️ No automatic reminders needed at this time')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/send_manual_reminder/<int:task_id>', methods=['POST'])
def send_manual_reminder_route(task_id):
    """Send manual reminder for a specific task - Admin only"""
    if 'user' not in session or users[session['user']]['role'] != 'admin':
        return redirect(url_for('login'))
    
    reminder_message = request.form.get('reminder_message', '')
    reminder_type = request.form.get('reminder_type', 'manual')
    
    success, message = send_manual_reminder(task_id, reminder_message, reminder_type)
    
    if success:
        flash(f'✅ {message}')
    else:
        flash(f'❌ {message}')
    
    return redirect(request.referrer or url_for('admin_dashboard'))

def get_reminder_history(task_id):
    """Get reminder history for a specific task"""
    task = next((t for t in tasks if t.id == task_id), None)
    if not task:
        return []
    
    return task.reminders

@app.route('/task_reminder_history/<int:task_id>')
def task_reminder_history(task_id):
    """View reminder history for a specific task - Admin only"""
    if 'user' not in session:
        return redirect(url_for('login'))
    
    user = session['user']
    if user not in users:
        return redirect(url_for('login'))
    
    # Check if user has permission to view this task
    task = next((t for t in tasks if t.id == task_id), None)
    if not task:
        flash('Task not found')
        return redirect(url_for('admin_dashboard'))
    
    # Only admin can view reminder history
    if users[user]['role'] != 'admin':
        flash('You do not have permission to view reminder history')
        return redirect(url_for('admin_dashboard'))
    
    reminder_history = get_reminder_history(task_id)
    
    return render_template('task_reminder_history.html',
                         task=task,
                         reminder_history=reminder_history,
                         users=users)

@app.route('/test_email')
def test_email():
    """Test email functionality"""
    if 'user' not in session or users[session['user']]['role'] != 'admin':
        return redirect(url_for('login'))
    
    try:
        test_email = users[session['user']]['email']
        send_email(test_email,
                  'Email Test - Prosonic Task Manager',
                  f'''Hello {users[session['user']]['name']},

This is a test email from your Prosonic Task Management System.

Email Configuration:
- SMTP Server: smtp.prosonic.in
- Port: 587
- From: sm@prosonic.in

If you receive this email, your email configuration is working correctly!

Best regards,
Prosonic Task Management System''')
        
        flash('✅ Test email sent successfully! Check your inbox.')
    except Exception as e:
        flash(f'❌ Email test failed: {str(e)}')
    
    return redirect(url_for('admin_dashboard'))



@app.route('/reports/monthly')
def monthly_report():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    user = session['user']
    if user not in users:
        return redirect(url_for('login'))

    if users[user]['role'] != 'admin':
        return redirect(url_for('login'))

    year = int(request.args.get('year', datetime.now().year))
    month = int(request.args.get('month', datetime.now().month))
    
    monthly_stats = get_monthly_stats(year, month)
    
    # Department-wise breakdown
    dept_breakdown = {}
    for dept_id, dept_data in departments.items():
        dept_tasks = [task for task in tasks 
                     if task.department == dept_id and 
                     task.created_date.year == year and 
                     task.created_date.month == month]
        
        dept_breakdown[dept_id] = {
            'name': dept_data['name'],
            'total': len(dept_tasks),
            'completed': len([t for t in dept_tasks if t.status == 'validated']),
            'pending': len([t for t in dept_tasks if t.status == 'pending']),
            'in_progress': len([t for t in dept_tasks if t.status in ['accepted', 'completed']])
        }
    
    return render_template('reports/monthly_report.html',
                         monthly_stats=monthly_stats,
                         dept_breakdown=dept_breakdown,
                         year=year,
                         month=month)

@app.route('/reports/employee')
def employee_report():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    user = session['user']
    if user not in users:
        return redirect(url_for('login'))

    if users[user]['role'] != 'admin':
        return redirect(url_for('login'))

    employee_id = request.args.get('employee_id')
    if employee_id and employee_id in users:
        employee_stats = get_employee_stats(employee_id)
        employee_tasks = [task for task in tasks if task.assigned_to == employee_id]
        
        return render_template('reports/employee_report.html',
                             employee=users[employee_id],
                             employee_stats=employee_stats,
                             employee_tasks=employee_tasks)
    
    # All employees report
    all_employee_stats = {}
    for user_id, user_data in users.items():
        if user_data['role'] == 'member':
            all_employee_stats[user_id] = get_employee_stats(user_id)
    
    return render_template('reports/employee_report.html',
                         all_employee_stats=all_employee_stats,
                         users=users)

@app.route('/reports/stage_wise')
def stage_wise_report():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    user = session['user']
    if user not in users:
        return redirect(url_for('login'))

    if users[user]['role'] != 'admin':
        return redirect(url_for('login'))

    # Stage-wise breakdown
    stage_stats = {
        'pending': len([t for t in tasks if t.status == 'pending']),
        'accepted': len([t for t in tasks if t.status == 'accepted']),
        'completed': len([t for t in tasks if t.status == 'completed']),
        'validated': len([t for t in tasks if t.status == 'validated']),
        'reopened': len([t for t in tasks if t.status == 'reopened'])
    }
    
    # Category-wise breakdown
    category_stats = defaultdict(lambda: {'total': 0, 'completed': 0, 'pending': 0})
    for task in tasks:
        category_stats[task.category]['total'] += 1
        if task.status == 'validated':
            category_stats[task.category]['completed'] += 1
        elif task.status == 'pending':
            category_stats[task.category]['pending'] += 1
    
    return render_template('reports/stage_wise_report.html',
                         stage_stats=stage_stats,
                         category_stats=dict(category_stats),
                         task_categories=task_categories)

@app.route('/admin/master_data')
def master_data_management():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    user = session['user']
    if user not in users:
        return redirect(url_for('login'))

    if users[user]['role'] != 'admin':
        return redirect(url_for('login'))

    return render_template('admin/master_data.html',
                         departments=departments,
                         projects=projects,
                         task_categories=task_categories,
                         users=users,
                         kra_kpi=kra_kpi)

@app.route('/admin/add_department', methods=['POST'])
def add_department():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    user = session['user']
    if user not in users:
        return redirect(url_for('login'))

    if users[user]['role'] != 'admin':
        return redirect(url_for('login'))

    dept_id = request.form['dept_id']
    dept_name = request.form['dept_name']
    manager = request.form['manager']
    
    departments[dept_id] = {
        'name': dept_name,
        'manager': manager
    }
    
    flash('Department added successfully!')
    return redirect(url_for('master_data_management'))

@app.route('/admin/add_project', methods=['POST'])
def add_project():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    user = session['user']
    if user not in users:
        return redirect(url_for('login'))

    if users[user]['role'] != 'admin':
        return redirect(url_for('login'))

    project_id = request.form['project_id']
    project_name = request.form['project_name']
    department = request.form['department']
    start_date = request.form['start_date']
    end_date = request.form['end_date']
    
    projects[project_id] = {
        'name': project_name,
        'department': department,
        'start_date': start_date,
        'end_date': end_date
    }
    
    flash('Project added successfully!')
    return redirect(url_for('master_data_management'))

@app.route('/admin/add_user', methods=['POST'])
def add_user():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    user = session['user']
    if user not in users:
        return redirect(url_for('login'))

    if users[user]['role'] != 'admin':
        return redirect(url_for('login'))

    username = request.form['username']
    password = request.form['password']
    name = request.form['name']
    email = request.form['email']
    role = request.form['role']
    department = request.form['department']
    
    users[username] = {
        'password': password,
        'role': role,
        'name': name,
        'email': email,
        'department': department
    }
    
    if role == 'manager':
        users[username]['team'] = []
    elif role == 'member':
        users[username]['manager'] = None
    
    flash('User added successfully!')
    return redirect(url_for('master_data_management'))

@app.route('/debug/users')
def debug_users():
    """Debug route - DISABLED IN PRODUCTION"""
    if not app.debug:
        return "Debug route disabled in production", 403
    if 'user' not in session:
        return redirect(url_for('login'))
    user = session['user']
    if user not in users:
        return 'Unauthorized', 403
    return '<br>'.join([f"{u} | {users[u]['name']} | {users[u]['role']} | {users[u]['email']}" for u in users])

@app.route('/debug/users_public')
def debug_users_public():
    """Public route to show all users for debugging (no auth required) - DISABLED IN PRODUCTION"""
    if not app.debug:
        return "Debug route disabled in production", 403
    user_list = []
    for username, user_data in users.items():
        user_list.append(f"{username} | {user_data['name']} | {user_data['role']} | {user_data['email']}")
    return '<br>'.join(user_list)

# --- AI Assistant Routes ---

@app.route('/ai/chat')
def ai_chat():
    """AI Chat interface"""
    if 'user' not in session:
        return redirect(url_for('login'))
    
    user = session['user']
    if user not in users:
        return redirect(url_for('login'))
    
    ai_enabled = ai_assistant.enabled if ai_assistant else False
    
    return render_template('ai_chat.html', 
                         user_data=users[user],
                         ai_enabled=ai_enabled)

@app.route('/ai/chat_message', methods=['POST'])
def ai_chat_message():
    """Handle AI chat messages"""
    if 'user' not in session:
        return jsonify({'error': 'Not authenticated'})
    
    user = session['user']
    if user not in users:
        return jsonify({'error': 'Invalid user'})
    
    message = request.form.get('message', '')
    if not message:
        return jsonify({'error': 'No message provided'})
    
    # Get user's tasks for context
    user_tasks = [task for task in tasks if task.assigned_to == user]
    
    # Get AI response
    if ai_assistant:
        response = ai_assistant.chat_with_context(message, users[user], user_tasks)
    else:
        response = "AI Assistant is not available at the moment. Please try again later."
    
    return jsonify({
        'response': response,
        'timestamp': datetime.now().strftime('%H:%M')
    })

@app.route('/ai/analyze_tasks')
def ai_analyze_tasks():
    """AI task analysis"""
    if 'user' not in session:
        return redirect(url_for('login'))
    
    user = session['user']
    if user not in users:
        return redirect(url_for('login'))
    
    user_tasks = [task for task in tasks if task.assigned_to == user]
    analysis = ai_assistant.analyze_tasks(user_tasks, users[user]['role'])
    
    return render_template('ai_analysis.html',
                         analysis=analysis,
                         user_data=users[user],
                         tasks=user_tasks,
                         ai_enabled=ai_assistant.enabled)

@app.route('/ai/productivity_tips')
def ai_productivity_tips():
    """AI productivity tips"""
    if 'user' not in session:
        return redirect(url_for('login'))
    
    user = session['user']
    if user not in users:
        return redirect(url_for('login'))
    
    # Get user's personal stats
    personal_stats = get_employee_stats(user)
    tips = ai_assistant.get_productivity_tips(users[user]['role'], personal_stats)
    
    return render_template('ai_tips.html',
                         tips=tips,
                         user_data=users[user],
                         personal_stats=personal_stats,
                         ai_enabled=ai_assistant.enabled)

@app.route('/ai/suggest_improvements', methods=['POST'])
def ai_suggest_improvements():
    """AI task improvement suggestions"""
    if 'user' not in session:
        return jsonify({'error': 'Not authenticated'})
    
    user = session['user']
    if user not in users:
        return jsonify({'error': 'Invalid user'})
    
    task_description = request.form.get('task_description', '')
    if not task_description:
        return jsonify({'error': 'No task description provided'})
    
    suggestions = ai_assistant.suggest_task_improvements(task_description, users[user]['role'])
    
    return jsonify({'suggestions': suggestions})

@app.route('/admin/view_member/<username>')
def admin_view_member(username):
    """Admin can view any member's dashboard"""
    if 'user' not in session:
        return redirect(url_for('login'))
    
    user = session['user']
    if user not in users:
        return redirect(url_for('login'))

    if users[user]['role'] != 'admin':
        return redirect(url_for('login'))
    
    if username not in users:
        flash('User not found', 'error')
        return redirect(url_for('admin_dashboard'))
    
    target_user = users[username]
    if target_user['role'] not in ['member', 'manager']:
        flash('Can only view member and manager dashboards', 'error')
        return redirect(url_for('admin_dashboard'))
    
    # Get tasks for the target user
    user_tasks = [task for task in tasks if task.assigned_to == username]
    
    # Get user stats
    user_stats = get_employee_stats(username)
    
    # Date-wise task breakdown
    date_wise_tasks = defaultdict(list)
    for task in user_tasks:
        date_key = task.created_date.strftime('%Y-%m-%d')
        date_wise_tasks[date_key].append(task)
    
    return render_template('member_dashboard.html',
                         tasks=user_tasks,
                         user=target_user,
                         users=users,
                         user_stats=user_stats,
                         date_wise_tasks=date_wise_tasks,
                         is_admin_view=True)

@app.route('/admin/task_details/<int:task_id>')
def admin_task_details(task_id):
    """Admin can view detailed task information"""
    if 'user' not in session:
        return redirect(url_for('login'))
    
    user = session['user']
    if user not in users:
        return redirect(url_for('login'))

    if users[user]['role'] != 'admin':
        return redirect(url_for('login'))
    
    # Find the task
    task = None
    for t in tasks:
        if t.id == task_id:
            task = t
            break
    
    if not task:
        flash('Task not found', 'error')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('task_details.html',
                         task=task,
                         users=users,
                         is_admin_view=True)

@app.route('/member/task_details/<int:task_id>')
def member_task_details(task_id):
    """Member can view detailed task information"""
    if 'user' not in session:
        return redirect(url_for('login'))
    
    user = session['user']
    if user not in users:
        return redirect(url_for('login'))

    if users[user]['role'] != 'member':
        return redirect(url_for('login'))
    
    # Find the task
    task = None
    for t in tasks:
        if t.id == task_id and t.assigned_to == user:
            task = t
            break
    
    if not task:
        flash('Task not found or not assigned to you', 'error')
        return redirect(url_for('member_dashboard'))
    
    return render_template('task_details.html',
                         task=task,
                         users=users,
                         is_admin_view=False)

@app.route('/manager/task_details/<int:task_id>')
def manager_task_details(task_id):
    """Manager can view detailed task information"""
    if 'user' not in session:
        return redirect(url_for('login'))
    
    user = session['user']
    if user not in users:
        return redirect(url_for('login'))

    if users[user]['role'] != 'manager':
        return redirect(url_for('login'))
    
    # Find the task
    task = None
    for t in tasks:
        if t.id == task_id and t.assigned_to in users[user].get('team', []):
            task = t
            break
    
    if not task:
        flash('Task not found or not assigned to your team', 'error')
        return redirect(url_for('manager_dashboard'))
    
    return render_template('task_details.html',
                         task=task,
                         users=users,
                         is_admin_view=False)

@app.route('/manager/view_member/<username>')
def manager_view_member(username):
    """Manager can view a specific team member's dashboard"""
    if 'user' not in session:
        return redirect(url_for('login'))
    
    user = session['user']
    if user not in users:
        return redirect(url_for('login'))

    if users[user]['role'] != 'manager':
        return redirect(url_for('login'))
    
    # Check if the member is in the manager's team
    if username not in users[user].get('team', []):
        flash('You can only view members of your team', 'error')
        return redirect(url_for('manager_dashboard'))
    
    target_user = users[username]
    user_tasks = [task for task in tasks if task.assigned_to == username]
    
    # Calculate user stats
    user_stats = {}
    if user_tasks:
        completed_tasks = [task for task in user_tasks if task.status == 'validated']
        avg_kra_score = sum(task.kra_score for task in completed_tasks if task.kra_score > 0) / len(completed_tasks) if completed_tasks else 0
        user_stats = {
            'total_tasks': len(user_tasks),
            'completed_tasks': len(completed_tasks),
            'avg_kra_score': avg_kra_score
        }
    
    # Group tasks by date
    date_wise_tasks = {}
    for task in user_tasks:
        date_key = task.created_date.strftime('%Y-%m-%d')
        if date_key not in date_wise_tasks:
            date_wise_tasks[date_key] = []
        date_wise_tasks[date_key].append(task)
    
    return render_template('member_dashboard.html',
                         tasks=user_tasks,
                         user=target_user,
                         users=users,
                         user_stats=user_stats,
                         date_wise_tasks=date_wise_tasks,
                         is_manager_view=True)

if __name__ == '__main__':
    print("Starting Flask application...")
    print(f"Environment: {'PRODUCTION' if not app.debug else 'DEVELOPMENT'}")
    print(f"Debug mode: {app.debug}")
    print(f"Email enabled: {EMAIL_CONFIG['enabled']}")
    print(f"Current working directory: {os.getcwd()}")
    try:
        port = int(os.environ.get('PORT', 8080))
        print(f"Starting Flask on port: {port}")
        app.run(host='0.0.0.0', port=port, debug=app.debug)
    except Exception as e:
        print(f"Error starting Flask app: {e}")
        import traceback
        traceback.print_exc()
