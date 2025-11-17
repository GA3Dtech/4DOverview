
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
import string
import zipfile
from pathlib import Path

import FreeCAD
import FreeCADGui
from PySide import QtCore, QtGui, QtWidgets  # FreeCAD's PySide!


class CentralView(QtWidgets.QWidget):
    def __init__(self,projectfolderpath):
        projectname = str(Path(projectfolderpath).name)


        super().__init__()
        self.projectfolderpath = projectfolderpath
        layout = QtWidgets.QVBoxLayout(self)
        label = QtWidgets.QLabel(f"<h2>Project: {projectname}</h2>")
       #button = QtWidgets.QPushButton("Click me")
        layout.addWidget(label)
        #layout.addWidget(button)
        #button.clicked.connect(lambda: label.setText("Hello :)"))

        #scrollable area with all files miniatures
        self.scroll = QtWidgets.QScrollArea()
        self.scroll.setWidgetResizable(True)
        layout.addWidget(self.scroll, 1)

        # grid widget for content
        self.container = QtWidgets.QWidget()
        self.grid = QtWidgets.QGridLayout(self.container)
        self.grid.setSpacing(10)
        self.scroll.setWidget(self.container)

        # --- label on Miniature
        self.info_label = QtWidgets.QLabel("Click here")
        layout.addWidget(self.info_label)

        # initial miniature loading
        self.load_thumbnails()

        

    def load_thumbnails(self):
        """image loading from folder """
        #THUMB_DIR = os.path.expanduser("~/4DOverview")  # path to 4DOverview folder
        THUMB_DIR =  Path(self.projectfolderpath) / "4DOverview"

        for i in reversed(range(self.grid.count())):
            w = self.grid.itemAt(i).widget()
            if w:
                w.setParent(None)

        if not os.path.isdir(THUMB_DIR):
            os.makedirs(THUMB_DIR, exist_ok=True)
            self.info_label.setText(f"no folder found {THUMB_DIR}")
            return

        images = [f for f in os.listdir(THUMB_DIR)
                  if f.lower().endswith(('.png', '.jpg', '.jpeg', '.svg'))]
        
        # alphabetical and numerical order
        images.sort()

        if not images:
            self.info_label.setText("no image found in folder 4DOverview.")
            return

        self.info_label.setText(f"{len(images)} thumbnail miniatures found")

        cols = 4
        for idx, img in enumerate(images):
            thumb = ThumbnailWidget(os.path.join(THUMB_DIR, img))
            thumb.clicked.connect(self.on_thumbnail_clicked)
            r, c = divmod(idx, cols)
            self.grid.addWidget(thumb, r, c)

    def on_thumbnail_clicked(self, path):
        """Action to do when clicking the miniature """
        self.info_label.setText(f" thumbnail clicked {os.path.basename(path)}")

        # opening the targeted file
        path = Path(path)
        #path = path.parents[1]  # 2 folder back
        #fcstd = os.path.splitext(path)[0] + ".FCStd"
        fcstd = path.parent.parent / (path.stem + ".FCStd")
        print(fcstd)
        if os.path.exists(fcstd):
            FreeCAD.open(str(fcstd))  
        else:
            QtWidgets.QMessageBox.information(self, "Action thumbnail clicked", f"File not found: {fcstd}")


# --- function to find all file .fcstd in the folder ---
def fForAllFcstd(folder_path) :

    for filename in os.listdir(folder_path):
        if filename.lower().endswith(".fcstd"):
            file_path = os.path.join(folder_path, filename)
            print(f"Opening {file_path}")

            # open file
            doc = FreeCAD.open(file_path)
            
            # code for each file
            mycode(doc)
            
            # Sauvegarder le document 
            # doc.save()
            
            # close file
            FreeCAD.closeDocument(doc.Name)
            print(f"{filename} done & closed \n")

