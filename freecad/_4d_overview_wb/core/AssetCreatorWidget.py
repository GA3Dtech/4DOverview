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
import FreeCAD
import FreeCADGui
from PySide6 import QtWidgets, QtCore
import os


class AssetCreator(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Create Asset")
        self.setMinimumWidth(420)
        self._setup_ui()

    def _setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)

        # --- Target folder ---
        folder_layout = QtWidgets.QHBoxLayout()
        folder_label = QtWidgets.QLabel("Target folder:")
        self.folder_edit = QtWidgets.QLineEdit()
        browse_btn = QtWidgets.QPushButton("...")
        browse_btn.clicked.connect(self.browse_folder)
        folder_layout.addWidget(folder_label)
        folder_layout.addWidget(self.folder_edit)
        folder_layout.addWidget(browse_btn)
        layout.addLayout(folder_layout)

        # --- Filename (model name) ---
        name_layout = QtWidgets.QHBoxLayout()
        name_label = QtWidgets.QLabel("Modele XX_AssetPast/BUY_000_description :")
        self.name_edit = QtWidgets.QLineEdit()
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_edit)
        layout.addLayout(name_layout)

        # --- Create button ---
        self.create_btn = QtWidgets.QPushButton("Create Asset")
        self.create_btn.setStyleSheet("font-weight: bold;")
        self.create_btn.clicked.connect(self.create_asset)
        layout.addWidget(self.create_btn)

        self.setLayout(layout)

    def browse_folder(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, "choose target folder")
        if folder:
            self.folder_edit.setText(folder)

    def create_asset(self):
        gui = FreeCADGui
        app = FreeCAD
        sel = gui.Selection.getSelection()

        if not sel:
            QtWidgets.QMessageBox.warning(self, "no selection", "Please select object in active document")
            return

        target_folder = self.folder_edit.text().strip()
        filename = self.name_edit.text().strip()

        if not target_folder:
            QtWidgets.QMessageBox.warning(self, "missing folder", "Please select target folder")
            return
        if not filename:
            QtWidgets.QMessageBox.warning(self, "missing name", "Please enter a model name")
            return

        # create a new document
        new_doc = app.newDocument(filename)

        # copy the selection in active document
        src_doc = gui.ActiveDocument.Document
        app.ActiveDocument = src_doc
        gui.Selection.clearSelection()
        for obj in sel:
            gui.Selection.addSelection(obj)
        gui.runCommand('Std_Copy', 0)

        # paste selection in new document
        app.ActiveDocument = new_doc
        gui.runCommand('Std_Paste', 0)
        
        # V,F 
        gui.SendMsgToActiveView("ViewFit")
        gui.activeDocument().activeView().viewIsometric()

        # Dialogbox to save document with modelname as suggestion
        suggested_path = os.path.join(target_folder, f"{filename}.FCStd")
        save_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Saving Asset",
            suggested_path,
            "FreeCAD Files (*.FCStd)"
        )

        if save_path:
            new_doc.saveAs(save_path)
            QtWidgets.QMessageBox.information(self, "Asset created", f"asset saved here :\n{save_path}")

        self.close()


def launch_asset_creator():
    dialog = AssetCreator()
    dialog.exec()


if __name__ == "__main__":
    launch_asset_creator()
