#!/bin/bash

# Delete old files
sudo rm -r /var/www/fail2ban*

# Install requirements
sudo apt-get install -y git python3-pip gunicorn

cd /var/www

# Clone the repository
sudo git clone https://github.com/beetwenty/fail2ban-webui.git

# Change to project directory
cd fail2ban-webui

# Create and activate a virtual environment (optional)
sudo apt-get install -y python3-venv
sudo python3 -m venv venv
source venv/bin/activate

# Install the required dependencies
sudo pip install -r requirements.txt

# Create Gunicorn config file
sudo cat <<EOF > gunicorn.conf.py
workers = 4
bind = '127.0.0.1:5000'
accesslog = '/var/log/gunicorn/access.log'
errorlog = '/var/log/gunicorn/error.log'
EOF

# Create the error log directory
sudo mkdir -p /var/log/gunicorn

# Create a service for the server
sudo cat <<EOF > /etc/systemd/system/fail2ban-web.service
[Unit]
Description=Fail2ban-web server
After=network.target

[Service]
User=root
WorkingDirectory=/var/www/fail2ban-webui
ExecStart=/usr/bin/gunicorn -c /var/www/fail2ban-webui/gunicorn.conf.py app:app

[Install]
WantedBy=multi-user.target
EOF

# Start and enable the service
sudo systemctl daemon-reload
sudo systemctl enable fail2ban-web.service
sudo systemctl start fail2ban-web.service
sudo systemctl status fail2ban-web.service
