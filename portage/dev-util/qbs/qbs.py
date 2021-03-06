# -*- coding: utf-8 -*-
import info


class subinfo(info.infoclass):
    def setTargets( self ):       
        self.targets["1.4.4"] = "http://download.qt.io/official_releases/qbs/1.4.4/qbs-src-1.4.4.tar.gz"
        self.targetInstSrc["1.4.4"] = "qbs-src-1.4.4"
        self.targetDigestUrls["1.4.4"] = (["http://download.qt.io/official_releases/qbs/1.4.4/qbs-src-1.4.4.tar.gz.sha256"], EmergeHash.HashAlgorithm.SHA256)

        self.svnTargets["master"] = "git://code.qt.io/qt-labs/qbs.git"
        self.defaultTarget = "1.4.4"

    def setDependencies( self ):
        self.dependencies['libs/qtbase'] = 'default'


from Package.Qt5CorePackageBase import *

class Package( Qt5CorePackageBase ):
    def __init__( self, **args ):
        Qt5CorePackageBase.__init__( self )
        self.subinfo.options.qmake.proFile = "qbs.pro"
        self.subinfo.options.configure.defines = " \"QBS_INSTALL_PREFIX = %s\" " % EmergeStandardDirs.emergeRoot().replace("\\", "/")


