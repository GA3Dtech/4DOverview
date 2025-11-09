
import FreeCADGui
import FreeCAD
from PySide6 import QtWidgets , QtCore, QtGui
import os
import string, zipfile
from pathlib import Path



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
        THUMB_DIR =  Path(self.projectfolderpath)

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
        

def save_incremented_version(doc):
    """
      Sauvegarde une version incrementee d'un document FreeCAD (.FCStd)
    dans <chemin_du_fichier>/4DOverview/.NomDuFichier/
    avec extraction du thumbnail ou capture si absent.
    
    Usage :
        save_incremented_version(FreeCAD.ActiveDocument)
    """
    import FreeCAD, FreeCADGui, zipfile, string, os
    from pathlib import Path

    # --- document validation
    if not doc or not doc.FileName:
        FreeCAD.Console.PrintError("document not found \n")
        return

    filepath = Path(doc.FileName)
    dirname = filepath.parent
    basename = filepath.stem

    # --- Dossiers de sauvegarde 
    overview_dir = dirname / "4DOverview"
    project_dir = overview_dir / f".{basename}"
    project_dir.mkdir(parents=True, exist_ok=True)

    # --- search the older versions
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

    # --- main Save
    doc.save()

    # --- full path
    fcstd_path = project_dir / f"{basename}_{new_version}.FCStd"
    png_path = project_dir / f"{basename}_{new_version}.png"

    # --- version saved
    doc.saveCopy(str(fcstd_path))
    FreeCAD.Console.PrintMessage(f" versionned file {fcstd_path}\n")

    # --- Extraction of thumbnail 
    try:
        with zipfile.ZipFile(fcstd_path, 'r') as z:
            thumb_candidates = [f for f in z.namelist() if f.lower().endswith("thumbnail.png")]
            if thumb_candidates:
                with z.open(thumb_candidates[0]) as thumb:
                    with open(png_path, "wb") as out:
                        out.write(thumb.read())
                FreeCAD.Console.PrintMessage("thumbnail extracted \n")
            else:
                raise FileNotFoundError
    except Exception:
        FreeCAD.Console.PrintMessage("no thumb found\n")
        try:
            view = FreeCADGui.ActiveDocument.ActiveView
            view.saveImage(str(png_path), 1024, 768, "Transparent")
        except Exception as e:
            FreeCAD.Console.PrintError(f"error capture {e}\n")

    FreeCAD.Console.PrintMessage(f" Version {new_version} saved in   {project_dir}\n")


        

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
    
def makeView(folderpath) :

    # create and insert central view
    mw = FreeCADGui.getMainWindow()
    mdi = mw.findChild(QtWidgets.QMdiArea)
    sub = mdi.addSubWindow(CentralView(folderpath))
    sub.setWindowTitle("TimeLine")
    sub.showMaximized()