# nerodmnc.py

## Standard daemon (option A)

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

TIMEOUT = 3.0

class Query():
  """A daemon query class."""

  def __init__(self, name, callback):
    self.name = name
    self.callback = callback
    self.tprocess = 0
    self.scsc = 0
    self.errc = 0

  def process(self, kwargs):
    try:
      rv = self.callback(**kwargs)
      self.scsc += 1
      self.tprocess = time.time()
      return rv
    except Exception as err:
      self.errc += 1
      raise err

class DaemonA(object):

    def __init__(self, name):
        self.name = name
        self.pd = pathlib.Path.home() / '.neronet' / self.name
        self.pfout = self.pd / 'out'
        self.pferr = self.pd / 'err'
        self.pfpid = self.pd / 'pid'
        self.pfport = self.pd / 'port'
        self.pd.mkdir(parents=True, exist_ok=True)
        self.port = 0
        self.doquit = False
        self.trun = 0
        self.queries = {}
        self._add_query('uptime', self.qry_uptime)
        self._add_query('status', self.qry_status)
        self._add_query('stop', self.qry_stop)

    def _add_query(self, name, callback):
        self.queries[name] = Query(name, callback)

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

    def cleanup(self, outfiles=False):
        """Remove daemon instance related files."""
        self.log('cleanup(): Removing instance related files...')
        files = [self.pfpid, self.pfport] + \
            ([self.pfout, self.pferr] if outfiles else [])
        self.log('cleanup(): Files: %s' % (files))
        for pf in files:
            if pf.exists():
                self.log('cleanup(): Removing "%s"...' % (pf))
                pf.unlink()

    def quit(self):
        self.cleanup()
        self.log("quit(): Exiting... Bye!")
        sys.exit(0)

    def run(self):
        self.trun = time.time()
        context = daemon.DaemonContext(
            working_directory=str(self.pd),
            umask=0o002,
            pidfile=lockfile.FileLock(str(self.pd / 'pid')),
            stdout=self.pfout.open('w', encoding='utf-8'),
            stderr=self.pferr.open('w', encoding='utf-8'),
            files_preserve=[],
        )
        context.signal_map = {
            signal.SIGTERM: self.quit,
            signal.SIGHUP: self.quit,
            signal.SIGQUIT: self.quit,
            signal.SIGUSR1: self.quit, # reload
        }
        self.log('run(): Entering daemon context...')
        with context:
            # Create a socket with a timeout and bind it to any available port on
            # localhost
            sckt = socket.socket()
            sckt.settimeout(TIMEOUT)
            sckt.bind(('localhost', 0))
            # Put the socket into server mode and retrieve the chosen port number
            sckt.listen(1)
            port = sckt.getsockname()[1]
            self.pfport.write_text(str(port))
            self.log('run(): Starting to listen at %s...' % (str(sckt.getsockname())))
            sckt.listen(1)
            while not self.doquit:
                self.log('run(): Looping...')
                try:
                    conn, addr = sckt.accept()
                    self.log('run(): Handling...')
                    self.handle(conn)
                except socket.timeout:
                    self.log('run(): Timeout...')
                except socket.error as err:
                    self.err('run(): Socket error: %s' % (socket.error), err)
                #thread = threading.Thread(target=self.handle, args=[conn])
                #thread.daemon = True
                #thread.start()
            self.quit()

    def handle(self, sckt):
        self.log(str(sckt.getsockname()))
        byts = sckt.recv(4096)
        data = pickle.loads(byts)
        self.log('Received %s' % (data))
        self.uptime = time.time() - self.trun
        self.reply = {'rv': 9, 'uptime': self.uptime}
        if data and 'name' in data and 'kwargs' in data:
            name = data['name']
            kwargs = data['kwargs']
            if name in self.queries:
                self.queries[name].process(kwargs)
            else:
                self.reply['msgbody'] = 'Unsupported query "%s"!' % (name)
        sckt.sendall(pickle.dumps({'name': 'reply', 'kwargs': self.reply}, -1))

    def qry_uptime(self):
        self.reply['rv'] = 0

    def qry_status(self):
        self.reply['msgbody'] = 'Hi! I\'m alive since %d secs!' % (self.uptime)
        self.reply['rv'] = 0

    def qry_stop(self):
        self.reply['msgbody'] = 'Ok but I\'m sad to say good bye!'
        self.reply['rv'] = 0
        self.doquit = True

    def query(self, name, **kwargs):
        self.log('Query(%s, %s)...' % (name, kwargs))
        host = '127.0.0.1'
        port = int(self.pfport.read_text())
        # Create a TCP/IP socket
        sckt = socket.socket()
        sckt.settimeout(TIMEOUT)
        # Connect to the daemon
        self.log('Connecting to (%s, %d)...' % (host, port))
        sckt.connect((host, port))
        sckt.sendall(pickle.dumps({'name': name, 'kwargs': kwargs}, -1))
        self.log('Listening for a reply...')
        try:
            byts = sckt.recv(4096)
            data = pickle.loads(byts) if byts else None
            self.log('Received %s' % (data))
        except socket.timeout:
            self.log('No reply received.')
            data = None
        self.log('Closing socket.')
        sckt.close()
        return data

    def is_alive(self):
      if self.pfport.exists():
          try:
              uptime = self.query('uptime')['kwargs']['uptime']
              return uptime > 0 if uptime != None else False
          except ConnectionRefusedError:
              self.err('Unable to connect to the daemon.')
      return False

    def start(self):
        """Start the daemon."""
        self.log('start(): Starting the daemon...')
        # Remove old files...
        if self.is_alive():
            self.err('start(): Already running!')
            return
        self.cleanup(outfiles=True)
        # Start the daemon
        self.log('start(): Executing run...')
        self.run()

    def stop(self):
        """Stop the daemon."""
        self.log('stop(): Stopping the daemon...')
        if not self.is_alive():
            self.err('stop(): The daemon is not running!')
            return
        self.query('stop')
        time.sleep(TIMEOUT*0.5)
        if self.pfport.exists():
            self.err("stop(): The daemon failed to cleanup!")
            self.cleanup()
        else:
            self.log("stop(): The daemon exited cleanly.")

    def restart(self):
        """Restart the daemon."""
        self.log("restart(): Restarting the daemon...")
        self.stop()
        self.start()

