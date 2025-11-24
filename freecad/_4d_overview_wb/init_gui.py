import os
import FreeCADGui as Gui
import FreeCAD as App

#core function of the wb loading
from freecad. _4d_overview_wb.core import StartDockWidget

translate=App.Qt.translate
QT_TRANSLATE_NOOP=App.Qt.QT_TRANSLATE_NOOP

ICONPATH = os.path.join(os.path.dirname(__file__), "resources")
TRANSLATIONSPATH = os.path.join(os.path.dirname(__file__), "resources", "translations")

# Add translations path
Gui.addLanguagePath(TRANSLATIONSPATH)
Gui.updateLocale()

class _4DOverviewWB(Gui.Workbench):
    """
    class which gets initiated at startup of the gui
    """
    MenuText = translate("Workbench", "4D Overview")
    ToolTip = translate("Workbench", "a simple 4D Overview")
    Icon = os.path.join(ICONPATH, "4doverview.svg")
    toolbox = []

    def GetClassName(self):
        return "Gui::PythonWorkbench"

    def Initialize(self):
        """
        This function is called at the first activation of the workbench.
        here is the place to import all the commands
        """
        # NOTE: Context for this commands must be "Workbench".
        self.appendToolbar(QT_TRANSLATE_NOOP("Workbench", "Tools"), self.toolbox)
        self.appendMenu(QT_TRANSLATE_NOOP("Workbench", "Tools"), self.toolbox)

    def Activated(self):
        '''
        code which should be computed when a user switch to this workbench
        '''
        StartDockWidget.start()

    def Deactivated(self):
        '''
        code which should be computed when this workbench is deactivated
        '''
        pass

Gui.addWorkbench(_4DOverviewWB())
