
import FreeCADGui
import FreeCAD
from PySide6 import QtWidgets
import os
import string, zipfile

class CentralView(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        layout = QtWidgets.QVBoxLayout(self)
        label = QtWidgets.QLabel("<h2>Project Overview</h2>")
       #button = QtWidgets.QPushButton("Click me")
        layout.addWidget(label)
        #layout.addWidget(button)
        #button.clicked.connect(lambda: label.setText("Hello :)"))

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


# --- function to execute for each file .fcstd ---
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
                        with open(png_path, "wb") as out:
                            out.write(thumb.read())
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

        FreeCAD.Console.PrintMessage(f"Version {new_version} sauvegardée dans {project_dir}\n")

# --- Incremental File Naming
def increment_version(last_version):
    """Incrémente une version sur deux lettres minuscules : 'aa' -> 'ab', ..., 'az' -> 'ba'"""
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
    
def makeView() :

    # create and insert central view
    mw = FreeCADGui.getMainWindow()
    mdi = mw.findChild(QtWidgets.QMdiArea)
    sub = mdi.addSubWindow(CentralView())
    sub.setWindowTitle("Overview")
    sub.showMaximized()