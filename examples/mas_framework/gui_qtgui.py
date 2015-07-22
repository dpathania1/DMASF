# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'gui_gui.ui'
#
# Created: Mon Jul 31 14:51:05 2006
#      by: The PyQt User Interface Compiler (pyuic) 3.13
#
# WARNING! All changes made in this file will be lost!


from qt import *


class serverUI(QWidget):
    def __init__(self,parent = None,name = None,fl = 1):
        QWidget.__init__(self,parent,name,fl)

        if not name:
            self.setName("serverUI")

        self.windowwidth = 800
        self.windowheight = 600

        self.simstateframex = 0
        self.simstateframey = self.windowheight - 140
        self.simstateframewidth = self.windowwidth - 200
        self.simstateframeheight = 140
        
        self.simstateframe = QFrame(self,"simstateframe")
        self.simstateframe.setGeometry(QRect(self.simstateframex,self.simstateframey,self.simstateframewidth,self.simstateframeheight))
        self.simstateframe.setFrameShape(QFrame.StyledPanel)
        self.simstateframe.setFrameShadow(QFrame.Raised)

        self.machinename = QLabel(self.simstateframe,"machinename")
        self.machinename.setGeometry(QRect(20,0,180,31))
        self.machinename.setAlignment(QLabel.AlignCenter)

        self.state = QLabel(self.simstateframe,"state")
        self.state.setGeometry(QRect(self.simstateframewidth - 200,0,170,30))
        self.state.setAlignment(QLabel.AlignCenter)

        self.simstatelabel = QLabel(self.simstateframe,"simstatelabel")
        self.simstatelabel.setGeometry(QRect(30,110,120,20))
        self.simstatelabel.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        self.simstate = QLineEdit(self.simstateframe,"simstate")
        self.simstate.setGeometry(QRect(160,110,140,21))
        self.simstate.setAlignment(QLineEdit.AlignHCenter)
        self.simstate.setReadOnly(1)

        self.add = QPushButton(self.simstateframe,"add")
        self.add.setGeometry(QRect(310,110,61,21))

        self.delete = QPushButton(self.simstateframe,"delete")
        self.delete.setGeometry(QRect(370,110,61,21))

        self.listofclients = QListBox(self.simstateframe,"listofclients")
        self.listofclients.setGeometry(QRect(20,30,self.simstateframewidth - 30,70))
        self.listofclients.setVariableHeight(0)

        self.controlframe = QFrame(self,"controlframe")
        self.controlframe.setGeometry(QRect(self.windowwidth - 200,self.windowheight - 140,171,140))
        self.controlframe.setFrameShape(QFrame.StyledPanel)
        self.controlframe.setFrameShadow(QFrame.Raised)
        self.controlframe.setLineWidth(2)

        self.guicontrols = QLabel(self.controlframe,"guicontrols")
        self.guicontrols.setGeometry(QRect(0,0,160,31))
        self.guicontrols.setAlignment(QLabel.AlignCenter)

        self.zoomin = QPushButton(self.controlframe,"zoomin")
        self.zoomin.setGeometry(QRect(30,30,40,30))

        self.up = QPushButton(self.controlframe,"up")
        self.up.setGeometry(QRect(70,30,40,30))

        self.zoomout = QPushButton(self.controlframe,"zoomout")
        self.zoomout.setGeometry(QRect(110,30,40,30))

        self.left = QPushButton(self.controlframe,"left")
        self.left.setGeometry(QRect(30,60,40,30))

        self.right = QPushButton(self.controlframe,"right")
        self.right.setGeometry(QRect(110,60,40,30))

        self.record = QPushButton(self.controlframe,"record")
        self.record.setGeometry(QRect(30,90,40,30))

        self.down = QPushButton(self.controlframe,"down")
        self.down.setGeometry(QRect(70,90,40,30))

        self.stop = QPushButton(self.controlframe,"stop")
        self.stop.setGeometry(QRect(110,90,40,30))

        self.play = QPushButton(self.controlframe,"play")
        self.play.setGeometry(QRect(70,60,40,30))

        self.openglFrame = QFrame(self,"openglFrame")
        self.openglFrame.setGeometry(QRect(0,0,self.windowwidth,self.windowheight - 140))
        self.openglFrame.setFrameShape(QFrame.StyledPanel)
        self.openglFrame.setFrameShadow(QFrame.Raised)

        self.languageChange()

        self.resize(QSize(self.windowwidth,self.windowheight).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)


    def languageChange(self):
        self.setCaption(self.__tr("MultiAgent System Server Interface"))
        self.state.setText(self.__tr("State"))
        self.machinename.setText(self.__tr("Machine Name"))
        self.simstatelabel.setText(self.__tr("Simulation State"))
        self.add.setText(self.__tr("Add "))
        self.delete.setText(self.__tr("Delete"))
        self.listofclients.clear()
        self.guicontrols.setText(self.__tr("GUI Controls"))
        self.zoomin.setText(self.__tr("+"))
        QToolTip.add(self.zoomin,self.__tr("Zoom In"))
        self.up.setText(self.__tr("^"))
        QToolTip.add(self.up,self.__tr("Up"))
        self.zoomout.setText(self.__tr("-"))
        QToolTip.add(self.zoomout,self.__tr("Zoom Out"))
        self.left.setText(self.__tr("<"))
        QToolTip.add(self.left,self.__tr("Left"))
        self.right.setText(self.__tr(">"))
        QToolTip.add(self.right,self.__tr("Right"))
        self.record.setText(self.__tr("(i)"))
        QToolTip.add(self.record,self.__tr("Record"))
        self.down.setText(self.__tr("v"))
        QToolTip.add(self.down,self.__tr("Down"))
        self.stop.setText(self.__tr("[o]"))
        QToolTip.add(self.stop,self.__tr("Stop"))
        self.play.setText(self.__tr("> / ||"))
        QToolTip.add(self.play,self.__tr("Start / Pause"))


    def __tr(self,s,c = None):
        return qApp.translate("serverUI",s,c)
