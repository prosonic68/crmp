#!/bin/bash

# VPS Deployment Script for Prosonic Task Manager

echo "🚀 Deploying Prosonic Task Manager to VPS..."

# Update system
sudo apt update
sudo apt upgrade -y

# Install Python and pip
sudo apt install python3 python3-pip python3-venv -y

# Install Nginx
sudo apt install nginx -y

# Create app directory
sudo mkdir -p /var/www/prosonic-task-manager
sudo chown $USER:$USER /var/www/prosonic-task-manager

# Copy app files (you'll need to upload your files)
# scp -r ./* user@your-server:/var/www/prosonic-task-manager/

# Create virtual environment
cd /var/www/prosonic-task-manager
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create systemd service
sudo tee /etc/systemd/system/prosonic-task-manager.service > /dev/null <<EOF
[Unit]
Description=Prosonic Task Manager
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/prosonic-task-manager
Environment="PATH=/var/www/prosonic-task-manager/venv/bin"
ExecStart=/var/www/prosonic-task-manager/venv/bin/gunicorn --workers 3 --bind unix:prosonic-task-manager.sock -m 007 wsgi:app

[Install]
WantedBy=multi-user.target
EOF

# Start and enable service
sudo systemctl start prosonic-task-manager
sudo systemctl enable prosonic-task-manager

# Configure Nginx
sudo tee /etc/nginx/sites-available/prosonic-task-manager > /dev/null <<EOF
server {
    listen 80;
    server_name your-domain.com;

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/prosonic-task-manager/prosonic-task-manager.sock;
    }
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/prosonic-task-manager /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx

echo "✅ Deployment complete! Your app should be available at http://your-domain.com" 