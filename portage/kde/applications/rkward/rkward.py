import os
import subprocess
import info

class subinfo( info.infoclass ):
    def setTargets( self ):
        self.svnTargets[ 'gitHEAD' ] =  '[git]kde:rkward|frameworks'
        for ver in ['0.6.4']:
            self.targets[ver] = 'http://download.kde.org/stable/rkward/' + ver + '/rkward-' + ver + '.tar.gz'
            self.targetInstSrc[ ver] = 'rkward-' + ver
        self.defaultTarget = 'gitHEAD'

    def setDependencies( self ):
        self.dependencies[ 'binary/r-base' ] = 'default'
        if self.buildTarget in ['0.6.4', '0.6.5']:
            # Hm, will this still work at all? kate port does not seem to provide KDE 4 version, anymore
            self.dependencies[ 'kde/kate' ] = 'default'  # provides katepart
        else:
            self.dependencies["frameworks/ki18n"] = "default"
            self.dependencies["frameworks/ktexteditor"] = "default"
            self.dependencies["frameworks/kwindowsystem"] = "default"
            self.dependencies["frameworks/kdewebkit"] = "default"
            # not strictly dependencies, but should be included in the package
            self.dependencies["kde/kate"] = "default"
            self.dependencies["frameworks/breeze-icons"] = "default"

from Source.GitSource import *

class RKTranslations( GitSource ):
    def __init__( self, rkwardPackage ):
        GitSource.__init__( self )
        self.rkwardPackage = rkwardPackage

    def repositoryUrl( self ):
        return "[git]kde:scratch/tfry/rkward-po-export"

    def checkoutDir( self ):
        """ clone _into_ the RKWard source tree """
        return os.path.join( self.rkwardPackage.checkoutDir(), "i18n", "po")

    def sourceDir( self ):
        return self.checkoutDir( self )

from Package.CMakePackageBase import *
from Packager.NullsoftInstallerPackager import *

class Package( CMakePackageBase):
    def __init__( self ):
        CMakePackageBase.__init__( self )
        self.blacklist_file = [
            NSIPackagerLists.runtimeBlacklist  #, os.path.join(os.path.dirname(__file__), 'blacklist.txt')
        ]
        self.changePackager(NullsoftInstallerPackager)

        if compiler.isX64():
            self.r_dir = os.path.join( self.mergeDestinationDir(), "lib", "R", "bin", "x64" )
        else:
            self.r_dir = os.path.join( self.mergeDestinationDir(), "lib", "R", "bin", "i386" )
        self.subinfo.options.configure.defines = " -DR_EXECUTABLE=" + os.path.join (self.r_dir, "R.exe").replace( "\\\\", "/" )
        if compiler.isMSVC():
            self.realconfigure = self.configure
            self.configure = self.msvcconfigure

    def fetch( self ):
        ret = CMakePackageBase.fetch( self )
        EmergeDebug.info( "Fetching translations" )
        RKTranslations( self ).fetch()
        return ret

    def install( self ):
        # Make installation movable, by providing rkward.ini with relative path to R
        ret = CMakePackageBase.install( self )
        rkward_ini = open( os.path.join( self.imageDir(), "bin", "rkward.ini" ), "w" )
        if compiler.isX64():
            rkward_ini.write( "R executable=../lib/R/bin/x64/R.exe\n" )
        else:
            rkward_ini.write( "R executable=../lib/R/bin/i386/R.exe\n" )
        rkward_ini.close()
        return ret

    def msvcconfigure( self ):
        # Need to create a .lib-file for R.dll, first
        dump = subprocess.check_output(["dumpbin", "/exports", os.path.join(self.r_dir, "R.dll")]).decode("latin1").splitlines ()
        exports = []
        for line in dump:
            fields = line.split ()
            if len (fields) != 4:
                continue
            exports.append(fields[3])
        self.enterBuildDir()
        deffile = open(os.path.join(self.buildDir(), "R.def"), 'w')
        deffile.write("EXPORTS\r\n")
        deffile.write("\r\n".join(exports) + "\r\n")
        deffile.close()
        subprocess.call(["lib", "/def:R.def", "/out:R.lib", "/machine:x86"])

        # Now configure as usual.
        return self.realconfigure()

    def createPackage(self):
        self.defines[ "productname" ] = "RKWard"
        self.defines[ "executable" ] = "bin\\rkward.exe"
        self.defines[ "icon" ] = os.path.join(self.sourceDir(), "rkward", "icons", "app-icon", "rkward.ico")

        self.ignoredPackages.append("binary/mysql-pkg")

        return TypePackager.createPackage(self)
