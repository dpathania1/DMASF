from api import *
import random

class CGlobalVariables:
  def setGlobals(self, dictValues):
    self.__dict__ = dictValues


class defworldhandler:
  """The default world handler. The user should overload the relevant functions to
  define the environment behaviour."""
  globalData =  CGlobalVariables()
  def begin(self, apiInstance):
    """apiinstance is the instance of the api so that agents can be created, etc."""
    pass
  
  def beginUpdate(self,simtime, apiInstance):
    """This function is called at the beginning of each iteration. If this function returns True it means\
    that the global variables in the simulation have been changed.
    """
    pass
  
  def endUpdate(self,simtime,apiInstance):
    """This function is called at the end of each iteration."""
    return False
  
  def end(self, apiInstance):
    """This function is called at the end of the simulation."""
    pass
  

  
