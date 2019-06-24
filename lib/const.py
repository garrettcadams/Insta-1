# Info
AUTHOR = 'Pure-L0G1C'
VERSION = 'v3.0.0'


# Database
DB_PATH = 'sessions.db'


# Login
CSRFTOKEN_URL = 'https://www.instagram.com/accounts/login/'
LOGIN_URL = 'https://www.instagram.com/accounts/login/ajax/'

# Limits
CSRFTOKEN_DELAY = 10 * 60  # Sec. Updates token every n seconds
MAX_ATTEMPT_TIME = 25  # Sec. Max time an attempt is suppose to last
MAX_ATTEMPT_PROXY = 16  # Max attempts per proxy

# Credentials
OUTPUT_FILE = 'Accounts.txt'

# Threads
MODES = {
    0: 128,
    1: 64,
    2: 32,
    3: 16,
    4: 8
}

# Display
DISPLAY_MODE = {
    'clean': 0,
    'verbose': 1
}

# Session
SESSION_AUTOSAVE_TIME = 15  # Secs
