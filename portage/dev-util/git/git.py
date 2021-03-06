# -*- coding: utf-8 -*-
import tempfile

import EmergeDebug
import info
import utils


class subinfo(info.infoclass):
    def setTargets( self ):
        ver = "2.7.4"
        arch = 32
        if compiler.isX64():
            arch = 64

        self.targets[ver]  ="https://github.com/git-for-windows/git/releases/download/v%s.windows.1/PortableGit-%s-%s-bit.7z.exe" % (ver, ver, arch)
        self.archiveNames[ver] = "PortableGit-%s-%s-bit.7z" % (ver, arch)
        self.targetInstallPath[ ver ] = "git"
        self.defaultTarget = ver

    def setDependencies(self):
        self.buildDependencies['dev-util/7zip']   = 'default'

from Package.BinaryPackageBase import *

class Package(BinaryPackageBase):
    def __init__( self):
        BinaryPackageBase.__init__(self)
        self.subinfo.options.merge.destinationPath = "dev-utils"

    def install( self ):
        if not BinaryPackageBase.install(self):
            return False
        utils.copyFile(os.path.join(self.packageDir(),"git.exe"),os.path.join(self.imageDir(),"bin","git.exe"))
        return True

    def qmerge(self):
        if not BinaryPackageBase.qmerge(self):
            return False
        gitbash = os.path.join(self.rootdir, "dev-utils", "git", "git-bash.exe")
        utils.system( "%s --no-needs-console --hide --no-cd --command=post-install.bat" % gitbash, cwd = os.path.join( EmergeStandardDirs.emergeRoot(), "dev-utils", "git"))
        tmpFile = tempfile.TemporaryFile()
        git = os.path.join(self.rootdir,"dev-utils","git","bin","git")
        utils.system( "%s config --global --get url.git://anongit.kde.org/.insteadof" % git,
                      stdout=tmpFile, stderr=tmpFile  )
        tmpFile.seek( 0 )
        for line in tmpFile:
            if str(line,'UTF-8').find("kde:")>-1:
                return True
        EmergeDebug.debug("adding kde related settings to global git config file", 1)
        utils.system( "%s config --global url.git://anongit.kde.org/.insteadOf kde:" % git)
        utils.system( "%s config --global url.ssh://git@git.kde.org/.pushInsteadOf kde:" % git)
        utils.system( "%s config --global core.autocrlf false" % git)
        utils.system( "%s config --system core.autocrlf false" % git)
        return True

