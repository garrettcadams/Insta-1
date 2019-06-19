# Info
AUTHOR = 'Mohamed(Pure-L0G1C)'
VERSION = 'v3.0.0'


# Database
DB_PATH = 'Sessions.db'


# Login
CSRFTOKEN_URL = 'https://www.instagram.com/accounts/login/'
LOGIN_URL = 'https://www.instagram.com/accounts/login/ajax/'

# Limits
CSRFTOKEN_DELAY = 10  # sec
MAX_ATTEMPT_TIME = 20  # sec. Max time an attempt is suppose to last

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
