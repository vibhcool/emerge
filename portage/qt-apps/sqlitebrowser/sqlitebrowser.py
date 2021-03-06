# -*- coding: utf-8 -*-
import os

import info
from Package.CMakePackageBase import *

from EmergeOS.osutils import OsUtils


class subinfo(info.infoclass):
    def setTargets( self ):
        self.targets['3.8.0'] = 'https://github.com/sqlitebrowser/sqlitebrowser/archive/v3.8.0.tar.gz'
        self.archiveNames['3.8.0'] = "sqlitebrowser-3.8.0.tar.gz"
        self.targetInstSrc[ '3.8.0' ] = 'sqlitebrowser-3.8.0'
        self.targetDigests['3.8.0'] = (['f638a751bccde4bf0305a75685e2a72d26fc3e3a69d7e15fd84573f88c1a4d92'], EmergeHash.HashAlgorithm.SHA256)
        
        self.defaultTarget = '3.8.0'
        self.shortDescription = "DB Browser for SQLite"


    def setDependencies( self ):
        self.dependencies['libs/qtbase'] = 'default'


class Package( CMakePackageBase ):
    def __init__( self, **args ):
        CMakePackageBase.__init__(self)
        self.subinfo.options.configure.defines = "-DUSE_QT5=ON"
