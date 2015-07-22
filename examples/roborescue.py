from mas_framework import *
import random
import sys
import pickle

class WH(defworldhandler):
  def spawnSmoke(self, st, api):
    fields  = {}
    fields['starttime'] = st
    fields['ttl'] = random.randint(40, 60)
    fields['x'] = random.randint(100, 1000)
    fields['y'] = random.randint(100, 1000)
    fields['size'] = 40
    fields['color'] = COLOR_GRAY
    fields['shape'] = SHAPE_SQUARE
    assert(isinstance(api, API))
    api.createAgent('smoke', fields)
   
    
  def endUpdate(self, simtime, api):
    if (not simtime % 10):
      self.spawnSmoke(simtime, api)
    self.killSmokes(simtime, api)
      
  def killSmokes(self, simtime, api):
    assert(isinstance(api, API))
    for i in api.db.getAgentsOfType('smoke'):     
      fd = api.db.readObject('smoke', i)
      if simtime > fd['ttl'] + fd['starttime']:
        api.killAgent('smoke', i)


class SMOKE(defagenthandler):
  def update(self, simtime):
    if self.getMessages():
      self.kill()
    return

  
class RESCUEVEHICLE(defagenthandler):
  
  def move(self):
    if self.tx == -1:
      return 0
    speed = 5.0
    dist = math.sqrt((self.tx - self.fields['x']) ** 2 + (self.ty - self.fields['y']) ** 2)
    self.fields['x'] += (self.tx - self.fields['x']) * speed / dist
    self.fields['y'] += (self.ty - self.fields['y']) * speed / dist
    if (dist < 5):
      self.sendMessage('smoke', self.smid, "DIE")
    return 1
  
  def update(self, simtime):
    assert(isinstance(self.db, DB))
    msgs = self.getMessages()

    cdist = 100000000
    cobj = None
    self.tx = -1
    self.ty = -1
    self.smid = -1
    
    known_smokes = pickle.loads(self.fields['smkid'])
    ks = []
    if known_smokes:     
      
      for i in known_smokes:
        cobj = self.db.readObject('smoke', i)
        if cobj:      
          ks.append(i)
          stdist = math.sqrt((cobj['x'] - self.fields['x']) ** 2 + (cobj['y'] - self.fields['y']) ** 2)
          if (stdist < cdist):
            cdist = stdist
            self.tx = cobj['x']
            self.ty = cobj['y']
            self.smid = i        

    for i in msgs:
      ks.append(int(i[3]))
        
    self.fields['smkid'] = pickle.dumps(ks)
    self.move()
    self.writeState()
 

class HELICOPTER(defagenthandler):
  def update(self, simtime):
    assert(isinstance(self.db, DB))
    l1 = self.db.getAgentsOfType('smoke')
    smoke_list = pickle.loads(self.fields['smokes'])

    rvlst = self.db.getAgentsOfType('rv')
    
    for i in l1:
      if i in smoke_list:
        continue
      
      for k in rvlst:
        self.sendMessage('rv', k, i)
        
    self.fields['smokes'] = pickle.dumps(l1)
    self.writeState()
    

api = api.API()
api.db.clearDB()
api.registerAgentType("smoke", SMOKE, None, {"starttime": TYPE_INTEGER, "ttl" : TYPE_INTEGER})
api.registerAgentType('helicopter', HELICOPTER, None, {"smokes" : TYPE_STRING})
api.registerAgentType('rv', RESCUEVEHICLE, None, {'smkid': TYPE_LSTRING})

api.createAgent('helicopter', {'shape': SHAPE_TRIANGLE, 'color' : COLOR_BLUE, 'smokes': pickle.dumps([]), 'size' : 20, 'x' : 1100, 'y': 1100})
api.createAgent('rv', {'shape' : SHAPE_CIRCLE, 'color' : COLOR_GREEN, 'smkid' : pickle.dumps([]), 'x' : 100, 'y' : 100, 'size': 20})                
api.createAgent('rv', {'shape' : SHAPE_CIRCLE, 'color' : COLOR_GREEN, 'smkid' : pickle.dumps([]), 'x' : 500, 'y' : 500, 'size': 20})                
api.createAgent('rv', {'shape' : SHAPE_CIRCLE, 'color' : COLOR_GREEN, 'smkid' : pickle.dumps([]), 'x' : 900, 'y' : 900, 'size': 20})                
api.createAgent('rv', {'shape' : SHAPE_CIRCLE, 'color' : COLOR_GREEN, 'smkid' : pickle.dumps([]), 'x' : 400, 'y' : 400, 'size': 20})                
api.createAgent('rv', {'shape' : SHAPE_CIRCLE, 'color' : COLOR_GREEN, 'smkid' : pickle.dumps([]), 'x' : 900, 'y' : 100, 'size': 20})                
api.createAgent('rv', {'shape' : SHAPE_CIRCLE, 'color' : COLOR_GREEN, 'smkid' : pickle.dumps([]), 'x' : 100, 'y' : 900, 'size': 20})                


api.registerWorldHandler(WH)

api.start1()
