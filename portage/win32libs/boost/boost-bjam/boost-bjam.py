import info
class subinfo(info.infoclass):
    def setTargets(self):
        self.versionInfo.setDefaultValues("", tarballInstallSrc = self.package.replace("boost-","").replace("-", "_") )

        self.homepage = 'http://www.boost.org/'

        self.shortDescription = 'portable C++ libraries'


    def setDependencies( self ):
        self.buildDependencies['virtual/base'] = 'default'
        self.dependencies['win32libs/boost-headers'] = 'default'


from Package.BoostPackageBase import *

class Package(BoostPackageBase):
    def __init__(self, **args):
        BoostPackageBase.__init__(self)

    def install(self):
        for root, dirs, files in os.walk( os.path.join( portage.getPackageInstance( 'win32libs',
                'boost-headers' ).sourceDir(), "tools", "build", "v2", "engine" ) ):
            if "bjam.exe" in files:
                utils.copyFile( os.path.join( root, "bjam.exe" ),
                               os.path.join( self.imageDir(), "bin", "bjam.exe" ) )
        return True

    def make(self):
        cmd  = "build.bat "
        if compiler.isMinGW():
            cmd += "gcc"
        else:
            if compiler.isMSVC2005():
                cmd += "vc8"
            elif compiler.isMSVC2008():
                cmd += "vc9"
            elif compiler.isMSVC2010():
                cmd += "vc10"
        if utils.verbose() >= 1:
            print(cmd)
        utils.system(cmd, cwd = os.path.join(portage.getPackageInstance('win32libs',
                'boost-headers').sourceDir(),"tools","build","v2","engine")) or utils.die(
                "command: %s failed" % (cmd))
        return True


