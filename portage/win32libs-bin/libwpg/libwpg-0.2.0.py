# This package-script is automatically updated by the script win32libsupdater.py
# which can be found in your emerge/bin folder. To update this package, run
# win32libsupdater.py (and commit the results)
# based on revision git8d98549fa35d1051e68f25f7d709440a5ea796a7

from Package.BinaryPackageBase import *
import os
import info

class subinfo( info.infoclass ):
    def setTargets( self ):
        repoUrl = 'http://downloads.sourceforge.net/kde-windows'

        for version in [ '0.2.0' ]:
            self.targets[ version ]          = self.getPackage( repoUrl, 'libwpg', version )
            self.targetDigestUrls[ version ] = self.getPackage( repoUrl, 'libwpg', version, '.tar.bz2.sha1' )

        self.defaultTarget = '0.2.0'


    def setDependencies( self ):
        if not utils.envAsBool( 'EMERGE_ENABLE_IMPLICID_BUILDTIME_DEPENDENCIES' ):
            self.buildDependencies[ 'gnuwin32/wget' ] = 'default'
        self.runtimeDependencies[ 'win32libs-bin/libwpd' ] = 'default'


    def setBuildOptions( self ):
        self.disableHostBuild = False
        self.disableTargetBuild = True

class Package(BinaryPackageBase):
  def __init__(self):
    self.subinfo = subinfo()
    BinaryPackageBase.__init__( self )

if __name__ == '__main__':
    Package().execute()
