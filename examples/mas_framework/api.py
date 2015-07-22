#api.py the main API LAYER
#written by Aprameya Rao, Manish Jain {aprameya, manish_jain}@students.iiit.net

#from constants import *

import cPickle as pickle
from apibase import *
from db import *
from host import *
from ui_interface import *

import time
import threading
import logging
import bisect

#from gui_qtinterface import *

import sys

class API(APIBASE):
  global agent_types
  

  def setupLogger(self):
    """Sets up the logger settings so that errors and other outputs can be monitored."""
    self.logger = logging.getLogger('apiserver')
    self.logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    #add formatter to ch and fh

    fh = logging.FileHandler('log.apiserver')
#    fh.setLevel(LOG_LEVEL)
    fh.setFormatter(formatter)
    sh = logging.StreamHandler()
    #sh.setLevel(LOG_LEVEL)
    sh.setFormatter(formatter)

    self.logger.addHandler(fh)
    self.logger.addHandler(sh)
    self.logger.disabled = BLOGGING_DISABLED

  
  def __init__(self):
    """Initializes default values, creates threads and sets up the system. Important
    initialisations include setting bRestartSimulation to False and
    SchedulerType = SCHEDULER_DYNAMIC."""
    super(API, self).__init__()
    
    self.bRestartSimulation = False

    self.SchedulerType = SCHEDULER_DYNAMIC
    self.lstHosts = []

    #If this variable is true the server will send a CMD_UPDATESIMENV to the hosts
    self.bSimulationEnvUpdated = False
    #These dictionaries contain data required for the simulation environment
    self.dictNewDeletedIds = {}
    self.dictMaxIds = {}
    
    self.simtime = 0 #time of the current simulation
    self.maxsimtime = -1
    

    self.objUIInterface = None

    self.quit = False



    self.MainLoopThread = threading.Thread(target = self.start)
    self.evStartSim = threading.Event()
    self.evStartSim.clear()
    
  def startSim(self):
    """Called by the GUI when start is clicked. Starts of the simulation. This function doesnot
    make a call to canStartSim to check. This function doesnt return anything."""
    print 'evStartSim set'
    self.evStartSim.set()

  
  def canStartSim(self):
    """Checks for the activity of all hosts and finds out whether simulation can be started or
    not. Return Value = True or False"""
    for i in self.lstHosts:
      if i.state != S_READY: 
        self.logger.debug('Host : ' + i.szHost + ':' + str(i.iPort) + ' not ready')
        return False
    return True


  def setSimName(self, szSimName):
    """Sets the name of the simulation. A directory with this name is created in the home
    directory and the simulation files are stored there. The default name is UnnamedSim. If a
    directory with this name already exists, a directory with the name szSimName_N is created
    where N is the smallest possible positive integer.
    Function can fail if it is unable to create a table with the following simname (which might
    be desired in case of resumption of a simulation).
    Return Value = None"""
    super(API, self).setSimName(szSimName)
    dictSettings[S_SQL_MESSAGETABLE] += szSimName
    try:
      self.db.createTables()
    except: 
      pass
      
  def setMaxSimTime(self, maxtime):
    """Maxtime = -1(default) is infinity. 'maxtime' is the number of iterations for which the
    simulation will run and NOT the time.
    Return Value = None"""
    self.maxsimtime = maxtime
  
  def registerAgentType(self, agtype, handler, renderfunc, fields):
    """REGISTERS an agent type with fields dict. It creates the DB table for the
    specified agent type. Table name: agtype.
    agtype: Agent Type
    handler: Class which will handle the agent of that type. If handler is none then that agent will not be updated ...
    renderfunc: Function to be used by the GUI to draw an agent of that type. Used only when
    shape specified is SHAPE_USER
    
    fields: properties of that agent. The fields dictionary should have a format like
    dict['property_name'] = datatype where datatype can be either of the following - TYPE_INTEGER,
    TYPE_FLOAT, TYPE_STRING, TYPE_LSTRING(large string). To implement complex data types use
    the python pickle module to convert data to lstring format.
    
    The system also provides the following default properties -
    id, x, y, size, theta, shape, color.
    The shapes allowed are defined in constants.py. They include SHAPE_TRIANGLE, SHAPE_CIRCLE,
    SHAPE_SQUARE and SHAPE_USER. Only in case SHAPE_USER is set, then and only then the user
    specified renderfunc will be used to draw the agents.
    The colors allowed are COLOR_BLACK, COLOR_WHITE, COLOR_BLUE, COLOR_GREEN, COLOR_RED,
    COLOR_YELLOW, COLOR_GRAY. Besides these, the color can also be specified as RGB(r,g,b)
    where r,g,b should be positive integers between 0 and 255.

    Return Value = S_OK or ERR_DBERR
    """
    iMaxTypeId = 0
    for i in agent_types.keys():
      if agent_types[i]['__TypeId__'] >= iMaxTypeId:
        iMaxTypeId = agent_types[i]['__TypeId__']
        
    
    self.dictNewDeletedIds[agtype] = []
    self.dictMaxIds[agtype] = -1


    bTableExists = False

    if self.bRestartSimulation:
      self.db.curs.execute('drop table if exists ' + agtype)
    else:
      self.db.curs.execute('show tables')
      for i in self.db.curs.fetchall():
        if i[0] == agtype:
          bTableExists = True
          break
        
    iMinExistingId = -1
    iMaxExistingId = -1
    if bTableExists:
      self.db.curs.execute('select min(id), max(id) from ' + str(agtype))
      lstRes = self.db.curs.fetchall()
      iMinExistingId = int(lstRes[0][0])
      iMaxExistingId = int(lstRes[0][1])
      if iMinExistingId == None or iMaxExistingId == None:
        bTableExists = False
      

    newobj = {}
    if not bTableExists:
      newobj['__minId__'] = 1
      newobj['__maxId__'] = 1 
    else:
      newobj['__minId__'] = iMinExistingId
      newobj['__maxId__'] = iMaxExistingId + 1
      
    #print "REgister agent type: ", agtype, iMinExistingId, iMaxExistingId
    newobj['__lstDeletedIds__'] = []
    newobj['__TypeId__'] = iMaxTypeId + 1
    newobj['__type__'] = agtype
    newobj['__handler__'] = handler
    newobj['__renderfunc__'] = renderfunc
    
    newobj['__properties__'] = fields
    newobj['__properties__']['id'] = TYPE_INTEGER
    newobj['__properties__']['x'] = TYPE_FLOAT
    newobj['__properties__']['y'] = TYPE_FLOAT
    newobj['__properties__']['z'] = TYPE_FLOAT
    newobj['__properties__']['size'] = TYPE_INTEGER
    newobj['__properties__']['theta'] = TYPE_FLOAT
    newobj['__properties__']['shape'] = TYPE_INTEGER
    newobj['__properties__']['color'] = TYPE_INTEGER
    
    newobj['__cache__'] = {}
    newobj['__cache__']['__valid__'] = 0
    
    for i in CACHE_PERTYPE:
      newobj['__cache__'][i] = None
    
    agent_types[agtype] = newobj

    #for the create table statement
    #will create the list of fields and type of field
    flist = []
    for i in newobj['__properties__'].keys():
      newobj['__cache__'][i] = {}
      for j in CACHE_PERFIELD:
        newobj['__cache__'][i][j] = None
      if i == 'id':
        flist.append('id integer PRIMARY KEY')
      else:        
        flist.append(i + " " + newobj['__properties__'][i])
    
    query = 'CREATE TABLE ' + agtype + ' (\n' + ','.join(flist) + ');'

    self.logger.debug('Register Agent Type: ' + agtype + 'SQL \n' + query)
    try:
      qr = self.db.curs.execute(query)
      self.logger.debug('results: ' + str(qr))
    #query = 'CREATE INDEX ' + agtype + '_id ' + ' ON ' + agtype + ' (id);' 
    #self.db.curs.execute(query)
    except:
      return ERR_DBERR
    
    #try
    #self.db.writeType(agtype)
    
    return S_OK
    
  def killAgent(self,agtype,agentId):
    """This kills the agent specified by agtype, agentID. A deleted agent is just an agent whose
    agent code will never be executed. A message to a killed agent may not
    necessarily fail, just that it will never be read.
    Return Value = None"""
    global agent_types
    bisect.insort_left(agent_types[agtype]['__lstDeletedIds__'], agentId)
    self.dictNewDeletedIds[agtype].append(agentId)
    self.SetSimEnvUpdated()
    self.db.deleteObject(agtype,agentId)
  
  def createAgent(self, agtype, fields):
    """It creates an agent of type 'agtype' with the values of the properties specified in
    dictionary 'fields'. These properties are those which are specified while calling
    registerAgentType or the default agent properties (id, size, x, y, theta, shape, color).
    id of the agent is automatically calculated and set.
    Return Value = S_OK."""

    global agent_types
    
    #self.db.curs.execute('select max(id) from ' + agtype + ';')
    id = agent_types[agtype]['__maxId__']
    agent_types[agtype]['__maxId__'] += 1
    self.dictMaxIds[agtype] = id + 1
    self.SetSimEnvUpdated()
      
    fields['id'] = id
    
    if ( not fields.has_key("shape") ):
      fields["shape"] = SHAPE_TRIANGLE
    
    if ( not fields.has_key("color") ):
      fields["color"] = COLOR_BLUE
      
    if ( not fields.has_key("theta") ):
      fields["theta"] = 0
      
    if ( not fields.has_key("size") ):
      fields["size"] = 40
    
    query = self.db.insertQueryFromFields(agtype, fields)
    #print query
    #self.db.updatelist.append(query)
    self.db.curs.execute(query)
    
    return S_OK;
  
  def registerWorldHandler(self, worldhandler):
    """The system will use 'worldhandler' to handle the world.
    Return Value = None."""
    global world_handler
    world_handler = worldhandler
  
  def bSimDone(self):
    """Returns whether simulation is completed or not.
    Return Value = True, 0(in caes of maxsimtime is set to -1, or the number of iterations left
    for the simulation to complete."""
    if self.quit == True:
      return True
    elif self.maxsimtime == -1:
      return 0
    else:
      return (self.simtime) > self.maxsimtime

  def cleanNullTerminatedString(self, szNullTerm):
    #Warning: DEPRECATED
    """This function is used while connecting to the hosts. It cleans the null terminated
    strings. """
    for i in xrange(len(szNullTerm)):
      if szNullTerm[i] == '\x00':
        return szNullTerm[:i]
    return szNullTerm
      

  def unpackSimulationCommand(self, szCommand):
    """This function is used to unpack the commands sent over to the hosts. It is used by hosts.
    Structure of the command specified in packSimulationCommand.
    """
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
    """Packs the commands in the following structure: 
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
                              
                               
  def createSimulationCommandsStatic(self, iSimTime):
    """This function creates the simulation commands to be sent to different hosts.
    It also finds out the agent ranges to be simulated by different hosts, in case of a static
    scheduler.
    """
    dictCommands = {}
    
    dictAgentCount = {}
    dictAgents = {}
    for i in self.db.readTypes():
      if agent_types[i]['__handler__'] == None:
        continue
      dictAgents[i] = agent_types[i]['__minId__']
      dictAgentCount[i] = agent_types[i]['__maxId__'] - agent_types[i]['__minId__']
    
    iNumHosts = len(self.lstHosts)

    for i in xrange(len(self.lstHosts)):
      dictCommands[i] = [CMD_SIMULATE, iSimTime]
      
      lstKeys = dictAgentCount.keys()
      for j in lstKeys:
        lstThisCommand = [j]
        
        iIdLow = -1
        iIdHigh = -1
        if i == len(self.lstHosts) - 1:
          iIdLow = dictAgents[j]
          iIdHigh = agent_types[j]['__maxId__']
        else:      
          iSlice = int(float(dictAgentCount[j]) / float(iNumHosts)) + 1
          iIdLow = dictAgents[j]
          iIdHigh = iIdLow + iSlice
          dictAgents[j] = iIdHigh
        
        lstThisCommand.append(iIdLow)
        lstThisCommand.append(iIdHigh)
        
        dictCommands[i].append(lstThisCommand)

    return dictCommands
    
    
    #global agent_types


    #iAgentCount = 0
    #dictAgents = {}
    #for i in self.db.readTypes():
      #dictAgents[i] = agent_types[
      #iAgentCount += len(dictAgents[i])

    #iHostCount = len(self.lstHosts)
    #iAgentsPerHost = iAgentCount / iHostCount + 1
    

    #iHostId =  0
    #lstThisHost = []
    #dictCommands = {}
    #for i in xrange(len(self.lstHosts)):
      #dictCommands[i] = [CMD_SIMULATE, iSimTime]
      #for j in dictAgents.keys():
        #lstThisType = [j]
        #if not (i == len(self.lstHosts) - 1):
          #lstThisType.extend(dictAgents[j][iAgentsPerHost * i : iAgentsPerHost * (i + 1)])
        #else:
          #lstThisType.extend(dictAgents[j][iAgentsPerHost * i :])
        #dictCommands[i].append(lstThisType)                             
      ##dictCommands[i] = pickle.dumps(dictCommands[i])
      
    #return dictCommands
      
  def createSimulationCommands(self, iSimTime):
    """This function creates the simulation command on the basis of the scheduler used.
    The scheduler used is specified in SchedulerType which gets its setting from
    dictSettings['SchedulerType']. """
    if self.SchedulerType == SCHEDULER_DYNAMIC:
      return self.createSimulationCommandsDynamic(iSimTime)
    elif self.SchedulerType == SCHEDULER_STATIC:
      return self.createSimulationCommandsStatic(iSimTime)
      
  def createSimulationCommandsDynamic(self, iSimTime):
    """Creates the simulation commands to be sent over to the hosts in case of dynamic scheduler.
    Structure of Command Packet for SIM
    id = SIM

    command[0] = 'SIM'
    command[1] = 'Current sim time'
    command[2][0] = 'type name'
    command[2][1] = 'id low'
    command[2][2] = 'id high'
    command[3][0] = 'type name'
    command[3][1] = 'id low'
    command[3][2] = 'id high'"""
    
    dictCommands = {}
    
    dictAgentCount = {}
    dictAgents = {}
    for i in self.db.readTypes():
      if agent_types[i]['__handler__'] == None:
        continue
      dictAgents[i] = agent_types[i]['__minId__']
      dictAgentCount[i] = agent_types[i]['__maxId__'] - agent_types[i]['__minId__']
    
    times = []

    # Number of agents to be scheduled by one host is inversely proportional to the time it took
    # to simulate one agent in the previous iteration.
        
    for i in self.lstHosts:
      times.append(float(i.iterTime[CMD_SIMULATE] + i.iterTime[CMD_UPDATEDB]) / i.iTotalCount)
      
    lcm = 1
    for i in times:
      lcm *= i
      
    # times list defines the ratio in which the agents have to be distributed. times[0]:times[1]..
    # defines the ratio of the number of agents to be given to host_0:host_1...
    
    times = [float(lcm) / i for i in times]

    
    totaltime = sum(times)
    
    for i in xrange(len(self.lstHosts)):
      dictCommands[i] = [CMD_SIMULATE, iSimTime]
      
      lstKeys = dictAgentCount.keys()
      for j in lstKeys:
        lstThisCommand = [j]
        
        iIdLow = -1
        iIdHigh = -1
        if i == len(self.lstHosts) - 1:
          iIdLow = dictAgents[j]
          iIdHigh = agent_types[j]['__maxId__']
        else:      
          iSlice = int(times[i] / totaltime * dictAgentCount[j]) + 1
          iIdLow = dictAgents[j]
          iIdHigh = iIdLow + iSlice
          dictAgents[j] = iIdHigh
        
        lstThisCommand.append(iIdLow)
        lstThisCommand.append(iIdHigh)
        
        dictCommands[i].append(lstThisCommand)

    return dictCommands
    
       
  def addHost(self, host, port):
    """Adds a host to the system.
    Return Value: SUCCESS"""
    h = HOST()
    self.lstHosts.append(h)
    h.createThread(self.szSimName, host, port, 'traffic', 'localhost', 'traffic', 'SimTraffic')
    return SUCCESS

  def deleteHost(self, iHostIndex):
    """Currently a host cannot be deleted dynamically. Function returns FAILURE."""
    return FAILURE

  def restartSimulation(self):
    """Restart simulation MUST be called after setting simname and before registering
    any agent types. It clears the db. If this function is not called, the system resumes
    simulation where it left last. However, this might not work properly if another simulation
    with an agent type of the same name is created and run in the meanwhile."""
    # ------------------------------------------------# 
    self.bRestartSimulation = True
    self.db.curs.execute('drop table if exists ' + dictSettings[S_SQL_MESSAGETABLE])
    self.db.createTables()
    # ------------------------------------------------# 
    #return self.db.clearDB()

  def sendMessage(self, from_type, from_id, to_type, to_id, simtime, message):
    """Sends a message from the from_agent to the to_agent. However, the user may not call
    this for sending messages. He can use sendMessage provided with the agent handler."""
    self.db.sendMessageSynchronous(from_type, from_id, to_type, to_id, simtime, message)

    
  def Initialize(self):
    """Initialises the system and also reads the command line options.
    The command line format is:
    python main.py help
    OR
    python main.py <scheduler type>
    OR
    python main.py <scheduler type> -nogui <host:port> [<host:port>...]

    It then starts the simulation in case of -nogui. In case of gui, the simulation is
    started after atleast one host has been added and then play is clicked.
    """
    if len(sys.argv) > 1:
      if sys.argv[1] == 'help':
        print "Syntax - python main.py <scheduler type> -nogui [<host> <host>]"
      elif sys.argv[1] == 'static' :
        self.SchedulerType = SCHEDULER_STATIC
        del sys.argv[1]
      elif sys.argv[1] == 'dynamic':
        self.SchedulerType = SCHEDULER_DYNAMIC
        del sys.argv[1]
        
    
    self.bLaunchGUI = True
    if len(sys.argv) > 2:
      if '-nogui' in sys.argv:
        self.bLaunchGUI = False
  
    self.objUIInterface = UIInterface(self,self.bLaunchGUI)
    for i in self.lstDrawAgentList:
      self.objUIInterface.addDrawAgent(i[0],i[1])
    self.objUIInterface.setDrawAllFlag(self.bDrawAllFlag)
    self.objUIInterface.app.exec_loop()

  def SetSimEnvUpdated(self):
    self.bSimulationEnvUpdated = True
    
  def UnSetSimEnvUpdated(self):
    self.bSimulationEnvUpdated = False
    for i in self.dictNewDeletedIds.keys():
      self.dictNewDeletedIds[i] = []
      
    for i in self.dictMaxIds.keys():
      self.dictMaxIds[i] = -1
    
  def isSimEnvChanged(self):
    return self.bSimulationEnvUpdated == True
  
  def createSimEnvChangedComand(self):
    #Structure of list of command data :
    #[[typename, maxid, newdeleted items], [typename, maxid, newdeleteditemns]]
    dictSimCommands = {}
    for i in self.dictMaxIds.keys():
      if self.dictMaxIds[i] != -1:
        dictSimCommands[i] = [i, self.dictMaxIds[i], []]
    
    for i in self.dictNewDeletedIds.keys():
      if self.dictNewDeletedIds[i]:
        if dictSimCommands.has_key(i):
          dictSimCommands[i][2] = self.dictNewDeletedIds[i]
        else:
          dictSimCommands[i] = [i, -1, self.dictNewDeletedIds[i]]
          
    lstCommand = []
    for i in dictSimCommands.keys():
      lstCommand.append(dictSimCommands[i])
      
    return lstCommand
        
   
  def start(self):
    """This starts the simulation with the settings provided earlier. The simulation states
    are written to a file called 'benchmark' in the current directory, apart from the settings of
    the logger."""
    fBenchMark = open('benchmark', 'w')
    fBenchMark.write( '=(')
    global agent_types
    self.logger.debug('Instantiating wh')
    wh = world_handler()
    self.simtime = 0
    
    dictCommands = {}
    
    self.db.curs.execute('ALTER TABLE ' + dictSettings[S_SQL_MESSAGETABLE]+ ' disable keys')
    wh.begin(self)
    self.db.curs.execute('ALTER TABLE ' + dictSettings[S_SQL_MESSAGETABLE] + ' enable keys')
    self.SetSimEnvUpdated()
    
    
    if not self.bLaunchGUI : 
      for i in sys.argv[sys.argv.index('-nogui') + 1:]:
        if i.lower() == '-nogui':
          continue
        szHost = i[:i.find(':')]
        iPort = int(i[i.find(':') + 1:])
        self.addHost(szHost, iPort)
    
      for i in self.lstHosts:
        while i.getState() != S_READY:
          print "Waiting for host: ", i.szHost, ':', i.iPort
          time.sleep(1)
                   

    lstCommands = [CMD_GLOBALSCHANGED, pickle.dumps(wh.globalData.__dict__)]
    for i in xrange(len(self.lstHosts)):
      self.lstHosts[i].sendCommand(CMD_GLOBALSCHANGED, lstCommands)
      self.logger.debug('Sent command Updateglobals to: ' + str(self.lstHosts[i].szHost) + ':' + str(self.lstHosts[i].iPort))
      
    for i in self.lstHosts:
      i.wait()
      
          
          
          
    print "Starting Simulation"
    iIterCount = 0
    while True:
      self.evStartSim.wait()
      if self.bSimDone():
        break

      self.logger.debug('-'*50)
      self.logger.debug('Mainloop beginning. simtime = ' + str(self.simtime))

      loop_stime = time.time()

      #SimEnvUpdated needs to be sent before scheduling is done
      if wh.beginUpdate(self.simtime, self) == True:
        lstCommands = [CMD_GLOBALSCHANGED, pickle.dumps(wh.globalData.__dict__)]
        for i in xrange(len(self.lstHosts)):
          self.lstHosts[i].sendCommand(CMD_GLOBALSCHANGED, lstCommands)
          self.logger.debug('Sent command Updateglobals to: ' + str(self.lstHosts[i].szHost) + ':' + str(self.lstHosts[i].iPort))
          
        for i in self.lstHosts:
          i.wait()
      
      if self.isSimEnvChanged():
        lstCommands = self.createSimEnvChangedComand()
        for i in xrange(len(self.lstHosts)):
          self.lstHosts[i].sendCommand(CMD_UPDATESIMENV, [CMD_UPDATESIMENV, lstCommands])
          self.logger.debug('Sent Command SIMENV to: ' + str(self.lstHosts[i].szHost) + ':' + str(self.lstHosts[i].iPort))
          
        for i in self.lstHosts:
          i.wait()
          
        self.UnSetSimEnvUpdated()
            
    

      iCreateSimCommand = time.time()
      if not (self.simtime % 1):
        dictCommands = self.createSimulationCommands(self.simtime)
      
      iSendSim = time.time()
      for i in xrange(len(self.lstHosts)):
        self.lstHosts[i].sendCommand(CMD_SIMULATE, (dictCommands[i]))
        self.logger.debug('Sent Command SIMULATTE to: ' + str(self.lstHosts[i].szHost) + ':' + str(self.lstHosts[i].iPort))
        
      iWaitSim = time.time()  
      for i in self.lstHosts:
        self.logger.debug('Waiting on SIMULATE ' + str(i.szHost) + ':' + str(i.iPort))
        i.wait()
        self.logger.debug('Woke Up on SIMULATE ' + str(i.szHost) + ':' + str(i.iPort))        
        
      iUpdateDB = time.time()
      ##############################
      if dictSettings[S_FLUSHMESSAGES]:
        self.db.curs.execute('delete from ' + dictSettings[S_SQL_MESSAGETABLE])
      #for i in agent_types.keys():
      #  self.db.curs.execute('alter table ' + i + ' disable keys')
      self.db.curs.execute('alter table ' + dictSettings[S_SQL_MESSAGETABLE]+ ' disable keys')
      #############################

      for i in self.lstHosts:
        i.sendCommand(CMD_UPDATEDB, [CMD_UPDATEDB])
        self.logger.debug('Sent UpdateDB to ' + str(i.szHost) + ':' + str(i.iPort))
        
      iWaitUpdateDB = time.time()
      for i in self.lstHosts:
        self.logger.debug('Waiting on UPDATEDB ' + str(i.szHost) + ':' + str(i.iPort))
        i.wait()
        self.logger.debug('Woke up on UPDATEDB ' + str(i.szHost) + ':' + str(i.iPort))        
      


      ###################################
      #for i in agent_types.keys():
      #  self.db.curs.execute('alter table ' + i + ' enable keys')
      self.db.curs.execute('alter table ' + dictSettings[S_SQL_MESSAGETABLE]+ ' enable keys')
      ########################################


      
      if self.bLaunchGUI:
        self.objUIInterface.updateUI(self.simtime)

      iEnd = time.time()
      
      self.simtime += 1

      #update the gui now

      #-------------------
      

      
      iIterCount += 1
      
      if not (self.simtime % 1) and 1:
        fBenchMark.write(str((time.time() - loop_stime) * 1000) + ' + ')
        fBenchMark.flush()

        print ("FT: " + str(time.time() - loop_stime) + " - " + str(self.simtime))
        #self.logger.debug("FT: " + str(time.time() - loop_stime) + " - " + str(self.simtime) + '\n')
        lstTimes = [ iSendSim - iCreateSimCommand, iWaitSim - iSendSim, iUpdateDB - iWaitSim, iWaitUpdateDB - iUpdateDB, iEnd - iWaitUpdateDB]
        lstTimes = [(i * 1000) for i in lstTimes]
        print ( "TIMES:", '-' * 30 )
        #self.logger.debug("TIMES\n")
        logTimes = ""
        for i in lstTimes:
          logTimes +=  '%.2f'%(i,) + ","
        print (logTimes)
        #self.logger.debug(str(logTimes) + '\n')
        for i in self.lstHosts:
          ival = sum(i.iterTime.values())
          print ( "Host: ", i.szHost, ':', i.iPort, '-',  ival, i.iTotalCount, float(ival) / float(i.iTotalCount))
          #self.logger.debug(str( ("Host: ", i.szHost, ':', i.iPort, '-',  ival, i.iTotalCount, float(ival) / float(i.iTotalCount)),))
          #self.logger.debug('\n')
        print ('='*50)
        
        if wh.endUpdate(self.simtime, self) == True:
          self.quit = True
          
      
    wh.end(self)
    
    for i in self.lstHosts:
      i.sendCommand(CMD_QUIT, [CMD_QUIT])
    fBenchMark.write(' 0) / ' + str(iIterCount))
    fBenchMark.close()

  def exit(self):
    """Exits the threads of the api. Does not exit the other threads of the GUI"""
    print "called exit"
    self.quit = True
    self.evStartSim.set()

  def addDrawAgent(self, type, id):
    if not self.objUIInterface:
      self.lstDrawAgentList.append((type,id))
    else:
      self.objUIInterface.addDrawAgent(type, id)

  def deleteDrawAgent(self, type, id):
    if not self.objUIInterface:
      self.lstDrawAgentList.remove(type, id)
    else:
      self.objUIInterface.deleteDrawAgent(type, id)

  def setDrawAllFlag(self, bFlag):
    if not self.objUIInterface:
      self.bDrawAllFlag = bFlag
    else:
      self.objUIInterface.setDrawAllFlag(bFlag)
