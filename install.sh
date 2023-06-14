#!/bin/bash

sudo apt-get install -y git
sudo apt-get install -y python3 pip

cd /var/www

# Clone the repository
sudo git clone https://github.com/beetwenty/fail2ban-webui.git

# change to project directory
cd fail2ban-webui

#install the required dependencies
sudo pip install -r requrements.txt

#install gunicorn
sudo apt-get install -y gunicorn 

#create gunicorn config file 
sudo cat << EOF > gunicorn.conf.py
workers = 4
bind = '127.0.0.1:5000'
accesslog = '/var/log/gunicorn/access.log'
errorlog = '/var/log/gunicorn/error.log'
EOF

#create the error log directory
sudo mkdir /var/log/gunicorn

#create a service for the server
sudo cat << EOF > /etc/systemd/system/fail2ban-web.service
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
sudo systemctl daemon-reload
sudo systemctl start fail2ban-web.service
sudo systemctl enable fail2ban-web.service
sudo systemctl status fail2ban-web.service
