
import FreeCADGui
import FreeCAD
from PySide6 import QtWidgets
import os

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
    # Exemple : affiche le nombre d'objets dans le document
    print(f"Document {doc.Name} \n")
    
def makeView() :

    # create and insert central view
    mw = FreeCADGui.getMainWindow()
    mdi = mw.findChild(QtWidgets.QMdiArea)
    sub = mdi.addSubWindow(CentralView())
    sub.setWindowTitle("Overview")
    sub.showMaximized()