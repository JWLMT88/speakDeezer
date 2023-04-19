import hashlib
import os
import appdirs
from pathlib import Path
import subprocess
import datetime

appdata_dir = Path.home() / 'AppData' / 'Local' / 'speakDeezer'

APP_NAME = 'speakDeezer'
USER_FILE = appdata_dir / 'users.txt' #os.path.join(appdirs.user_data_dir(APP_NAME), 'users.txt')
CURRENT_USER_FILE = appdata_dir / 'current_user.txt' #os.path.join(appdirs.user_data_dir(APP_NAME), 'current_user.txt')

def register(username, password):
    # hash password
    hashed_password = hash_password(password)
    # Create the directory if it doesn't exist
    appdata_dir.mkdir(parents=True, exist_ok=True)
    # check if user file exists
    if not os.path.exists(USER_FILE):
        # create user file if it doesn't exist
        os.makedirs(os.path.dirname(USER_FILE), exist_ok=True)
        with open(USER_FILE, 'w') as f:
            f.write('')
    
    # check if username is already taken
    if check_username_exists(username):
        print('Username already taken')
        return False
    
    # add user to file
    with open(USER_FILE, 'a') as f:
        f.write(f'{username}:{hashed_password}\n')
    # log in user
    login(username, password)
    return True

def login(username, password):
    # check if user file exists
    if not os.path.exists(USER_FILE):
        print('No users registered yet')
        return False
    
    # check if username and password match
    with open(USER_FILE, 'r') as f:
        for line in f:
            line = line.strip()
            parts = line.split(':')
            if parts[0] == username:
                hashed_password = parts[1]
                if check_password(password, hashed_password):
                    # log in user
                    with open(CURRENT_USER_FILE, 'w') as cu:
                        cu.write(username)
                    print(f'Logged in as {username}')
                    return True
                else:
                    print('Incorrect password')
                    return False
    
    print('User not found')
    return False

def logout():
    # log out user
    os.remove(CURRENT_USER_FILE)

def get_current_user():
    # check if current user file exists
    if os.path.exists(CURRENT_USER_FILE):
        with open(CURRENT_USER_FILE, 'r') as cu:
            username = cu.read().strip()
            return username
    else:
        return None

def hash_password(password):
    password_bytes = password.encode('utf-8')
    hash_object = hashlib.sha256(password_bytes)
    hashed_password = hash_object.hexdigest()
    return hashed_password

def check_password(password, hashed_password):
    if hash_password(password) == hashed_password:
        return True
    else:
        return False

def check_username_exists(username):
    if not os.path.exists(USER_FILE):
        return False
    
    with open(USER_FILE, 'r') as f:
        for line in f:
            line = line.strip()
            parts = line.split(':')
            if parts[0] == username:
                return True
    
    return False

def check_subscription_status():
    try:
        result = subprocess.run(['python', 'subtype.py'], capture_output=True, text=True)
        subscription_status = result.stdout.strip()
    except:
        print('Error checking subscription status')
        return False
    
    if subscription_status == 'active':
        expiration_date = datetime.date.today() + datetime.timedelta(days=365)
        sub_dict = {'status': 'active', 'expiration_date': str(expiration_date)}
    else:
        sub_file = Path('sub.xml')
        if sub_file.is_file():
            with open(sub_file, 'r') as f:
                sub_dict = eval(f.read())
                if sub_dict['status'] == 'trial':
                    trial_start_date = datetime.datetime.strptime(sub_dict['start_date'], '%Y-%m-%d').date()
                    today_date = datetime.date.today()
                    trial_days = (today_date - trial_start_date).days
                    if trial_days >= 14:
                        sub_dict['status'] = 'expired'
                    else:
                        sub_dict['days_remaining'] = 14 - trial_days
                else:
                    sub_dict['status'] = 'expired'
        else:
            expiration_date = datetime.date.today() + datetime.timedelta(days=14)
            sub_dict = {'status': 'trial', 'start_date': str(datetime.date.today()), 'expiration_date': str(expiration_date), 'days_remaining': 14}
    
    with open('sub.xml', 'w') as f:
        f.write(str(sub_dict))
    
    return sub_dict


