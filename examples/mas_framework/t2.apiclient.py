import SocketServer
import socket
import struct
import os
import shutil
import logging
from mysocket import *
from constants import *  


class APICLIENT(SocketServer.BaseRequestHandler):
  def setup(self):
    self.logger = logging.getLogger('apiclient')
    self.logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    #add formatter to ch and fh

    fh = logging.FileHandler('log.apiclient')
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    sh = logging.StreamHandler()
    sh.setLevel(logging.DEBUG)
    sh.setFormatter(formatter)

    self.logger.addHandler(fh)
    self.logger.addHandler(sh)
    

  def getfile(self):
    assert(isinstance(self.request, socket.socket))
    
    fileheader = readPacket(self.request)
    filesize = struct.unpack('i', fileheader[:4])[0]
    filename = fileheader[4:]
    filedata = ""
    iLenRead = 0

    while iLenRead < filesize:
      filedata += self.request.recv(filesize - iLenRead)
      iLenRead = len(filedata)
    
    f = open(filename, 'w')
    f.write(filedata)
    f.close()
    
    
  
  def handle(self):
    
    assert(isinstance(self.request, socket.socket))
    os.chdir('/new_backups/traffic/')
    self.request.send("HELO")
    self.logger.debug('HELO received\n')
    
    simname = readPacket(self.request)
    self.logger.debug('Simname = ' + simname + '\n')    
    self.request.send('FILENAME')
    
    try:
      os.mkdir(simname)
    except:
      shutil.rmtree(simname)
      os.mkdir(simname)

    os.chdir(simname)
    
    numfiles = int(readPacket(self.request))
    self.logger.debug('Numfiles = ' + str(numfiles))
    
    while numfiles:
      numfiles -= 1
      self.getfile()
    
    self.request.send("SFC")
    
    hostporthdr = readPacket(self.request)
    self.logger.debug('HostPort = ' + hostporthdr + '\n')
    f = open('settings', 'w')
    f.write(hostporthdr)
    f.close()
    
    self.request.send("HPC")
    #not portable code
    shutil.copytree('/new_backups/traffic/mas_framework/mas_framework', './mas_framework')
    shutil.move('mas_framework/apistub.py', 'mas_framework/api.py')
    
    os.system('python main.py')

    self.request.close()
    
tcpserver = SocketServer.TCPServer(('localhost', TEMP_PORT + 3), APICLIENT)
tcpserver.serve_forever()
