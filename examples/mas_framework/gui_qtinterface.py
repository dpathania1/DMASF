# This class is inherited from qtgui class and has the code
# for the behaviour of the form defined in qtqui.py

from qt import *
from gui_addclient import *

#from gui_qgl import *
from new_gui import *

from gui import *

import threading

class UI(serverUI):
    def __init__ (self,objUIinstance, parent = None, name=None, fl=0):
        serverUI.__init__(self,parent,name,fl)
        
        self.UIInstance = objUIinstance
        
        self.newclient = addclient(self)

        self.opengl = GUI()

        self.tOpenglThread = threading.Thread ( target = self.opengl.initWindow )

        #self.glwindowwidth = self.windowwidth - 10
        #self.glwindowheight = self.windowheight - 145

        #self.openglwindow = GLSimulation(self.openglFrame)
        #self.openglwindow.setGeometry(QRect(5,5,self.glwindowwidth,self.glwindowheight))

        #self.openglwindow.setOrtho(2*self.glwindowwidth,2*self.glwindowheight)

        self.newclient = addclient(self)

        self.running = False

        #connections
        self.connect(self.add, SIGNAL("clicked()"), self.addClicked)
        self.connect(self.delete, SIGNAL("clicked()"), self.deleteClicked)

        self.connect(self.up, SIGNAL("clicked()"),self.upClicked)
        self.connect(self.down, SIGNAL("clicked()"),self.downClicked)
        self.connect(self.left, SIGNAL("clicked()"),self.leftClicked)
        self.connect(self.right, SIGNAL("clicked()"),self.rightClicked)
        
        self.connect(self.zoomin, SIGNAL("clicked()"),self.zoominClicked)
        self.connect(self.zoomout, SIGNAL("clicked()"),self.zoomoutClicked)
        
        self.connect(self.play, SIGNAL("clicked()"),self.playClicked)
        self.connect(self.stop, SIGNAL("clicked()"),self.stopClicked)

        self.connect(self.record, SIGNAL("clicked()"),self.recordClicked)
        #-----------
        
    def deleteClicked(self):
        if ( self.listofclients.currentItem() != -1):
            if self.UIInstance.deleteHost(self.listofclients.currentItem()== SUCCESS ):
                self.listofclients.removeItem(self.listofclients.currentItem() )
                
    def addClicked(self):
        #function called when addclient is clicked
        self.newclientadded = False
        self.newclientaddress = ""
        self.newclientport = -1
        self.newclient.show()

    def addItem(self):
        if self.newclientadded:
            if self.UIInstance.addHost('UnnamedSim', str(self.newclientaddress), int(str(self.newclientport))) == SUCCESS:
                print 'adding host'
                self.listofclients.insertItem(str(self.newclientaddress) + ":" + str(self.newclientport))

    def setsimstate(self,state):
        self.simstate.setText(state)

    def upClicked(self):
        self.opengl.viewY -= 10
        
    def downClicked(self):
        self.opengl.viewY += 10

    def leftClicked(self):
        self.opengl.viewX += 10

    def rightClicked(self):
        self.opengl.viewX -= 10

    def zoominClicked(self):
        self.opengl.width -= 25
        self.opengl.height = self.openglwindow.width * self.glwindowheight/self.glwindowwidth
        self.opengl.reinitializeGL()
    
    def zoomoutClicked(self):
        self.opengl.width += 25
        self.opengl.height = self.openglwindow.width * self.glwindowheight/self.glwindowwidth
        self.opengl.reinitializeGL()

    def playClicked(self):
        print "play has been clicked"
        
        if not self.running:
            if self.UIInstance.canStartSim():
                print 'starting sim'
                self.UIInstance.startSim()
                self.tOpenglThread.start()
                self.running = True


    def stopClicked(self):
        self.timerstate = False

        self.opengl.bStopUpdating = True
        # self.openglwindow.timer.stop()

    def recordClicked(self):
        return
    
    def closeEvent(self, qCloseEvent):
        print "Close clicked"
        self.UIInstance.quit()
        self.opengl.killGL()
        QWidget.closeEvent(self,qCloseEvent)
        print "Quit API, GL and QT"
        
    def updateGL(self):
        # if self.openglwindow.bDrawing == True:
        #     return
        self.opengl.update()

    def addDrawAgent(self, type, id):
        self.opengl.addDrawAgent(type,id)

    def deleteDrawAgent(self, type, id):
        self.opengl.deleteDrawAgent(type, id)

    def setDrawAllFlag(self, bFlag):
        self.opengl.setDrawAllFlag(bFlag)