def fForAllFcstdO(folder_path) :

    for filename in os.listdir(folder_path):
        if filename.lower().endswith(".fcstd"):
            file_path = os.path.join(folder_path, filename)
            print(f"Opening {file_path}")

            # open file
            doc = FreeCAD.open(file_path)
            
            # code for each file
            mycodeO(doc)
            
            # Sauvegarder le document 
            # doc.save()
            
            # close file
            FreeCAD.closeDocument(doc.Name)
            print(f"{filename} done & closed \n")


# --- function to execute for each file .fcstd ---
def mycodeO (doc):
    print(f"Document {doc.Name} \n")

    if not doc or not doc.FileName:
        FreeCAD.Console.PrintError("No document found\n")
    else:
        filepath = doc.FileName
        dirname = os.path.dirname(filepath)
        basename = os.path.splitext(os.path.basename(filepath))[0]

        # folder 4DOverview in the Project folder : Project/4DOverview/
        overview_dir = os.path.join(dirname, "4DOverview")
        if not os.path.exists(overview_dir):
            os.mkdir(overview_dir)

        # Save the file
        #doc.save() # not necessary if you want to update the thumbnail with actual settings you must do it
        # faster and lighter without especially on cloud parallelized storage

        # path for "inwork" FreeCAD files
        png_path_inwork = os.path.join(overview_dir, f"{basename}.png")

            # Extraction of thumbnail from .FCStd
        try:
            with zipfile.ZipFile(filepath , 'r') as z:
                thumb_candidates = [f for f in z.namelist() if f.lower().endswith("thumbnail.png")]
                if thumb_candidates:
                    with z.open(thumb_candidates[0]) as thumb:
                        data = thumb.read()  # read once
                    # write to both destinations !!

                    with open(png_path_inwork, "wb") as out:
                        out.write(data)
                    FreeCAD.Console.PrintMessage("Miniature extracted.\n")
                else:
                    raise FileNotFoundError
                
        except Exception:
            # fallback : capture de la vue actuelle
            FreeCAD.Console.PrintMessage("No Miniature found , capture scene instead.\n")
            view = FreeCADGui.ActiveDocument.ActiveView



def mycode (doc):
    print(f"Document {doc.Name} \n")

    if not doc or not doc.FileName:
        FreeCAD.Console.PrintError("No document found\n")
    else:
        filepath = doc.FileName
        dirname = os.path.dirname(filepath)
        basename = os.path.splitext(os.path.basename(filepath))[0]

        # folder 4DOverview in the Project folder : Project/4DOverview/
        overview_dir = os.path.join(dirname, "4DOverview")
        if not os.path.exists(overview_dir):
            os.mkdir(overview_dir)

        # subfolder .NameofFile : Project/4DOverview/.NameofFile001  - .NameofFiles002 etc...
        project_dir = os.path.join(overview_dir, f".{basename}")
        if not os.path.exists(project_dir):
            os.mkdir(project_dir)

        # Check and list already existing version file
        existing = [f for f in os.listdir(project_dir) if f.endswith(".FCStd")]
        existing_versions = []
        for f in existing:
            parts = f.split("_")
            if len(parts) > 1:
                version = parts[-1].split(".")[0]
                if len(version) == 2 and all(c in string.ascii_lowercase for c in version):
                    existing_versions.append(version)

        last_version = sorted(existing_versions)[-1] if existing_versions else None
        new_version = increment_version(last_version)

        # Save the file
        doc.save()

        # path for "inwork" FreeCAD files
        png_path_inwork = os.path.join(overview_dir, f"{basename}.png")

        # path for versions of file
        fcstd_path = os.path.join(project_dir, f"{basename}_{new_version}.FCStd")
        png_path = os.path.join(project_dir, f"{basename}_{new_version}.png")
        gltf_path = os.path.join(project_dir, f"{basename}_{new_version}.gltf")

        # Save version of FreeCAD file
        doc.saveCopy(fcstd_path)

        # Extraction of thumbnail from .FCStd
        try:
            with zipfile.ZipFile(fcstd_path, 'r') as z:
                thumb_candidates = [f for f in z.namelist() if f.lower().endswith("thumbnail.png")]
                if thumb_candidates:
                    with z.open(thumb_candidates[0]) as thumb:
                        data = thumb.read()  # read once
                    # write to both destinations !!
                    with open(png_path, "wb") as out:
                        out.write(data)
                    with open(png_path_inwork, "wb") as out:
                        out.write(data)
                    FreeCAD.Console.PrintMessage("Miniature extracted.\n")
                else:
                    raise FileNotFoundError
                
        except Exception:
            # fallback : capture de la vue actuelle
            FreeCAD.Console.PrintMessage("No Miniature found , capture scene instead.\n")
            view = FreeCADGui.ActiveDocument.ActiveView
        
        if False :

            # Export GLTF (toute la scène visible)
            try:
                import ImportGui
                visible_objs = []
                for obj in doc.Objects:
                    try:
                        if hasattr(obj, "ViewObject") and getattr(obj.ViewObject, "Visibility", True):
                            visible_objs.append(obj)
                    except Exception:
                        # sécurité : on inclut par défaut si pas d'attribut
                        visible_objs.append(obj)

                if visible_objs:
                    ImportGui.export(visible_objs, gltf_path)
                    FreeCAD.Console.PrintMessage("Export GLTF réussi.\n")
                else:
                    FreeCAD.Console.PrintMessage("Aucun objet visible à exporter.\n")
            except Exception as e:
                FreeCAD.Console.PrintError(f"Erreur export GLTF: {e}\n")

        FreeCAD.Console.PrintMessage(f"Version {new_version} saved in {project_dir}\n")

