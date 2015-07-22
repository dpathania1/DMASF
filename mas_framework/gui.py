#!/usr/bin/env python

#
# This code was created by Richard Campbell '99 (ported to Python/PyOpenGL by John Ferguson 2000)
#
# The port was based on the PyOpenGL tutorial module: dots.py  
#
# If you've found this code useful, please let me know (email John Ferguson at hakuin@voicenet.com).
#
# See original source and C based tutorial at http://nehe.gamedev.net
#
# Note:
# -----
# This code is not a good example of Python and using OO techniques.  It is a simple and direct
# exposition of how to use the Open GL API in Python via the PyOpenGL package.  It also uses GLUT,
# which in my opinion is a high quality library in that it makes my work simpler.  Due to using
# these APIs, this code is more like a C program using function based programming (which Python
# is in fact based upon, note the use of closures and lambda) than a "good" OO program.
#
# To run this code get and install OpenGL, GLUT, PyOpenGL (see http://www.python.org), and PyNumeric.
# Installing PyNumeric means having a C compiler that is configured properly, or so I found.  For 
# Win32 this assumes VC++, I poked through the setup.py for Numeric, and chased through disutils code
# and noticed what seemed to be hard coded preferences for VC++ in the case of a Win32 OS.  However,
# I am new to Python and know little about disutils, so I may just be not using it right.
#
# BTW, since this is Python make sure you use tabs or spaces to indent, I had numerous problems since I 
# was using editors that were not sensitive to Python.
#
import time
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from constants import *
from db import *
import sys
import math
import pickle

ESCAPE = '\033'

# Some api in the chain is translating the keystrokes to this octal string
# so instead of saying: ESCAPE = 27, we use the following.

class GUI:
    def __init__ (self, width = 1600, height= 1200, resX = 640, resY = 480, windowname="MAS Simulation"):
        self.db = DB()
        assert isinstance ( self.db, DB )
        self.width = width
        self.height = height
        self.resX = resX
        self.resY = resY
        self.windowname = windowname
        self.displaytime = 0
        self.types_list = []
    
        self.viewX = 0
        self.viewY = 0

        self.window = None
        
        # self.bDrawing = False
        self.bDrawAllFlag = True
        self.lstDrawAgents = []
                
        self.lstDrawAgentData = [] #Contains the agents that need to be drawn for the DrawAgent Mode

        self.bUpdateNow = True

        self.bStopUpdating = False
        
    def killGL(self):
        if self.window==None:
            return
        glutDestroyWindow(self.window)
        
    def initGL(self):
        glClearColor(0.0, 0.0, 0.0, 0.0) # 

        glClearDepth(1.0)	
        glDepthFunc(GL_LESS)	
        glEnable(GL_DEPTH_TEST)	
        glShadeModel(GL_SMOOTH)	
        
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()	
        # Calculate The Aspect Ratio Of The Window
        glOrtho(0, self.width, 0, self.height, 0, 100)    
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        

        # The function called when our window is resized (which shouldn't happen if you enable fullscreen, below)
    def ReSizeGLScene(self, Width, Height):
        if Height == 0:						# Prevent A Divide By Zero If The Window Is Too Small 
            Height = 1
        
        self.resX = Width
        self.resY = Height
        glViewport(0, 0, self.resX, self.resY)		# Reset The Current Viewport And Perspective Transformation
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, self.width, 0, self.height, 0, 100)    
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
    def drawSquare(self,size):
        glBegin(GL_POLYGON)
        glVertex2d(0,0)
        glVertex2d(0,size)
        glVertex2d(size,size)
        glVertex2d(size,0)
        glEnd()
        
#glVertex2d(-size,-size)
#       glVertex2d(size,-size)
#       glVertex2d(size,size)
#       glVertex2d(-size,size)
    def drawCircle(self,size):
        glBegin(GL_TRIANGLE_FAN)
        glVertex2d(0,0)
        for i in xrange(0,370,10):
            glVertex2f(math.cos(i * math.pi/180.0) * size, math.sin(i * math.pi/180.0) * size)
        glEnd()
        
    def drawTriangle(self,size):
        glPushMatrix()
        # glRotatef(-90,0,0,1)
        
        glBegin(GL_TRIANGLES)
        glVertex2d(0,0)
        glVertex2d(size,0)
        glVertex2d(size/2,size)
