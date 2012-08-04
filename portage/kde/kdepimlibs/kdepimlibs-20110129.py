import info

class subinfo(info.infoclass):
    def setTargets( self ):
        self.svnTargets['gitHEAD'] = '[git]kde:kdepimlibs'
        for version in ['4.4', '4.5', '4.6', '4.7', '4.8', '4.9']:
            self.svnTargets[version] = '[git]kde:kdepimlibs|KDE/%s' % version
        self.defaultTarget = 'gitHEAD'

    def setDependencies( self ):
        self.dependencies['kde/kdelibs'] = 'default'
        self.dependencies['kdesupport/akonadi'] = 'default'
        self.dependencies['win32libs-sources/cyrus-sasl-src'] = 'default'
        self.dependencies['win32libs-sources/boost-src'] = 'default'
        self.dependencies['win32libs-sources/libical-src'] = 'default'
        self.dependencies['binary/gpg4win-e5'] = 'default'
        self.dependencies['win32libs-bin/openldap'] = 'default'
        self.shortDescription = "the base libraries for PIM related services"

from Package.CMakePackageBase import *

class Package(CMakePackageBase):
    def __init__( self ):
        self.subinfo = subinfo()
        CMakePackageBase.__init__( self )

if __name__ == '__main__':
    Package().execute()
