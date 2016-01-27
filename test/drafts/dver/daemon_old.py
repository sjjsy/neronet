# daemon_old.py

class DaemonOLD():

    def add_query(self, name, callback):
        self._queries[name] = Query(name, callback)

    def log_pform(self, prefix, message):
        return '%s %s  %s\n' % (prefix,
            time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
            message)

    def log(self, message):
        sys.stdout.write(self.log_pform('LOG', message))

    def wrn(self, message):
        sys.stdout.write(self.log_pform('WRN', message))

    def err(self, message, err=None):
        output = self.log_pform('ERR', message)
        sys.stdout.write(output)
        if err:
            sys.stderr.write(output)
            traceback.print_exc()
            sys.stderr.write('\n')
        else:
            sys.stderr.write(output)

    def abort(self, message, err=None):
        self.err(message, err)
        self.quit()

    def _cleanup(self, outfiles=False):
        """Remove daemon instance related files."""
        self.log('cleanup(): Removing instance related files...')
        files = [self._pfpid, self._pfport] + \
            ([self._pfout, self._pferr] if outfiles else [])
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
        self._pdir.mkdir(parents=True, exist_ok=True)
        self._cleanup(outfiles=True)
        context = daemon.DaemonContext(
            working_pdirectory=str(self._pdir),
            umask=0o002,
            pidfile=lockfile.FileLock(str(self._pdir / 'pid')),
            stdout=self._pfout.open('w', encoding='utf-8'),
            stderr=self._pferr.open('w', encoding='utf-8'),
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
            sckt.bind(('localhost', self.port))
            # Put the socket into server mode and retrieve the chosen port number
            sckt.listen(1)
            host, self.port = sckt.getsockname()
            self._pfport.write_text(str(self.port))
            self.log('run(): Starting to listen at %s %d...' % (host, self.port))
            sckt.listen(1)
            while not self._doquit:
                self.log('run(): Looping...')
                try:
                    conn, addr = sckt.accept()
                    self.log('run(): Handling...')
                    self._handle(conn)
                except socket.timeout:
                    self.log('run(): Timeout...')
                    self.ontimeout()
                except socket.error as err:
                    self.err('run(): Socket error: %s' % (socket.error), err)
                #thread = threading.Thread(target=self.handle, args=[conn])
                #thread.daemon = True
                #thread.start()
                if not self._pfport.exists():
                    self.log('run(): Port file disappeared! Aborting...')
                    self._doquit = True
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
        sckt.sendall(pickle.dumps(self._reply, -1))

    def qry_uptime(self):
        self._reply['rv'] = 0

    def qry_status(self):
        self._reply['msgbody'] = 'Hi! I\'m alive since %d secs!' % (self._uptime)
        self._reply['rv'] = 0

    def qry_stop(self):
        self._reply['msgbody'] = 'Ok but I\'m sad to say good bye!'
        self._reply['rv'] = 0
        self._doquit = True

    def ontimeout(self):
        pass

class QueryInterface():

    class NoPortFileError(RuntimeError): pass
    class NoPortNumberError(RuntimeError): pass

    def __init__(self, daemon, port=None, host='127.0.0.1', verbose=False):
        self.daemon = daemon
        self.port = port
        self.host = host
        self.verbose = verbose
        try:
            self.determine_port()
        except self.NoPortFileError:
            pass

    def inf(self, msg):
        if not self.verbose: return
        print(msg)

    def wrn(self, msg):
        if not self.verbose: return
        print('WRN: %s' % (msg))

    def err(self, msg):
        if not self.verbose: return
        print('ERR: %s' % (msg))

    def abort(self, code, msg):
        print('ABORT: %s' % (msg))
        sys.exit(code)

    def determine_port(self):
        if self.port:
            return
        localhost = neronet.core.get_hostname()
        if self.host in ('127.0.0.1', 'localhost', localhost):
            if self.daemon._pfport.exists():
                self.port = int(self.daemon._pfport.read_text())
            else:
                raise self.NoPortFileError('No daemon port file!')
                #self.abort(10, 'No daemon port file found! Is it running?')
        else:
            raise self.NoPortNumberError('No daemon port number!')
            #self.abort(10, 'No daemon port number defined!')

    def query(self, name, *pargs, trials=4, **kwargs):
        self.inf('Query(%s, %s, %s)...' % (name, pargs, kwargs))
        self.determine_port()
        if name not in self.daemon._queries:
            raise RuntimeError('No such query "%s"!' % (name))
            #self.abort(11, 'No such query "%s"!' % (name))
        # Create a TCP/IP socket
        sckt = socket.socket()
        sckt.settimeout(TIMEOUT)
        # Connect to the daemon
        self.inf('Connecting to (%s, %d)...' % (self.host, self.port))
        for i in range(trials):
            try:
                sckt.connect((self.host, self.port))
                data = {'name': name, 'args': pargs, 'kwargs': kwargs}
                self.inf('Sending data...')
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
            except ConnectionRefusedError:
                time.sleep(0.3)
        raise RuntimeError('Unable to connect to the daemon!')
        #self.abort(11, 'Unable to connect to the daemon.')

    def daemon_is_alive(self):
        try:
            reply = self.query('uptime')
            if not reply or 'uptime' not in reply:
                return False
            uptime = reply['uptime']
            return uptime > 0 if uptime != None else False
        except self.NoPortFileError:
            return False

    def cleanup(self):
        """Erase daemon instance related files."""
        self.daemon._cleanup(outfiles=True)

    def start(self):
        """Start the daemon."""
        self.inf('start(): Starting the daemon...')
        print('FORKING')
        if os.fork() == 0:
            print('FORKED')
            self.daemon._run()
        time.sleep(1.0)
        print('FORK WENT')

    def stop(self):
        """Stop the daemon."""
        self.inf('stop(): Stopping the daemon...')
        if not self.daemon_is_alive():
            self.wrn('stop(): The daemon is not running!')
            return
        self.query('stop')
        time.sleep(TIMEOUT*0.5)
        if self.daemon._pfport.exists():
            self.wrn('stop(): The daemon failed to cleanup!')
            self.daemon._cleanup()
        else:
            self.inf("stop(): The daemon exited cleanly.")

    def restart(self):
        """Restart the daemon."""
        self.inf("restart(): Restarting the daemon...")
        self.stop()
        self.start()

class Cli(QueryInterface):
    """A base class for easy control of daemons."""

    #RE_ARG = re.compile(r'--(\w+) (\w+)* (\w+=\w+)*')
    ## Command line argument parser regexes
    # Function name identifier
    RE_pfUNC = re.compile(r'--([\w.]+)')
    # Keyword argument
    RE_KARG = re.compile(r'([\w.]+=.*)')
    # Positional argument
    RE_PARG = re.compile(r'(.*)')

    def __init__(self, daemon):
        super().__init__(daemon)
        self.funcs = {
            'default': self.func_default,
            'cleanup': self.func_cleanup,
            'start': self.func_start,
            'stop': self.func_stop,
            'restart': self.func_restart,
            'query': self.func_query,
        }

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
            mtch = self.RE_pfUNC.fullmatch(arg)
            if mtch:
                work_queue.append((func, pargs, kargs))
                func = mtch.group(1)
                pargs = []
                kargs = {}
                continue
            mtch = self.RE_KARG.fullmatch(arg)
            if mtch:
                kargs[mtch.group(1)] = mtch.group(2)
                continue
            mtch = self.RE_PARG.fullmatch(arg)
            if mtch:
                pargs.append(mtch.group(1))
                continue
            self.abort(1, 'Unrecognized argument: "%s"' % (arg))
        work_queue.append((func, pargs, kargs))
        for work in work_queue:
            func, pargs, kargs = work
            if func in self.funcs:
                self.inf('Executing function "%s" with %s %s...' 
                    % (func, pargs, kargs))
                self.funcs[func](*pargs, **kargs)
            else:
                self.abort(2, 'Unrecognized function: "%s"' % (func))

    def func_default(self):
        pass
        #raise NotImplementedError('The default function is not implemented!')

    def func_cleanup(self):
        """Erase daemon instance related files."""
        self.cleanup()

    def func_start(self):
        """Start the daemon."""
        self.start()

    def func_stop(self):
        """Stop the daemon."""
        self.stop()

    def func_restart(self):
        """Restart the daemon."""
        self.restart()

    def func_query(self, name, *pargs, **kwargs):
        reply = self.query(name, *pargs, **kwargs)
        if not reply:
            self.err('No reply received!')
        else:
            self.inf('Received a reply with code %d.' % (reply['rv']))
            if 'msgbody' in reply:
              self.inf('Message:\n%s' % (reply['msgbody']))