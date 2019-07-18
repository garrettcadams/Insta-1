# Date: 06/08/2019
# Author: Mohamed
# Description: A browser

import time
import requests
import lib.const as const


class Browser:

    '''Browser
    '''

    def __init__(self, username: str, password: str, proxy: dict, csrftoken: str) -> None:

        # consts
        self.proxy = proxy
        self.username = username
        self.password = password
        self.csrftoken = csrftoken

        # states
        self.is_processed = False
        self.is_attempted = False
        self.proxy_failed = False
        self.is_authenticated = False
        self.time_started = time.time()
        self.password_attempted = False

        self.time_elapsed = None

    def parse_resp(self, resp) -> None:
        '''Parse the response of the API.
        '''

        if 'authenticated' in resp:
            if resp['authenticated']:
                self.is_authenticated = True
        elif 'message' in resp:
            if resp['message'] == 'checkpoint_required':
                self.is_authenticated = True
            else:
                self.proxy_failed = True

        elif resp['errors'] in resp:
            self.proxy_failed = True

    def login(self) -> None:
        '''Make a request to Instagram's login API.
        '''

        headers = {
            'x-csrftoken': self.csrftoken,
            'accept-language': 'en-US,en;q=0.9',
            # 'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 9_3_2 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Mobile/13F69 Instagram 8.4.0 (iPhone7,2; iPhone OS 9_3_2; nb_NO; nb-NO; scale=2.00; 750x1334'
        }

        data = {
            'username': self.username,
            'password': self.password
        }

        try:
            resp = requests.post(
                data=data,
                headers=headers,
                proxies=self.proxy,
                url=const.LOGIN_URL,
                timeout=const.MAX_ATTEMPT_TIME
            )

            self.parse_resp(resp.json())
            self.password_attempted = True
            self.time_elapsed = time.time() - self.time_started
        except:
            self.proxy_failed = True
        finally:
            self.is_attempted = True
