from PySide6 import QtWidgets, QtCore
import FreeCADGui
import os

from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import QSize, Qt

class FourOverviewMainPanel(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("4D Overview - Main")
        layout = QtWidgets.QVBoxLayout(self)

        # --- Project folder selection ---
        toplineQW = QtWidgets.QHBoxLayout()
        self.folderLabel = QtWidgets.QLabel("Project Folder:")
        self.folderPath = QtWidgets.QLineEdit()
        self.browseBtn = QtWidgets.QPushButton("browse")
        self.browseBtn.clicked.connect(self.selectFolder)
        toplineQW .addWidget(self.folderLabel)
        toplineQW .addWidget(self.folderPath)
        toplineQW .addWidget(self.browseBtn)
        layout.addLayout(toplineQW)

        # --- Overview generator button ---

        self.OverviewGeneratorButton = QtWidgets.QPushButton("Overview")
        self.OverviewGeneratorButton.setMinimumHeight(40)
        layout.addWidget(self.OverviewGeneratorButton)
        self.OverviewGeneratorButton.clicked.connect(self.functionGenerate)





        # --- Test Text ---
        label = QtWidgets.QLabel("Bienvenue dans 4D Overview")
        layout.addWidget(label)





        #---------------GUI Prepa END ------------------#

    # --- 
    def selectFolder(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(self, "Choose a folder")
        if path:
            self.folderPath.setText(path)
            self.checkFolderStructure4D(path)


    # ---
    def checkFolderStructure4D(self, root):
        """Create the 4DOverview files Structures : ./4DOverview/.FileName"""
        overview = os.path.join(root, "4DOverview")
        if not os.path.exists(overview):
            os.makedirs(overview)
        for f in os.listdir(root):
            if f.endswith(".FCStd"):
                name = os.path.splitext(f)[0]
                sub = os.path.join(overview, f".{name}")
                if not os.path.exists(sub):
                    os.makedirs(sub)


    # ---
    def functionGenerate(self) :
        print("Generate 4DOverview of the project folder")
        

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



