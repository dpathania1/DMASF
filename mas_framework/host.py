from mysocket import *
from constants import *
import socket
import struct
import os
import random
import threading
import logging
import sys
import time
import random
import cPickle as pickle
class HOST:
  def setupLogger(self):
    """sets up the logger"""
    self.logger = logging.getLogger('host-' + self.szHost + ':' + str(self.iPort))
    self.logger.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    #add formatter to ch and fh

    fh = logging.FileHandler('log.host-' + str(self.szHost) + ':' + str(self.iPort))
    fh.setFormatter(formatter)
    sh = logging.StreamHandler()
    sh.setFormatter(formatter)

    self.logger.addHandler(fh)
    self.logger.addHandler(sh)

    self.logger.disabled = BLOGGING_DISABLED
    
  def __init__(self):
    """creates sockets, events and threads to communicate with the hosts"""
    self.state = E_UNKNOWN
    self.sockInit = socket.socket()
    self.EventLock = threading.Lock()
    self.bWaiting = False
    self.HostEventObject = threading.Event()
    self.HostEventObject.clear()
    self.APIEventObject = threading.Event()
    self.APIEventObject.clear()
    self.lastSendTime = {}
    self.iterTime = {CMD_SIMULATE : 1, CMD_UPDATEDB:0, CMD_UPDATESIMENV:0}
    self.iTotalCount = 1



 
  def setState(self, newState):
    """sets the state of the simulation"""
    self.state = newState
  
  def getState(self):
    return self.state
        
  def sendFile(self, filename):
    """Transfers file over to the apiclient on the host."""
    filedata = open(filename).read()
    filesize = len(filedata)
    sendPacket(self.sockInit, struct.pack('i', filesize) +  filename)
    self.sockInit.send(filedata)

  def listdir(self, dirname):
    """Listing of the current directory."""
    rv = []
    for i in os.listdir(dirname):
      if (not os.path.isdir(i) and i[-3:] == ".py"):
        rv.append(i)
    return rv
  
  def sendCommand(self, szCommand, lstCommandData):
    """SzCommandData is what is to be sent to the host"""
        
    #For time gathering purposes, iTotalCount tells the number of agents simulated
    if szCommand == CMD_SIMULATE:
      self.iTotalCount = 0
      for i in lstCommandData[2:]:
        self.iTotalCount += i[2] - i[1]
          
    szCommandData = pickle.dumps(lstCommandData)

    self.setState(szCommand)
    #self.state = szCommand

    sendPacket(self.sockData, szCommandData)
    self.lastSendTime[self.state] = time.time()
    self.logger.debug('Receieved Command ' + szCommand + ' from API - event object set. Main loop should wake up' )
    self.HostEventObject.clear()    
    self.APIEventObject.set()
    
  def wait(self):
    """Waits till the HostEvent is not set."""
    self.HostEventObject.wait()
    
  def analyzeACK(self, szPacket):
    
    """analyze the Acknowledgement from the apiclient on the host."""
    
    #IV: Optimize code here. Create a class Command with two methods cmd (returning
    #the command text) and ack (returning the ack). Let self.state be a command object
    #and then this function can be just return self.state = S_OK or not etc ...
    
    if self.state == CMD_SIMULATE:
      if szPacket == CMD_ACK_SIMULATE:
        self.setState(S_OK)
        #self.state = S_OK
      else:
        self.setState(E_UNKNOWN)
        #self.state = E_UNKNOWN
    elif self.state == CMD_UPDATEDB:
      if szPacket == CMD_ACK_UPDATEDB:
        self.state = S_OK
      else:
        self.state = E_UNKNOWN
    elif self.state == CMD_UPDATESIMENV:
      if szPacket == CMD_ACK_UPDATESIMENV:
        self.state = S_OK
      else:
        self.state = E_UNKNOWN
    elif self.state == CMD_GLOBALSCHANGED:
      if szPacket == CMD_ACK_GLOBALSCHANGED:
        self.state = S_OK
      else:
        self.state = E_UNKNOWN
    elif self.state == CMD_QUIT:
      if szPacket == CMD_ACK_QUIT:
        self.state = S_QUIT
      else:
        self.state = E_UNKNOWN
    elif self.state == S_READY:
      self.state = S_READY
    return self.state
          
  def disconnect(self):
    self.sockData.close()
    
  def mainLoop(self):
    """The mainloop that connects and reads the packets sent"""
    self.connect(self.szSimname, self.szHost, self.iPort, self.szDBName, self.szDBHost, self.szDBUser, self.szDBPass)


    if self.state != S_READY:
      return 0

    self.logger.debug('MAINLOOP ready for simulation')
    while 1:
      self.logger.debug('Waiting for command from API' )
      self.APIEventObject.wait() #i got a command. I am processing it. so set host event object to clear

      self.logger.debug('Mainloop - received command from API' )
      self.APIEventObject.clear()

      self.logger.debug('Mainloop - API will wait when it calls wait' )
