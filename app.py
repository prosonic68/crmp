print('app.py is running')
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from datetime import datetime, timedelta
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import calendar
from collections import defaultdict

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this in production

# Enhanced Data storage with master data
departments = {
    'IT': {'name': 'Information Technology', 'manager': 'manager1'},
    'HR': {'name': 'Human Resources', 'manager': 'manager2'},
    'FIN': {'name': 'Finance', 'manager': 'manager3'},
    'MKT': {'name': 'Marketing', 'manager': 'manager4'}
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

users = {
    'admin': {'password': 'admin', 'role': 'admin', 'name': 'Admin User', 'email': 'admin@company.com', 'department': 'IT'},
    'manager1': {'password': 'manager123', 'role': 'manager', 'name': 'John Manager', 'email': 'manager@company.com', 'department': 'IT', 'team': ['user1', 'user2']},
    'manager2': {'password': 'manager123', 'role': 'manager', 'name': 'Sarah HR Manager', 'email': 'hr@company.com', 'department': 'HR', 'team': ['user3', 'user4']},
    'manager3': {'password': 'manager123', 'role': 'manager', 'name': 'Mike Finance Manager', 'email': 'finance@company.com', 'department': 'FIN', 'team': ['user5', 'user6']},
    'manager4': {'password': 'manager123', 'role': 'manager', 'name': 'Lisa Marketing Manager', 'email': 'marketing@company.com', 'department': 'MKT', 'team': ['user7', 'user8']},
    'user1': {'password': 'user123', 'role': 'member', 'name': 'Alice Developer', 'email': 'alice@company.com', 'department': 'IT', 'manager': 'manager1'},
    'user2': {'password': 'user123', 'role': 'member', 'name': 'Bob Tester', 'email': 'bob@company.com', 'department': 'IT', 'manager': 'manager1'},
    'user3': {'password': 'user123', 'role': 'member', 'name': 'Carol HR Assistant', 'email': 'carol@company.com', 'department': 'HR', 'manager': 'manager2'},
    'user4': {'password': 'user123', 'role': 'member', 'name': 'David Recruiter', 'email': 'david@company.com', 'department': 'HR', 'manager': 'manager2'},
    'user5': {'password': 'user123', 'role': 'member', 'name': 'Eve Accountant', 'email': 'eve@company.com', 'department': 'FIN', 'manager': 'manager3'},
    'user6': {'password': 'user123', 'role': 'member', 'name': 'Frank Analyst', 'email': 'frank@company.com', 'department': 'FIN', 'manager': 'manager3'},
    'user7': {'password': 'user123', 'role': 'member', 'name': 'Grace Designer', 'email': 'grace@company.com', 'department': 'MKT', 'manager': 'manager4'},
    'user8': {'password': 'user123', 'role': 'member', 'name': 'Henry Copywriter', 'email': 'henry@company.com', 'department': 'MKT', 'manager': 'manager4'}
}

tasks = []
task_requests = []
kra_scores = {}

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
        self.department = department or users[assigned_to]['department']
        self.accepted_date = None
        self.completion_date = None
        self.validation_date = None
        self.roadmap = []
        self.reminders = []
        self.extension_requests = []
        self.kra_score = 0
        self.quality_score = 0
        self.collaboration_score = 0

def send_email(to_email, subject, body):
    """Send email notification (configure with your SMTP settings)"""
    try:
        # Configure your SMTP settings here
        # msg = MIMEMultipart()
        # msg['From'] = 'your-email@company.com'
        # msg['To'] = to_email
        # msg['Subject'] = subject
        # msg.attach(MIMEText(body, 'plain'))
        # server = smtplib.SMTP('smtp.gmail.com', 587)
        # server.starttls()
        # server.login('your-email@company.com', 'your-password')
        # server.send_message(msg)
        # server.quit()
        print(f"Email sent to {to_email}: {subject}")
    except Exception as e:
        print(f"Email sending failed: {e}")

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
    if 'user' not in session:
        return redirect(url_for('login'))
    
    user = session['user']
    user_data = users[user]
    
    if user_data['role'] == 'admin':
        return redirect(url_for('admin_dashboard'))
    elif user_data['role'] == 'manager':
        return redirect(url_for('manager_dashboard'))
    else:
        return redirect(url_for('member_dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username in users and users[username]['password'] == password:
            session['user'] = username
            return redirect(url_for('home'))
        else:
            flash('Invalid credentials')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'user' not in session or users[session['user']]['role'] != 'admin':
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
    if 'user' not in session or users[session['user']]['role'] != 'manager':
        return redirect(url_for('login'))
    
    manager = session['user']
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

@app.route('/member/dashboard')
def member_dashboard():
    if 'user' not in session or users[session['user']]['role'] != 'member':
        return redirect(url_for('login'))
    
    member = session['user']
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
                         personal_stats=personal_stats)

@app.route('/create_task', methods=['GET', 'POST'])
def create_task():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        assigned_to = request.form['assigned_to']
        timeline_days = int(request.form['timeline_days'])
        priority = request.form['priority']
        category = request.form['category']
        project_id = request.form['project_id'] if request.form['project_id'] else None
        
        task = Task(
            id=len(tasks) + 1,
            title=title,
            description=description,
            assigned_by=session['user'],
            assigned_to=assigned_to,
            timeline_days=timeline_days,
            priority=priority,
            category=category,
            project_id=project_id
        )
        
        # Create roadmap
        days_per_phase = timeline_days // 4
        for i in range(4):
            phase_date = task.created_date + timedelta(days=days_per_phase * (i + 1))
            task.roadmap.append({
                'phase': f'Phase {i+1}',
                'date': phase_date.strftime('%Y-%m-%d'),
                'description': f'Complete {25 * (i+1)}% of the task'
            })
        
        tasks.append(task)
        
        # Send notification to assigned user
        assigned_user = users[assigned_to]
        send_email(assigned_user['email'], 
                  f'New Task Assigned: {title}',
                  f'You have been assigned a new task: {title}\nTimeline: {timeline_days} days\nPlease review and accept.')
        
        flash('Task created successfully!')
        return redirect(url_for('home'))
    
    # Get available team members based on user role
    user = session['user']
    user_data = users[user]
    
    if user_data['role'] == 'admin':
        available_members = [u for u in users if users[u]['role'] == 'member']
    elif user_data['role'] == 'manager':
        available_members = user_data['team']
    else:
        available_members = []
    
    # Get available projects for user's department
    available_projects = {}
    if user_data['role'] in ['admin', 'manager']:
        dept = user_data['department']
        available_projects = {pid: pdata for pid, pdata in projects.items() if pdata['department'] == dept}
    
    return render_template('create_task.html', 
                         available_members=available_members,
                         available_projects=available_projects,
                         task_categories=task_categories)

@app.route('/accept_task/<int:task_id>')
def accept_task(task_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    
    task = next((t for t in tasks if t.id == task_id), None)
    if task and task.assigned_to == session['user']:
        task.status = 'accepted'
        task.accepted_date = datetime.now()
        
        # Send notification to manager
        manager = users[task.assigned_to]['manager']
        manager_email = users[manager]['email']
        send_email(manager_email,
                  f'Task Accepted: {task.title}',
                  f'Task "{task.title}" has been accepted by {users[session["user"]]["name"]}')
        
        flash('Task accepted successfully!')
    
    return redirect(url_for('member_dashboard'))

@app.route('/request_extension/<int:task_id>', methods=['POST'])
def request_extension(task_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    
    task = next((t for t in tasks if t.id == task_id), None)
    if task and task.assigned_to == session['user']:
        extra_days = int(request.form['extra_days'])
        reason = request.form['reason']
        
        extension_request = {
            'task_id': task_id,
            'requested_by': session['user'],
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
    
    task = next((t for t in tasks if t.id == task_id), None)
    if task and task.assigned_to == session['user']:
        task.status = 'completed'
        task.completion_date = datetime.now()
        
        # Send notification to manager
        manager = users[task.assigned_to]['manager']
        manager_email = users[manager]['email']
        send_email(manager_email,
                  f'Task Completed: {task.title}',
                  f'Task "{task.title}" has been completed by {users[session["user"]]["name"]}. Please review and validate.')
        
        flash('Task marked as completed!')
    
    return redirect(url_for('member_dashboard'))

@app.route('/validate_task/<int:task_id>')
def validate_task(task_id):
    if 'user' not in session:
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

@app.route('/reports/monthly')
def monthly_report():
    if 'user' not in session:
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
    if 'user' not in session or users[session['user']]['role'] != 'admin':
        return redirect(url_for('login'))
    
    return render_template('admin/master_data.html',
                         departments=departments,
                         projects=projects,
                         task_categories=task_categories,
                         users=users,
                         kra_kpi=kra_kpi)

@app.route('/admin/add_department', methods=['POST'])
def add_department():
    if 'user' not in session or users[session['user']]['role'] != 'admin':
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
    if 'user' not in session or users[session['user']]['role'] != 'admin':
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
    if 'user' not in session or users[session['user']]['role'] != 'admin':
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

if __name__ == '__main__':
    app.run(debug=True)
