#
# copyright (c) 2009 Ralf Habacker <ralf.habacker@freenet.de>
#
import EmergeDebug
import utils

from Source.SourceFactory import *

class MultiSource(object):
    """ provides multi source type api """
    def __init__(self):
        object.__init__(self)
        EmergeDebug.trace("MultiSource __init__", 2)
        self.__source = None

    @property
    def source(self):
        # pylint: disable=E1101
        # multiple inheritance: MultiSource is never the only
        # superclass, others define self.source, self.subinfo etc.
        # TODO: This code should mostly be in the class defining self.source etc.
        if not self.__source:
            self.__source = SourceFactory(self.subinfo)
            self.__source.localFileNames = self.localFileNames.__get__(self, MultiSource)
        return self.__source

    def localFileNames( self ):
        EmergeDebug.trace("MultiSource localFileNames", 2)
        if self.subinfo.archiveName() == "":
            return self.source.localFileNamesBase()
        if isinstance(self.subinfo.archiveName(), (list, tuple)):
            return self.subinfo.archiveName()
        else:
            return (self.subinfo.archiveName(), )

    def fetch( self, repopath = None ):
        EmergeDebug.trace("MultiSource fetch", 2)
        return self.source.fetch( repopath )

    def checkDigest(self):
        EmergeDebug.trace("MultiSource checkDigest", 2)
        return self.source.checkDigest()

    def unpack(self):
        EmergeDebug.trace("MultiSource unpack", 2)
        # pylint: disable=E1101
        # multiple inheritance: MultiSource is never the only
        # superclass, others define self.buildSystemType.
        self.source.buildSystemType = self.buildSystemType
        return self.source.unpack()

    def checkoutDir(self):
        EmergeDebug.trace("MultiSource checkoutDir", 2)
        return self.source.checkoutDir()

    def sourceDir(self):
        EmergeDebug.trace("MultiSource sourceDir", 2)
        return self.source.sourceDir()

    def repositoryUrl(self, index=0):
        EmergeDebug.trace("MultiSource repositoryUrl", 2)
        return self.source.repositoryUrl(index)

    def repositoryUrlCount(self):
        EmergeDebug.trace("MultiSource repositoryUrlCount", 2)
        return self.source.repositoryUrlCount()

    def applyPatches(self):
        EmergeDebug.trace("MultiSource applyPatches", 2)
        return self.source.applyPatches()

    def applyPatch(self):
        raise Exception('MultiSource.applyPatch is deprecated. '
                'it calls self.source.applyPatch without arguments which must fail')
        # utils.trace( "MultiSource applyPatch", 2 )
        # return self.source.applyPatch()

    def createPatch(self):
        EmergeDebug.trace("MultiSource createPatch", 2)
        return self.source.createPatch()

    def getUrls(self):
        EmergeDebug.trace("MultiSource getUrls", 2)
        return self.source.getUrls()

    def sourceVersion(self):
        EmergeDebug.trace("MultiSource sourceVersion", 2)
        return self.source.sourceVersion()

    def sourceRevision(self):
        EmergeDebug.trace("MultiSource sourceVersion", 2)
        return self.source.sourceRevision()

        
    def printSourceVersion(self):
        EmergeDebug.trace("MultiSource printSourceVersion", 2)
        print(self.source.sourceVersion())
        return True
