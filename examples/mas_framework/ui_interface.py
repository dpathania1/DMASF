from constants import *
from qt import *

from gui_qtinterface import *

import sys
import threading

class UIInterface:
    """This class acts as an interface between the UI classes and the main API class."""
    def __init__(self, api, bLaunchGUI = True):
        """initializes, creates a different thread for the GUI if bLaunchGUI is true"""
        print "bLaunchGUI: ",
        print bLaunchGUI

        self.bLaunchGUI = bLaunchGUI
        
        self.api = api
        # self.gui = None
        if bLaunchGUI:

            self.updateGLThread = threading.Thread(target = self.updateGL)
            self.evUpdateGL = threading.Event()
            self.evUpdateGL.clear()
            
            self.app = QApplication(sys.argv)
            self.objUI = UI(self)
            self.objUI.show()
            self.app.setMainWidget(self.objUI)
            self.api.MainLoopThread.start()
            self.updateGLThread.start()
        else:
            self.api.evStartSim.set()
            self.api.start()

    def addHost(self, simname, host, port):
        #WARNING: simname is now taken by default ...
        return self.api.addHost(str(host), int(port))

    def deleteHost(self, iHostIndex):
        return self.api.deleteHost(iHostIndex)

    def canStartSim(self):
        print self.api.canStartSim()
        return self.api.canStartSim()

    def startSim(self):
        self.api.startSim()

    def updateUI(self, simtime = 0):        
        if dictSettings[S_DRAWAGENTMODE] and \
        (not simtime % dictSettings[S_DRAWAGENTMODEREDRAWTIME]) and \
        agent_types.has_key('__draw__'):
            #WARNING: optimize this...
            self.objUI.opengl.lstDrawAgentData = self.api.db.readObjects('__draw__', agent_types['__draw__']['__minId__'], agent_types['__draw__']['__maxId__'])
              
            
            
        if self.bLaunchGUI :
            self.objUI.updateGL()
            #self.evUpdateGL.set()

    def updateGL(self):
        while not self.api.bSimDone():
            self.evUpdateGL.wait()
            self.evUpdateGL.clear()
            self.objUI.updateGL()
    
    def quit(self):
        print "exiting api"
        self.api.exit()

    def addDrawAgent(self, type, id):
        self.objUI.addDrawAgent(type, id)

    def deleteDrawAgent(self, type, id):
        self.objUI.deleteDrawAgent(type, id)

    def setDrawAllFlag(self, bFlag):
        self.objUI.setDrawAllFlag(bFlag)
