import info


class subinfo(info.infoclass):
    def setTargets( self ):
        self.versionInfo.setDefaultValues( )

        self.shortDescription = "KWidgetsAddons"
        

    def setDependencies( self ):
        self.buildDependencies["virtual/base"] = "default"
        self.buildDependencies["dev-util/extra-cmake-modules"] = "default"
        self.dependencies["libs/qtbase"] = "default"
        self.dependencies["libs/qttools"] = "default"
        self.dependencies["libs/qttools"] = "default"

from Package.CMakePackageBase import *

class Package(CMakePackageBase):
    def __init__( self ):
        CMakePackageBase.__init__( self )


    

