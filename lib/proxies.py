# Date: 06/03/2019
# Author: Mohamed
# Description: Proxies

import requests
from queue import Queue
from collections import deque
from requests_html import HTMLSession


class Proxies:

    '''Public proxies scraper.
    '''

    def __init__(self, max_proxy_expired=64) -> None:
        self.URL = 'https://www.sslproxies.org/'
        self._proxies: 'Queue[dict]' = Queue()
        self._proxy_expired: deque = deque()
        self._max_proxy_expired = max_proxy_expired

    def _fetch_proxies(self) -> None:
        '''Scrapes for SSL proxies.
        '''

        session = HTMLSession()

        try:
            resp = session.get(self.URL)
        except:
            return

        for row in resp.html.find('#proxylisttable', first=True).find('tbody', first=True).find('tr'):

            td = row.find('td')
            ip, port = td[0].text, td[1].text

            addr = '{}:{}'.format(ip, port)
            proxy = {'http': addr, 'https': addr}

            if proxy in self._proxy_expired:
                continue

            self._proxies.put(proxy)

    def qsize(self) -> int:
        '''Return the number of proxies in the queue.
        '''

        return self._proxies.qsize()

    def get_proxy(self) -> dict:
        '''Returns a proxy when called.
        Returns an empty dict when fails.
        '''

        if self._proxies.qsize():
            return self._proxies.get()
        else:
            self._fetch_proxies()

        if self._proxies.qsize():
            return self._proxies.get()

        return {}

    def proxy_expired(self, proxy: dict) -> None:
        '''Suspendes a proxy until it gets push out of the suspension list.
        '''

        if len(self._proxy_expired) >= self._max_proxy_expired:
            self._proxy_expired.popleft()

        self._proxy_expired.append(proxy)
