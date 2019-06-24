# Date: 06/03/2019
# Author: Mohamed
# Description: Proxies

from requests_html import HTMLSession
from collections import deque
import requests


class Proxies:

    '''Scrape public proxies.
    '''

    def __init__(self, max_proxy_expired=64) -> None:
        self._proxies = deque()
        self._proxy_expired: deque = deque()
        self._max_proxy_expired = max_proxy_expired

        self.links = {
            'http': [
                'https://www.sslproxies.org/',
                'https://free-proxy-list.net/'
            ],

            'socks': ['https://www.socks-proxy.net/']
        }

    def qsize(self) -> int:
        '''Returns the size of the queue.
        '''

        return len(self._proxies)

    def _scrape(self, URL, session, proxy_type: str) -> None:
        '''Scrape the proxy of the given site.
        '''

        try:
            resp = session.get(
                URL,
                headers={'accept-language': 'en-US,en;q=0.9'}
            )
        except:
            return

        for row in resp.html.find('#proxylisttable', first=True).find('tbody', first=True).find('tr'):

            td = row.find('td')
            ip, port = td[0].text, td[1].text

            if proxy_type == 'socks':
                addr = '{}://{}:{}'.format(td[4].text, ip, port)
            else:
                addr = '{}:{}'.format(ip, port)

            proxy = {'http': addr, 'https': addr}

            if proxy in self._proxy_expired:
                continue

            if proxy in self._proxies:
                continue

            self._proxies.append(proxy)

    def _fetch_proxies(self) -> None:
        '''Scrapes for proxies.
        '''

        session = HTMLSession()

        for proxy_type in self.links:
            for URL in self.links[proxy_type]:
                self._scrape(URL, session, proxy_type)

    def get_proxy(self) -> dict:
        '''Returns a proxy when called.
        Returns an empty dict when fails.
        '''

        if self.qsize():
            return self._proxies.popleft()
        else:
            try:
                self._fetch_proxies()
            except:
                pass

        if self.qsize():
            return self._proxies.popleft()

        return {}

    def proxy_expired(self, proxy: dict) -> None:
        '''Suspendes a proxy until it gets push out of the suspension list.
        '''

        if len(self._proxy_expired) >= self._max_proxy_expired:
            self._proxy_expired.popleft()

        self._proxy_expired.append(proxy)