#glVertex2d(-size,-size/2)
#       glVertex2d(size,-size/2)
#       glVertex2d(0,size/2)
        glEnd()
        
        glPopMatrix()
    
    def drawObjectWithoutRead(self, type, obj):
        glPushMatrix()

        glTranslatef(obj["x"], obj["y"] , obj["z"])
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
            #pass
            agent_types[type]["__renderfunc__"](obj)

        else:
            print "ERROR.. cannot identify the shape of object"
        
        glPopMatrix()
        
    
    def drawObject(self,type,id):
        # print "Drawing object: "+ type + " " + str(id)
        obj = self.db.readObject ( type, id ) # obj is a dict
        if not obj:
            return
        self.drawObjectWithoutRead(type, obj)
        
    def drawGLSceneDrawAgentMode(self):
        for i in self.lstDrawAgentData:
            self.drawObjectWithoutRead('__draw__', i)
        return
    
    def drawGLSceneGeneral(self):
        if self.bDrawAllFlag:
            for i in agent_types.keys():
                for j in xrange(agent_types[i]['__minId__'], agent_types[i]['__maxId__'], dictSettings[S_NUMAGENTSTOFETCHATONCE]):
                    iQueryLowIndex = j
                    iQueryHighIndex = j + dictSettings[S_NUMAGENTSTOFETCHATONCE]
                    if (agent_types[i]['__maxId__'] - j) < dictSettings[S_NUMAGENTSTOFETCHATONCE]:
                        iQueryHighIndex = agent_types[i]['__maxId__']
            
                    lstDictAgentData = self.db.readObjects(i, iQueryLowIndex, iQueryHighIndex)

                    for k in lstDictAgentData:
                        self.drawObjectWithoutRead(i,k)
                    
        else:
            for i in self.lstDrawAgents:
                # type, id
                self.drawObject(i[0], i[1])
        
        return
 
    def DrawGLScene(self):
        # Clear The Screen And The Depth Buffer
        # time.sleep(2)

        # print "in drawing code"
        if self.bStopUpdating:
            return
        
        if not self.bUpdateNow:
            return

        # self.bDrawing = True
        # print "drawing in opengl window"
        
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()	# Reset The View 
        
        glTranslatef(self.viewX, self.viewY,0)

        if dictSettings[S_DRAWAGENTMODE] == True:
            self.drawGLSceneDrawAgentMode()
        else:
            self.drawGLSceneGeneral()
            
        

               
        glutSwapBuffers()

        # self.bDrawing = False
        self.bUpdateNow = False
        
    def keyPressed( self, *args ):
        
        if args[0] == ESCAPE:
            self.killGL()
            sys.exit(0)
        
        if args[0] == 'z' :
            self.width += 100
            self.height += 100*640/480.0
        if args[0] == 'x' :
            self.width -= 100
            self.height -= 100*640/480.0
            
        self.ReSizeGLScene(640,480)


    def mouseMove(self,button, state, x, y):
        if x > 500:
            self.viewX -= 150
        if x < 100:
            self.viewX += 150
        if y < 100:
            self.viewY -= 150
        if y > 380:
            self.viewY += 150
    
    def setWindowName(self,windowname):
        self.windowname = windowname
        
    def initWindow(self):
        glutInit([])
        glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
        
        glutInitWindowSize(self.resX, self.resY)
        
        glutInitWindowPosition(0, 0)
        
        self.window = glutCreateWindow(self.windowname)
        
        glutDisplayFunc(self.DrawGLScene)
        glutIdleFunc(self.DrawGLScene)
        
        glutMouseFunc(self.mouseMove)
        glutKeyboardFunc(self.keyPressed)

        glutReshapeFunc(self.ReSizeGLScene)
        self.initGL()
        self.ReSizeGLScene(self.resX, self.resY)
        
        # Start Event Processing Engine	

        glutMainLoop()
    
    # Print message to console, and kick off the main to get it rolling.

    def setDrawAllFlag(self, bFlag):
        self.bDrawAllFlag = bFlag
    
    def addDrawAgent( self, type, id):
        if (type,id) not in self.lstDrawAgents:
            self.lstDrawAgents.append( (type,id) )

    def deleteDrawAgent ( self, type, id):
        if (type,id) in self.lstDrawAgents:
            self.lstDrawAgents.remove( (type,id) )

    def update(self):
        self.bUpdateNow = True

        
