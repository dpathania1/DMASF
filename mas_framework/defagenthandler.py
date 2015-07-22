from db import *
import copy
#from OpenGL.GL import *
class defagenthandler:
  """The default class that handles the agents. The user should inherit it and overload
  the update(self, simtime) function."""
 
  def __init__(self, db, agtype, id, simtime, globalData = None):
    """Initializes the Db and other fields."""
    self.db = db
    assert(isinstance(self.db, DB))    
    self.fields = {}
    self.agtype = agtype
    self.id = id
    self.simtime = simtime
    self.globalData = globalData

    
  def kill(self):
    """kills self."""
    self.db.deleteObject(self.agtype, self.id)
    return
    
  def sendMessageSynchronous(self, to_type, to_id, message):
    """Sends message synchronously(immediately) to the agent(to_type, to_id)"""
    self.db.sendMessageSynchronous(self.agtype, self.id, to_type, to_id, self.simtime, message)
    
  def sendMessage(self, to_type, to_id, message):
    """Send a message to the agent specified to_type, to_id. Message is a 255 length character array. Message is sent after the completion of the iteration."""
    self.db.sendMessage(self.agtype, self.id, to_type, to_id, self.simtime, message)

  def getMessages(self):
    """Retrieves own inbox as a list of tuples.
    lst[i] = (TYPE_FROM, ID_FROM, simtime, Message)
    """
    return self.db.getMessages(self.agtype, self.id)
  
  def setState(self, fields):
    """Internal function. sets state and cache of current state."""
    self.fields = fields
    self.cache = copy.copy(self.fields)
    
  def readState(self):
    """Reads own state from the db, and caches it."""
    #st = time.time()
    self.fields = self.db.readObject(self.agtype, self.id)
    self.cache = copy.copy(self.fields)
    #if self.fields['id'] == 4:
    #  print "READ STATE: ", time.time() - st
    
  def writeStateSynchronous(self):
    """Writes the state in the db immediately."""
    for i in self.cache:
      if i == 'id':
        continue
      if self.fields[i] == self.cache[i]:
        del self.fields[i]
    self.db.writeObjectSynchronous(self.agtype, self.fields)


  
  def writeState(self):
    """Writes the state in the db after the current iteration."""
    return self.writeStateold()
  
  def writeStatenew(self):
    """rather call writeState"""
    self.db.writeObject(self.agtype, self.fields)
  
  def writeStateold(self):
    for i in self.cache:
      if i == 'id':
        continue
      if self.fields[i] == self.cache[i]:
        del self.fields[i]
    self.db.writeObject(self.agtype, self.fields)

     
  def update(self, simtime):
    """Function to be extended by the user to do agent action."""
    pass
    
