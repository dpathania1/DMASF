from mas_framework import *
import random
import sys
import pickle
import math

def drawHelicopter(obj):
  # size = obj["size"]
  glBegin(GL_POLYGON)
  glVertex2d(0,0)
  glVertex2d(0,10)
  glVertex2d(10,10)
  glVertex2d(25,15)
  glVertex2d(30,25)
  glVertex2d(45,25)
  glVertex2d(60,10)
  glVertex2d(75,10)
  glVertex2d(85,25)
  glVertex2d(85,-10)
  glVertex2d(10,-10)
  glEnd()

  glBegin(GL_POLYGON)
  glVertex2d(25,-10)
  glVertex2d(25,-20)
  glVertex2d(10,-25)
  glVertex2d(60,-25)
  glVertex2d(60,-20)
  glVertex2d(55,-10)
  glEnd()

  glBegin(GL_LINE)
  glVertex2d(37,25)
  glVertex2d(37,35)
  glEnd()

  glBegin(GL_LINE)
  glVertex2d(20,35)
  glVertex2d(55,35)
  glEnd()

  glBegin(GL_LINE)
  glVertex2d(33,30)
  glVertex2d(41,40)
  glEnd()

  
def drawRV(obj):

  glPushMatrix()
  # size = obj["size"]
  glBegin(GL_POLYGON)
  glVertex2d(0,0)
  glVertex2d(0,15)
  glVertex2d(20,20)
  glVertex2d(30,40)
  glVertex2d(50,40)
  glVertex2d(70,15)
  glVertex2d(70,0)
  glEnd()

  color = int2RGB( COLOR_BLACK )
  glColor3f(color[0]/255.0,color[1]/255.0,color[2]/255.0)
  
  glBegin(GL_POLYGON)
  glVertex2d(10,0)
  glVertex2d(25,0)
  glVertex2d(20,-10)
  glVertex2d(15,-10)
  glEnd()

  glTranslatef(30,0,0)
  glBegin(GL_POLYGON)
  glVertex2d(10,0)
  glVertex2d(25,0)
  glVertex2d(20,-10)
  glVertex2d(15,-10)
  glEnd()
  glPopMatrix()

def drawSmoke(obj):
  size = obj["size"]
  glPushMatrix()
  glBegin(GL_TRIANGLE_FAN)
  glVertex2d(0,0)
  for i in xrange(0,370,10):
    glVertex2f(math.cos(i * math.pi/180.0) * size, math.sin(i * math.pi/180.0) * size)
  glEnd()

  glTranslatef(-size,-10,0)
  glBegin(GL_TRIANGLE_FAN)
  glVertex2d(0,0)
  for i in xrange(0,370,10):
    glVertex2f(math.cos(i * math.pi/180.0) * size, math.sin(i * math.pi/180.0) * size)
  glEnd()
  glPopMatrix()

  glPushMatrix()
  glTranslatef(size,-10,0)
  glBegin(GL_TRIANGLE_FAN)
  glVertex2d(0,0)
  for i in xrange(0,370,10):
    glVertex2f(math.cos(i * math.pi/180.0) * size, math.sin(i * math.pi/180.0) * size)
  glEnd()
  glPopMatrix()

  glPushMatrix()
  glTranslatef(0,-20,0)
  glBegin(GL_TRIANGLE_FAN)
  glVertex2d(0,0)
  for i in xrange(0,370,10):
    glVertex2f(math.cos(i * math.pi/180.0) * size, math.sin(i * math.pi/180.0) * size)
  glEnd()
  glPopMatrix()


class WH(defworldhandler):
  def begin(self):
    global api
    api.createAgent('helicopter', {'shape': SHAPE_USER, 'color' : COLOR_BLUE, 'smokes': pickle.dumps([]), 'size' : 20, 'x' : 1100, 'y': 1100})
    api.createAgent('helicopter', {'shape': SHAPE_USER, 'color' : COLOR_BLUE, 'smokes': pickle.dumps([]), 'size' : 20, 'x' : 200, 'y': 300})
    color_rv = RGB(200,200,200)
    api.createAgent('rv', {'shape' : SHAPE_USER, 'color' : color_rv, 'smkid' : pickle.dumps([]), 'x' : 100, 'y' : 100, 'size': 20})                
    api.createAgent('rv', {'shape' : SHAPE_USER, 'color' : color_rv, 'smkid' : pickle.dumps([]), 'x' : 500, 'y' : 500, 'size': 20})                
    api.createAgent('rv', {'shape' : SHAPE_USER, 'color' : color_rv, 'smkid' : pickle.dumps([]), 'x' : 900, 'y' : 900, 'size': 20})                
    api.createAgent('rv', {'shape' : SHAPE_USER, 'color' : color_rv, 'smkid' : pickle.dumps([]), 'x' : 400, 'y' : 400, 'size': 20})                
    api.createAgent('rv', {'shape' : SHAPE_USER, 'color' : color_rv, 'smkid' : pickle.dumps([]), 'x' : 900, 'y' : 100, 'size': 20})                
    api.createAgent('rv', {'shape' : SHAPE_USER, 'color' : color_rv, 'smkid' : pickle.dumps([]), 'x' : 100, 'y' : 900, 'size': 20})
    self.spawnSmoke(0, api)
    self.spawnSmoke(0, api)
    self.spawnSmoke(0, api)
    self.spawnSmoke(0, api)
    self.spawnSmoke(0, api)
    self.spawnSmoke(0, api)

  def spawnSmoke(self, st, api):
    fields  = {}
    fields['starttime'] = st
    fields['ttl'] = random.randint(40, 60)
    fields['x'] = random.randint(100, 1200)
    fields['y'] = random.randint(100, 1100)
    fields['size'] = 20
    fields['color'] = RGB(120,120,120)
    fields['shape'] = SHAPE_USER
    assert(isinstance(api, API))
    api.createAgent('smoke', fields)
   
    
  def endUpdate(self, simtime, api):
    # print "Simtime:", simtime
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
api.restartSimulation()
api.registerAgentType("smoke", SMOKE, drawSmoke, {"starttime": TYPE_INTEGER, "ttl" : TYPE_INTEGER})
api.registerAgentType('helicopter', HELICOPTER, drawHelicopter, {"smokes" : TYPE_STRING})
api.registerAgentType('rv', RESCUEVEHICLE, drawRV, {'smkid': TYPE_LSTRING})

api.registerWorldHandler(WH)

api.setDrawAllFlag(True)
api.Initialize()
