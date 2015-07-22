#apistub.py the main API LAYER
#written by Aprameya Rao, Manish Jain {aprameya, manish_jain}@students.iiit.net

# This file is copied as api.py on all the hosts. It provides dummy functions for
# user calls like createAgent and registerAgentType for the server will do those
# activities.

from constants import *
from apibase import *
from defworldhandler import CGlobalVariables
import cPickle as pickle

import struct
from mysocket import *
import time
import threading
import logging
import os
import bisect

class SIMULATER:
  """This is the actual class that will run the simulation on the host."""
  def setupLogger(self):
    """Initializes logging.
    For more detail, refer to the documentation of python logger."""
    self.logger = logging.getLogger('SIMULATOR' + str(self.iSimulatorID))
    self.logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    #add formatter to ch and fh

    #fh = logging.FileHandler('log.apistub')
    #fh.setLevel(logging.DEBUG)
    #fh.setFormatter(formatter)
    sh = logging.StreamHandler()
    sh.setLevel(logging.DEBUG)
    sh.setFormatter(formatter)

    #self.logger.addHandler(fh)
    self.logger.addHandler(sh)
    self.logger.disabled = BLOGGING_DISABLED
    
  def __init__(self, id, globalData):
    """Initializes the simulator object. Creates a new thread and sets up the logger."""

    self.globalData = globalData
    
    self.bSimNameSet = False
    self.iSimulatorID = id
    self.setupLogger()

    self.db = DB(id)
    self.evSimulate = threading.Event()
    self.evSimulate.clear()
    self.evSyncDB = threading.Event()
    self.evAPI = threading.Event()
    self.evAPI.clear()
    self.evSyncDB.clear()
    self.threadSyncDB = threading.Thread(target = self.syncDBLoop)
    self.thread = threading.Thread(target = self.mainloop)
    self.thread.start()
    self.bQuit = False
    self.szSimName = "UnnamedSim"

  def syncDB(self):
    """Sets the events such as to synchronise the DB """
    self.evAPI.clear()
    self.evSyncDB.set()
    
  def syncDBLoop(self):
    """Event based synchronisation. Runs in a while 1 and waits for events."""
    while 1:
      self.evSyncDB.wait()
      if self.bQuit == True:
        return
      
      self.evSyncDB.clear()
      self.db.syncDB()
     
      self.evAPI.set()

  def mainloop(self):
    """Main loop which executes the agent code. It processes the agents
    whose id's lie within self.iIdLow and self.iIdHigh of type self.szType"""
    global agent_types
    while 1:
      self.evSimulate.wait()
      self.logger.debug('Entered Mainloop')
      if self.bQuit == True:      
        return
    
      self.evSimulate.clear()
    
      if self.szType != None and self.simtime != None and self.iIdLow!= -1 and self.iIdHigh != -1:
        
        if dictSettings[S_SYNCHRONOUSWRITES]:
          for i in xrange(self.iIdLow, self.iIdHigh):
            
            if agent_types[self.szType]['__lstDeletedIds__']:          
              p = bisect.bisect_right(agent_types[self.szType]['__lstDeletedIds__'], i)
              if p == 0 and agent_types[self.szType]['__lstDeletedIds__'][0] == i:
                continue            
              if agent_types[self.szType]['__lstDeletedIds__'][p - 1] == i:
                continue            
            
            ag = agent_types[self.szType]['__handler__'](self.db, self.szType, i, self.simtime, self.globalData)
            ag.readState()
            ag.update(self.simtime)
        else:
          for i in xrange(self.iIdLow, self.iIdHigh, dictSettings[S_NUMAGENTSTOFETCHATONCE]):
            

            iQueryLowIndex = i
            iQueryHighIndex = i + dictSettings[S_NUMAGENTSTOFETCHATONCE]
            if (self.iIdHigh - i) < dictSettings[S_NUMAGENTSTOFETCHATONCE]:
              iQueryHighIndex = self.iIdHigh
            
            lstDictAgentData = self.db.readObjects(self.szType, iQueryLowIndex, iQueryHighIndex)
            
            for j in lstDictAgentData:            
              ag = agent_types[self.szType]['__handler__'](self.db, self.szType, j['id'], self.simtime, self.globalData)
              ag.setState(j)
              ag.update(self.simtime)
        
      self.logger.debug('Done simulating')
        
      self.evAPI.set()
    
  def quit(self):
    self.bQuit = True
    self.evSyncDB.set()
    self.evSimulate.set()
    self.db.shutDown()
    
  def wait(self):
    self.evAPI.wait()
    
    
  def simulate(self, simtime, szType, iIdLow, iIdHigh):
    """This simulator object will simulate the agents of type 'szType' with  ids
    between iIdLow and iIdHigh"""
    self.szType = szType
    self.simtime = simtime
    self.iIdLow = iIdLow
    self.iIdHigh = iIdHigh
    self.logger.debug('SIMULATING:' + str(szType) + ' ' + str(iIdLow) + ' ' + str(iIdHigh))  

    self.evAPI.clear()
    self.evSimulate.set()
    


