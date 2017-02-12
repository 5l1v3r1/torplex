import binascii
import os
import shutil
import subprocess
import time

import stem
from stem.control import Controller


DEFAULT_START_PORT = 13337
DEFAULT_DATA_DIR_DIR = '/tmp/torplex-data-dirs'


class TorBase(object):

    def get_port(self):
        return self.socks_port

    def kill(self):
        self.proc.kill()
        if os.path.isdir(self.data_dir):
            shutil.rmtree(self.data_dir)

    def connect(self):
        ctrl = Controller.from_port(port=self.control_port)
        ctrl.authenticate(password=self.password)
        return ctrl

    def wait_for(self):
        while True:
            try:
                ctrl = Controller.from_port(port=self.control_port)
                ctrl.close()
                break
            except stem.SocketError:
                time.sleep(.01)


class TorManager(object):

    def __init__(self, start_port=DEFAULT_START_PORT, data_dir_dir=DEFAULT_DATA_DIR_DIR, tor_exe='tor'):

        def it():
            x = start_port
            while True:
                yield x, x + 1
                x += 2

        self.port_it = it()
        self.tor_exe = tor_exe
        self.data_dir_dir = data_dir_dir
        self.tors = set()

        class Tor(TorBase):

            def __init__(tor):

                tor.socks_port, tor.control_port = next(self.port_it)
                tor.data_dir = os.path.join(self.data_dir_dir, binascii.hexlify(os.urandom(16)))
                tor.password = binascii.hexlify(os.urandom(8))

                with open('/dev/null', 'w') as devnull:
                    tor.proc = subprocess.Popen([
                            self.tor_exe,
                            '--HashedControlPassword', self._hash_password(tor.password),
                            '--SocksPort', str(tor.socks_port),
                            '--ControlPort', str(tor.control_port),
                            '--DataDirectory', tor.data_dir,
                            ],
                        stdout=devnull,
                        stderr=devnull,
                        )

        self.Tor = Tor

        if not os.path.isdir(data_dir_dir):
            os.mkdir(data_dir_dir)


    def _hash_password(self, password):
        return subprocess.check_output([self.tor_exe, '--hash-password', password])[:-1]

    def spawn(self):
        tor = self.Tor()
        self.tors.add(tor)
        return tor

    def get_tors(self):
        return self.tors
