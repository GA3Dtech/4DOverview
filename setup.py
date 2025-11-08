from setuptools import setup
import os

version_path = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                            "freecad", "_4d_overview_wb", "version.py")
with open(version_path) as fp:
    exec(fp.read())

setup(name='freecad._4d_overview_wb',
      version=str(__version__),
      packages=['freecad',
                'freecad._4d_overview_wb'],
      maintainer="GA3Dtech - Alain D. G.",
      maintainer_email="ga3d.tech2021@gmail.com",
      url="https://github.com/GA3Dtech/4DOverview",
      description="(4DOverview: A K.I.S.S. FreeCAD Workbench for easy file management, including overview, Time Travel, Assets, Bill of Process, Bill of Materials, and more.)",
      install_requires=[('numpy',)],
      include_package_data=True)
