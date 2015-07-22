import SocketServer
import socket
import struct
import os
import shutil
import logging
from mysocket import *
from constants import *  
import sys

class APICLIENT(SocketServer.BaseRequestHandler):
  """ This is the daemon which needs to be run on the host.
  Assumes mas_framework directory is present in sys.path[0] (default if apiclient
  is run from the same directory)
  """
  def setup(self):
    """Setups the logger"""
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
    """Gets a file from the server. Used to transfer user code to the host."""
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
    """Handle of the socket request."""
    
    assert(isinstance(self.request, socket.socket))
    szSimDir = os.path.join(os.environ['HOME'], 'simulations')
    if not os.path.exists(szSimDir):
      os.mkdir(szSimDir)
      
    os.chdir(szSimDir)
    self.request.send("HELO")
    self.logger.debug('HELO received\n')
    
    simname = readPacket(self.request)
    self.logger.debug('Simname = ' + simname + '\n')    
    self.request.send('FILENAME')
    
    i = 0
    basename = simname
    while 1:     
      try:
        self.logger.debug('Making Directory - ' + simname)
        os.mkdir(simname)
        break
      except:
        simname = basename + '_' + str(i)
        i += 1



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
    
    szScriptName = readPacket(self.request)
    self.request.send("HPC")

    #WARNING: This should be independent of module name. Fix it.
    shutil.copytree(sys.path[0], './mas_framework')
    shutil.move('mas_framework/apistub.py', 'mas_framework/api.py')
    
    L = ['python', szScriptName]
    os.spawnvpe(os.P_NOWAIT, L[0], L, os.environ)

    self.request.close()
  
iport = TEMP_PORT # default 2000
if len(sys.argv) == 2:
  iport = int(sys.argv[1])

tcpserver = SocketServer.TCPServer(('', iport), APICLIENT)
tcpserver.serve_forever()
