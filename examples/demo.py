from __future__ import print_function
import requests
from stem.control import Listener
from torplex import TorManager


with TorManager() as man:

    for _ in range(20):
        man.spawn()

    print('\nSERVERS:\n')

    for t in man.get_tors():
        c = t.connect()
        host, port = c.get_listeners(Listener.SOCKS)[0]
        assert port == t.get_port()
        print('{}:{}'.format(host, port))
        c.close()

    print('\nIP ADDRESSES:\n')

    for t in man.get_tors():
        s = requests.Session()
        proxy = 'socks5://localhost:{}'.format(t.get_port())
        s.proxies['http'] = proxy
        s.proxies['https'] = proxy
        print(s.get('http://ipecho.net/plain').text)
