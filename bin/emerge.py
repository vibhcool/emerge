#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# this will emerge some programs...

# copyright:
# Holger Schroeder <holger [AT] holgis [DOT] net>
# Patrick Spendrin <ps_ml [AT] gmx [DOT] de>
# Hannah von Reth <vonreth [AT] kde [DOT] org>

# The minimum python version for emerge please edit here
# if you add code that changes this requirement

import sys

import EmergeDebug
import EmergeTimer

import time
import datetime
import traceback
import argparse
import collections
import copy

import compiler
import portageSearch
import InstallDB
import portage
import utils
import threading
from EmergeConfig import *

def destroyEmergeRoot():
    del InstallDB.installdb
    root = EmergeStandardDirs.emergeRoot()
    for entry in os.listdir(root):
        path = os.path.join(root, entry)
        if path == EmergeStandardDirs.etcDir():
            for entry in os.listdir(path):
                if not entry == "kdesettings.ini":
                    etcPath = os.path.join(path, entry)
                    if os.path.isdir(etcPath):
                        utils.cleanDirectory(etcPath)
                        utils.OsUtils.rmDir(etcPath, True)
                    else:
                        utils.OsUtils.rm(etcPath, True)
        elif not path in [ EmergeStandardDirs.downloadDir(), EmergeStandardDirs.emergeRepositoryDir(),
                           os.path.join(EmergeStandardDirs.emergeRoot(), "python") ]:
            utils.cleanDirectory(path)
            utils.OsUtils.rmDir(path, True)

def packageIsOutdated( category, package ):
    newest = portage.PortageInstance.getNewestVersion( category, package )
    installed = InstallDB.installdb.getInstalledPackages( category, package )
    for pack in installed:
        version = pack.getVersion( )
        if newest != version:
            return True


@utils.log
def doExec( package, action, continueFlag = False ):
    with EmergeTimer.Timer("%s for %s" % ( action, package ), 1 ):
        EmergeDebug.info("Action: %s for %s" % (action, package))
        ret = package.execute( action )
        if not ret:
            EmergeDebug.warning("Action: %s for %s FAILED" % (action, package))
        return ret or continueFlag


def handlePackage( category, packageName, buildAction, continueFlag, skipUpToDateVcs ):
    with EmergeTimer.Timer("HandlePackage %s/%s" % (category, packageName), 3) as timer:
        EmergeDebug.debug_line()
        EmergeDebug.info("Handling package: %s, action: %s" % (packageName, buildAction))

        success = True
        package = portage.getPackageInstance( category, packageName )
        if package is None:
            raise portage.PortageException( "Package not found", category, packageName )

        if buildAction in [ "all", "full-package", "update", "update-all" ]:
            if emergeSettings.getboolean("ContinuousIntegration", "UseCache", "False"):
                if doExec( package, "fetch-binary"):
                    return True
            success = success and doExec( package, "fetch", continueFlag )
            skip = False
            if success and skipUpToDateVcs and package.subinfo.hasSvnTarget( ):
                revision = package.sourceVersion( )
                for p in InstallDB.installdb.getInstalledPackages( category, packageName ):
                    if p.getRevision( ) == revision:
                        EmergeDebug.info("Skipping further actions, package is up-to-date")
                        skip = True
            if not skip:
                success = success and doExec( package, "unpack", continueFlag )
                success = success and doExec( package, "compile" )
                success = success and doExec( package, "cleanimage" )
                success = success and doExec( package, "install" )
                if buildAction in [ "all", "update", "update-all" ]:
                    success = success and doExec( package, "qmerge" )
                if buildAction == "full-package" or emergeSettings.getboolean("ContinuousIntegration", "CreateCache"):
                    success = success and doExec( package, "package" )
                success = success or continueFlag
        elif buildAction in [ "fetch", "fetch-binary", "unpack", "configure", "compile", "make", "checkdigest",
                              "dumpdeps", "test",
                              "package", "unmerge", "cleanimage", "cleanbuild", "createpatch",
                              "geturls",
                              "print-revision",
                              "print-files"
                            ]:
            success = doExec( package, buildAction, continueFlag )
        elif buildAction == "install":
            success = doExec( package, "cleanimage" )
            success = success and doExec( package, "install", continueFlag )
        elif buildAction == "qmerge":
            #success = doExec( package, "cleanimage" )
            #success = success and doExec( package, "install")
            success = success and doExec( package, "qmerge" )
        elif buildAction == "print-source-version":
            print( "%s-%s" % ( packageName, package.sourceVersion( ) ) )
            success = True
        elif buildAction == "print-package-version":
            print( "%s-%s-%s" % ( packageName, compiler.getCompilerName( ), package.sourceVersion( ) ) )
            success = True
        elif buildAction == "print-targets":
            portage.printTargets( category, packageName )
            success = True
        else:
            success = EmergeDebug.error("could not understand this buildAction: %s" % buildAction)

        timer.stop()
        utils.notify( "Emerge %s %s" % (buildAction, "succeeded" if success else "failed"),
                      "%s of %s/%s %s after %s" % ( buildAction, category, packageName, "succeeded" if success else "failed", timer), buildAction)
        return success


