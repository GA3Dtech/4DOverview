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
import shutil
import string
import zipfile
from pathlib import Path

import FreeCAD
import FreeCADGui
from PySide import QtCore, QtGui, QtWidgets  # Freecad's PySide!


class CentralView(QtWidgets.QWidget):
    def __init__(self, projectfolderpath):
        projectname = str(Path(projectfolderpath).name)

        super().__init__()
        self.projectfolderpath = projectfolderpath
        layout = QtWidgets.QVBoxLayout(self)
        label = QtWidgets.QLabel(f"<h2>Project: {projectname}</h2>")
        layout.addWidget(label)

        # Scrollable area containing all file thumbnails
        self.scroll = QtWidgets.QScrollArea()
        self.scroll.setWidgetResizable(True)
        layout.addWidget(self.scroll, 1)

        # Grid widget for content
        self.container = QtWidgets.QWidget()
        self.grid = QtWidgets.QGridLayout(self.container)
        self.grid.setSpacing(10)
        self.scroll.setWidget(self.container)

        # Label below the grid
        self.info_label = QtWidgets.QLabel("Click here")
        layout.addWidget(self.info_label)

        # Load thumbnails on initialization
        self.load_thumbnails()

    def load_thumbnails(self):
        """Load and display thumbnails sorted by version suffix (_aa, _ab, etc.)"""
        THUMB_DIR = Path(self.projectfolderpath)

        # Clear the existing grid
        for i in reversed(range(self.grid.count())):
            w = self.grid.itemAt(i).widget()
            if w:
                w.setParent(None)

        # Check if the folder exists
        if not THUMB_DIR.is_dir():
            THUMB_DIR.mkdir(parents=True, exist_ok=True)
            self.info_label.setText(f"No folder found: {THUMB_DIR}")
            return

        # List valid images
        images = [
            f for f in os.listdir(THUMB_DIR)
            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.svg'))
        ]

        if not images:
            self.info_label.setText("No image found in folder 4DOverview.")
            return

        # Extract version suffix (_aa, _ab, etc.)
        def extract_suffix(filename):
            stem = Path(filename).stem
            parts = stem.split("_")
            if len(parts) > 1:
                suffix = parts[-1]
                # Convert suffix to tuple for consistent sorting: _aa -> (0,0), _ab -> (0,1)
                if len(suffix) == 2 and suffix.isalpha():
                    return tuple(ord(c) - ord('a') for c in suffix.lower())
                elif suffix.lower().startswith("v") and suffix[1:].isdigit():
                    return (999, int(suffix[1:]))  # numeric versions come after letters
            return (-1, -1)  # files without suffix come first

        # Sort images by suffix
        images.sort(key=extract_suffix)

        self.info_label.setText(f"{len(images)} thumbnail miniatures found")

        # Display thumbnails in grid
        cols = 4
        for idx, img in enumerate(images):
            thumb = ThumbnailWidget(os.path.join(THUMB_DIR, img))
            thumb.clicked.connect(self.on_thumbnail_clicked)
            r, c = divmod(idx, cols)
            self.grid.addWidget(thumb, r, c)

    def on_thumbnail_clicked(self, path):
        # When clicking a thumbnail, show a dialog with two options
        self.info_label.setText(f" thumbnail clicked {os.path.basename(path)}")

        path = Path(path)
        clicked_fcstd = path.parent / (path.stem + ".FCStd")
        print(clicked_fcstd)

        if not clicked_fcstd.exists():
            QtWidgets.QMessageBox.warning(self, "File not found", f"File not found: {clicked_fcstd}")
            return

        # Determine the real file to overwrite
        # Example: /.../4DOverview/.Nouveau2/Nouveau2_ab.FCStd -> /.../Nouveau2.FCStd
        real_fcstd = None
        path = Path(path)
        base_name = path.stem.split("_")[0]  # remove version suffix (_ab, _v2, etc.)

        # The real folder is two levels above the .FCStd file
        # It has the same name as the hidden folder but without the leading dot
        hidden_dir = path.parent.name
        clean_dir = hidden_dir[1:] if hidden_dir.startswith(".") else hidden_dir

        # Go three levels up (out of 4DOverview)
        target_parent = path.parent.parent.parent

        # Build the path of the real file
        real_fcstd = target_parent / (clean_dir + ".FCStd")

        # Check existence
        if not real_fcstd.exists():
            print(f"Original file not found: {real_fcstd}")
        else:
            print(f"Original file detected: {real_fcstd}")

        if real_fcstd is None:
            QtWidgets.QMessageBox.warning(self, "Original not found", "Could not locate the real file to overwrite.")
            return

        # Create a small dialog window
        dlg = QtWidgets.QDialog(self)
        dlg.setWindowTitle("File Action")
        layout = QtWidgets.QVBoxLayout(dlg)

        label = QtWidgets.QLabel(f"Clicked file: {clicked_fcstd}\n\nOriginal file: {real_fcstd}")
        layout.addWidget(label)

        btn_open = QtWidgets.QPushButton("Open this file")
        btn_overwrite = QtWidgets.QPushButton("Overwrite the original file")
        btn_cancel = QtWidgets.QPushButton("Cancel")

        layout.addWidget(btn_open)
        layout.addWidget(btn_overwrite)
        layout.addWidget(btn_cancel)

        # Define button actions
        def open_file():
            FreeCAD.open(str(clicked_fcstd))
            dlg.accept()

        def overwrite_file():
            reply = QtWidgets.QMessageBox.question(
                dlg, "Confirmation",
                f"Do you really want to overwrite:\n{real_fcstd}\nwith\n{clicked_fcstd}?",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
            )
            if reply == QtWidgets.QMessageBox.Yes:
                try:
                    shutil.copy2(clicked_fcstd, real_fcstd)
                    # Automatically reopen the updated file
                    try:
                        for doc in FreeCAD.listDocuments().values():
                            if Path(doc.FileName) == real_fcstd:
                                FreeCAD.closeDocument(doc.Name)
                                break
                        FreeCAD.open(str(real_fcstd))
                    except Exception as e:
                        QtWidgets.QMessageBox.warning(
                            dlg, "Refresh error",
                            f"Could not reopen {real_fcstd}\n\n{e}"
                        )
                except Exception as e:
                    QtWidgets.QMessageBox.warning(
                        dlg, "Error",
                        f"Failed to copy: {e}"
                    )
            dlg.accept()

        btn_open.clicked.connect(open_file)
        btn_overwrite.clicked.connect(overwrite_file)
        btn_cancel.clicked.connect(dlg.reject)

        dlg.exec()


