import binascii
import os
import signal
import shutil
import subprocess

import stem
from stem.control import Controller


START_PORT = 13337
BASE_DIR = '/tmp/torplex'


class TorBase(object):

    def get_port(self):
        return self.socks_port

    def connect(self):
        ctrl = Controller.from_port(port=self.control_port)
        ctrl.authenticate(password=self.password)
        return ctrl

    def kill(self):
        os.kill(self.pid, signal.SIGKILL)

    def cleanup(self):
        if os.path.isdir(self.data_dir):
            shutil.rmtree(self.data_dir)


class TorManager(object):

    def __init__(self, start_port=START_PORT, base_dir=BASE_DIR, tor_exe='tor'):

        def it():
            x = start_port
            while True:
                yield x, x + 1
                x += 2

        self.port_it = it()
        self.tor_exe = tor_exe
        self.base_dir = base_dir
        self.tors = set()

        if not os.path.isdir(self.base_dir):
            os.mkdir(self.base_dir)

        class Tor(TorBase):

            def __init__(tor):

                tid = binascii.hexlify(os.urandom(16)).decode('utf-8')
                tor.socks_port, tor.control_port = next(self.port_it)
                tor.data_dir = os.path.join(self.base_dir, tid)
                tor.password = binascii.hexlify(os.urandom(8)).decode('utf-8')

                subprocess.check_call([
                        self.tor_exe,
                        '--HashedControlPassword', self._hash_password(tor.password),
                        '--SocksPort', str(tor.socks_port),
                        '--ControlPort', str(tor.control_port),
                        '--RunAsDaemon', '1',
                        '--PidFile', 'pid',
                        '--DataDirectory', tor.data_dir,
                        ],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    )

                with open(os.path.join(tor.data_dir, 'pid'), 'r') as pf:
                    tor.pid = int(pf.read())

        self.Tor = Tor


    def _hash_password(self, password):
        return subprocess.check_output([self.tor_exe, '--hash-password', password])[:-1]


    def spawn(self):
        tor = self.Tor()
        self.tors.add(tor)
        return tor


    def get_tors(self):
        return self.tors


    def remove(self, tor):
        self.tors.remove(tor)
        tor.kill()
        tor.cleanup()


    def remove_all(self):
        # Avoid modifying set during iteration
        for t in list(self.tors):
            self.remove(t)


    def __enter__(self):
        return self


    def __exit__(self, exc_type, exc_val, exc_tb):
        self.remove_all()
        return False
