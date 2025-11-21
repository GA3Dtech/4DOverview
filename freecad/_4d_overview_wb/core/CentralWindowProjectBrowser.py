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
import FreeCAD, FreeCADGui
from PySide import QtWidgets, QtCore, QtGui  # Freecad's PySide!
from pathlib import Path
import os

from freecad. _4d_overview_wb.core import CentralWindowOverview

class ProjectBrowser(QtWidgets.QWidget):
    """Main view to browse projects in the main folder containing all projects"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Project Browser")

        # --- Layout 
        layout = QtWidgets.QVBoxLayout(self)

        # --- select master folder ---
        top_bar = QtWidgets.QHBoxLayout()
        self.path_edit = QtWidgets.QLineEdit()
        self.path_edit.setPlaceholderText("Choose master folder")
        self.path_btn = QtWidgets.QPushButton("...")
        self.path_btn.clicked.connect(self.select_root_folder)
        top_bar.addWidget(self.path_edit, 1)
        top_bar.addWidget(self.path_btn)
        layout.addLayout(top_bar)

        # --- Zone scrollable  ---
        self.scroll = QtWidgets.QScrollArea()
        self.scroll.setWidgetResizable(True)
        layout.addWidget(self.scroll, 1)

        # --- grid container ---
        self.container = QtWidgets.QWidget()
        self.grid = QtWidgets.QGridLayout(self.container)
        self.grid.setSpacing(15)
        self.scroll.setWidget(self.container)

        # --- Label  ---
        self.info_label = QtWidgets.QLabel("first select a folder")
        layout.addWidget(self.info_label)

    # -------------------------------------------------------------------------
    def select_root_folder(self):
        """choose root project folder"""
        folder = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Select root folder", str(Path.home())
        )
        if folder:
            self.path_edit.setText(folder)
            self.load_projects(Path(folder))

    # -------------------------------------------------------------------------
    def load_projects(self, root_path: Path):
        """look at all subfolder to extract thumbnails"""
        for i in reversed(range(self.grid.count())):
            w = self.grid.itemAt(i).widget()
            if w:
                w.setParent(None)

        if not root_path.exists():
            self.info_label.setText(f"no folder{root_path}")
            return

        project_dirs = [p for p in root_path.iterdir() if p.is_dir()]
        if not project_dirs:
            self.info_label.setText("no project found in this folder")
            return
        
        # Reverse alphabetical and numerical order
        project_dirs.sort()
        project_dirs.reverse()

        cols = 3
        for idx, project_dir in enumerate(project_dirs):
            project_thumb = self.make_project_thumbnail(project_dir)
            project_thumb.clicked.connect(self.on_project_clicked)
            r, c = divmod(idx, cols)
            self.grid.addWidget(project_thumb, r, c)

        self.info_label.setText(f"{len(project_dirs)} projects detected")

    # -------------------------------------------------------------------------
    def make_project_thumbnail(self, project_dir: Path):
        """Grey (if empty) or mixed miniature generation """
        overview = project_dir / "4DOverview"
        thumbs = list(overview.glob("*.png"))

        if not thumbs:
            pix = QtGui.QPixmap(200, 200)
            pix.fill(QtGui.QColor("#cccccc"))  # grey if no images
            return ProjectThumbnail(project_dir, pix)

        # load 4 miniature max
        thumbs = thumbs[:4]
        size = 200
        composite = QtGui.QPixmap(size, size)
        composite.fill(QtGui.QColor("#f0f0f0"))
        painter = QtGui.QPainter(composite)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        n = len(thumbs)
        positions = {
            1: [(0, 0, size, size)],
            2: [(0, 0, size//2, size), (size//2, 0, size//2, size)],
            3: [(0, 0, size//2, size//2), (size//2, 0, size//2, size//2), (size//4, size//2, size//2, size//2)],
            4: [(0, 0, size//2, size//2), (size//2, 0, size//2, size//2),
                (0, size//2, size//2, size//2), (size//2, size//2, size//2, size//2)]
        }
        for thumb, pos in zip(thumbs, positions[n]):
            img = QtGui.QPixmap(str(thumb)).scaled(pos[2], pos[3],
                                                   QtCore.Qt.KeepAspectRatioByExpanding,
                                                   QtCore.Qt.SmoothTransformation)
            painter.drawPixmap(pos[0], pos[1], img)
        painter.end()

        return ProjectThumbnail(project_dir, composite)

    # -------------------------------------------------------------------------
    def on_project_clicked(self, project_path: str):

        self.info_label.setText(f"Project selected {Path(project_path).name}")
        # we open the Overview - View of the selected project
        CentralWindowOverview.makeView(project_path)



# ============================================================================
class ProjectThumbnail(QtWidgets.QFrame):
    """Clickable thumbnail representing an entire project"""
    clicked = QtCore.Signal(str)

    def __init__(self, project_dir: Path, pixmap: QtGui.QPixmap, size=200):
        super().__init__()
        self.project_dir = project_dir
        self.setFixedSize(size, size + 30)
        self.setCursor(QtCore.Qt.PointingHandCursor)
        self.setStyleSheet("""
            QFrame {
                border-radius: 8px;
                background-color: #fafafa;
            }
            QFrame:hover {
                border: 2px solid #0078d7;
                background-color: #eef6ff;
            }
            QLabel {
                font-size: 11px;
            }
        """)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        img_label = QtWidgets.QLabel()
        img_label.setPixmap(pixmap)
        img_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(img_label, 1)

        text_label = QtWidgets.QLabel(project_dir.name)
        text_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(text_label, 0)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.clicked.emit(str(self.project_dir))


# ============================================================================
def show_project_browser():
    mw = FreeCADGui.getMainWindow()
    mdi = mw.findChild(QtWidgets.QMdiArea)
    sub = mdi.addSubWindow(ProjectBrowser())
    sub.setWindowTitle("Project Browser")
    sub.showMaximized()
