import info


class subinfo(info.infoclass):
    def setDependencies( self ):
        self.buildDependencies['virtual/base'] = 'default'
        self.dependencies['libs/qtbase'] = 'default'
        # qtquick1 is optional
        #self.dependencies['libs/qtquick1'] = 'default'

    def setTargets( self ):
        self.svnTargets['gitHEAD'] = '[git]kde:phonon'        
        for ver in ['4.7.0','4.7.1', '4.8.0', '4.8.1', '4.8.2']:
            self.targets[ver] = 'http://download.kde.org/stable/phonon/%s/phonon-%s.tar.xz' % (ver ,ver)
            self.targetInstSrc[ver] = 'phonon-%s' % ver       
        for ver in ['4.8.3']:
            self.targets[ver] = 'http://download.kde.org/stable/phonon/%s/src/phonon-%s.tar.xz' % (ver ,ver)
            self.targetInstSrc[ver] = 'phonon-%s' % ver
        self.patchToApply['4.7.0'] = ("phonon-4.7.0-fix-dll-linkage.diff", 1) # upstream
        self.targetDigests['4.7.0'] = 'feda28afe016fe38eb253f2be01973fc0226d10f'
        self.targetDigests['4.7.1'] = 'f1d3214a752d97028dc4ed910a832c1272951522'
        self.targetDigests['4.8.0'] = 'b01da88ddba0d2d501bf1b6bb86abbff61ab6a12'
        self.targetDigests['4.8.1'] = '652872be8144c88974aa1992de5ae705a90e3be1'
        self.targetDigests['4.8.3'] = 'aac5dc44ae4821e6165c6735b9c6063dd111ac03'
        
        self.shortDescription = "a Qt based multimedia framework"
        self.defaultTarget = 'gitHEAD'

from Package.CMakePackageBase import *

class Package(CMakePackageBase):
    def __init__( self ):
        CMakePackageBase.__init__( self )
        self.subinfo.options.configure.defines = " -DPHONON_BUILD_EXAMPLES=OFF -DPHONON_BUILD_TESTS=OFF -DPHONON_INSTALL_QT_EXTENSIONS_INTO_SYSTEM_QT=ON -DPHONON_BUILD_PHONON4QT5=ON"
        if not self.subinfo.options.isActive("win32libs/dbus"):
            self.subinfo.options.configure.defines += " -DPHONON_NO_DBUS=ON "
            

        
