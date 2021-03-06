import os
import shutil

import info


class subinfo(info.infoclass):
    def setDependencies( self ):
        self.buildDependencies['virtual/bin-base'] = 'default'

    def setTargets( self ):
        self.targets['2.46'] = 'http://downloads.sourceforge.net/sourceforge/nsis/nsis-2.46.zip'
        self.targetDigests['2.46'] = 'adeff823a1f8af3c19783700a6b8d9054cf0f3c2'
        self.defaultTarget = '2.46'

from Package.BinaryPackageBase import *

class Package(BinaryPackageBase):
    def __init__( self ):
        BinaryPackageBase.__init__(self)
        self.subinfo.options.merge.destinationPath = os.path.join("dev-utils")
        self.subinfo.options.merge.ignoreBuildType = True

    def install( self ):
        localFileDir = self.localFileNames()[0].replace(".zip", "")
        destPath = os.path.join (self.imageDir(), "nsis")
        os.makedirs (destPath, exist_ok=True)
        for f in os.listdir(os.path.join(self.workDir(), localFileDir)):
            shutil.move(os.path.join(self.workDir(), localFileDir, f), destPath)
        os.rmdir(os.path.join(self.workDir(), localFileDir))
        os.makedirs (os.path.join (self.imageDir(), "bin"), exist_ok=True)
        for f in ['makensis', 'makensisw', 'nsis']:
            shutil.copy(os.path.join(self.packageDir(), "wrapper.bat"), os.path.join(self.imageDir(), "bin", f + ".bat"))
        return True