class APISTUB(APIBASE):
  """This class will act as the API class for the host objects. It provides the reverse
  network connections and dummy functions for function calls like registerAgentType
  which get executed at the server. It creates as many simulator objects as specified
  in self.iSimulatorCount(default = 10) to execute the agents."""
  global agent_types
  def setupLogger(self):
    self.logger = logging.getLogger('apistub')
    self.logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    #add formatter to ch and fh

    fh = logging.FileHandler('log.apistub')
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    sh = logging.StreamHandler()
    sh.setLevel(logging.DEBUG)
    sh.setFormatter(formatter)

    self.logger.addHandler(fh)
    self.logger.addHandler(sh)
    self.logger.disabled = BLOGGING_DISABLED

  
  def __init__(self):
    """ Does reverse connect, creates simulators and calls the apibase's init."""
    self.setupLogger()
    self.revConnect()
    #rev connect must happen FIRST
    super(APISTUB, self).__init__()

    self.globalData = CGlobalVariables()
    
    self.iSimulatorCount = 10
    self.lstSimulators = []
    
    for i in xrange(self.iSimulatorCount):
      simulator = SIMULATER(i, self.globalData)
      self.lstSimulators.append(simulator)

  def revConnect(self):
    """Does reverse connect with the server and the db. DB settings are recvd from the 
    server. DO NOT INSTANTIATE DB BEFORE YOU DO REVCONNECT."""
    szSettings = open('settings').read()
    iRemotePort = struct.unpack('i', szSettings[:4])[0]
    szRemoteHost = szSettings[4:]

    self.logger.debug("Connecting to: " +  szRemoteHost + ":" + str(iRemotePort) + '\n')
    self.logger.debug('Sleeping 2 seconds')
 
    self.sockData = socket.socket()
    self.sockData.connect((szRemoteHost, iRemotePort))
    self.logger.debug("Connected to: " +  szRemoteHost + ":" + str(iRemotePort) + '\n')
    
    self.sockData.send("HELO")
    
    self.szDBName = readPacket(self.sockData)
    DB_NAME = self.szDBName
    self.szDBHost = readPacket(self.sockData)
    DB_HOST = self.szDBHost
    self.szDBUser = readPacket(self.sockData)
    DB_USER = self.szDBUser
    self.szDBPass = readPacket(self.sockData)
    DB_PASSWD = self.szDBPass
    
    
    self.logger.debug("Ready for simulation. DBname = %s, DBhost = %s, DBUser = %s, DBPass = %s\n" % (self.szDBName, self.szDBHost, self.szDBUser, self.szDBPass))
    self.sockData.send("GOT SETTINGS")
    
  def registerAgentType(self, agtype, handler, renderfunc, fields):
    """REGISTERS an agent type with fields dict (refer API.registerAgentType)"""
    iMaxTypeId = 0
    for i in agent_types.keys():
      if agent_types[i]['__TypeId__'] >= iMaxTypeId:
        iMaxTypeId = agent_types[i]['__TypeId__']
        
    
    newobj = {}
    newobj['__minId__'] = 1
    newobj['__maxId__'] = 1 + 99999999
    newobj['__lstDeletedIds__'] = []
    newobj['__TypeId__'] = iMaxTypeId + 1
    newobj['__type__'] = agtype
    newobj['__handler__'] = handler
    newobj['__renderfunc__'] = renderfunc
    
    newobj['__properties__'] = fields
    newobj['__properties__']['id'] = TYPE_INTEGER
    newobj['__properties__']['x'] = TYPE_FLOAT
    newobj['__properties__']['y'] = TYPE_FLOAT
    newobj['__properties__']['size'] = TYPE_INTEGER
    newobj['__properties__']['theta'] = TYPE_FLOAT
    newobj['__properties__']['shape'] = TYPE_INTEGER
    newobj['__properties__']['color'] = TYPE_INTEGER
    
    newobj['__cache__'] = {}
    newobj['__cache__']['__valid__'] = 0
    
    for i in CACHE_PERTYPE:
      newobj['__cache__'][i] = None

    for i in newobj['__properties__'].keys():
      newobj['__cache__'][i] = {}
      for j in CACHE_PERFIELD:
        newobj['__cache__'][i][j] = None

    agent_types[agtype] = newobj
    # This does not create table in the DB for it
    # is done by the server.
    return S_OK
    
  def cleanNullTerminatedString(self, szNullTerm):
    for i in xrange(len(szNullTerm)):
      if szNullTerm[i] == '\x00':
        return szNullTerm[:i]
    return szNullTerm
      

  def unpackSimulationCommand(self, szCommand):
    """Returns a list unpacking the command sent in szCommand"""
    lstCommand = ['','']
    
    iCurPos = 0
    
    t1 = struct.unpack('16si', szCommand[:iCurPos + struct.calcsize('16si')])
    iCurPos += struct.calcsize('16si')
    lstCommand[0] = self.cleanNullTerminatedString(t1[0])
    lstCommand[1] = t1[1]
    
    iTypeCount = struct.unpack('i', szCommand[iCurPos:iCurPos + struct.calcsize('i')])[0]
    iCurPos += struct.calcsize('i')
    
    for i in xrange(iTypeCount):
      
      lstThisAgent = []
      szTypeName = struct.unpack('16s', szCommand[iCurPos: iCurPos+struct.calcsize('16s')])[0]
      iCurPos += struct.calcsize('16s')
           
      szTypeName = self.cleanNullTerminatedString(szTypeName)
      
      lstThisAgent = [szTypeName]
      
      iAgentCount = struct.unpack('i', szCommand[iCurPos:iCurPos+struct.calcsize('i')])[0]
      iCurPos += struct.calcsize('i')
      
      for j in xrange(iAgentCount):
        iCurAgentId = struct.unpack('i', szCommand[iCurPos:iCurPos+struct.calcsize('i')])[0]
        iCurPos += struct.calcsize('i')
        lstThisAgent.append(iCurAgentId)
      
      lstCommand.append(lstThisAgent)
      
    return lstCommand
  
  def packSimulationCommand(self, lstCommand):
    """Packs the list in a string.
    Byte structure
    0-15 = Command name
    16-19 = simtime
    20-23 = number of types
    24-39 = typename
    40-43 = number of agents
    ....."""
    szCommand = ""
    szCommand = struct.pack('16si', lstCommand[0], lstCommand[1])
    szCommand += struct.pack('i', len(lstCommand[2:]))
    for i in lstCommand[2:]:
      szCommand += struct.pack('16s', i[0])
      szCommand += struct.pack('i', len(i[1:]))
      for j in i[1:]:
        szCommand += struct.pack('i', j)

    return szCommand
  
  
  def Initialize(self):
    """Starts the simulation"""
    self.start()
    
  def errProc(self, szErrMsg):
    """In case of Error, log the error and quit all simulators."""
    self.logger.critical(szErrMsg)
    self.logger.debug(szErrMsg)
    for i in self.lstSimulators:
      i.quit()
    return False
   
  def start(self):
    """ Starts the simulation."""
    global agent_types

    while 1:
      self.logger.debug('Reading Command')
      try:
        pkCommand = readPacket(self.sockData)
      except:
        return self.errProc('Socket Error in reading command')
      
      command = pickle.loads(pkCommand)#self.unpackSimulationCommand(pkCommand)
      self.logger.debug('Received Command ' + command[0])
      
      if command[0] == CMD_SIMULATE:

        simtime = command[1]
        for i in xrange(2, len(command)):
          szType = command[i][0]
          iTotalIdLow = command[i][1]
          iTotalIdHigh = command[i][2]
          
          c = 0
          self.logger.debug('starting simulating')
          
          for j in self.lstSimulators:
            assert(isinstance(j, SIMULATER))
            idLow = int(float(iTotalIdHigh - iTotalIdLow) / float(self.iSimulatorCount) * c) + iTotalIdLow
            idHigh = int(float(iTotalIdHigh - iTotalIdLow) / float(self.iSimulatorCount) * (c + 1)) + iTotalIdLow
            self.logger.debug('simulating from: ' + str(idLow) + ':' + str(idHigh))
            if c == len(self.lstSimulators) - 1:
              j.simulate(simtime, szType, idLow, iTotalIdHigh)
            elif idLow != idHigh:
              j.simulate(simtime, szType, idLow, idHigh)
            elif idLow == idHigh:
              j.simulate(None, None, -1, -1)
            c = c + 1

          self.logger.debug('waiting for simulators')
          for j in self.lstSimulators:
            j.wait()
          
          #for j in xrange(1, len(command[i])):
            #iAgentId = command[i][j]
            #ag = agent_types[szType]['__handler__'](self.db, szType, iAgentId, simtime)
            #ag.readState()
            #ag.update(simtime)
        
        
        self.logger.debug('Sending ACK for SIMULATE')
        try:          
          sendPacket(self.sockData, CMD_ACK_SIMULATE)
        except:
          return self.errProc('Socket SIMULATE error')


      elif command[0] == CMD_UPDATEDB:
        self.logger.debug('updatedb')
        #self.db.syncDB()
        for i in self.lstSimulators:
          i.db.syncDB()       
        for i in self.lstSimulators:
          i.wait()
        try:
          sendPacket(self.sockData, CMD_ACK_UPDATEDB)
        except:
          return self.errProc('Socket updatedb error')
        
      elif command[0] == CMD_UPDATESIMENV:
        global agent_types
        self.logger.debug('Update sim env')
        lstCommands = command[1]
        for i in lstCommands:
          szTypeName = i[0]
          iMaxId = i[1]
          lstDeletedIds = i[2]
          if iMaxId != -1:
            agent_types[szTypeName]['__maxId__'] = iMaxId
          if lstDeletedIds:
            for j in lstDeletedIds:
              bisect.insort_left(agent_types[szTypeName]['__lstDeletedIds__'], j)
        
        try:
          sendPacket(self.sockData, CMD_ACK_UPDATESIMENV)
        except:
          return self.errProc('Socket updatesimenv error')
              
      elif command[0] == CMD_GLOBALSCHANGED:
        self.globalData.setGlobals(pickle.loads(command[1]))
        
        try:
          sendPacket(self.sockData, CMD_ACK_GLOBALSCHANGED)
        except:
          return self.errProc('Socket updateglobals ack error')
        
      elif command[0] == CMD_QUIT:
        self.logger.debug('quitting')
        for j in self.lstSimulators:
          j.quit()
        sendPacket(self.sockData, CMD_ACK_QUIT)
        self.sockData.shutdown(0)
        self.sockData.close()
        return 0

API = APISTUB
