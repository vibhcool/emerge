import info
from Package.CMakePackageBase import *

class subinfo(info.infoclass):
    def setTargets( self ):
        self.targets['0.7.3'] = 'http://code.compeng.uni-frankfurt.de/attachments/download/174/Vc-0.7.3.tar.gz'
        self.targetDigests['0.7.3'] = 'aa41aeddac59abc60f292de8fdedbe70a4b49108'
        self.targetInstSrc['0.7.3'] = "Vc-0.7.3"
        self.patchToApply['0.7.3'] = ("Vc-0.7.3-20140107.diff", 1)

        # Note: at the moment Vc does not provide a stable MSVC-compatible release.
        # Please update the default target to a tarball once one is made available.
        self.svnTargets['gitHEAD'] = 'https://github.com/VcDevel/Vc.git|0.7'
        self.targetSrcSuffix['gitHEAD'] = 'git'
        self.targetConfigurePath['gitHEAD'] = ''
        self.shortDescription = 'Portable, zero-overhead SIMD library for C++'
        self.defaultTarget = 'gitHEAD'

    def setDependencies( self ):
        self.buildDependencies['virtual/base'] = 'default'

class Package(CMakePackageBase):
    def __init__( self, **args ):
        CMakePackageBase.__init__( self )


        self.subinfo.options.configure.defines = " -DBUILD_TESTING=OFF "
        if compiler.isMSVC():
            self.subinfo.options.configure.defines += " -DCMAKE_CXX_FLAGS=/FS "
