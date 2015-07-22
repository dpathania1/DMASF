# This file contains the behaviour for the addclient ui

from qt import *
from gui_addclientui import *

class addclient(addclientui):
    def __init__ (self,parent = None, name=None, modal=True,fl=0):
        addclientui.__init__(self,parent,name,modal,fl)

        self.parent = parent

        self.connect(self.buttonOk,SIGNAL("clicked()"),self.acc)
        self.connect(self.buttonCancel,SIGNAL("clicked()"),self.rej)

    def rej(self):
        self.close()        
        
    def acc(self):
        self.parent.newclientadded = True
        self.parent.newclientaddress = self.clientaddress.text()
        self.parent.newclientport = self.clientport.text()

        self.parent.addItem()
        self.close()

