from PySide6 import QtWidgets, QtCore
import FreeCADGui

class FourOverviewMainPanel(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("4D Overview - Main")
        layout = QtWidgets.QVBoxLayout(self)
        label = QtWidgets.QLabel("Bienvenue dans 4D Overview")
        layout.addWidget(label)
        

def start () :
    # create the  dock
    main_win = FreeCADGui.getMainWindow()

    #check if already activated
    dock_name = "FourOverviewMainPanel"
    existing_dock = main_win.findChild(QtWidgets.QDockWidget, dock_name)

    if existing_dock is None: 

        dock_widget = QtWidgets.QDockWidget("4D Tools", main_win)
        dock_widget.setWidget(FourOverviewMainPanel())
        dock_widget.setObjectName("FourOverviewMainPanel")

        # use of needed QtCore flags
        main_win.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock_widget)
        dock_widget.show()

    else :

        print(f"The pannel '{dock_name}' is already open, bring it front")
        existing_dock.show()
        existing_dock.raise_()



