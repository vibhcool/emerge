import info

class subinfo(info.infoclass):
    def setTargets( self ):
        self.targets['3.1.6-1'] = "http://downloads.sourceforge.net/sourceforge/gnuwin32/gawk-3.1.6-1-bin.zip"
        self.targetDigests['3.1.6-1'] = 'bda507655eb3d15059d8a55a0daf6d697a15f632'
        self.defaultTarget = '3.1.6-1'

    def setDependencies( self ):
        self.buildDependencies['virtual/bin-base'] = 'default'

from Package.BinaryPackageBase import *

class Package(BinaryPackageBase):
    def __init__( self):
        BinaryPackageBase.__init__(self)
        self.subinfo.options.merge.ignoreBuildType = True
        self.subinfo.options.merge.destinationPath = "dev-utils"

