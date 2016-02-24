import sys
import socket
import pickle

def sendmsg(host, port, msg):
  sckt = socket.socket()
  sckt.settimeout(5.0)
  sckt.connect((host, port))
  print('Sending data...')
  sckt.sendall(pickle.dumps(msg, -1))
  print('Listening for a reply...')
  try:
      byts = sckt.recv(1028)
      reply = pickle.loads(byts) if byts else None
      print('Received reply: %s' % (reply))
  except socket.timeout:
      print('No reply received!')
      reply = None
  print('Closing socket.')
  sckt.close()
  return reply

def serve(host, port):
  sckt = socket.socket()
  sckt.settimeout(5.0)
  sckt.bind((host, port))
  sckt.listen(1)
  host, port = sckt.getsockname()
  while True:
      print('Looping at (%s, %s)...' % (host, port))
      try:
          conn, addr = sckt.accept()
          print('Connected by %s!' % (str(conn.getsockname())))
          conn.settimeout(1.0)
          byts = conn.recv(1028)
          msg = pickle.loads(byts) if byts else None
          print('Received "%s".' % (msg))
          reply = str(int(msg) + 1) if msg else 'Give me an integer!'
          print('Sending the reply "%s"...' % (reply))
          # Send the reply to the connected socket
          conn.sendall(pickle.dumps(reply, -1))
      except socket.timeout:
          print('Timeout...')
      except socket.error as err:
          print('Socket error: %s' % (err))

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: HOST PORT MSG*')
        sys.exit(1)
    host = sys.argv[1]
    port = int(sys.argv[2])
    if len(sys.argv) > 3:
        for msg in sys.argv[3:]:
            sendmsg(host, port, msg)
    else:
        serve(host, port)