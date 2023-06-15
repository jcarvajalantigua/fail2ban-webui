#!/bin/bash

# Store the current working directory
current_dir=$(pwd)

# Go to the project directory
cd /var/www/fail2ban-webui

# Check if there are updates in the repository
git fetch
if [ $(git rev-parse HEAD) != $(git rev-parse @{u}) ]; then
    # Pull the latest changes
    git pull

    # Check if there are changes in the requirements.txt file
    if ! cmp -s requirements.txt requirements.txt.bak; then
        # Install the updated requirements
        source venv/bin/activate
        pip install -r requirements.txt
        cp requirements.txt requirements.txt.bak
    fi

    # Restart the service
    sudo systemctl restart fail2ban-web.service
else
    echo "No updates available."
fi

# Return to the original working directory
cd "$current_dir"
