# This class will contain the behaviour of the opengl
# simulation component

# Parent needs to set the following attribs
# glwindowwidth : width of gl window
# glwindowheight : height of gl window
# both attribs will be used in call to glOrtho

# viewX : translation on X axis
# viewY : translation on Y axis
# both attribs will be used in a call to glTranslatef before glPushMatrix

# default width of window=1010, height=590

from qt import *
from qtgl import *

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

from db import *

import math
import threading
class GLSimulation (QGLWidget):
    def __init__(self, parent=None,name=None, sharewidget=None, fl=0):
        # parentclass will be class which will provide it with the required attribs
        QGLWidget.__init__(self,parent,name,sharewidget,fl)

        #initial values
        self.db = DB()
        self.displaytime  = 0

        self.bViewportCall = False

        self.initX = 0
        self.initY = 0
        self.width = 600
        self.height = 400

        self.viewX = 0
        self.viewY = 0

        self.viewportX = self.initX
        self.viewportY = self.initY
        self.viewportWidth = self.width
        self.viewportHeight = self.height
        self.bDrawing = False
        
    def setOrtho(self, iWidth, iHeight, iX = 0, iY = 0):
        """ decides the coordinates of the end points of the
        opengl window """
        self.initX = iX
        self.initY = iY
        self.width = iWidth
        self.height = iHeight
        if not self.bViewportCall:
            self.viewportX = iX
            self.viewportY = iY
            self.viewportWidth = iWidth
            self.viewportHeight = iHeight

    def setViewport(self, iWidth, iHeight, iX = 0, iY = 0):
        """ This doesnt work as it should.
        Supposed to set the viewport,
        but the call to this is never made """
        self.bViewportCall = True
        self.viewportX = iX
        self.viewportY = iY
        self.viewportWidth = iWidth
        self.viewportHeight = iHeight

    def setCamera(self, viewX=0, viewY=0):
        """ Results in a translation of all objects
        by -viewX , -viewY before they are drawn"""
        self.viewX = viewX
        self.viewY = viewY
      
    def initializeGL(self):
        """ called once, at the time of initializing"""
        glClearColor(0, 0, 0, 1.0)
        # chk this out -> this clears the screen with black whereas in other programs
        # 0.9,0.9,1.0,1.0 clear the screen to black

        glClearDepth(1.0)	
        glDepthFunc(GL_LESS)	
        glEnable(GL_DEPTH_TEST)	
        glShadeModel(GL_SMOOTH)	

        #glViewport(self.viewportX, self.viewportY, self.viewportWidth, self.viewportY)
        #glViewport(0,0, self.width, self.height)
        
        # Reset The Current Viewport And Perspective Transformation

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        glOrtho(self.initX, self.width, self.initY, self.height, 0, 100)
        
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def resizeGL(self,Width,Height):
        """ this is called only the first time widget gets initialized
        this wont be required in this
        because resize wont be possible
        thr is no slot attached corresponding to the resize event """
        return
    
    def drawGLScene(self):
        
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        print "Drawglscene 1"
        
        if ( not (self.displaytime % 100 )):
            self.types_list = self.db.readTypes()
            
        self.displaytime += 1
        
        glTranslatef(-self.viewX, -self.viewY,0)

        print "translated"
        for i in self.types_list:
            ll = self.db.getAgentsOfType(i)
            for j in ll:
                self.drawObject(i, j)


        self.bDrawing = False
        print "Exiting drawGL"
        #self.evRunOnce.set()

        

    def paintGL(self):
        """ actual drawing of objects """
        print "Entereing paintGL"
        if self.bDrawing == True:
            print "Drawing was true so quit"
            return
        
        
        self.bDrawing = True
        threadDrawGL = threading.Thread(target = self.drawGLScene)
        threadDrawGL.start()
        #self.drawGLScene()
        
        
    def reinitializeGL(self):
        self.initializeGL()

    def drawSquare(self,size):
        glBegin(GL_POLYGON)
        glVertex2d(-size,-size)
        glVertex2d(size,-size)
        glVertex2d(size,size)
        glVertex2d(-size,size)
        glEnd()
        
    def drawCircle(self,size):
        glBegin(GL_TRIANGLE_FAN)
        glVertex2d(0,0)
        for i in xrange(0,370,10):
            glVertex2f(math.cos(i * math.pi/180.0) * size, math.sin(i * math.pi/180.0) * size)
        glEnd()
        
    def drawTriangle(self,size):
        glPushMatrix()
        glRotatef(-90,0,0,1)
        
        glBegin(GL_TRIANGLES)
        glVertex2d(-size,-size/2)
        glVertex2d(size,-size/2)
        glVertex2d(0,size/2)
        glEnd()
        
        glPopMatrix()
        
    def drawObject(self,type,id):
        obj = self.db.readObject ( type, id ) # obj is a dict
        if not obj:
            return

        glPushMatrix()

        glTranslatef(obj["x"], obj["y"] , 0)
        glRotatef(math.degrees(obj["theta"]), 0, 0, 1)        
        color = int2RGB ( obj["color"] )

        glColor3f(color[0]/255.0, color[1]/255.0,color[2]/255.0)
        
        if ( obj["shape"] == SHAPE_SQUARE ):
            self.drawSquare(obj["size"])
            
        elif ( obj["shape"] == SHAPE_CIRCLE ):
            self.drawCircle ( obj["size"] )
        
        elif ( obj["shape"] == SHAPE_TRIANGLE ):
            self.drawTriangle(obj["size"])
            
        elif ( obj["shape"] == SHAPE_USER ):
            pass
            #agent_types[type]["__renderfunc__"](obj)
            
        else:
            print "ERROR.. cannot identify the shape of object"
        
        glPopMatrix()
 
    