#      try:
      szPacket = readPacket(self.sockData)
      self.iterTime[self.state] = time.time() - self.lastSendTime[self.state]
#      except:
#        self.state = E_UNKNOWN
#        self.logger.critical(sys.exc_info());
#        self.logger.critical("SOCKET ERROR")        
#        break
      
      if self.analyzeACK(szPacket) == S_QUIT:
        self.disconnect()
        self.HostEventObject.set()
        self.APIEventObject.set()
        return

      
      self.logger.debug('Going to set HostEventObject')
      self.HostEventObject.set()
      self.logger.debug('Mainloop - API will wake up now if waiting on me' )
      if self.state == E_UNKNOWN:
        
        return
    
  def createThread(self, simname, host, port, dbname, dbhost, dbuser, dbpass):
    self.szSimname = simname
    self.szHost = host
    self.iPort = port
    self.szDBName = dbname
    self.szDBHost = dbhost
    self.szDBUser = dbuser
    self.szDBPass = dbpass
    self.setupLogger()
    self.thread = threading.Thread(target = self.mainLoop)
    self.thread.start()
    return
      
                                   
                                  
  def connect(self, simname, host, port, dbname, dbhost, dbuser, dbpass):

    assert(isinstance(self.sockInit, socket.socket))
    self.state = S_INITIALIZING
    self.sockInit.connect((host, port))
    if self.sockInit.recv(1024) != 'HELO':
      self.state = E_UNABLETOCONNECT
      return
      
    sendPacket(self.sockInit, simname)
    if self.sockInit.recv(1024) != 'FILENAME':
      self.state = E_UNABLETOTRANSFER
      return

    lstDir = self.listdir('.')
    sendPacket(self.sockInit, str(len(lstDir)))

    for i in lstDir:
      self.sendFile(i)
      
    if self.sockInit.recv(1024) != 'SFC':
      self.state = E_UNABLETOTRANSFER
      return


    self.socklisten = socket.socket()

    while 1:
      try:
        port = random.randint(1024, 65000)
        self.socklisten.bind((dictSettings[S_LOCALINTERFACEIP],port))
        self.socklisten.listen(4)
        break
      except:
        pass

    self.logger.debug('Listening on ' + dictSettings[S_LOCALINTERFACEIP] + ':' + str(port))
    sendPacket(self.sockInit, struct.pack('i', port) +  dictSettings[S_LOCALINTERFACEIP])
    sendPacket(self.sockInit, str(os.path.split(sys.argv[0])[1]))        
    if  self.sockInit.recv(1024) != 'HPC':
      self.state = E_UNABLETOTRANSFER
      return
    
   
    self.sockData, self.remote_addr = self.socklisten.accept()
    
    if self.sockData.recv(1024) != 'HELO':
      self.state = E_UNABLETOREVCONNECT
      return
    self.logger.debug('Remote host = ' + self.remote_addr[0] + ' : ' + str(self.remote_addr[1]))
    sendPacket(self.sockData, dbname)
    sendPacket(self.sockData, dbhost)
    sendPacket(self.sockData, dbuser)
    sendPacket(self.sockData, dbpass)


    self.logger.debug('Sent DB settings')
    
    if self.sockData.recv(1024) == 'GOT SETTINGS':
      self.logger.debug('Host : ' + self.szHost + ':' + str(self.iPort) + ' is ready')
      self.state = S_READY
      return

    self.logger.debug('Unknown error')
    self.state = E_UNKNOWN
    return
    
  
