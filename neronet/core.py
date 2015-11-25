# core.py
#
# Core class and function definitions

import os
import sys
import datetime
import socket
import pickle
import time
import psutil
from signal import signal, SIGTERM, SIGQUIT
from traceback import print_exc
from pathlib import Path

TIME_OUT = 5.0
"""float: how long the socket waits before failing when sending data
"""
class Logger:
    """A class to simplify logging."""
    def __init__(self, name):
        self.name = name

    def log(self, msg):
        """prints datetime, process name, process message"""
        # Print to stdout in a clear format
        print('%s %s: %s' % (datetime.datetime.now(), self.name, msg))

class Socket:
    """A class to simplify socket usage."""
    def __init__(self, logger, host, port):
        # Save key attributes
        self.logger = logger
        self.host = host
        self.port = port

    def send_data(self, data):
        """Create a socket, send data over it, and close it"""
        # Create a TCP/IP socket
        sock = socket.socket()
        sock.settimeout(TIME_OUT)
        # Connect to the mother
        #self.logger.log('Connecting to (%s, %s)...' % (self.host, self.port))
        sock.connect((self.host, self.port))
        # Send data
        #self.logger.log('Sending data "%s"...' % (data))
        sock.sendall(pickle.dumps(data, -1))
        # Close socket
        #self.logger.log('Closing socket...')
        sock.close()

class Daemon(object):
    """A generic daemon class."""

    class NoPidFileError(Exception):
        pass

    def __init__(self, pd):
        self.pd = Path.home() / '.neronet' / pd
        self.pfout = self.pd / 'out'
        self.pferr = self.pd / 'err'
        self.pfpid = self.pd / 'pid'
        self.pfport = self.pd / 'port'
        self.cleanup_files = [self.pfpid, self.pfport]
        self.restart_files = [self.pfout, self.pferr] + self.cleanup_files

    def log_form(self, prefix, message):
        return '%s %s  %s\n' % (prefix,
            time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), message)

    def log(self, message):
        sys.stdout.write(self.log_form('LOG', message))

    def wrn(self, message):
        sys.stdout.write(self.out('WRN', message))

    def err(self, message, err=None):
        output = self.log_form('ERR', message)
        sys.stdout.write(output)
        if err:
            sys.stderr.write(output)
            print_exc()
            sys.stderr.write('\n')
        else:
            sys.stderr.write(output)

    def write_pid(self):
        self.pfpid.write_text(str(self.pid))

    def write_port(self):
        self.pfport.write_text(str(self.port))

    def _read_i_or_nan(self, pf):
        try:
            return int(pf.read_text())
        except:
            return None

    def rpfpid(self):
        self.pid = self._read_i_or_nan(self.pfpid)
        return self.pid

    def rpfport(self):
        self.port = self._read_i_or_nan(self.pfport)
        return self.port

    def is_running(self):
        return self.rpfpid() != None

    def cleanup(self):
        """Remove daemon instance related files."""
        self.log("cleanup(): Removing instance related files...")
        for pf in self.cleanup_files:
            if not pf.exists():
                continue
            self.log('cleanup(): Removing "%s"...' % (pf))
            pf.unlink()

    def quit(self):
        self.cleanup()
        self.log("quit(): Exiting... Bye!")
        sys.exit(0)

    def recv_signal(self, sign, frme):
        self.log('recv_signal(): Received signal "%s"!' % (sign))
        if sign in (SIGTERM, SIGQUIT):
            self.quit()

    def daemonize(self):
        """Daemonize the process.

        Essentially
        - Daemonizes the process by double forking
        - Redefines a few variables and a few handles to unix signals
        - Defines stdout, stderr and logging streams
        - Writes the pid file
        """

        # Exit first parent (first fork)
        self.log("daemonize(): Daemonizing the process...")
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError as err:
            self.err('daemonize(): Fork #1 failed!', err=err)
            sys.exit(1)

        # Decouple from parent environment
        os.chdir(self.pd)
        os.setsid()
        os.umask(0)

        # Do second fork
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError as err:
            self.err('daemonize(): Fork #2 failed!', err=err)
            sys.exit(1)

        # Redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()
        so = self.pfout.open('w', encoding='utf-8')
        se = self.pferr.open('w', encoding='utf-8')
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

        # Update PID
        self.pid = os.getpid()
        self.write_pid()

        # Add signal handlers
        self.log('daemonize(): Adding a signal handler...')
        signal(SIGTERM, self.recv_signal)
        signal(SIGQUIT, self.recv_signal)

        # Print encoding info
        import locale
        self.log(
            'daemonize(): Active encodings: %s, %s...' %
            (sys.getfilesystemencoding(), locale.getpreferredencoding()))

    def start(self):
        """Start the daemon."""
        # Check for a pfpid to see if the daemon already runs
        if self.is_running():
            self.err('start(): The daemon is already running!' % (self.pfpid))
            sys.exit(1)
        self.log('start(): Starting the daemon...')
        # Remove old files...
        for pf in self.restart_files:
            if pf.exists():
                pf.unlink()
        # Start the daemon
        self.daemonize()
        self.log('start(): Executing run...')
        self.run()

    def stop(self):
        """Stop the daemon."""
        self.log('stop(): Stopping the daemon...')
        # Get the pid from the pfpid
        pid = self.rpfpid()
        if not pid:
            self.err("stop(): The daemon is not running!")
            raise self.NoPidFileError
        try:
            proc = psutil.Process(pid)
            if 'python' not in proc.name():
        except psutil.NoSuchProcess:
            self.err("stop(): The pid file is deprecated!")
        else:
            if not proc.is_running():
                self.err("stop(): The daemon has already stopped running!")
            else:
                proc.send_signal(SIGQUIT)
                time.sleep(0.3)
                self.log("stop(): Daemon terminated!")
        if self.pfpid.exists():
            self.log("stop(): ERR: The daemon failed to cleanup!")
            self.pfpid.unlink()


    def restart(self):
        """Restart the daemon."""
        self.log("restart(): Restarting the daemon...")
        try:
            self.stop()
        except self.NoPidFileError:
            pass
        self.start()

    def run(self):
        """
        You should override this method when you subclass DaemonBase. It will be called after the process has been
        daemonized by start() or restart().
        """
        self.loge("run(): Running an abstract function!!!")
        sys.exit(1)
