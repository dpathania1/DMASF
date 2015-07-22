
#DB.py database layer for mas framework
#Written by Aprameya Rao, Manish Jain , {aprameya, manish_jain}@students.iiit.net
import time
import random
import os
import threading
from constants import *

import MySQLdb

class DB:
  """Provides an interface to the Database."""
  global agent_types
  
  def __init__(self, iDBInstantiaterId = -1):
    """ Initializes the DB module. Makes a connection to the database whose settings
    are specified in constants.py . If an id (!= -1) is provided, fileDBBuffer is
    not created (used by simulator objects). """
    if iDBInstantiaterId != -1:
      self.fileDBBuffer = open(str(iDBInstantiaterId) + '.dbbuffer', 'w')
    else:
      # on all hosts when simulator objects create db instances.
      self.fileDBBuffer = None
    
    self.lockFileDBBuffer = threading.Lock()
    
    self.conn = MySQLdb.connect(db = DB_NAME, host = DB_HOST, passwd = DB_PASSWD, user = DB_USER)
    self.curs = self.conn.cursor()
    self.updatelist = [] #the thing which contains queries to be updated into db at the end of an iteration
    self.dUpdateListAgent = {}
    self.lstMessages = []
    
  def shutDown(self):
    """Closes the db cursor, file dbBuffer and connection."""
    if not self.curs:
      return
    self.curs.close()
    self.curs = None
    
    self.conn.close()
    self.conn = None
    
    if self.fileDBBuffer:
      self.fileDBBuffer.close()
      self.fileDBBuffer = None

  def createTables(self):
    """Creates the message table and the message index."""
    #self.curs.execute("create table %s(type varchar(32) primary key not null)" %(SQL_TYPESTABLE,))    
    self.curs.execute(SQL_CREATEMESSAGES % (dictSettings[S_SQL_MESSAGETABLE],))
    self.curs.execute(SQL_CREATEMESSAGESINDEX %(dictSettings[S_SQL_MESSAGETABLE],dictSettings[S_SQL_MESSAGETABLE]))
    
  def invalidateCache(self, agtype):
    """invalidates the cached values of aggregate functions for agtype"""
    if not self.isCacheValid(agtype):
      return
    agent_types[agtype]['__cache__']['__valid__'] = None
    
    for i in CACHE_PERTYPE:
      agent_types[agtype]['__cache__'][i] = None
      
    for i in CACHE_PERFIELD:
      for j in agent_types[agtype]['__properties__'].keys():
        agent_types[agtype]['__cache__'][j][i] = None
    
    
  def isCacheValid(self, agtype):
    """Returns whether the cache is valid or not."""
    return agent_types[agtype]['__cache__']['__valid__']
    
  def clearDB(self):
    """Clears the database of ALL the tables.
    The simulation cannot be resumed after this."""
    self.curs.execute('Show tables;')
    ll = self.curs.fetchall()
    for i in ll:
      if 'tr_' not in i[0]:
        self.curs.execute('DROP TABLE ' + i[0] + ';')
    self.createTables()

  def sendMessageSynchronous(self, from_type, from_id, to_type, to_id, simtime, message):
    """This function sends the message from one agent to the another instantly.
    If this is used, the targeted agent will receive the message in the current iteration
    itself."""
    iFromIdType = IdTypeFromIdType(from_type, from_id)
    iToIdType = IdTypeFromIdType(to_type, to_id)
    query =  'INSERT INTO ' +  dictSettings[S_SQL_MESSAGETABLE]
    query += ' VALUES (%(iFromIdType)d, %(iToIdType)d, %(simtime)d, "%(message)s");' %locals()
    self.curs.execute(query)

    
  def sendMessage(self, from_type, from_id, to_type, to_id, simtime, message):
    """This function sends the message to the targeted agent after the current iteration.
    That means that all the messages sent by all the agents will be received only in the
    next iteration. A call to syncMessages should be made when using this."""
    self.lstMessages.append((IdTypeFromIdType(from_type, from_id), IdTypeFromIdType(to_type, to_id), simtime, message))
    return