def handleSinglePackage( packageName, action, args ):
    deplist = [ ]
    packageList = [ ]
    originalPackageList = [ ]
    categoryList = [ ]
    targetDict = dict( )

    if action == "update-all":
        installedPackages = portage.PortageInstance.getInstallables( )
        if portage.PortageInstance.isCategory( packageName ):
            EmergeDebug.debug("Updating installed packages from category " + packageName, 1)
        else:
            EmergeDebug.debug("Updating all installed packages", 1)
        packageList = [ ]
        for mainCategory, mainPackage in installedPackages:
            if portage.PortageInstance.isCategory( packageName ) and ( mainCategory != packageName ):
                continue
            if InstallDB.installdb.isInstalled( mainCategory, mainPackage, args.buildType ) \
                    and portage.isPackageUpdateable( mainCategory, mainPackage ):
                categoryList.append( mainCategory )
                packageList.append( mainPackage )
        EmergeDebug.debug("Will update packages: " + str(packageList), 1)
    elif args.list_file:
        listFileObject = open( args.list_file, 'r' )
        for line in listFileObject:
            if line.strip( ).startswith( '#' ): continue
            try:
                cat, pac, tar, _ = line.split( ',' )
            except:
                continue
            categoryList.append( cat )
            packageList.append( pac )
            originalPackageList.append( pac )
            targetDict[ cat + "/" + pac ] = tar
    elif packageName:
        packageList, categoryList = portage.getPackagesCategories( packageName )

    for entry in packageList:
        EmergeDebug.debug("Checking dependencies for: %s" % entry, 1)

    for mainCategory, entry in zip( categoryList, packageList ):
        deplist = portage.solveDependencies( mainCategory, entry, deplist, args.dependencyType,
                                              maxDepth = args.dependencydepth )
    # no package found
    if len( deplist ) == 0:
        category = ""
        if not packageName.find( "/" ) == -1:
            (category, package) = packageName.split( "/" )
        portageSearch.printSearch( category, packageName )
        return False

    for item in deplist:
        item.enabled = args.ignoreAllInstalled

        if args.ignoreInstalled and item.category in categoryList and item.package in packageList or packageIsOutdated(
                item.category, item.package ):
            item.enabled = True

        if item.category + "/" + item.package in targetDict:
            item.target = targetDict[ item.category + "/" + item.package ]

        if args.target in list(
                portage.PortageInstance.getAllTargets( item.category, item.package ).keys( ) ):
            # if no target or a wrong one is defined, simply set the default target here
            item.target = args.target

        EmergeDebug.debug("dependency: %s" % item, 1)
    if not deplist:
        EmergeDebug.debug("<none>", 1)

    EmergeDebug.debug_line(1)

    #for item in deplist:
    #    cat = item[ 0 ]
    #    pac = item[ 1 ]
    #    ver = item[ 2 ]

    #    if portage.isInstalled( cat, pac, ver, buildType) and updateAll and not portage.isPackageUpdateable( cat, pac, ver ):
    #        print "remove:", cat, pac, ver
    #        deplist.remove( item )

    if action == "install-deps":
        # the first dependency is the package itself - ignore it
        # TODO: why are we our own dependency?
        del deplist[ 0 ]
    elif action == "update-direct-deps":
        for item in deplist:
            item.enabled = True

    deplist.reverse( )

    # package[0] -> category
    # package[1] -> package
    # package[2] -> version

    info = deplist[ -1 ]
    if not portage.PortageInstance.isVirtualPackage( info.category, info.package ) and \
        not action in [ "all", "install-deps"] and\
        not args.list_file or\
        action in ["print-targets"]:#not all commands should be executed on the deps if we are a virtual packages
        # if a buildAction is given, then do not try to build dependencies
        # and do the action although the package might already be installed.
        # This is still a bit problematic since packageName might not be a valid
        # package
        # for list files, we also want to handle fetching & packaging per package
        if not handlePackage( info.category, info.package, action, args.doContinue, args.update_fast ):
            return False

    else:
        if args.dumpDepsFile:
            dumpDepsFileObject = open( args.dumpDepsFile, 'w+' )
            dumpDepsFileObject.write( "# dependency dump of package %s\n" % ( packageName ) )
        for info in deplist:
            isVCSTarget = False

            if args.dumpDepsFile:
                dumpDepsFileObject.write( ",".join( [ info.category, info.package, info.target, "" ] ) + "\n" )

            isLastPackage = info == deplist[ -1 ]
            if args.outDateVCS or (args.outDatePackage and isLastPackage):
                isVCSTarget = portage.PortageInstance.getUpdatableVCSTargets( info.category, info.package ) != [ ]
            isInstalled = InstallDB.installdb.isInstalled( info.category, info.package )
            if args.list_file and action != "all":
                info.enabled = info.package in originalPackageList
            if ( isInstalled and not info.enabled ) and not (
                            isInstalled and (args.outDateVCS or (
                                    args.outDatePackage and isLastPackage) ) and isVCSTarget ):
                if EmergeDebug.verbose() > 1 and info.package == packageName:
                    EmergeDebug.warning("already installed %s/%s" % (info.category, info.package))
                elif EmergeDebug.verbose() > 2 and not info.package == packageName:
                    EmergeDebug.warning("already installed %s/%s" % (info.category, info.package))
            else:
                # in case we only want to see which packages are still to be build, simply return the package name
                if args.probe:
                        EmergeDebug.warning("pretending %s" % info)
                else:
                    if action in [ "install-deps", "update-direct-deps" ]:
                        action = "all"

                    if not handlePackage( info.category, info.package, action, args.doContinue, args.update_fast ):
                        EmergeDebug.error("fatal error: package %s/%s %s failed" % \
                                          ( info.category, info.package, action ))
                        return False

    EmergeDebug.new_line()
    return True

