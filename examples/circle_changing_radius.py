from mas_framework import *
import random
import math


class WH(defworldhandler):
  def begin(self, api):

    #Initializing the global variable in the begin function
    #The global variable will be called rad (radius) and its inital value is 10 units
    self.globalData.rad = 10

    #Creating agents ...
    for i in xrange(10):
      ff = {}
      ff['x'] = random.randint(0, 100)
      ff['y'] = random.randint(0, 100)
      ff['size'] = 10
      ff['move'] = random.randint(0, 1)
      ff['shape'] = SHAPE_TRIANGLE
      api.createAgent("test", ff)

  def beginUpdate(self, simtime, api):
    #Every 10 iterations increment the radius by ten units
    #NOTE that the beginUpdate returns True when the global variable has changed
    #so that the changes are sent to each SIMULATOR
    if not simtime % 10:
      self.globalData.rad += 10
      return True

    #Returns False when no change to the global variables.
    return False

class CIRCLE(defagenthandler):
  def update(self, simtime):
    #Here, we are acccesing the global variable rad ...
    #NOTE that an agent cannot change global variables.
    rad = self.globalData.rad
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

    #General printing to check that it works - the agent with id 2 will print the radius\
    #and iteration number. The radius will increase by 10 every 10 iterations
    if self.fields['id'] == 2:
      print simtime, rad


api = api.API()
api.setSimName('circleap')
api.setDrawAllFlag(True)
api.restartSimulation()

api.registerAgentType("test", CIRCLE, None, {})

api.registerWorldHandler(WH)

api.Initialize()
