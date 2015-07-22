import logging

DB_NAME = 'traffic'
DB_USER = 'traffic'
DB_PASSWD = 'traffic123'
DB_HOST = 'localhost'

SCHEDULER_STATIC = 'static'
SCHEDULER_DYNAMIC = 'dynamic'

S_NUMAGENTSTOKEEPINMEMORY = 's_numagentstokeepinmemory'#10000
S_NUMAGENTSTOFETCHATONCE = 's_numagentstofetchatonce'#10000
S_FLUSHMESSAGES = 's_flushmessages'#True
S_SYNCHRONOUSWRITES = 's_synchronouswrites'#False
S_SQL_MESSAGETABLE = 's_sql_messagetable'
S_LOCALINTERFACEIP = 's_localip'
S_DRAWAGENTMODE = 's_drawagentmode'
S_DRAWAGENTMODEREDRAWTIME = 's_drawagentrefreshiter'

dictSettings = {}
dictSettings[S_DRAWAGENTMODEREDRAWTIME] = 10
dictSettings[S_DRAWAGENTMODE] = False
dictSettings[S_LOCALINTERFACEIP] = '172.16.9.15'
dictSettings[S_SQL_MESSAGETABLE] = "m_messages_wumpus"
dictSettings[S_SYNCHRONOUSWRITES] = False
dictSettings[S_FLUSHMESSAGES] = True
dictSettings[S_NUMAGENTSTOFETCHATONCE] = 10000 #these many agents are fetched in
# one query from the database. In case of sufficient main memory, the value can be set
# very high, (approx. 10,000,000 for 512 MB RAM with agents with only default properties
dictSettings[S_NUMAGENTSTOKEEPINMEMORY] = 10000
# These many agents are kept in main memory, rest are flushed onto the secondary storage.
# In case of sufficient main memory, this value can be set high as previous one.

LOG_LEVEL = logging.DEBUG

BLOGGING_DISABLED = True#False#True #False (boolean - Logging disabler)
AGGREGATE_SUM = " SUM(%s) " #Aggregate queries supported by the system.
AGGREGATE_AVG = " AVG(%s) "
AGGREGATE_MAX = " MAX(%s) "
AGGREGATE_MIN = " MIN(%s) "
AGGREGATE_COUNT = " COUNT(%s) "
TEMP_PORT = 2000 # default port on which the server tries to connect to the host
#PERFIELD are the values that are cached for each field of an agent type
CACHE_PERFIELD = [AGGREGATE_AVG, AGGREGATE_MAX, AGGREGATE_MIN, AGGREGATE_SUM]
# It caches the values of the above mentioned functions and sets cache as corrupted
# if any of the tuples in the associated fields is updated.
CACHE_PERTYPE = [AGGREGATE_COUNT]
# It caches the values of the above mentioned functions and sets cache is corrupted
# if any agent is added or deleted

agent_types = {}
world_handler = None;

# The following datatypes are allowed
# A new type can be added here, with the associated sql syntax
# for example TYPE_DATE = 'date default null'

TYPE_INTEGER = 'integer default 0 not null'
TYPE_STRING = 'char(255) default NULL '
TYPE_FLOAT = 'float default 0 not null'
TYPE_LSTRING = 'text default NULL '

# The string types need to handled separately because of requirement of double
# quotes '"' in SQL queries. This list is the list of all string types.
# In case a new type is added, add it here if it requires '"' in SQL queries.
TYPE_STRINGTYPES = [TYPE_STRING, TYPE_LSTRING]

# This is the SQL query used to create message table. The name of the message table
# is specified in dictSettions[S_SQL_MESSAGETABLE]
# Query needs to be changed if MySQL changes it syntax or another DB is used.

SQL_CREATEMESSAGES = """
CREATE TABLE %s (fromIdType integer,
toIdType integer,
time integer, 
message varchar(255));""" 

# creates index for the message table
SQL_CREATEMESSAGESINDEX = """CREATE INDEX idx_%s ON %s (toIdType);""" 

# Return codes, State_Ok and ErrorCodes
S_OK = 0
ERR_INVALIDTYPE = 1
ERR_DBERR = 2
SUCCESS = 1
FAILURE = 0

# Shapes that the GUI will draw.
SHAPE_USER = 0 # user can supply a render function stored in agent types __renderfunc__
SHAPE_TRIANGLE = 1
SHAPE_CIRCLE = 2
SHAPE_SQUARE = 3

# Colors allowed by the system.

# r,g,b values need be positive integers in [0,255]
def RGB(r,g,b):
  return (r<<16)|(g<<8)|b

COLOR_BLACK = RGB(0,0,0)
COLOR_WHITE = RGB(255,255,255)

COLOR_BLUE = RGB(0,0,255)
COLOR_GREEN = RGB(0,255,0)
COLOR_RED = RGB(255,0,0)

COLOR_YELLOW = RGB(255,255,0)

COLOR_GRAY = RGB(100, 100, 100)

# the least significant 24bits of a 32bit integer are used in the following manner
# to determine the specified color.
def int2RGB(cval): 
  red = cval >> 16 # 11111111 00000000 00000000
  green = (cval & (255 << 8)) >> 8 #00000000 11111111 00000000
  blue = cval & 255 # 00000000 00000000 11111111  
  return ( red, green,blue)

def IdFromIdType(iIdType):
  """Find the ID or an agent. An agent is identified in 32 bits as 4-bit TYPE
  and then 28-bit ID. This function finds out the ID."""
  return iIdType & 0x0FFFFFFF

def TypeFromIdType(iIdType):
  """Find the ID or an agent. An agent is identified in 32 bits as 4-bit TYPE
  and then 28-bit ID. This function finds out the Type."""
  iType = iIdType >> 28
  for iLoop in agent_types.keys():
    if agent_types[iLoop]['__TypeId__'] == iType:
      return iLoop
  
def IdTypeFromIdType(szType, iId):
  """Finds out the 32 bit representation of the agent from its ID and Type.
  An agent is identified in 32 bits as 4-bit TYPE and then 28-bit ID."""
  
  return (agent_types[szType]['__TypeId__'] << 28) | iId

# States in which the hosts can be
S_READY = "Ready"
S_SIMULATING = "Simulating"
S_SYNCDB = "Syncing DB"
S_QUIT = "Quitting"
E_UNKNOWN = "Unknown Error"
S_INITIALIZING = "Initializing Connection to Client"
E_UNABLETOCONNECT = "Unable to Connect"
E_UNABLETOTRANSFER = "Unable to Transfer files"
E_UNABLETOREVCONNECT = "Unable to reverse connect"

# Commands sent over to the hosts.
# CMD_* cannot be more than 16 chars in length
CMD_SIMULATE = "SIM"
CMD_UPDATEDB = "UPDATEDB"
CMD_UPDATESIMENV = "UPDATESIMENV"
CMD_ACK_UPDATESIMENV = "UPDATESIMENVCOMPLETE"
CMD_GLOBALSCHANGED = "GLOBALSCHANGED"
CMD_ACK_GLOBALSCHANGED = "ACKGLOBALSCHANGED"
CMD_ACK_SIMULATE = "SIM COMPLETE"
CMD_ACK_UPDATEDB = "UPDATEDB COMPLETE"
CMD_QUIT = "QUIT"
CMD_ACK_QUIT = "QUIT COMPLETE"


  