class ActionHandler:
    class StoreTrueAction(argparse._StoreTrueAction):
        def __call__(self, parser, namespace, values, option_string=None):
            ActionHandler.StoreAction._addOrdered(namespace, self.dest, self.const)
            super().__call__(parser, namespace, values, option_string)

    class StoreAction(argparse._StoreAction):
        """http://stackoverflow.com/a/9028031"""
        def __call__(self, parser, namespace, values, option_string=None):
            ActionHandler.StoreAction._addOrdered(namespace, self.dest, values)
            super().__call__(parser, namespace, values, option_string)

        @staticmethod
        def _addOrdered(namespace, key, value):
            if not 'ordered_args' in namespace:
                setattr(namespace, 'ordered_args', collections.OrderedDict())
            namespace.ordered_args[key] = value


    def __init__(self, parser):
        self.parser = parser
        self.actions = {}

    def _addAction(self, actionName, help = None, **kwargs):
        arg = self.parser.add_argument("--%s" % actionName,
                                       help = "[Action] %s" % (help if help else ""), **kwargs)
        self.actions[arg.dest] = actionName

    def addAction(self, actionName, **kwargs):
        self._addAction(actionName, action = ActionHandler.StoreTrueAction, **kwargs)

    def addActionWithArg(self, actionName, **kwargs):
        self._addAction(actionName, action = ActionHandler.StoreAction, **kwargs)

    def parseFinalAction(self, args, defaultAction):
        '''Returns the list of actions or [defaultAction]'''
        return [self.actions[x] for x in args.ordered_args.keys()] if hasattr(args, "ordered_args") else [defaultAction]


