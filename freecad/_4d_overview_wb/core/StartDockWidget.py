# ***************************************************************************
#   Copyright (c) 2025 GA3D - www.ga3d.tech
#
#   This file is part of the GA3D 4DOverview project.
#
#   The GA3D 4DOverview core is free software: you can redistribute it and/or
#   modify it under the terms of the GNU Lesser General Public License (LGPL)
#   as published by the Free Software Foundation, either version 2.1 of the
#   License, or (at your option) any later version.
#
#   This library is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#   GNU Lesser General Public License for more details.
#
#   You should have received a copy of the GNU Lesser General Public License
#   along with this library. If not, see <https://www.gnu.org/licenses/>.
#
#   For custom extensions or commercial adaptations, please contact:
#   ga3d.tech2021@gmail.com
# ***************************************************************************



from PySide6 import QtWidgets, QtCore
import FreeCADGui
import FreeCAD
import os

from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import QSize, Qt

from freecad. _4d_overview_wb.core import CentralWindowGeneric
from freecad. _4d_overview_wb.core import CentralWindowOverview
from freecad. _4d_overview_wb.core import CentralWindowTimeLine
from freecad. _4d_overview_wb.core import CentralWindowProjectBrowser
from freecad. _4d_overview_wb.core import AssetCreatorWidget

class FourOverviewMainPanel(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("4D Overview - Main")
        layout = QtWidgets.QVBoxLayout(self)

          # --- Project Browser view button ---

        self.ProjectBrowserButton = QtWidgets.QPushButton("Projects Browser")
        self.ProjectBrowserButton.setMinimumHeight(40)
        layout.addWidget(self.ProjectBrowserButton)
        self.ProjectBrowserButton.clicked.connect(self.functionProjectBrowser)

        # --- Ligne horizontale   ---
        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.HLine)       # Ligne horizontale
        layout.addWidget(line)

        # --- Project folder selection ---
        self.path = None
        toplineQW = QtWidgets.QHBoxLayout()
        self.folderLabel = QtWidgets.QLabel("Project Folder:")
        self.folderPath = QtWidgets.QLineEdit()
        self.browseBtn = QtWidgets.QPushButton("...")
        self.browseBtn.clicked.connect(self.selectFolder)
        toplineQW .addWidget(self.folderLabel)
        toplineQW .addWidget(self.folderPath)
        toplineQW .addWidget(self.browseBtn)
        layout.addLayout(toplineQW)

        

         # --- Overview view button ---

        self.OverviewViewButton = QtWidgets.QPushButton("Overview - View")
        self.OverviewViewButton.setMinimumHeight(40)
        layout.addWidget(self.OverviewViewButton)
        self.OverviewViewButton.clicked.connect(self.functionView)

        # --- Overview generator button ---

        self.OverviewGeneratorButtonO = QtWidgets.QPushButton("Overview - Generate O only")
        self.OverviewGeneratorButtonO.setMinimumHeight(40)
        layout.addWidget(self.OverviewGeneratorButtonO)
        self.OverviewGeneratorButtonO.clicked.connect(self.functionGenerateO)

        # --- Overview generator button ---

        self.OverviewGeneratorButtonOT = QtWidgets.QPushButton("Overview - Generate O + T")
        self.OverviewGeneratorButtonOT.setMinimumHeight(40)
        layout.addWidget(self.OverviewGeneratorButtonOT)
        self.OverviewGeneratorButtonOT.clicked.connect(self.functionGenerateOT)

        # --- Ligne horizontale   ---
        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.HLine)       # Ligne horizontale
        layout.addWidget(line)

        # --- Asset creator widget button ---

        self.AssetCreatorButton = QtWidgets.QPushButton("Asset Creator")
        self.AssetCreatorButton.setMinimumHeight(40)
        layout.addWidget(self.AssetCreatorButton)
        self.AssetCreatorButton.clicked.connect(self.functionAssetCreator)

        layout.addWidget(line)

        # --- TimeLine view button ---

        self.TimeLineViewButton = QtWidgets.QPushButton("Timeline - View")
        self.TimeLineViewButton.setMinimumHeight(40)
        layout.addWidget(self.TimeLineViewButton)
        self.TimeLineViewButton.clicked.connect(self.functionTimeLine)

        self.TimeLineIncButton = QtWidgets.QPushButton("++")
        self.TimeLineIncButton.setMinimumHeight(40)
        layout.addWidget(self.TimeLineIncButton)
        self.TimeLineIncButton.clicked.connect(self.functionTimeInc)





        # --- Test Text ---
        label = QtWidgets.QLabel("Bienvenue dans 4D Overview")
        layout.addWidget(label)





        #---------------GUI Prepa END ------------------#

    # --- 
    def selectFolder(self):
        self.path = QtWidgets.QFileDialog.getExistingDirectory(self, "Choose a folder")
        if self.path:
            self.folderPath.setText(self.path)
            self.checkFolderStructure4D(self.path)


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
    def functionGenerateO(self) :
        print("Generate 4DOverview of the project folder - Overview Only")

        if self.path == None :
            self.selectFolder()
        
        CentralWindowOverview.fForAllFcstdO(self.path)
        CentralWindowOverview.makeView(self.path)


    # ---
    def functionGenerateOT(self) :
        print("Generate 4DOverview of the project folder and Versionning")

        if self.path == None :
            self.selectFolder()
        
        CentralWindowOverview.fForAllFcstd(self.path)
        CentralWindowOverview.makeView(self.path)

    # ---
    def functionView(self) :
        print("View 4DOverview of the project folder")

        if self.path == None :
            self.selectFolder()
        
        CentralWindowOverview.makeView(self.path)

        # ---
    def functionProjectBrowser(self) :
        print("Project Browser start in central view")
        
        CentralWindowProjectBrowser.show_project_browser()

         # ---
    def functionAssetCreator(self) :
        print("starting the Asset Creator Widget")
        
        AssetCreatorWidget.launch_asset_creator()

    # ---
    def functionTimeLine(self) :
        print("View 4DOverview TimeLine of actual file")

        #if self.path == None :
        #    self.selectFolder()

        doc = FreeCAD.ActiveDocument
        if doc and doc.FileName:
            print(doc.FileName)
        else:
            print("no active file")
        base_dir = os.path.dirname(doc.FileName)
        basename = os.path.basename(doc.FileName)               # ex: "myPart.FCStd"
        name_no_ext = os.path.splitext(basename)[0]             # ex: "myPart"
        target_path = os.path.join(base_dir,"4DOverview" ,f".{name_no_ext}")

        CentralWindowTimeLine.makeView(target_path)
    
        # ---
    def functionTimeInc(self) :
        print("create a version (time increment) ")

        #if self.path == None :
        #    self.selectFolder()
        doc = FreeCAD.ActiveDocument
        if doc and doc.FileName:
            print(doc.FileName)
        else:
            print("no active file")

        CentralWindowTimeLine.save_incremented_version(doc)
        

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



