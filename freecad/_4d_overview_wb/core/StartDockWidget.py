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
#   For custom extensions or commercial adaptations, please   ---  :
#     ---
# ***************************************************************************

import os

import FreeCAD
import FreeCADGui
from PySide import QtCore, QtWidgets  # FreeCAD's PySide! Can be PySide2 or PySide6.


from freecad. _4d_overview_wb.core import (
    AssetCreatorWidget,
    CentralWindowOverview,
    CentralWindowProjectBrowser,
    CentralWindowTimeLine,
)


class FourOverviewMainPanel(QtWidgets.QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.setWindowTitle("4D Overview - Main")
        layout = QtWidgets.QVBoxLayout(self)

        # Project Browser view button.
        self.ProjectBrowserButton = QtWidgets.QPushButton("Projects Browser")
        self.ProjectBrowserButton.setMinimumHeight(40)
        layout.addWidget(self.ProjectBrowserButton)
        self.ProjectBrowserButton.clicked.connect(self.browse_project)

        # Horizontal line.
        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.HLine)
        layout.addWidget(line)

        # Project folder selection.
        self.path = None
        toplineQW = QtWidgets.QHBoxLayout()
        self.folderLabel = QtWidgets.QLabel("Project Folder:")
        self.folderPath = QtWidgets.QLineEdit()
        self.browseBtn = QtWidgets.QPushButton("...")
        self.browseBtn.clicked.connect(self.select_folder)
        toplineQW .addWidget(self.folderLabel)
        toplineQW .addWidget(self.folderPath)
        toplineQW .addWidget(self.browseBtn)
        layout.addLayout(toplineQW)

         # Overview view button.
        self.OverviewViewButton = QtWidgets.QPushButton("Overview - View")
        self.OverviewViewButton.setMinimumHeight(40)
        layout.addWidget(self.OverviewViewButton)
        self.OverviewViewButton.clicked.connect(self.view_project)

        # Overview generator button.
        self.OverviewGeneratorButtonO = QtWidgets.QPushButton("Overview - Generate O only")
        self.OverviewGeneratorButtonO.setMinimumHeight(40)
        layout.addWidget(self.OverviewGeneratorButtonO)
        self.OverviewGeneratorButtonO.clicked.connect(self.generate_overview)

        # Overview+timeline generator button.
        self.OverviewGeneratorButtonOT = QtWidgets.QPushButton("Overview - Generate O + T")
        self.OverviewGeneratorButtonOT.setMinimumHeight(40)
        layout.addWidget(self.OverviewGeneratorButtonOT)
        self.OverviewGeneratorButtonOT.clicked.connect(self.generate_overview_timeline)

        # Horizontal line.
        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.HLine)
        layout.addWidget(line)

        # Asset creator widget button.
        self.AssetCreatorButton = QtWidgets.QPushButton("Asset Creator")
        self.AssetCreatorButton.setMinimumHeight(40)
        layout.addWidget(self.AssetCreatorButton)
        self.AssetCreatorButton.clicked.connect(self.create_asset)
        layout.addWidget(line)

        # TimeLine view button.
        self.TimeLineViewButton = QtWidgets.QPushButton("Timeline - View")
        self.TimeLineViewButton.setMinimumHeight(40)
        layout.addWidget(self.TimeLineViewButton)
        self.TimeLineViewButton.clicked.connect(self.view_time_line)

        self.TimeLineIncButton = QtWidgets.QPushButton("++")
        self.TimeLineIncButton.setMinimumHeight(40)
        layout.addWidget(self.TimeLineIncButton)
        self.TimeLineIncButton.clicked.connect(self.save_new_version)

        # Test Text.
        label = QtWidgets.QLabel("Bienvenue dans 4D Overview")
        layout.addWidget(label)

    def select_folder(self) -> None:
        self.path = QtWidgets.QFileDialog.getExistingDirectory(self, "Choose a folder")
        if self.path:
            self.folderPath.setText(self.path)
            self.check_folder_structure_4d(self.path)

    def check_folder_structure_4d(self, root) -> None:
        """Create the 4DOverview file structure.

        Create the 4DOverview file structure: ./4DOverview/.FileName.
        """
        overview = os.path.join(root, "4DOverview")
        if not os.path.exists(overview):
            os.makedirs(overview)
        for f in os.listdir(root):
            if f.endswith(".FCStd"):
                name = os.path.splitext(f)[0]
                sub = os.path.join(overview, f".{name}")
                if not os.path.exists(sub):
                    os.makedirs(sub)

    def generate_overview(self) -> None:
        FreeCAD.Console.PrintMessage("Generate 4DOverview of the project folder - Overview Only")
        if self.path is None:
            self.select_folder()
        CentralWindowOverview.fForAllFcstdO(self.path)
        CentralWindowOverview.make_view(self.path)

    def generate_overview_timeline(self) -> None:
        FreeCAD.Console.PrintMessage("Generate 4DOverview of the project folder and Versionning")
        if self.path is None:
            self.select_folder()
        CentralWindowOverview.fForAllFcstd(self.path)
        CentralWindowOverview.make_view(self.path)

    def view_project(self) -> None:
        FreeCAD.Console.PrintMessage("View 4DOverview of the project folder")
        if self.path is None:
            self.select_folder()
        CentralWindowOverview.make_view(self.path)

    def browse_project(self) -> None:
        CentralWindowProjectBrowser.show_project_browser()

    def create_asset(self) -> None:
        FreeCAD.Console.PrintMessage("starting the Asset Creator Widget")
        AssetCreatorWidget.launch_asset_creator()

    def view_time_line(self) -> None:
        doc = FreeCAD.activeDocument()
        if not doc or not doc.FileName:
            FreeCAD.Console.PrintMessage("No active file to show the timeline for")
            return

        FreeCAD.Console.PrintMessage(f'Viewing 4DOverview timeLine of "{doc.FileName}"')
        base_dir = os.path.dirname(doc.FileName)
        basename = os.path.basename(doc.FileName)               # ex: "myPart.FCStd"
        name_no_ext = os.path.splitext(basename)[0]             # ex: "myPart"
        target_path = os.path.join(base_dir,"4DOverview" ,f".{name_no_ext}")

        CentralWindowTimeLine.make_view(target_path)

    def save_new_version(self) -> None:
        doc = FreeCAD.activeDocument()
        CentralWindowTimeLine.save_incremented_version(doc)


def start() -> None:
    # Create the dock.
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
        existing_dock.show()
        existing_dock.raise_()
