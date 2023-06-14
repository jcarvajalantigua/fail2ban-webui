#!/bin/bash

cd /var/www

# Clone the repository
git clone https://github.com/beetwenty/fail2ban-webui.git

# change to project directory
cd fail2ban-webui

#install the required dependencies
pip install -r requrements.txt

#install gunicorn
apt-get install gunicorn

#create gunicorn config file 
cat << EOF > gunicorn.conf.py
workers = 4
bind = '127.0.0.1:5000'
accesslog = '/var/log/gunicorn/access.log'
errorlog = '/var/log/gunicorn/error.log'
EOF

#create the error log directory
mkdir /var/log/gunicorn

#create a service for the server
cat << EOF > /etc/systemd/system/fail2ban-web.service
[Unit]
Description=Fail2ban-web server
After=network.target

[Service]
User=root
WorkingDirectory=/var/www/fail2ban-webui
ExecStart=gunicorn -c /var/www/fail2ban-webui/gunicorn.conf.py app:app

[Install]
WantedBy=multi-user.target
EOF

# start and enable the service
systemctl daemon-reload
systemctl start fail2ban-web.service
systemctl enable fail2ban-web.service
systemctl status fail2ban-web.service
