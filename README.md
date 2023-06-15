# Fail2ban Webui

Fail2ban Webui is a web interface for managing Fail2ban on your server. It provides a user-friendly interface to view and manage banned IP addresses, configure jails, and monitor the status of Fail2ban.

## Features

- View a list of banned IP addresses
- Unban IP addresses
- Configure and manage Fail2ban jails
- Monitor the status of Fail2ban service

## Installation 
### option 1 (recomended)

1. Clone the repository:
```bash
git clone https://github.com/beetwenty/fail2ban-webui.git
```
2. Change to the project directory:
```bash
cd fail2ban-webui
```
3. Install the required dependencies:
```bash
pip install -r requirements.txt
```
4. Install gunicorn
```bash
apt-get install gunicorn
```
5. create gunicorn config file
```bash
vi gunicorn.conf.py
```
example
```python
workers = 4
bind = '127.0.0.1:5000'
accesslog = '/var/log/gunicorn/access.log'
errorlog = '/var/log/gunicorn/error.log'
```
6. create the error log dir.
```bash
mkdir /var/log/gunicorn
```
7. create a service for the server.
```bash
vi /etc/systemd/system/fail2ban-web.service
```
```python
[Unit]
Description=Fail2ban-web server
After=network.target

[Service]
User=root
WorkingDirectory=/var/www/fail2ban-webui
ExecStart=gunicorn -c /var/www/fail2ban-webui/gunicorn.conf.py app:app

[Install]
WantedBy=multi-user.target
```
8. start and enable the service.
```bash
systemctl daemon-reload
systemctl start fail2ban-web.service
systemctl enable fail2ban-web.service
```
### option 2
1. download install script.
   ```bash
   wget https://raw.githubusercontent.com/BeeTwenty/fail2ban-webui/master/install.sh
  ```
2. run the installer
```bash
sudo bash install.sh
```


the web ui should now be available at http://localhost:5000/ use your servers login
## Contributing

Contributions are welcome! If you find any bugs or have suggestions for improvements, please open an issue or submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE).

## Acknowledgements

Fail2ban Web is built using Flask,
