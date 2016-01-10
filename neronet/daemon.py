# daemon.py

"""
Classes to make it possible to create asynchronous processes that can be
communicated with.
"""

import os
import sys
import time
import signal
import daemon
import lockfile
import pathlib
import traceback
#import threading
import socket
import pickle
import re

TIMEOUT = 3.0

class Query():
  """A daemon query class."""

  def __init__(self, name, callback):
    self.name = name
    self.callback = callback
    self.tprocess = 0
    self.scsc = 0
    self.errc = 0

  def process(self, *args, **kwargs):
    try:
      #print('process:', self.callback, args, kwargs)
      rv = self.callback(*args, **kwargs)
      self.scsc += 1
      self.tprocess = time.time()
      return rv
    except Exception as err:
      self.errc += 1
      raise err

class Daemon():

    def __init__(self, name):
        self._name = name
        self._dir = pathlib.Path.home() / '.neronet' / self._name
        self._fout = self._dir / 'out'
        self._ferr = self._dir / 'err'
        self._fpid = self._dir / 'pid'
        self._fport = self._dir / 'port'
        self._dir.mkdir(parents=True, exist_ok=True)
        self._port = 0
        self._doquit = False
        self._trun = 0
        self._queries = {}
        self.add_query('uptime', self.qry_uptime)
        self.add_query('status', self.qry_status)
        self.add_query('stop', self.qry_stop)

    def add_query(self, name, callback):
        self._queries[name] = Query(name, callback)

    def log_form(self, prefix, message):
        return '%s %s  %s\n' % (prefix,
            time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
            message)

    def log(self, message):
        sys.stdout.write(self.log_form('LOG', message))

    def wrn(self, message):
        sys.stdout.write(self.log_form('WRN', message))

    def err(self, message, err=None):
        output = self.log_form('ERR', message)
        sys.stdout.write(output)
        if err:
            sys.stderr.write(output)
            traceback.print_exc()
            sys.stderr.write('\n')
        else:
            sys.stderr.write(output)

    def _cleanup(self, outfiles=False):
        """Remove daemon instance related files."""
        self.log('cleanup(): Removing instance related files...')
        files = [self._fpid, self._fport] + \
            ([self._fout, self._ferr] if outfiles else [])
        self.log('cleanup(): Files: %s' % (files))
        for f in files:
            if f.exists():
                self.log('cleanup(): Removing "%s"...' % (f))
                f.unlink()

    def _quit(self):
        self._cleanup()
        self.log("quit(): Exiting... Bye!")
        sys.exit(0)

    def _run(self):
        self._trun = time.time()
        context = daemon.DaemonContext(
            working_directory=str(self._dir),
            umask=0o002,
            pidfile=lockfile.FileLock(str(self._dir / 'pid')),
            stdout=self._fout.open('w', encoding='utf-8'),
            stderr=self._ferr.open('w', encoding='utf-8'),
            files_preserve=[],
        )
        context.signal_map = {
            signal.SIGTERM: self._quit,
            signal.SIGHUP: self._quit,
            signal.SIGQUIT: self._quit,
            signal.SIGUSR1: self._quit, # reload
        }
        self.log('run(): Entering daemon context...')
        with context:
            # Create a socket with a timeout and bind it to any available port on
            # localhost
            sckt = socket.socket()
            sckt.settimeout(TIMEOUT)
            sckt.bind(('localhost', self._port))
            # Put the socket into server mode and retrieve the chosen port number
            sckt.listen(1)
            port = sckt.getsockname()[1]
            self._fport.write_text(str(port))
            self.log('run(): Starting to listen at %s...' % (str(sckt.getsockname())))
            sckt.listen(1)
            while not self._doquit:
                self.log('run(): Looping...')
                try:
                    conn, addr = sckt.accept()
                    self.log('run(): Handling...')
                    self._handle(conn)
                except socket.timeout:
                    self.log('run(): Timeout...')
                except socket.error as err:
                    self.err('run(): Socket error: %s' % (socket.error), err)
                #thread = threading.Thread(target=self.handle, args=[conn])
                #thread.daemon = True
                #thread.start()
            self._quit()

    def _handle(self, sckt):
        self.log(str(sckt.getsockname()))
        byts = sckt.recv(4096)
        data = pickle.loads(byts)
        self.log('Received %s' % (data))
        self._uptime = time.time() - self._trun
        self._reply = {'rv': 9, 'uptime': self._uptime}
        if data and 'name' in data:
            name = data['name']
            args = data['args'] if 'args' in data else []
            kwargs = data['kwargs'] if 'kwargs' in data else {}
            if name in self._queries:
                self.log('Running query "%s" with %s %s...' % (name, args, kwargs))
                self._queries[name].process(*args, **kwargs)
            else:
                self._reply['msgbody'] = 'Unsupported query "%s"!' % (name)
        data = {'name': 'reply', 'kwargs': self._reply}
        sckt.sendall(pickle.dumps(data, -1))

    def qry_uptime(self):
        self._reply['rv'] = 0

    def qry_status(self):
        self._reply['msgbody'] = 'Hi! I\'m alive since %d secs!' % (self._uptime)
        self._reply['rv'] = 0

    def qry_stop(self):
        self._reply['msgbody'] = 'Ok but I\'m sad to say good bye!'
        self._reply['rv'] = 0
        self._doquit = True

