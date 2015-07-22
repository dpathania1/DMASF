# This file is generated by pyuic and contains the code
# for the appearance of the QDialog for the addition of a
# new client

# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'addclient.ui'
#
# Created: Sat Jul 22 22:05:44 2006
#      by: The PyQt User Interface Compiler (pyuic) 3.15.1
#
# WARNING! All changes made in this file will be lost!

from qt import *

class addclientui(QDialog):
    def __init__(self,parent = None,name = None,modal = True,fl=0):
        QDialog.__init__(self,parent,name,modal,fl)

        if not name:
            self.setName("addclient")

        self.setSizeGripEnabled(1)
        
        LayoutWidget = QWidget(self,"Layout1")
        LayoutWidget.setGeometry(QRect(20,240,476,33))
        Layout1 = QHBoxLayout(LayoutWidget,0,6,"Layout1")

        self.clientaddress = QLineEdit(self,"clientaddress")
        self.clientaddress.setGeometry(QRect(290,60,170,41))

        self.clientport = QLineEdit(self,"clientport")
        self.clientport.setGeometry(QRect(290,110,170,41))

        self.buttonHelp = QPushButton(LayoutWidget,"buttonHelp")
        self.buttonHelp.setAutoDefault(1)
        Layout1.addWidget(self.buttonHelp)
        Horizontal_Spacing2 = QSpacerItem(20,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        Layout1.addItem(Horizontal_Spacing2)

        self.buttonOk = QPushButton(LayoutWidget,"buttonOk")
        self.buttonOk.setAutoDefault(1)
        self.buttonOk.setDefault(1)
         
        Layout1.addWidget(self.buttonOk)

        self.buttonCancel = QPushButton(LayoutWidget,"buttonCancel")
        self.buttonCancel.setAutoDefault(1)
        Layout1.addWidget(self.buttonCancel)

        self.addclientlabel = QLabel(self,"addclientlabel")
        self.addclientlabel.setGeometry(QRect(40,60,221,40))
        self.addclientlabel.setAlignment(QLabel.AlignCenter)

        self.addclientportlabel = QLabel(self,"addclientportlabel")
        self.addclientportlabel.setGeometry(QRect(40,120,221,40))
        self.addclientportlabel.setAlignment(QLabel.AlignCenter)

        self.languageChange()

        self.resize(QSize(511,282).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

    def languageChange(self):
        self.setCaption(self.__tr("Add Client"))
        self.buttonHelp.setText(self.__tr("&Help"))
        self.buttonHelp.setAccel(self.__tr("F1"))
        self.buttonOk.setText(self.__tr("&OK"))
        self.buttonOk.setAccel(QString.null)
        self.buttonCancel.setText(self.__tr("&Cancel"))
        self.buttonCancel.setAccel(QString.null)
        self.addclientlabel.setText(self.__tr("Client Address"))
        self.addclientportlabel.setText(self.__tr("Client Port"))

    def __tr(self,s,c = None):
        return qApp.translate("addclient",s,c)
