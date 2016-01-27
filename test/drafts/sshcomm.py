
def send():
    foo = {'nam': 13}
    process = subprocess.Popen(['sshcomm receive', '--input'],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    sout, serr = process.communicate(pickle.dumps(foo), timeout=5.0)
    print('Output:\n%s' % (sout))

def receive():
    data = input()
    print('Data:\n%s\n' % (data))
    while(not ("***" in data)):
        data = input("") # pickle.loads()
        print('Data:\n%s\n' % (data))
    #data = sys.stdin.readLine() # pickle.loads()
    #print('Data:\n%s\n' % (data))
