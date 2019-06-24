# Date: 06/08/2019
# Author: Mohamed
# Description: Password manager

import os
import time
from hashlib import sha256
from collections import deque
from lib.session import Session

from lib.display import Display


class Password:

    '''Password manager.
    '''

    def __init__(self, username, wordlist, max_passwords=64) -> None:

        # Consts
        self.session = None
        self.wordlist = wordlist
        self.username = username
        self.display = Display()
        self.max_passwords = max_passwords
        self.total_lines = self.count_lines(wordlist)

        # States
        self.EOF = False  # end of file
        self.is_alive = True

        # resume
        self.attempts = 0
        self.resume = False

        # Storages
        self.passwords = deque()

    def check_password_path(self) -> None:
        '''Checks to see if password path exists.
        '''

        if not os.path.exists(self.wordlist):
            self.display.danger(
                'Error', ':', 'Failed to locate the password list provided'
            )

            exit()

    def count_lines(self, wordlist) -> int:
        '''Count the number of lines in the wordlist.
        '''

        self.display.clear()
        self.check_password_path()

        lines = 0
        fingerprint = sha256(
            self.username.lower().strip().encode()
        ).hexdigest().encode()

        self.display.info('Loading password list', '', '...')
        time.sleep(3)

        with open(wordlist, 'rb') as f:

            for data in f:
                lines += 1
                chunk = sha256(data).hexdigest().encode()
                fingerprint = sha256(fingerprint + chunk).hexdigest().encode()

        self.session = Session(fingerprint)
        return lines

    def read_file(self) -> None:
        '''Read each line and append into the passwords deque.
        '''

        attempts = 0  # for resuming

        with open(self.wordlist, 'rt') as f:

            for line in f:

                if self.resume:
                    if attempts < self.attempts + self.size():
                        attempts += 1
                        continue
                    elif self.resume:
                        self.resume = False

                while self.size() >= self.max_passwords:

                    if self.is_alive:
                        time.sleep(0.5)
                        continue
                    else:
                        break

                if not self.is_alive:
                    break

                self.put_password(line.strip())

        # check if EOF is reached
        if self.is_alive:
            self.EOF = True
            self.stop()

    def put_password(self, pwd) -> None:
        '''Put a password into the passwords deque.
        '''

        if not pwd in self.passwords:
            self.passwords.appendleft(pwd)

    def size(self) -> int:
        '''Returns the size of the passwords deque.
        '''

        return len(self.passwords)

    def is_done(self) -> bool:
        '''Returns turn if EOF is reached and the passwords deque is empty.
        '''

        if self.EOF and self.size() == 0:
            return True
        return False

    def get_password(self) -> str:
        '''Get a password from the passwords deque.

        Returns an empty str if deque is empty.
        '''

        if self.size() == 0:
            return ''

        return self.passwords.popleft()

    def start(self) -> None:
        self.read_file()

    def stop(self) -> None:
        self.is_alive = False