class Cli():
    """A base class for easy control of daemons."""

    #RE_ARG = re.compile(r'--(\w+) (\w+)* (\w+=\w+)*')
    ## Command line argument parser regexes
    # Function name identifier
    RE_FUNC = re.compile(r'--([\w .]+)')
    # Positional argument
    RE_PARG = re.compile(r'([\w .]+)')
    # Keyword argument
    RE_KARG = re.compile(r'([\w.]+=[\w .]+)')

    def __init__(self, daemon):
        self.daemon = daemon
        self.funcs = {
            'default': self.func_default,
            'cleanup': self.func_cleanup,
            'start': self.func_start,
            'stop': self.func_stop,
            'restart': self.func_restart,
            'query': self.func_query,
            'status': self.func_status,
        }

    def inf(self, msg):
        print(msg)

    def wrn(self, msg):
        print('WRN: %s' % (msg))

    def err(self, code, msg):
        print('ERR: %s' % (msg))
        sys.exit(code)

    def query(self, name, *pargs, **kwargs):
        if not self.daemon._fport.exists():
            self.err(10, 'No daemon port file found! Is it running?')
        self.inf('Query(%s, %s, %s)...' % (name, pargs, kwargs))
        host = '127.0.0.1'
        port = int(self.daemon._fport.read_text())
        # Create a TCP/IP socket
        sckt = socket.socket()
        sckt.settimeout(TIMEOUT)
        # Connect to the daemon
        self.inf('Connecting to (%s, %d)...' % (host, port))
        sckt.connect((host, port))
        data = {'name': name, 'args': pargs, 'kwargs': kwargs}
        sckt.sendall(pickle.dumps(data, -1))
        self.inf('Listening for a reply...')
        try:
            byts = sckt.recv(4096)
            data = pickle.loads(byts) if byts else None
            self.inf('Received %s' % (data))
        except socket.timeout:
            self.inf('No reply received.')
            data = None
        self.inf('Closing socket.')
        sckt.close()
        return data

    def daemon_is_alive(self, trials=4):
      if self.daemon._fport.exists():
          for i in range(trials):
              try:
                  data = self.query('uptime')
                  if not data:
                      self.wrn('Unable to query the daemon.')
                      return False
                  uptime = data['kwargs']['uptime']
                  return uptime > 0 if uptime != None else False
              except ConnectionRefusedError:
                  time.sleep(0.3)
          self.wrn('Unable to connect to the daemon.')
      return False

    def parse_arguments(self, cli_args=None):
        """
          --func parg kwarg=kwvalue
        """
        cli_args = cli_args if cli_args else sys.argv[1:]
        work_queue = []
        func = 'default'
        pargs = []
        kargs = {}
        for arg in cli_args:
            self.inf('Parsing argument "%s"...' % (arg))
            mtch = self.RE_FUNC.fullmatch(arg)
            if mtch:
                work_queue.append((func, pargs, kargs))
                func = mtch.group(1)
                pargs = []
                kargs = {}
                continue
            mtch = self.RE_PARG.fullmatch(arg)
            if mtch:
                pargs.append(mtch.group(1))
                continue
            mtch = self.RE_KARG.fullmatch(arg)
            if mtch:
                kargs[mtch.group(1)] = mtch.group(2)
                continue
            self.err(1, 'Unrecognized argument: "%s"' % (arg))
        work_queue.append((func, pargs, kargs))
        for work in work_queue:
            func, pargs, kargs = work
            if func in self.funcs:
                self.inf('Executing function %s with %s %s...' 
                    % (func, pargs, kargs))
                self.funcs[func](*pargs, **kargs)
            else:
                self.err(2, 'Unrecognized function: "%s"' % (func))

    def func_default(self):
        pass
        #raise NotImplementedError('The default function is not implemented!')

    def func_cleanup(self):
        self.daemon._cleanup(outfiles=True)

    def func_start(self):
        """Start the daemon."""
        self.inf('start(): Starting the daemon...')
        # Remove old files...
        if self.daemon_is_alive():
            self.err(12, 'start(): Already running!')
            return
        self.daemon._cleanup(outfiles=True)
        # Start the daemon
        self.inf('start(): Executing run...')
        self.daemon._run()

    def func_stop(self):
        """Stop the daemon."""
        self.inf('stop(): Stopping the daemon...')
        if not self.daemon_is_alive():
            self.wrn('stop(): The daemon is not running!')
            return
        self.query('stop')
        time.sleep(TIMEOUT*0.5)
        if self.daemon._fport.exists():
            self.wrn('stop(): The daemon failed to cleanup!')
            self.daemon._cleanup()
        else:
            self.inf("stop(): The daemon exited cleanly.")

    def func_restart(self):
        """Restart the daemon."""
        self.inf("restart(): Restarting the daemon...")
        self.func_stop()
        self.func_start()

    def func_query(self, name, *pargs, **kwargs):
        data = self.query(name, *pargs, **kwargs)['kwargs']
        self.inf('Received a reply with code %d and message:\n%s' \
            % (data['rv'], data['msgbody']))

    def func_status(self):
        self.func_query('status')