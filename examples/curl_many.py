import time
import subprocess
from argparse import ArgumentParser

import requests
from torplex import TorManager


def main():
    parser = ArgumentParser(description="Curl the same url from multiple IP's at once into /dev/null")
    parser.add_argument('n', type=int, metavar='N', help='number of concurrent curls')
    parser.add_argument('url', metavar='URL', help='url to curl')
    parser.add_argument('-p', '--start-port', type=int, metavar='START_PORT', help='port for first Tor proxy server')
    args = parser.parse_args()
    curl_many(args.n, args.url, args.start_port)


def curl_many(n, url, start_port):

    man = TorManager() if start_port is None else TorManager(start_port=start_port)
    curls = set()

    try:

        for i in range(n):
            man.spawn().wait_for()

        print 'spawned tors'

        for t in man.get_tors():
            with open('/dev/null', 'w') as devnull:
                proc = subprocess.Popen([
                        'curl',
                        '-x',
                        'socks5://localhost:{}'.format(t.get_port()),
                        url,
                    ],
                    stdout=devnull,
                    stderr=devnull,
                    )
                curls.add(proc)

        print 'spawned curls'

        while True:
            time.sleep(1337)

    except Exception as e:
        raise

    finally:
        for tor in man.get_tors():
            tor.kill()
        for proc in curls:
            proc.kill()


if __name__ == '__main__':
    main()
