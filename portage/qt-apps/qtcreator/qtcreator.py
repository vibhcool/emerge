# -*- coding: utf-8 -*-
import info

class subinfo(info.infoclass):
    def setTargets( self ):       
        self.svnTargets[ "gitHEAD" ] = "git://code.qt.io/qt-creator/qt-creator.git"
        self.targets[ "4.0.2" ] = "http://download.qt-project.org/official_releases/qtcreator/4.0/4.0.2/qt-creator-opensource-src-4.0.2.tar.gz"
        self.targetDigests['4.0.2'] = 'ef7c5760d7dc72cb68ee1ddf84cb4245e41c39d5'
        self.targetInstSrc[ "4.0.2" ] = "qt-creator-opensource-src-4.0.2"
        self.defaultTarget = "4.0.2"

    def setDependencies( self ):
        self.dependencies['libs/qtbase'] = 'default'


from Package.Qt5CorePackageBase import *

class Package( Qt5CorePackageBase ):
    def __init__( self, **args ):
        Qt5CorePackageBase.__init__( self )

