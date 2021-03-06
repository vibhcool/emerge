#
# copyright (c) 2012 Hannah von Reth <vonreth@kde.org>
#
import EmergeDebug
from Package.PackageBase import *
from Source.MultiSource import *
from BuildSystem.Qt5CoreBuildSystem import *
from Packager.TypePackager import *

class Qt5CorePackageBase (PackageBase, MultiSource, Qt5CoreBuildSystem, TypePackager):
    """provides a base class for qt5 modules"""
    def __init__(self):
        EmergeDebug.debug("Qt5CorePackageBase.__init__ called", 2)
        PackageBase.__init__(self)
        MultiSource.__init__(self)
        Qt5CoreBuildSystem.__init__(self)
        TypePackager.__init__(self)
