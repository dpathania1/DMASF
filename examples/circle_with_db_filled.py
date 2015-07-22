from mas_framework import *
import random
import math


class WH(defworldhandler):
  def begin(self):
    return
    global api
    for i in xrange(1000):
      ff = {}
      ff['x'] = random.randint(0, 100)
      ff['y'] = random.randint(0, 100)
      ff['size'] = 10
      ff['move'] = random.randint(0, 1)
      ff['shape'] = SHAPE_TRIANGLE
      api.createAgent("test", ff)    

class CIRCLE(defagenthandler):
  def update(self, simtime):
    rad = 100
    speed = 0.2
    assert(isinstance(self.db, DB))
    cx = self.db.getAggregateValue('test', AGGREGATE_AVG, 'x')
    cy = self.db.getAggregateValue('test', AGGREGATE_AVG, 'y')

    theta = math.atan2(self.fields['y'] - cy, self.fields['x'] - cx)
    theta+= 0.1
    
    targetx = rad * math.cos(theta) + cx
    targety = rad * math.sin(theta) + cy
    
    self.fields['x'] += speed * (targetx - self.fields['x'])
    self.fields['y'] += speed * (targety - self.fields['y'])
    self.writeState()

api = api.API()

#api.restartSimulation()

api.registerAgentType("test", CIRCLE, None, {})

api.registerWorldHandler(WH)

api.Initialize()