# --- Incremental File Naming
def increment_version(last_version):
    """Incremental version numbering with 2 smalle letters indice : 'aa' -> 'ab', ..., 'az' -> 'ba'"""
    if not last_version or len(last_version) != 2:
        return "aa"
    letters = string.ascii_lowercase
    a, b = last_version
    if b != 'z':
        return a + letters[letters.index(b) + 1]
    else:
        if a != 'z':
            return letters[letters.index(a) + 1] + 'a'
        else:
            return 'aa'  # sécu au cas où on atteint 'zz'
        

class ThumbnailWidget(QtWidgets.QFrame):
    """Widget to get a clickable Miniature Thumbnail"""
    clicked = QtCore.Signal(str)  # signal vers  le chemin de l'image..

    def __init__(self, img_path, size=200):
        super().__init__()
        self.img_path = img_path
        self.size = size

        
        self.setFixedSize(size, size)
        self.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.setLineWidth(0)
        self.setCursor(QtCore.Qt.PointingHandCursor)
        self.setStyleSheet("""
            QFrame {
                border-radius: 6px;
                border: 0px solid #888;
                background-color: #f8f8f8;
            }
            QFrame:hover {
                border: 2px solid #0078d7;
                background-color: #eef6ff;
            }
            QLabel {
                color: #333;
                font-size: 11px;
            }
        """)

        # --- layout vertical ---
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(4)

        # --- image ---
        pix = QtGui.QPixmap(img_path)
        if not pix.isNull():
            pix = pix.scaled(size - 20, size - 40, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)

        self.label_img = QtWidgets.QLabel()
        self.label_img.setPixmap(pix)
        self.label_img.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.label_img, stretch=1)

        # --- file name without extension ---
        filename = os.path.splitext(os.path.basename(img_path))[0]
        self.label_name = QtWidgets.QLabel(filename)
        self.label_name.setAlignment(QtCore.Qt.AlignCenter)
        self.label_name.setWordWrap(True)
        layout.addWidget(self.label_name, stretch=0)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.clicked.emit(self.img_path)
            #print(self.img_path)
    
def makeView(projectfolderpath) :

    # create and insert central view
    mw = FreeCADGui.getMainWindow()
    mdi = mw.findChild(QtWidgets.QMdiArea)
    sub = mdi.addSubWindow(CentralView(projectfolderpath))
    sub.setWindowTitle("Overview")
    sub.showMaximized()