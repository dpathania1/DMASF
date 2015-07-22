import socket
import struct
import time
def sendPacket(sock, data):
  assert(isinstance(sock, socket.socket))
  l = len(data)  
  sock.send(struct.pack('i', l) +  data)



def readPacket(sock):
  assert(isinstance(sock, socket.socket))
  x = sock.recv(4)
  if not x or len(x) != 4:
    print "Error in read packet", time.time(), ' x=', x, ' lenx = ', len(x)
  x = struct.unpack('i', x)[0]
  buffer = ""
  iLenRead = 0
  data = ""
  while iLenRead < x:
    data = sock.recv(x - iLenRead)
    buffer += data
    iLenRead += len(data)
  return buffer
  
