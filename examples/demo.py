import requests
from stem.control import Listener
from torplex import TorManager

man = TorManager()

try:

    for _ in range(20):
        man.spawn().wait_for()

    print '\nSERVERS:\n'

    for t in man.get_tors():
        c = t.connect()
        host, port = c.get_listeners(Listener.SOCKS)[0]
        assert port == t.get_port()
        print '{}:{}'.format(host, port)
        c.close()

    print '\nIP ADDRESSES:\n'

    for t in man.get_tors():
        s = requests.Session()
        proxy = 'socks5://localhost:{}'.format(t.get_port())
        s.proxies['http'] = proxy
        s.proxies['https'] = proxy
        print s.get('http://ipecho.net/plain').text

except Exception as e:
    raise

finally:
    for tor in man.get_tors():
        tor.kill()