# --- Incremental File Naming
def increment_version(last_version):
    """Incremental version naming with two lowercase letters: 'aa' -> 'ab', ..., 'az' -> 'ba'"""
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
            return 'aa'  # fallback if 'zz' is reached


def save_incremented_version(doc):
    """
    Save an incremented version of a FreeCAD document (.FCStd)
    into <file_path>/4DOverview/.FileName/
    with thumbnail extraction or capture if missing.

    Usage:
        save_incremented_version(FreeCAD.ActiveDocument)
    """

    # --- Validate document
    if not doc or not doc.FileName:
        FreeCAD.Console.PrintError("Document not found\n")
        return

    filepath = Path(doc.FileName)
    dirname = filepath.parent
    basename = filepath.stem

    # --- Create backup folders
    overview_dir = dirname / "4DOverview"
    project_dir = overview_dir / f".{basename}"
    project_dir.mkdir(parents=True, exist_ok=True)

    # --- Find existing versions
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

    # --- Save main document
    doc.save()

    # --- Build full paths
    fcstd_path = project_dir / f"{basename}_{new_version}.FCStd"
    png_path = project_dir / f"{basename}_{new_version}.png"

    # --- Save versioned copy
    doc.saveCopy(str(fcstd_path))
    FreeCAD.Console.PrintMessage(f"Versioned file {fcstd_path}\n")

    # --- Extract thumbnail
    try:
        with zipfile.ZipFile(fcstd_path, 'r') as z:
            thumb_candidates = [f for f in z.namelist() if f.lower().endswith("thumbnail.png")]
            if thumb_candidates:
                with z.open(thumb_candidates[0]) as thumb:
                    with open(png_path, "wb") as out:
                        out.write(thumb.read())
                FreeCAD.Console.PrintMessage("Thumbnail extracted\n")
            else:
                raise FileNotFoundError
    except Exception:
        FreeCAD.Console.PrintMessage("No thumbnail found\n")
        try:
            view = FreeCADGui.ActiveDocument.ActiveView
            view.saveImage(str(png_path), 1024, 768, "Transparent")
        except Exception as e:
            FreeCAD.Console.PrintError(f"Error during capture {e}\n")

    FreeCAD.Console.PrintMessage(f"Version {new_version} saved in {project_dir}\n")


class ThumbnailWidget(QtWidgets.QFrame):
    """Widget that displays a clickable thumbnail"""
    clicked = QtCore.Signal(str)

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

        # Vertical layout
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(4)

        # Thumbnail image
        pix = QtGui.QPixmap(img_path)
        if not pix.isNull():
            pix = pix.scaled(size - 20, size - 40, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)

        self.label_img = QtWidgets.QLabel()
        self.label_img.setPixmap(pix)
        self.label_img.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.label_img, stretch=1)

        # File name without extension
        filename = os.path.splitext(os.path.basename(img_path))[0]
        self.label_name = QtWidgets.QLabel(filename)
        self.label_name.setAlignment(QtCore.Qt.AlignCenter)
        self.label_name.setWordWrap(True)
        layout.addWidget(self.label_name, stretch=0)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.clicked.emit(self.img_path)


def makeView(folderpath):
    # Create and insert central view into FreeCAD's MDI area
    mw = FreeCADGui.getMainWindow()
    mdi = mw.findChild(QtWidgets.QMdiArea)
    sub = mdi.addSubWindow(CentralView(folderpath))
    sub.setWindowTitle("TimeLine")
    sub.showMaximized()
