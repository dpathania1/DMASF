# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'gui_new.ui'
#
# Created: Wed Aug 30 22:41:38 2006
#      by: The PyQt User Interface Compiler (pyuic) 3.15.1
#
# WARNING! All changes made in this file will be lost!


from qt import *


class serverUI(QWidget):
    def __init__(self,parent = None,name = None,fl = 0):
        QWidget.__init__(self,parent,name,fl)

        if not name:
            self.setName("serverUI")



        self.simstateframe = QFrame(self,"simstateframe")
        self.simstateframe.setGeometry(QRect(0,10,440,140))
        self.simstateframe.setFrameShape(QFrame.StyledPanel)
        self.simstateframe.setFrameShadow(QFrame.Raised)

        self.simstatelabel = QLabel(self.simstateframe,"simstatelabel")
        self.simstatelabel.setGeometry(QRect(30,110,120,20))
        self.simstatelabel.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        self.simstate = QLineEdit(self.simstateframe,"simstate")
        self.simstate.setGeometry(QRect(160,110,140,21))
        self.simstate.setAlignment(QLineEdit.AlignHCenter)
        self.simstate.setReadOnly(1)

        self.delete = QPushButton(self.simstateframe,"delete")
        self.delete.setGeometry(QRect(370,110,61,21))

        self.listofclients = QListBox(self.simstateframe,"listofclients")
        self.listofclients.setGeometry(QRect(20,30,380,70))
        self.listofclients.setVariableHeight(0)

        self.state = QLabel(self.simstateframe,"state")
        self.state.setGeometry(QRect(230,0,170,30))
        self.state.setAlignment(QLabel.AlignCenter)

        self.add = QPushButton(self.simstateframe,"add")
        self.add.setGeometry(QRect(310,110,61,21))

        self.machinename = QLabel(self.simstateframe,"machinename")
        self.machinename.setGeometry(QRect(20,0,180,31))
        self.machinename.setAlignment(QLabel.AlignCenter)

        self.controlframe = QFrame(self,"controlframe")
        self.controlframe.setGeometry(QRect(440,10,171,140))
        self.controlframe.setFrameShape(QFrame.StyledPanel)
        self.controlframe.setFrameShadow(QFrame.Raised)
        self.controlframe.setLineWidth(2)

        self.zoomout = QPushButton(self.controlframe,"zoomout")
        self.zoomout.setGeometry(QRect(110,30,40,30))

        self.up = QPushButton(self.controlframe,"up")
        self.up.setGeometry(QRect(70,30,40,30))

        self.down = QPushButton(self.controlframe,"down")
        self.down.setGeometry(QRect(70,90,40,30))

        self.right = QPushButton(self.controlframe,"right")
        self.right.setGeometry(QRect(110,60,40,30))

        self.left = QPushButton(self.controlframe,"left")
        self.left.setGeometry(QRect(30,60,40,30))

        self.stop = QPushButton(self.controlframe,"stop")
        self.stop.setGeometry(QRect(110,90,40,30))

        self.record = QPushButton(self.controlframe,"record")
        self.record.setGeometry(QRect(30,90,40,30))

        self.play = QPushButton(self.controlframe,"play")
        self.play.setGeometry(QRect(70,60,40,30))

        self.zoomin = QPushButton(self.controlframe,"zoomin")
        self.zoomin.setGeometry(QRect(30,30,40,30))

        self.guicontrols = QLabel(self.controlframe,"guicontrols")
        self.guicontrols.setGeometry(QRect(0,0,160,31))
        self.guicontrols.setAlignment(QLabel.AlignCenter)

        self.languageChange()

        self.resize(QSize(612,154).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)


    def languageChange(self):
        self.setCaption(self.__tr("MultiAgent System Server Interface"))
        self.simstatelabel.setText(self.__tr("Simulation State"))
        self.delete.setText(self.__tr("Delete"))
        self.listofclients.clear()
        self.state.setText(self.__tr("State"))
        self.add.setText(self.__tr("Add "))
        self.machinename.setText(self.__tr("Machine Name"))
        self.zoomout.setText(self.__tr("-"))
        self.up.setText(self.__tr("^"))
        self.down.setText(self.__tr("v"))
        self.right.setText(self.__tr(">"))
        self.left.setText(self.__tr("<"))
        self.stop.setText(self.__tr("[o]"))
        self.record.setText(self.__tr("(i)"))
        self.play.setText(self.__tr("> / ||"))
        self.zoomin.setText(self.__tr("+"))
        self.guicontrols.setText(self.__tr("GUI Controls"))


    def __tr(self,s,c = None):
        return qApp.translate("serverUI",s,c)
