import paramiko
import subprocess
import geoip2.database
import secrets
import re
import logging
import spwd
from passlib.hash import sha512_crypt
from functools import wraps
from flask import Flask, render_template, request, redirect, session, url_for
from flask_bootstrap import Bootstrap
logger = logging.getLogger(__name__)



app = Flask(__name__)
bootstrap = Bootstrap(app)
app.secret_key = secrets.token_hex()
logging.basicConfig(level=logging.DEBUG)

# Path to the Fail2ban configuration file
FAIL2BAN_CONFIG_FILE = '/etc/fail2ban/jail.conf'

def get_country(ip):
    reader = geoip2.database.Reader('/var/www/fail2ban-webui/GeoLite2-Country/GeoLite2-Country.mmdb')
    try:
        response = reader.country(ip)
        country = response.country.name
    except geoip2.errors.AddressNotFoundError:
        country = 'Unknown'
    return country


def read_fail2ban_config():
    """
    Read the Fail2ban configuration file and extract the relevant settings.
    Modify this function based on the configuration options you want to expose.
    """
    config = {}

    with open(FAIL2BAN_CONFIG_FILE, 'r') as file:
        lines = file.readlines()

        # Example: Extract the value of maxretry from the configuration file
        for line in lines:
            if line.startswith('maxretry'):
                config['maxretry'] = line.split('=')[1].strip()
            elif line.startswith('bantime'):
                config['bantime'] = line.split('=')[1].strip()
            elif line.startswith('findtime'):
                config['findtime'] = line.split('=')[1].strip()

    return config

def write_fail2ban_config(config):
    """
    Write the modified Fail2ban configuration back to the file.
    Modify this function based on the configuration options you want to update.
    """
    with open(FAIL2BAN_CONFIG_FILE, 'r') as file:
        lines = file.readlines()

    with open(FAIL2BAN_CONFIG_FILE, 'w') as file:
        for line in lines:
            # Example: Update the maxretry value in the configuration file
            if line.startswith('maxretry'):
                file.write(f'maxretry = {config["maxretry"]}\n')
            elif line.startswith('bantime'):
                file.write(f'bantime = {config["bantime"]}\n')
            elif line.startswith('findtime'):
                file.write(f'findtime = {config["findtime"]}\n')
            else:
                file.write(line)

def reload_fail2ban():
    """
    Execute the Fail2ban reload command.
    """
    subprocess.run(['fail2ban-client', 'reload'], capture_output=True, text=True)


def get_banned_ips():
    command = ['fail2ban-client', 'status', 'sshd']
    result = subprocess.run(command, capture_output=True, text=True)
    output = result.stdout
    
    banned_ips = output.split('Banned IP list:')[1].strip().split()

    return banned_ips

def add_banned_ip(ip):
    if not re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', ip):
        raise ValueError("Invalid IP address format")

    command = ['fail2ban-client', 'set', 'sshd', 'banip', ip]
    subprocess.run(command, capture_output=True, text=True)

    

def delete_banned_ip(ip):
    if not re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', ip):
        raise ValueError("Invalid IP address format")

    command = ['fail2ban-client', 'set', 'sshd', 'unbanip', ip]
    subprocess.run(command, capture_output=True, text=True)





def authenticate_system(username, password):
    try:
        # Retrieve the user's encrypted password from the system password database
        encrypted_password = spwd.getspnam(username).sp_pwd

        # Generate the password hash using the provided password and the same salt as the user's password
        salt = encrypted_password.split('$')[2]
        password_hash = sha512_crypt.using(rounds=656000, salt=salt).hash(password)

        # Compare the encrypted password and the generated password hash
        if encrypted_password == password_hash:
            return True
        else:
            return False
    except KeyError:
        return False




def authenticate(username, password):
    # You can add additional authentication methods here
    if authenticate_system(username, password):
        return True
    else:
        return False


def system_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session or not authenticate_system(session['username'], session['password']):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
@system_login_required
def index():
    banned_ips = get_banned_ips()
    # Get top countries based on banned IPs
    top_countries = {}
    for ip in banned_ips:
        country = get_country(ip)
        top_countries[country] = top_countries.get(country, 0) + 1

    # Sort the countries based on the count
    sorted_countries = sorted(top_countries.items(), key=lambda x: x[1], reverse=True)

    return render_template('index.html', banned_ips=banned_ips, top_countries=sorted_countries)




@app.route('/config', methods=['GET', 'POST'])
@system_login_required
def config():
    if 'username' in session:
        if request.method == 'POST':
            # Retrieve form data and update the configuration
            maxretry = request.form.get('maxretry')
            bantime = request.form.get('bantime')
            findtime = request.form.get('findtime')

            config = read_fail2ban_config()
            config['maxretry'] = maxretry
            config['bantime'] = bantime
            config['findtime'] = findtime
            write_fail2ban_config(config)

            # Reload Fail2ban
            reload_fail2ban()

            # Redirect to the configuration page after saving
            return redirect(url_for('config'))
        else:
            # Read the current Fail2ban configuration
            config = read_fail2ban_config()
            banned_ips = get_banned_ips()
            return render_template('config.html', config=config, banned_ips=banned_ips) 
    else:
        return redirect(url_for('login'))

@app.route('/banip', methods=['POST'])
@system_login_required
def ban_ip():
    if 'username' in session:
        ip = request.form.get('ip')
        add_banned_ip(ip)
        return redirect(url_for('config'))
    else:
        return redirect(url_for('login'))

@app.route('/unbanip', methods=['POST'])
@system_login_required
def unban_ip():
    if 'username' in session:
        ip = request.form.get('ip')
        delete_banned_ip(ip)
        return redirect(url_for('config'))
    else:
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if authenticate(username, password):
            session['username'] = username
            session['password'] = password
            return redirect(url_for('index'))
        else:
            return render_template('login.html', message='Invalid credentials')
    else:
        return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0')
