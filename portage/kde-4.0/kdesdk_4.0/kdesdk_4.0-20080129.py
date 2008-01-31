import base
import utils
import os
import sys
import info

class subinfo(info.infoclass):
    def setTargets( self ):
        self.svnTargets['4.0.0'] = 'tags/KDE/4.0.0/kdesdk'
        self.svnTargets['4.0.1'] = 'tags/KDE/4.0.1/kdesdk'
        self.svnTargets['svnHEAD'] = 'branches/KDE/4.0/kdesdk'
        self.defaultTarget = 'svnHEAD'
    
    def setDependencies( self ):
        self.hardDependencies['kde-4.0/kdebase_4.0'] = 'default'
        
class subclass(base.baseclass):
    def __init__(self):
        base.baseclass.__init__( self, "" )
        self.instsrcdir = "kdesdk"
        self.subinfo = subinfo()
        self.kdeCustomDefines = ""
#        self.kdeCustomDefines = self.kdeCustomDefines + "-DBUILD_kate=OFF "
#        self.kdeCustomDefines = self.kdeCustomDefines + "-DBUILD_kapptemplate=OFF "
#        self.kdeCustomDefines = self.kdeCustomDefines + "-DBUILD_kbugbuster=OFF "
#        self.kdeCustomDefines = self.kdeCustomDefines + "-DBUILD_kcachegrind=OFF "
#        self.kdeCustomDefines = self.kdeCustomDefines + "-DBUILD_kdeaccounts-plugin=OFF "
#        self.kdeCustomDefines = self.kdeCustomDefines + "-DBUILD_kdepalettes=OFF "
#        self.kdeCustomDefines = self.kdeCustomDefines + "-DBUILD_strigi-analyzer=OFF "
#        self.kdeCustomDefines = self.kdeCustomDefines + "-DBUILD_kioslave=OFF "
#        self.kdeCustomDefines = self.kdeCustomDefines + "-DBUILD_kmtrace=OFF "
#        self.kdeCustomDefines = self.kdeCustomDefines + "-DBUILD_kprofilemethod=OFF "
#        self.kdeCustomDefines = self.kdeCustomDefines + "-DBUILD_kuiviewer=OFF "
#        self.kdeCustomDefines = self.kdeCustomDefines + "-DBUILD_poxml=OFF "
#        self.kdeCustomDefines = self.kdeCustomDefines + "-DBUILD_scripts=OFF "
#        self.kdeCustomDefines = self.kdeCustomDefines + "-DBUILD_umbrello=OFF "
#        self.kdeCustomDefines = self.kdeCustomDefines + "-DBUILD_doc=OFF "
        

    def unpack( self ):
        return self.kdeSvnUnpack()

    def compile( self ):
        return self.kdeCompile()

    def install( self ):
        return self.kdeInstall()

    def make_package( self ):
        return self.doPackaging( "kdesdk", os.path.basename(sys.argv[0]).replace("kdesdk_4.0-", "").replace(".py", ""), True )

if __name__ == '__main__':
    subclass().execute()
