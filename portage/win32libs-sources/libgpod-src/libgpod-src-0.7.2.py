import os
from shells import MSysShell
import info


class subinfo(info.infoclass):
    def setDependencies( self ):
        self.buildDependencies['dev-util/msys'] = 'default'
        self.dependencies['testing/glib-pkg'] = 'default'
        self.buildDependencies['dev-util/pkg-config'] = 'default'
        self.dependencies['win32libs-bin/sqlite'] = 'default'
        self.dependencies['testing/libplist-src'] = 'default'
        self.dependencies['dev-util/intltool'] = 'default'

    def setTargets( self ):
        for ver in ['0.7.2','0.8.0']:
            self.targets[ver] = 'http://downloads.sourceforge.net/sourceforge/gtkpod/libgpod-%s.tar.gz' % ver
            self.targetInstSrc[ver] = 'libgpod-%s' % ver
        self.patchToApply['0.7.2'] = ("libgpod-0.7.2.diff", 1)
        
        self.targetDigests['0.8.0'] = 'ddef7f3583535242b4928b300eb8aa6bc9a0e6dc'


        self.options.package.withCompiler = False
        self.shortDescription = "a library to access the contents of an iPod"
        self.defaultTarget = '0.8.0'

from Package.AutoToolsPackageBase import *

class Package(AutoToolsPackageBase):
    def __init__( self, **args ):
        self.subinfo = subinfo()
        AutoToolsPackageBase.__init__(self)
        self.subinfo.options.package.withCompiler = False
        self.subinfo.options.configure.defines = """--with-python=no --disable-static """
        
if __name__ == '__main__':
     Package().execute()
