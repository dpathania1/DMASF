from qt import *
from qtinterface import *
import sys

class main:
  def __init__(self):
    app = QApplication(sys.argv)
    form = UI()
    form.show()
    app.setMainWidget(form)
    app.exec_loop() 

if __name__ == "__main__":
  mainobj = main()