def main( ):
    parser = argparse.ArgumentParser( prog = "emerge",
                                      description = "Emerge is a tool for building KDE-related software under Windows. emerge automates it, looks for the dependencies and fetches them automatically.\
                                      Some options should be used with extreme caution since they will make your kde installation unusable in 999 out of 1000 cases.",
                                      epilog = """More information see the README or http://windows.kde.org/.
    Send feedback to <kde-windows@kde.org>.""" )

    parser.add_argument( "-p", "--probe", action = "store_true",
                         help = "probing: emerge will only look which files it has to build according to the list of installed files and according to the dependencies of the package." )
    parser.add_argument( "--list-file", action = "store",
                         help = "Build all packages from the csv file provided" )
    _def = emergeSettings.get( "General", "EMERGE_OPTIONS", "" )
    if _def == "": _def = []
    else: _def = _def.split( ";" )
    parser.add_argument( "--options", action = "append",
                         default = _def,
                         help = "Set emerge property from string <OPTIONS>. An example for is \"cmake.openIDE=1\" see options.py for more informations." )
    parser.add_argument( "-z", "--outDateVCS", action = "store_true",
                         help = "if packages from version control system sources are installed, it marks them as out of date and rebuilds them (tags are not marked as out of date)." )
    parser.add_argument( "-sz", "--outDatePackage", action = "store_true",
                         help = "similar to -z, only that it acts only on the last package, and works as normal on the rest." )
    parser.add_argument( "-q", "--stayquiet", action = "store_true",
                         dest = "stayQuiet",
                         help = "quiet: there should be no output - The verbose level should be 0" )
    parser.add_argument( "-t", "--buildtests", action = "store_true", dest = "buildTests",
                         default = emergeSettings.getboolean( "Compile", "BuildTests", False ) )
    parser.add_argument( "-c", "--continue", action = "store_true", dest = "doContinue" )
    parser.add_argument("-cc", "--create-cache", action="store_true", dest="createCache",
                        default=emergeSettings.getboolean("ContinuousIntegration", "CreateCache", "False"))
    parser.add_argument("-uc", "--use-cache", action="store_true", dest="useCache",
                        default=emergeSettings.getboolean("ContinuousIntegration", "UseCache", "False"))
    parser.add_argument( "--destroy-emerge-root", action = "store_true", dest = "doDestroyEmergeRoot",
                         default=False)
    parser.add_argument( "--offline", action = "store_true",
                         default = emergeSettings.getboolean( "General", "WorkOffline", False ),
                         help = "do not try to connect to the internet: KDE packages will try to use an existing source tree and other packages would try to use existing packages in the download directory.\
                          If that doesn't work, the build will fail." )
    parser.add_argument( "-f", "--force", action = "store_true", dest = "forced",
                         default = emergeSettings.getboolean( "General", "EMERGE_FORCED", False ) )
    parser.add_argument( "--buildtype", choices = [ "Release", "RelWithDebInfo", "MinSizeRel", "Debug" ],
                         dest = "buildType",
                         default = emergeSettings.get( "Compile", "BuildType", "RelWithDebInfo" ),
                         help = "This will override the build type set in your kdesettings.ini." )
    parser.add_argument( "-v", "--verbose", action = "count",
                         default = int( emergeSettings.get( "EmergeDebug", "Verbose", "0" ) ),
                         help = " verbose: increases the verbose level of emerge. Default is 1. verbose level 1 contains some notes from emerge, all output of cmake, make and other programs that are used.\
                          verbose level 2a dds an option VERBOSE=1 to make and emerge is more verbose highest level is verbose level 3." )
    parser.add_argument( "--trace", action = "store",
                         default = int( emergeSettings.get( "General", "EMERGE_TRACE", "0" ) ), type = int )
    parser.add_argument( "-i", "--ignoreInstalled", action = "store_true",
                         help = "ignore install: using this option will install a package over an existing install. This can be useful if you want to check some new code and your last build isn't that old." )
    parser.add_argument( "-ia", "--ignoreAllInstalled", action = "store_true",
                         help = "ignore all install: using this option will install all package over an existing install. This can be useful if you want to check some new code and your last build isn't that old." )

    parser.add_argument( "--target", action = "store",
                         help = "This will override the build of the default target. The default Target is marked with a star in the printout of --print-targets" )
    parser.add_argument( "--search", action = "store_true",
                         help = "This will search for a package or a description matching or similar to the search term." )
    parser.add_argument( "--noclean", action = "store_true",
                         default = emergeSettings.getboolean( "General", "EMERGE_NOCLEAN", False ),
                         help = "this option will try to use an existing build directory. Please handle this option with care - it will possibly break if the directory isn't existing." )
    parser.add_argument( "--clean", action = "store_false", dest = "noclean",
                         help = "oposite of --noclean" )
    parser.add_argument( "--patchlevel", action = "store",
                         default = emergeSettings.get( "General", "EMERGE_PKGPATCHLVL", "" ),
                         help = "This will add a patch level when used together with --package" )
    parser.add_argument( "--log-dir", action = "store",
                         default = emergeSettings.get( "General", "EMERGE_LOG_DIR", "" ),
                         help = "This will log the build output to a logfile in LOG_DIR for each package. Logging information is appended to existing logs." )
    parser.add_argument( "--dt", action = "store", choices = [ "both", "runtime", "buildtime" ], default = "both",
                         dest = "dependencyType" )
    parser.add_argument( "--update-fast", action = "store_true",
                         help = "If the package is installed from svn/git and the revision did not change all steps after fetch are skipped" )
    parser.add_argument( "-d", "--dependencydepth", action = "store", type = int, default = -1,
                         help = "By default emerge resolves the whole dependency graph, this option limits the depth of the graph, so a value of 1 would mean only dependencies defined in that package" )

    actionHandler = ActionHandler(parser)
    for x in sorted( [ "fetch", "fetch-binary", "unpack", "configure", "compile", "make",
                       "install", "install-deps", "qmerge", "manifest", "package", "unmerge", "test",
                       "checkdigest", "dumpdeps",
                       "full-package", "cleanimage", "cleanbuild", "createpatch", "geturls"] ):
        actionHandler.addAction( x )
    actionHandler.addAction( "update", help = "Update a single package" )

    # read-only actions
    actionHandler.addAction( "print-source-version" )
    actionHandler.addAction( "print-package-version" )
    actionHandler.addAction( "print-targets",
                             help = "This will show a list of available targets for the package" )
    actionHandler.addAction( "print-installed",
                             help = "This will show a list of all packages that are installed currently." )
    actionHandler.addAction( "print-installable",
                             help = "This will give you a list of packages that can be installed. Currently you don't need to enter the category and package: only the package will be enough." )
    actionHandler.addAction( "print-revision", help = "Print the revision of the package and exit" )
    actionHandler.addAction( "print-files", help = "Print the files installed by the package and exit" )
    actionHandler.addActionWithArg( "search-file", help = "Print packages owning the file" )

    # other actions
    actionHandler.addActionWithArg( "dump-deps-file", dest = "dumpDepsFile",
                                    help = "Output the dependencies of this package as a csv file suitable for emerge server." )

    parser.add_argument( "packageNames", nargs = argparse.REMAINDER )

    args = parser.parse_args( )

    if args.doDestroyEmergeRoot:
        destroyEmergeRoot()
        return True


    if args.stayQuiet:
        EmergeDebug.setVerbose(-1)
    elif args.verbose:
        EmergeDebug.setVerbose(args.verbose)

    emergeSettings.set( "General", "WorkOffline", args.offline )
    emergeSettings.set( "General", "EMERGE_NOCLEAN", args.noclean )
    emergeSettings.set( "General", "EMERGE_FORCED", args.forced )
    emergeSettings.set( "Compile", "BuildTests", args.buildTests )
    emergeSettings.set( "Compile", "BuildType", args.buildType )
    emergeSettings.set( "PortageVersions", "DefaultTarget", args.target )
    emergeSettings.set( "General", "EMERGE_OPTIONS", ";".join( args.options ) )
    emergeSettings.set( "General", "EMERGE_LOG_DIR", args.log_dir )
    emergeSettings.set( "General", "EMERGE_TRACE", args.trace )
    emergeSettings.set( "General", "EMERGE_PKGPATCHLVL", args.patchlevel )
    emergeSettings.set( "ContinuousIntegration", "CreateCache", args.createCache)
    emergeSettings.set( "ContinuousIntegration", "UseCache", args.useCache)

    portage.PortageInstance.options = args.options
    if args.search:
        for package in args.packageNames:
            category = ""
            if not package.find( "/" ) == -1:
                (category, package) = package.split( "/" )
            portageSearch.printSearch( category, package )
        return True


    for action in actionHandler.parseFinalAction(args, "all"):
        tempArgs = copy.deepcopy(args)

        if action in [ "install-deps", "update", "update-all", "package" ] or tempArgs.update_fast:
            tempArgs.ignoreInstalled = True

        if action in [ "update", "update-all" ]:
            tempArgs.noclean = True

        EmergeDebug.debug("buildAction: %s" % action)
        EmergeDebug.debug("doPretend: %s" % tempArgs.probe, 1)
        EmergeDebug.debug("packageName: %s" % tempArgs.packageNames)
        EmergeDebug.debug("buildType: %s" % tempArgs.buildType)
        EmergeDebug.debug("buildTests: %s" % tempArgs.buildTests)
        EmergeDebug.debug("verbose: %d" % EmergeDebug.verbose(), 1)
        EmergeDebug.debug("trace: %s" % tempArgs.trace, 1)
        EmergeDebug.debug("KDEROOT: %s" % EmergeStandardDirs.emergeRoot(), 1)
        EmergeDebug.debug_line()

        if action == "print-installed":
            InstallDB.printInstalled( )
        elif action == "print-installable":
            portage.printInstallables( )
        elif action == "search-file":
            portage.printPackagesForFileSearch(tempArgs.search_file)
        elif tempArgs.list_file:
            handleSinglePackage( "", action, tempArgs )
        else:
            for packageName in tempArgs.packageNames:
                if not handleSinglePackage( packageName, action, tempArgs ):
                    return False
    return True


if __name__ == '__main__':
    success= True
    with EmergeTimer.Timer("Emerge", 0):
        try:
            doUpdateTitle = True

            def updateTitle( startTime, title ):
                while ( doUpdateTitle ):
                    delta = datetime.datetime.now( ) - startTime
                    utils.OsUtils.setConsoleTitle( "emerge %s %s" % (title, delta) )
                    time.sleep( 1 )

            tittleThread = threading.Thread( target = updateTitle,
                                             args = (datetime.datetime.now( ), " ".join( sys.argv[ 1: ] ),) )
            tittleThread.setDaemon( True )
            tittleThread.start( )
            success = main()
        except KeyboardInterrupt:
            pass
        except portage.PortageException as e:
            if e.exception:
                EmergeDebug.debug(e.exception, 0)
                traceback.print_tb( e.exception.__traceback__)
            EmergeDebug.error(e)
        except Exception as e:
            print( e )
            traceback.print_tb( e.__traceback__ )
        finally:
            doUpdateTitle = False
            if emergeSettings.getboolean( "EmergeDebug", "DumpSettings", False ):
                emergeSettings.dump( )
    if not success:
        exit( 1 )

