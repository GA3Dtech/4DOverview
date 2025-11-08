
import FreeCADGui
from PySide6 import QtWidgets

class CentralView(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        layout = QtWidgets.QVBoxLayout(self)
        label = QtWidgets.QLabel("<h2>Project Overview</h2>")
       #button = QtWidgets.QPushButton("Click me")
        layout.addWidget(label)
        #layout.addWidget(button)
        #button.clicked.connect(lambda: label.setText("Hello :)"))


    
def makeView() :

    # create and insert central view
    mw = FreeCADGui.getMainWindow()
    mdi = mw.findChild(QtWidgets.QMdiArea)
    sub = mdi.addSubWindow(CentralView())
    sub.setWindowTitle("Overview")
    sub.showMaximized()