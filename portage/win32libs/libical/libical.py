import info

class subinfo(info.infoclass):
    def setTargets( self ):
        self.svnTargets['svnHEAD'] = 'libical'
        for v in [ '0.41', '0.42', '0.43', '0.44']:
            self.targets[ v ] = 'http://downloads.sourceforge.net/freeassociation/libical-' + v + '.tar.gz'
            self.targetInstSrc[ v ] = 'libical-' + v
        self.defaultTarget = '0.44'
        self.targetDigests['0.44'] = 'f781150e2d98806e91b7e0bee02abdc6baf9ac7d'
        self.patchToApply['0.44'] = [ ( 'libical-0.44-20100728.diff', 1 ),
                                      ( 'libical-0.44-20130614.diff', 1 ) ]
        self.shortDescription = "reference implementation of the icalendar data type and serialization format"

    def setDependencies( self ):
        self.buildDependencies['virtual/base'] = 'default'

from Package.CMakePackageBase import *

class Package(CMakePackageBase):
    def __init__( self, **args ):
        CMakePackageBase.__init__( self )
        self.subinfo.options.configure.defines = " -DUSE_BUILTIN_TZDATA=true -DICAL_UNIX_NEWLINE=false "

