import info
import compiler
class subinfo(info.infoclass):
    def setTargets( self ):
        self.svnTargets['gitHEAD'] = '[git]kde:kde-runtime'
        for version in ['4.4', '4.5', '4.6', '4.7', '4.8', '4.9']:
            self.svnTargets[version] = '[git]kde:kde-runtime|KDE/%s' % version
            self.patchToApply[version] = [('Kwallet-Autoallow-access-for-every-application.patch', 1)]
        self.defaultTarget = 'gitHEAD'

    def setDependencies( self ):
        self.dependencies['kde/kdelibs'] = 'default'
        self.dependencies['kde/kactivities'] = 'default'
        self.dependencies['kdesupport/oxygen-icons'] = 'default'
        self.dependencies['win32libs-bin/libssh'] = 'default'
        self.dependencies['kde/kactivities'] = 'default'
        self.dependencies['kde/kdepimlibs'] = 'default'
        self.dependencies['kde/nepomuk-core'] = 'default'
        if compiler.isMinGW_WXX():
            self.dependencies['win32libs-bin/libbfd'] = 'default'

from Package.CMakePackageBase import *

class Package(CMakePackageBase):
    def __init__( self ):
        self.subinfo = subinfo()
        CMakePackageBase.__init__( self )

if __name__ == '__main__':
    Package().execute()
