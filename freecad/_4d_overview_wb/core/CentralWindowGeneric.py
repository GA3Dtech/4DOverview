
import FreeCADGui
from PySide import QtWidgets  # FreeCAD's PySide!


class CentralView(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        layout = QtWidgets.QVBoxLayout(self)
        label = QtWidgets.QLabel("<h2>Overview Generic Window</h2>")
        button = QtWidgets.QPushButton("Click me")
        layout.addWidget(label)
        layout.addWidget(button)
        button.clicked.connect(lambda: label.setText("Hello :)"))


def make_view() :
    """Create and insert a central view."""
    mw = FreeCADGui.getMainWindow()
    mdi = mw.findChild(QtWidgets.QMdiArea)
    sub = mdi.addSubWindow(CentralView())
    sub.setWindowTitle("Overview")
    sub.showMaximized()
