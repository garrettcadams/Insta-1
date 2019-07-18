import os

# Info
AUTHOR = 'Pure-L0G1C'
VERSION = 'v3.0.0-Prem'


# Database
DB_PATH = os.path.abspath('sessions.db')


# Login
CSRFTOKEN_URL = 'https://www.instagram.com/accounts/login/'
LOGIN_URL = 'https://www.instagram.com/accounts/login/ajax/'

# Limits
CSRFTOKEN_DELAY = 10 * 60  # Sec. Updates token every n seconds
MAX_ATTEMPT_TIME = 30  # Sec. Max time an attempt is suppose to last
MAX_ATTEMPT_PROXY = 20  # Max attempts per proxy

# Credentials
OUTPUT_FILE = 'Accounts.txt'

# Threads
MODES = {
    0: 512,
    1: 256,
    2: 128,
    3: 64,
    4: 32,
    5: 16,
    6: 8,
    7: 8,
    8: 2
}

# Display
DISPLAY_MODE = {
    'clean': 0,
    'verbose': 1
}

# Session
SESSION_AUTOSAVE_TIME = 15  # Secs

# Proxies
MAX_PROXY_EXPIRED = 145
