# Date: 06/03/2019
# Author: Mohamed
# Description: Proxies

import lib.const as const
from collections import deque
from requests_html import HTMLSession


class OpenProxy:

    '''Scrape proxies from https://api.openproxy.space/
    '''

    def __init__(self):
        self.URL = 'https://api.openproxy.space/free-proxy-list'

    def _scrape(self, session) -> dict:
        '''Scrape the links and return the proxies.
        '''

        try:
            resp = session.get(
                self.URL,
                headers={
                    'accept-language': 'en-US,en;q=0.9', 
                    'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 9_3_2 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Mobile/13F69 Instagram 8.4.0 (iPhone7,2; iPhone OS 9_3_2; nb_NO; nb-NO; scale=2.00; 750x1334'
                }
            )

        except:
            yield {}

        for proxy in resp.json()['proxies']:

            addr = '{}:{}'.format(proxy['ip'], proxy['port'])
            protos = proxy['protocols']

            if 3 in protos:
                addr = 'socks4://{}'.format(addr)
            elif 4 in protos:
                addr = 'socks5://{}'.format(addr)

            yield {'http': addr, 'https': addr}

    def _fetch_proxies(self) -> dict:
        '''Scrapes for proxies.
        '''

        for proxy in self._scrape(HTMLSession()):
            yield proxy


class ProxiesSocks:

    '''Scrape proxies from https://free-socks.in/
    '''

    def __init__(self):
        self.links = {
            'http': ['https://free-socks.in/http-proxy-list/'],
            'socks': ['https://free-socks.in/socks-proxy-list/']
        }

    def _scrape(self, URL, session, proxy_type) -> dict:
        '''Scrape the links and return the proxies.
        '''

        try:
            resp = session.get(
                URL,
                headers={'accept-language': 'en-US,en;q=0.9', 'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 9_3_2 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Mobile/13F69 Instagram 8.4.0 (iPhone7,2; iPhone OS 9_3_2; nb_NO; nb-NO; scale=2.00; 750x1334'}
            )
        except:
            return {}

        for row in resp.html.find('tbody', first=True).find('tr'):

            row = row.find('td')
            ip_port, socks_type = row[1].text, row[2].text

            addr = '{}://{}'.format(socks_type,
                                    ip_port) if proxy_type == 'socks' else ip_port

            proxy = {'http': addr, 'https': addr}

            yield proxy

    def _fetch_proxies(self) -> dict:
        '''Scrapes for proxies.
        '''

        session = HTMLSession()

        for proxy_type in self.links:
            for URL in self.links[proxy_type]:
                for proxy in self._scrape(URL, session, proxy_type):
                    yield proxy


class Proxies:

    '''Scrape public proxies.
    '''

    def __init__(self) -> None:
        self._proxies: deque = deque()
        self._proxy_expired: deque = deque()
        self._max_proxy_expired: int = const.MAX_PROXY_EXPIRED
        self._extra_proxies: tuple = (ProxiesSocks(), OpenProxy())

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
                headers={'accept-language': 'en-US,en;q=0.9', 'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 9_3_2 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Mobile/13F69 Instagram 8.4.0 (iPhone7,2; iPhone OS 9_3_2; nb_NO; nb-NO; scale=2.00; 750x1334'}
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

        # Extra proxies
        for obj in self._extra_proxies:

            for proxy in obj._fetch_proxies():

                if proxy in self._proxy_expired:
                    continue

                if proxy in self._proxies:
                    continue

                self._proxies.append(proxy)

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