#     #warning: this code is deprecated
#     #update to new message table format
#     query =  'INSERT INTO ' +  dictSettings[S_SQL_MESSAGETABLE]

#     query += ' VALUES ("%(from_type)s", %(from_id)d, "%(to_type)s", %(to_id)d, %(simtime)d, "%(message)s");' %locals()

#     self.updatelist.append(query)
#     #self.curs.execute(query)
    

  def getMessages(self, agtype, agid):
    """Retrieves the inbox of the agent(agtype,agid).
    If flushing of messages is enabled, the message list is returned and the messages are
    deleted. 
    """
    query = 'SELECT fromIdType, time, message from ' + dictSettings[S_SQL_MESSAGETABLE]
    query += ' where toIdType = %d ; ' % (IdTypeFromIdType(agtype, agid))
    
    rv = self.curs.execute(query)
    lst = list(self.curs.fetchall())
    
    if not dictSettings[S_FLUSHMESSAGES]:
      query = 'DELETE FROM ' + dictSettings[S_SQL_MESSAGETABLE] + ' WHERE toIdType = %d' % (IdTypeFromIdType(agtype, agid))
      self.curs.execute(query)
      
    for i in xrange(len(lst)):
      lst[i] = (TypeFromIdType(lst[i][0]), IdFromIdType(lst[i][0]), lst[i][1], lst[i][2])
    return lst
  
  def readTypes(self):
    """returns a list of all types"""
    return agent_types.keys()
    #self.curs.execute("select * from %s"%(SQL_TYPESTABLE,))
    #return [i[0] for i in self.curs.fetchall()]

  # not called by the api anywhere
  def lockTable(self, table):
    pass
    #self.curs.executecreate('LOCK TABLE ' + table + ' WRITE ;');
    
  def unlockTable(self, table):
    pass
    #self.curs.execute('UNLOCK TABLES;');
    
  # function never called
  def clearUpdates(self):
    """Warning: deprecated. Never called, though designed to reset update list."""
    #TODO: is this function ever called
    self.updatelist = ""

  def readObjects(self, szAgentType, iLowId, iHighId):
    """Reads obects given by agtype and [iLowId, iHighId).
    Returns a list of dictionaries"""

    if not agent_types.has_key(szAgentType):
      return []
    
    curobj = agent_types[szAgentType]['__properties__']
    
    field_list = []
    for i in curobj.keys():    
      field_list.append(i)
      
    szQuery = 'SELECT ' + ','.join(field_list) + ' from ' + szAgentType + ' where id >= ' + str(iLowId) + ' and id < ' + str(iHighId)
    #szQuery = 'SELECT ' + ','.join(field_list) + ' from ' + szAgentType + ' where id = %s' 
    self.curs.execute(szQuery)
    
    lstRetVal = []
    for i in self.curs.fetchall():
      cdict = {}
      for j in xrange(len(field_list)):
        cdict[field_list[j]] = i[j]
      lstRetVal.append(cdict)
      
    return lstRetVal
    
  def readObject(self, agtype, id):
    """READS the object given by agtype and id. assuming all information is correct"""
    #rt = time.time()
    if not agent_types.has_key(agtype) :
      return {}
    
    curobj = agent_types[agtype]['__properties__']
    
    field_list = []
    for i in curobj.keys():    
      field_list.append(i)
    
    
    query = 'SELECT ' + ",".join(field_list) + ' from ' + agtype + ' where id = ' + str(id) + ';'
    ret_count = self.curs.execute(query)
    if ret_count == 0:
      return None

    lst = self.curs.fetchall()
    retval = []
    #for i in lst:
    cdict = {}
    cdict['__type__'] = agtype
    for j in xrange(len(field_list)):
      cdict[field_list[j]] = lst[0][j]
      #retval.append(cdict)    
    return cdict
    
  
  def writeObject(self, agtype, objectdata):
    """Writes the agent data and state of agtype to the database."""
    #warning: do not use syncdbnew. it is not updated to use minimum memory
    #return self.writeObjectold(agtype, objectdata)
    return self.writeObjectold(agtype, objectdata)
  
  
  def writeObjectnew(self, agtype, objectdata):
    """Object data must be a fields dictionary present in the agent class. It ignores any keys not defined initially in the agent specification"""
    #self.invalidateCache(agtype)

    lstUpdateValues = []
    value_list = []
    
    for i in agent_types[agtype]['__properties__'].keys():
      if i == 'id':
        continue
      lstUpdateValues.append(objectdata[i])
      
    if not lstUpdateValues:
      return
    lstUpdateValues.append(objectdata['id'])
    
    if self.dUpdateListAgent.has_key(agtype):
      self.dUpdateListAgent[agtype].append(tuple(lstUpdateValues))
    else:
      self.dUpdateListAgent[agtype] = [tuple(lstUpdateValues)]
      
  def dumpUpdateListToFile(self, lstUpdates):
    """The update list is the list of updates to be executed at the end of iteration.
    It may be very long in case when synchronous writes is disabled(default). This
    functions dumpbs the updates to the secondary storage."""
    self.lockFileDBBuffer.acquire()
    for i in lstUpdates:
        self.fileDBBuffer.write(i + '\n')
    self.fileDBBuffer.flush()    
    self.lockFileDBBuffer.release()
    
    
  def _createWriteObjectQuery(self, agtype, objectdata):
    """ Provides the SQL query to write object to the database."""
    value_list = []
    for i in objectdata.keys():
      if not agent_types[agtype]['__properties__'].has_key(i):
        continue
      if i == 'id':
        continue
      #if i != 'x' and i != 'y':
      #  continue;
      if agent_types[agtype]['__properties__'][i] in TYPE_STRINGTYPES :
        value_list.append(i + '=' + '"%s"' % (objectdata[i],))
      else:
        value_list.append(i + '=' + str(objectdata[i]))

    if not value_list:
      return ""
    query1 = 'update ' + agtype + ' set ' + ','.join(value_list) + ' where id = ' + str(objectdata['id']) + ';'
    return query1
    
  def writeObjectSynchronous(self, szType, dictObjectData):
    """Writes the object immediately"""
    szQuery = self._createWriteObjectQuery(szType, dictObjectData)
    if not szQuery:
      return
    
    self.curs.execute(szQuery)

  def writeObjectold(self, agtype, objectdata):
    """Object data must be a fields dictionary present in the agent class. It ignores any keys not defined initially in the\ agent specification"""
    #self.invalidateCache(agtype)
    query1 = self._createWriteObjectQuery(agtype, objectdata)
    
    if not query1:
      return
    
    if len(self.updatelist) > dictSettings[S_NUMAGENTSTOKEEPINMEMORY] and self.fileDBBuffer:
      lstUpdates = self.updatelist
      self.updatelist = []
      T = threading.Thread(target = self.dumpUpdateListToFile, args = (lstUpdates,))
      T.start()

    self.updatelist.append(query1)

    
  def deleteObject(self,agtype,agId):
    """ deletes the object from the database. """
    query = 'delete from %s where id = %d;' %(agtype, int(agId))
    #try

    self.curs.execute(query)
    
  def getAggregateValue(self, agtype, fn, column):
    """Gets the aggregate value of the agent type 'agtype' by applying the function 'fn'
    over the column 'column'.
    The allowed values of fn are specified in the constants.py as AGGREGATE_*
    """
    
    #todo: err handling code

    if (self.isCacheValid(agtype)):
      if fn in CACHE_PERTYPE:
        if agent_types[agtype]['__cache__'][fn]:
          return agent_types[agtype]['__cache__'][fn]
      else:
        if agent_types[agtype]['__cache__'][column][fn]:

          return agent_types[agtype]['__cache__'][column][fn]

    
    collist = fn % (column,)
    query = 'SELECT ' + collist + ' from ' + agtype + ';'
        
    self.curs.execute(query)
    nv = self.curs.fetchall()[0][0]
    agent_types[agtype]['__cache__']['__valid__'] = 1
    if fn in CACHE_PERTYPE:     
      agent_types[agtype]['__cache__'][fn] = nv
    else:
      agent_types[agtype]['__cache__'][column][fn] = nv
    return nv
    
    
  def writeType(self,typename):
    """warning: Deprecated. Not required, does nothing."""
    return
  #not reguired ever since the dictionary approach worked
  # self.curs.execute("insert into " + SQL_TYPESTABLE + " values (\"%s\")" %(typename,))
    
    
  def insertQueryFromFields(self, agtype, objectdata):
    """Return an insert query given objectdata which is a fields dictionary"""
         
    value_list = []
    field_list = []
    for i in objectdata.keys():
      if not agent_types[agtype]['__properties__'].has_key(i):
        continue
      field_list.append(i)
      if agent_types[agtype]['__properties__'][i] in TYPE_STRINGTYPES:       
        value_list.append('"%s"' % (objectdata[i],))
      else:

        value_list.append(str(objectdata[i]))
    
    fields = ','.join(field_list)
    
    query = 'INSERT INTO ' + str(agtype) + ' ( ' + fields + ' ) ' + ' VALUES (' + ','.join(value_list) + ' );'       

    return query
 
  def syncMessages(self):
    """In case when messages are sent asynchronously (default), a call to this will
    send the messages at the end of the iteration. It is automatically called by
    syncDB."""

    if self.lstMessages == []:
      return
    szQuery = 'INSERT INTO ' + dictSettings[S_SQL_MESSAGETABLE]
    szQuery += ' (fromIdType, toIdType, time, message) '
    szQuery += ' values (%s,%s,%s,%s)'
    

    xrangeIterOver = xrange(0, len(self.lstMessages), 5000)
    for i in xrange(len(xrangeIterOver) - 1):     
      self.curs.executemany(szQuery, self.lstMessages[xrangeIterOver[i]:xrangeIterOver[i + 1]])
    self.curs.executemany(szQuery, self.lstMessages[xrangeIterOver[len(xrangeIterOver) - 1]:])

    self.lstMessages = []
    
  def syncDB(self):
    """Synchronises the db at the end of the iteration. Mandatory if agents update
    or send messages asynchronously."""
    #warning: do not use syncdbnew. it is not updated to use minimum memory
    #return self.syncDBold()
    return self.syncDBold()
  
 
  def syncDBold(self):
    """Synchronises the db at the end of the iteration. Mandatory if agents update
    or send messages asynchronously."""
    self.syncMessages()
    #st = time.time()
    for i in self.readTypes():
      self.invalidateCache(i)



    for i in self.updatelist:
      self.curs.execute(i)


    del self.updatelist
    self.updatelist = []
    
    if not self.fileDBBuffer:
      return
    
    szFileName = self.fileDBBuffer.name

    self.lockFileDBBuffer.acquire()
    self.fileDBBuffer.close()
    fileDBBufferRead = open(szFileName, 'r')
    while 1:
      szCurrentLine = fileDBBufferRead.readline()
      if not szCurrentLine:
        break
      
      szCurrentLine = szCurrentLine[:-1] #removing \n
      self.curs.execute(szCurrentLine)
      
    fileDBBufferRead.close()
    
    self.fileDBBuffer = open(szFileName, 'w')
    self.lockFileDBBuffer.release()

  def syncDBnew(self):
    """Synchronises the db at the end of the iteration. Mandatory if agents update
    or send messages asynchronously.
    Warning: deprecated. Not optimized to use minimum main memory. Use syncDB.
    """
    self.syncMessages()
    #st = time.time()
    for i in self.readTypes():
      self.invalidateCache(i)

    for i in self.dUpdateListAgent.keys():
      szQuery = "update " + str(i) + ' set '
      value_list = []
      for j in agent_types[i]['__properties__']:

        if j == 'id':
          continue
        value_list.append( str(j) + ' = %s ')
      
      szQuery += ','.join(value_list)
      szQuery += ' where id = %s'
      self.curs.executemany(szQuery, self.dUpdateListAgent[i])
      self.dUpdateListAgent[i] = []

    self.updatelist = []
      
  def getAgentsOfType(self, agtype):
    """Returns of a list of all agent ids of type 'agtype'"""
    #st = time.time()
    self.curs.execute('select id from ' + str(agtype) + ';')
    lst = [i[0] for i in self.curs.fetchall()]

    return lst
  
             

                                
                                
    
    
