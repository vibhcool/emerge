# -*- coding: utf-8 -*-
import info
from Package.CMakePackageBase import *


class subinfo(info.infoclass):
    def setTargets( self ):
        self.svnTargets['gitHEAD'] = '[git]kde:kphotoalbum.git'

        self.defaultTarget = 'gitHEAD'

    def setDependencies( self ):
        self.dependencies['kde/kdegraphics'] = 'default'

class Package(CMakePackageBase):
    def __init__( self):
        CMakePackageBase.__init__(self)

