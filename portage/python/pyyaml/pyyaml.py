# -*- coding: utf-8 -*-
import info
from Package.PipPackageBase import *


class subinfo(info.infoclass):
    #def setDependencies( self ):

    def setTargets( self ):
        self.svnTargets['gitHEAD'] = ''
        self.shortDescription = "PyYAML is a Python module that implements the next generation YAML parser and emitter."
        self.defaultTarget = 'gitHEAD'


class Package( PipPackageBase ):
    def __init__( self, **args ):
        PipPackageBase.__init__(self)