import info

class subinfo( info.infoclass ):
    def setTargets( self ):
        self.svnTargets['gitHEAD'] = '[git]kde:kdepim'
        for version in ['4.4', '4.5', '4.6', '4.7', '4.8', '4.9']:
            self.svnTargets[version] = '[git]kde:kdepim|KDE/%s' % version
        self.defaultTarget = 'gitHEAD'

        # Workaround BUG 302342
        self.patchToApply['gitHEAD'] = ('fix_introduction_screen.diff', 1)

        self.patchToApply['4.8'] = [
                ('add-full-shutdown-button.patch', 1),
                ('fix_introduction_screen.diff', 1)]

        # To platform/package specific for master
        self.apply_branding("EMERGE_KDEPIME5_BRANDING_PATCHES")

    def setDependencies( self ):
        self.runtimeDependencies['kde/kde-runtime'] = 'default'
        self.runtimeDependencies['kde/kdepim-runtime'] = 'default'
        self.dependencies['kde/kdepimlibs'] = 'default'
        self.dependencies['kdesupport/grantlee'] = 'default'
        self.dependencies['win32libs-bin/sqlite'] = 'default'
        self.shortDescription = "KDE's Personal Information Management suite"

    def apply_branding( self, envVar ):
        """ Apply all Patches from the directory set as envVar """
        brandingDir = os.getenv( envVar )
        if not brandingDir:
            return
        else:
            brandingPatches = []
            for fname in os.listdir( brandingDir ):
                if fname.endswith(".patch") or fname.endswith( ".diff" ):
                    brandingPatches.append( (
                        os.path.join(brandingDir, fname), 1 ) )
            for target in self.svnTargets:
                if self.patchToApply.get(target):
                    self.patchToApply[target] += brandingPatches
                else:
                    self.patchToApply[target] = brandingPatches

from Package.CMakePackageBase import *

class Package( CMakePackageBase ):
    def __init__( self ):
        self.subinfo = subinfo()
        CMakePackageBase.__init__( self )
        self.subinfo.options.configure.defines = (
                    " -DKDEPIM_ENTERPRISE_BUILD=ON ")

    def qmerge( self ):
        ret = CMakePackageBase.qmerge(self)
        if self.isTargetBuild():
            mime_update = os.path.join(ROOTDIR, "bin",
                    "update-mime-database.exe")
            if os.path.isfile(mime_update):
                target_mimedb = os.path.join(ROOTDIR, self.buildPlatform(),
                        "share", "mime")
                utils.debug("calling update-mime-database: on %s " %\
                        target_mimedb, 1)
                cmd = "%s %s" % (mime_update, target_mimedb)
                return utils.system(cmd)
        return ret

if __name__ == '__main__':
    Package().execute()
