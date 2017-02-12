import os
import shutil
import subprocess
import time

import binascii

import stem
from stem.control import Controller


DEFAULT_START_PORT = 1337
DEFAULT_DATA_DIR_DIR = '/tmp/torplex-data-dirs'


def manager():
    return Manager(_inc_port_it(DEFAULT_START_PORT), 'tor', DEFAULT_DATA_DIR_DIR)


def _inc_port_it(start):
    port = start
    while True:
        yield port, port + 1
        port += 2



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



class Manager(object):

    def __init__(self, port_it, tor_exe, data_dir_dir):

        self.port_it = port_it
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