## Fully custom daemon (option B)

class DaemonB(object):

    """A generic daemon class.

    See:
    - https://www.python.org/dev/peps/pep-3143/
    - https://docs.python.org/3.5/library/socketserver.html
    - http://stackoverflow.com/questions/15652791/how-to-create-a-python-socket-listner-deamon
    """

    class NoPidFileError(Exception):
        pass

    def __init__(self, name):
        self.name = name
        self.pd = pathlib.Path.home() / '.neronet' / self.name
        self.pfout = self.pd / 'out'
        self.pferr = self.pd / 'err'
        self.pfpid = self.pd / 'pid'
        self.pfport = self.pd / 'port'
        self.pd.mkdir(parents=True, exist_ok=True)
        self.port = 0
        self.tdo = 5
        self.sckt = None

    def log_form(self, prefix, message):
        return '%s %s  %s\n' % (prefix,
            time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
            message)

    def log(self, message):
        sys.stdout.write(self.log_form('LOG', message))

    def wrn(self, message):
        sys.stdout.write(self.out('WRN', message))

    def err(self, message, err=None):
        output = self.log_form('ERR', message)
        #sys.stdout.write(output)
        if err:
            sys.stderr.write(output)
            print_exc()
            sys.stderr.write('\n')
        else:
            sys.stderr.write(output)

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

    def get_process(self):
        # Get the pid from the pfpid
        pid = self.rpfpid()
        if pid == None:
            return None
        try:
            proc = psutil.Process(pid)
            if 'nero' not in proc.name():
                raise psutil.NoSuchProcess
        except psutil.NoSuchProcess:
            self.err("is_running(): The pid file is deprecated!")
            self.cleanup()
            return None
        if proc.is_running():
            return proc

    def is_running(self):
        return self.get_process() != None

    def cleanup(self, outfiles=False):
        """Remove daemon instance related files."""
        self.log("cleanup(): Removing instance related files...")
        files = [self.pfpid, self.pfport] + \
            [self.pfout, self.pferr] if outfiles else []
        for pf in files:
            if pf.exists():
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
        os.chdir(str(self.pd))
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
        self.pfpid.write_text(str(self.pid))

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
            self.err('start(): The daemon is already running!')
            sys.exit(1)
        self.log('start(): Starting the daemon...')
        # Remove old files...
        self.cleanup(outfiles=True)
        # Start the daemon
        self.daemonize()
        self.log('start(): Executing run...')
        self.run()

    def stop(self):
        """Stop the daemon."""
        self.log('stop(): Stopping the daemon...')
        proc = self.get_process()
        if proc:
            proc.send_signal(SIGQUIT)
            time.sleep(0.4)
            self.log("stop(): Daemon terminated!")
        if self.pfpid.exists():
            self.err("stop(): The daemon failed to cleanup!")
            self.cleanup()

    def restart(self):
        """Restart the daemon."""
        self.log("restart(): Restarting the daemon...")
        try:
            self.stop()
        except self.NoPidFileError:
            pass
        self.start()

    def run(self):
        """The daemon process loop."""
        # Socket Initialization
        self.sckt = gsocket(self.port, self.tdo)
        # Port
        self.port = self.sckt.getsockname()[1]
        self.pfport.write_text(str(self.port))
        # Init callback
        self.daemon_init()
        # The Loop
        r = 0
        self.log('run: listening port %d (to: %s, pid: %d)...' %
                (self.port, self.tdo, self.pid))
        while True:
            out = None
            try:
                out = listenfordata(self.sckt)
            except Exception as err:
                self.err("run: listen error:\n%s\n" % (err))
            if out:
                dta, address = out
                ip, port = address
                self.log("run: msg from %s:%s: |%s|" % (ip, port, dta))
                self.onreceive(ip, port, dta)
            else:
                # Ontdo callback
                self.ontdo()

    def respond(self, ip, port, reply, args=()):
        sndreply(port, reply, args, self.sckt)

    def daemon_init(self):
        """
        You should override this method when you subclass the Daemon. It
        can be used to init the daemon as it will be called before the process
        enters the loop. It is executed also on restarts!
        """
        self.log("LD::init: WARNING: No init specified!!!")

    def onreceive(self, adda, addb, sin):
        """
        You should override this method when you subclass Daemon. It will be called after the process receives input
        """
        self.log("LD::onreceive: ERROR: No onreceive specified!!!")
        raise Exception("ERROR: No onreceive specified!!!")

    def ontdo(self):
        """
        You should override this method when you subclass Daemon. It will be called if the process does not receive input
        """
        self.log("LD::ontdo: nothing received...")