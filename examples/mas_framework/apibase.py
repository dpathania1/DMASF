#!/usr/bin/python

from constants import *
from db import *
class APIBASE(object):
  """This file is extended by both api and apistub.py
  The utility of this file is provide the functions that are common to both of those files"""
  def setupLogger(self):
    """This function was to setup the logger so that it would help in debugging"""
    pass
  
  def __init__(self):
    """Setups the logger, initializes the DB"""
    
    self.bSimNameSet = False
    self.db = DB()
    self.setupLogger()
    
    self.szSimName = "UnnamedSim"
    self.bSimNameSet = False

    # This is required because when the user sets the values of which all agents
    # to draw, objUIInterface is not initialed yet.
    # Possible solution is to write the code in self.initialize here
    
    self.bDrawAllFlag = False
    self.lstDrawAgentList = []
    
  def setSimName(self, szSimName):
    """Extended by the api class. Sets the name of the simulation. A directory with this name
    is created in the home directory and the simulation files are stored there. The default name
    is UnnamedSim. If a directory with this name already exists, a directory with the name
    szSimName_N is created where N is the smallest possible positive integer"""
    if self.bSimNameSet:
      assert 0, "Cannot call setsimname twice"
    self.bSimNameSet = True
    self.szSimName = szSimName


  def enableSynchronousWrites(self, bEnabled):
    """If this setting is set to True, the updates of the agents are written immediately onto
    the database, so that the chages are visible to the next agent to be processed. If this
    value is false(default), the changes of one agent are visible only after the current iteration.
    Thus all agents get the same world view in the same iteration."""
    dictSettings[S_SYNCHRONOUSWRITES] = bEnabled
  
  def disableFlushingMessages(self, bDisabled):
    """By default, the messages received by all agents in iterations prior to the previous one are
    deleted at the start of the current iteration. This helps in reducing the processing time
    of messages received. This function disables this flushing of old messages."""
    dictSettings[S_FLUSHMESSAGES] = bDisabled

  def setMaxSimTime(self, maxtime):
    """Extended by the api class. This function is to set how long the simulation will run.
    The value defines the number of iterations and NOT the time. By default the value is -1
    which means infinity."""
    return True
  
  def killAgent(self, agtype, agentId):
    """This function is extended by the api class. It is used to kill an agent."""
    return True
  
  def createAgent(self, agtype, fields):
    """This function is extended by the api class. It creates an agent of type 'agtype' with the
    properties 'fields'. These properties are added to the default set of properties which are
    id, size, x, y, theta."""
    return True
  
  def registerWorldHandler(self, worldhandler):
    """This function is extended by the api class. It tells the system as to which class should
    be used as the worldhandler."""
    return True
  
  def restartSimulation(self):
    """This function is extended by the api class. If this function is called, it will clear
    the database before starting the simulation. If it is not called, the data and the state
    of the previous run of the simulation remains and the simulation gets resumed."""
    return True
  
  def addDrawAgent(self, type, id):
    """This function specifies which all agents to draw in the GUI. By default all agents are
    drawn. That might slow down the system. A call to setDrawAllFlag(False) and then subsequent
    calls to this function tell the system which all agents to draw. The id of an agent can be
    determined by agent.fields['id']. Moreover, the ids are given in an auto_increment manner
    to the agents."""
    #IV: Implemented in API ... So that it would not crash with apistub
    return True

  def deleteDrawAgent(self, type, id):
    """This function removes the particular agent from the drawing list of the GUI, to which
    agents get added by calls to addDrawAgent(self, agtype, agentId). However, if the user has
    done setDrawAllFlag(True) (which is set by default), calls to this function are meaningless."""
    #IV: Implemented in API ... So that it would not crash with apistub
    return True

  def setDrawAllFlag(self, bFlag):
    """By default the value of this is True, that is all the agents will be drawn. However,
    that can be disabled by setting False in this function. Then subsequent calls to addDrawAgent
    and deleteDrawAgent specify which all agents to draw in the GUI"""
    #IV: Implemented in API ... So that it would not crash with apistub
    return True
  
  def enableDrawAgentMode(self, bEnabled):
    """By default this is false i.e. all agents are drawn. If this is set to true then 
    only the agents of agent type __draw__ will be drawn. These agents will also be kept in main
    memory"""
    dictSettings[S_DRAWAGENTMODE] = bEnabled
    
  def setDrawAgentRedrawTime(self, iTime):
    """Specifies after how long the draw agent data should be refreshed"""
    if iTime <= 0:
      return
    dictSettings[S_DRAWAGENTMODEREDRAWTIME] = iTime
      
    
  

  def exit(self):
    """This is to exit from the api. It is extended by the api class. This exits only the threads
    of the API and not the GUI or the Qt thread."""
    return 0

  
  
