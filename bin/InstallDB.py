import os
import sqlite3
import threading

import EmergeDebug
from EmergeConfig import *

import utils
import portage



class InstallPackage(object):
    """ InstallPackage finalizes an installation.

        If you call addInstalled or remInstalled an InstallPackage object is returned which
        you can use to handle file information with the InstallDB. For installation use code
        similar to this one:

        # get an InstallPackage object p
        p = InstallDB.installdb.addInstalled( "cat", "pac", "ver", "prefix" )
        # add files ( including the hash )
        p.addFiles( [ ( "file1", "hash1" ), ( "file2", "hash2" ), ( "file3", "hash3" ) ] )
        if failed:
            # in case we somehow need to go back
            p.revert()
        else:
            # finalize the installation
            p.install()

        Deinstallation works similar:
        p = InstallDB.installdb.remInstalled( "cat", "pac", "ver", "prefix" )
        # get the files ( including the hash )
        f = p.getFilesWithHashes()
        # f now contains [ ( "file1", "hash1" ), ( "file2", "hash2" ), ( "file3", "hash3" ) ]
        if failed:
            # in case we somehow need to go back
            p.revert()
        else:
            # finalize the uninstall
            p.uninstall()
    """

    def __init__( self, cursor, packageId ):
        self.cursor = cursor
        self.packageId = packageId
        self.fileDict = dict()

    def addFiles( self, fileDict ):
        """ appends files to the list of files to be installed """
        self.fileDict.update( fileDict )

    def getFilesWithHashes( self ):
        """ get the list of files (filename, fileHash tuples) for the given package """
        cmd = '''SELECT filename, fileHash FROM fileList WHERE packageId=?;'''
        EmergeDebug.debug("executing sqlcmd '%s' with parameter %s" % (cmd, str(self.packageId)), 2)
        self.cursor.execute(cmd, (self.packageId,))
        return self.cursor.fetchall()

    def getFiles( self ):
        """ get the list of files for the given package """
        cmd = '''SELECT filename FROM fileList WHERE packageId=?;'''
        EmergeDebug.debug("executing sqlcmd '%s' with parameter %s" % (cmd, str(self.packageId)), 2)
        self.cursor.execute(cmd, (self.packageId,))
        return self.cursor.fetchall()

    def getPackageInfo(self):
        cmd = '''SELECT category, packageName, version FROM packageList WHERE packageId=?'''
        self.cursor.execute(cmd, (self.packageId,))
        return self.cursor.fetchall()[0]

    def revert( self ):
        """ revert all changes made to the database, use with care """
        self.cursor.connection.rollback()

    def uninstall( self ):
        """ really uninstall that package """
        cmd = '''DELETE FROM fileList WHERE packageId=?;'''
        EmergeDebug.debug("executing sqlcmd '%s' with parameter %s" % (cmd, str(self.packageId)), 2)
        self.cursor.execute(cmd, (self.packageId,))
        cmd = '''DELETE FROM packageList WHERE packageId=?;'''
        EmergeDebug.debug("executing sqlcmd '%s' with parameter %s" % (cmd, str(self.packageId)), 2)
        self.cursor.execute(cmd, (self.packageId,))
        self.cursor.connection.commit()

    def install( self ):
        """ marking the package & package file list installed """
        fileNumber = len( self.fileDict )
        # keys() and values will stay in the same order if no changes are done in between calls
        # structure of each tuple:
        # fileId | packageId == package Id | filenames | file hashes
        dataList = list(zip( [ None ] * fileNumber, [ self.packageId ] * fileNumber, list(self.fileDict.keys()), list(self.fileDict.values()) ))

        cmd = '''INSERT INTO fileList VALUES (?, ?, ?, ?)'''
        EmergeDebug.debug("executing sqlcmd '%s' %s times" % (cmd, len(self.fileDict)), 2)
        self.cursor.executemany( cmd, dataList )

        # at last, commit all the changes so that they are committed only after everything is written to the
        # database
        self.cursor.connection.commit()

    def getRevision(self):
        self.cursor.execute("SELECT revision FROM packageList WHERE packageId == ?", (self.packageId,) )
        return self.cursor.fetchall()[0][0]

    def getVersion(self):
        self.cursor.execute("SELECT version FROM packageList WHERE packageId == ?", (self.packageId,) )
        return self.cursor.fetchall()[0][0]



class InstallDB(object):
    """ a database object which provides the methods for adding and removing a package and
        checking its installation status.
        In case the database doesn't exist if the constructor is called, a new database is constructed
    """

    def __init__( self, filename = None ):
        if filename == None:
            with TemporaryUseShortpath(False):
                filename = os.path.join( EmergeStandardDirs.etcPortageDir(), 'install.db' )

        self.dbfilename = filename
        self._prepareDatabase()

    def getLastId( self ):
        """ returns the last id from a table, which is essentially the  """
        cmd = '''SELECT max(packageId) FROM packageList;'''

        cursor = self.connection.cursor()
        cursor.execute( cmd )
        lastId = cursor.fetchall()[0]
        return lastId[0]

    def __constructWhereStmt( self, _dict ):
        params = []
        parametersUsed = False
        stmt = ""
#        if not prefix == '' or not category == '' or not package == '':
#            cmd += ''' WHERE'''
#
        for key in list(_dict.keys()):
            if not _dict[ key ] == None:
                if parametersUsed:
                    stmt += ''' AND'''
                stmt += ''' %s=?''' % key
                params.append( _dict[ key ] )
                parametersUsed = True
        if not stmt == "":
            stmt = ''' WHERE''' + stmt

        return stmt, params

    def isInstalled( self, category, package, version=None, prefix=None ):
        """ returns whether a package is installed. If version and prefix are empty, all versions
            and prefixes will be checked. """
        cmd = '''SELECT * FROM packageList'''
        # TODO: what is the difference between prefix=None and prefix=''? Both happens. Document.
        stmt, params = self.__constructWhereStmt( { 'prefix': prefix, 'category': category, 'packageName': package, 'version': version } )
        cmd += stmt
        cmd += ''';'''
        EmergeDebug.debug("executing sqlcmd '%s' with parameters: %s" % (cmd, tuple(params)), 2)

        cursor = self.connection.cursor()
        cursor.execute( cmd, tuple( params ) )
        isPackageInstalled = len( cursor.fetchall() ) > 0
        if isPackageInstalled:
            EmergeDebug.debug("""The package %s/%s has been installed in prefix '%s' with
                            version '%s'.""" % ( category, package, prefix, version ), 2)
        else:
            EmergeDebug.debug("""Couldn't find a trace that the package %s/%s has been installed in
                            prefix '%s' with version '%s'""" % ( category, package, prefix, version ), 1)
        cursor.close()
        return isPackageInstalled

    def getInstalled( self, category=None, package=None, prefix=None ):
        """ returns a list of the installed packages, which can be restricted by adding
            package, category and prefix.
        """
        cmd = '''SELECT category, packageName, version, prefix FROM packageList'''
        stmt, params = self.__constructWhereStmt( { 'prefix': prefix, 'category': category, 'packageName': package } )
        cmd += stmt
        cmd += ''';'''
        EmergeDebug.debug("executing sqlcmd '%s' with parameters: %s" % (cmd, tuple(params)), 2)

        cursor = self.connection.cursor()
        cursor.execute( cmd, tuple( params ) )
        values = cursor.fetchall()
        cursor.close()
        return values

    def getDistinctInstalled( self, category=None, package=None, prefix=None ):
        """ returns a list of the installed packages, which can be restricted by adding
            package, category and prefix.
        """
        cmd = '''SELECT DISTINCT category, packageName, version FROM packageList'''
        stmt, params = self.__constructWhereStmt( { 'prefix': prefix, 'category': category, 'packageName': package } )
        cmd += stmt
        cmd += ''';'''
        EmergeDebug.debug("executing sqlcmd '%s' with parameters: %s" % (cmd, tuple(params)), 2)

        cursor = self.connection.cursor()
        cursor.execute( cmd, tuple( params ) )
        values = cursor.fetchall()
        cursor.close()
        return values

    def getPackageIds( self, category = None, package = None, prefix = None ):
        """ returns a list of the ids of the packages, which can be restricted by adding
            package, category and prefix.
        """
        cmd = '''SELECT packageId FROM packageList'''
        stmt, params = self.__constructWhereStmt( { 'prefix': prefix, 'category': category, 'packageName': package } )
        cmd += stmt
        cmd += ''';'''
        EmergeDebug.debug("executing sqlcmd '%s' with parameters: %s" % (cmd, tuple(params)), 2)

        cursor = self.connection.cursor()
        cursor.execute( cmd, tuple( params ) )
        values = []
        for row in cursor:
            values.append( row[0] )
        return values

    def getPackagesForFileSearch(self, filename, prefix = None ):
        """ returns a list of tuple(InstallPackage(), filename) for packages providing a given file """

        cursor = self.connection.cursor()
        cmd = '''SELECT packageId, fileName FROM fileList WHERE filename LIKE ?;'''
        EmergeDebug.debug("executing sqlcmd '%s' with parameter %s" % (cmd, str(filename)), 2)
        cursor.execute(cmd, ("%" + filename + "%",))
        rows = cursor.fetchall()
        return [(InstallPackage(cursor, row[0]), row[1]) for row in rows]

    def addInstalled( self, category, package, version, prefix=None, ignoreInstalled=False, revision = "" ):
        """ adds an installed package """
        cursor = self.connection.cursor()
        if self.isInstalled( category, package, version, prefix ) and not ignoreInstalled:
            raise Exception( 'package %s/%s-%s already installed (prefix %s)' % ( category, package, version, prefix ) )

        params = [ None, prefix, category, package, version, revision ]
        cmd = '''INSERT INTO packageList VALUES (?, ?, ?, ?, ?, ?)'''
        EmergeDebug.debug("executing sqlcmd '%s' with parameters: %s" % (cmd, tuple(params)), 2)
        cursor.execute( cmd, tuple( params ) )
        return InstallPackage( cursor, self.getLastId() )

    def getInstalledPackages( self, category, package, prefix = None ):
        """ return an installed package """
        cursor = self.connection.cursor()
        return [ InstallPackage( cursor, pId ) for pId in self.getPackageIds( category, package, prefix ) ]

    def _prepareDatabase( self ):
        """ prepare a new database and add the required table layout """
        with TemporaryUseShortpath(False):
            if not os.path.exists( self.dbfilename ):
                if not os.path.exists( EmergeStandardDirs.etcPortageDir( ) ):
                    os.makedirs( EmergeStandardDirs.etcPortageDir( ) )
                print( "database does not exist yet: creating database", file = sys.stderr )
                self.connection = sqlite3.connect( self.dbfilename )
                cursor = self.connection.cursor()

                # first, create the required tables
                cursor.execute( '''CREATE TABLE packageList (packageId INTEGER PRIMARY KEY AUTOINCREMENT,
                                   prefix TEXT, category TEXT, packageName TEXT, version TEXT, revision TEXT)''' )
                cursor.execute( '''CREATE TABLE fileList (fileId INTEGER PRIMARY KEY AUTOINCREMENT,
                                   packageId INTEGER, filename TEXT, fileHash TEXT)''' )
                self.connection.commit()
            else:
                self.connection = sqlite3.connect( self.dbfilename )
                cursor = self.connection.cursor()
            cursor.execute( '''PRAGMA table_info('packageList')''')
            if not len(cursor.fetchall()) == 6:
                cursor.execute('''ALTER TABLE packageList ADD COLUMN revision TEXT''')
                self.connection.commit()


# get a global object
installdb = InstallDB()

# an additional function from portage.py
def printInstalled():
    """get all the packages that are already installed"""
    host = target = portage.alwaysTrue
    portage.printCategoriesPackagesAndVersions( installdb.getDistinctInstalled(), portage.alwaysTrue, host, target )

def main():
    """ Testing the class"""

    # add two databases
    tempdbpath1 = os.path.join( EmergeStandardDirs.emergeRoot(), "tmp", "temp1.db" )
    tempdbpath2 = os.path.join( EmergeStandardDirs.emergeRoot(), "tmp", "temp2.db" )

    if not os.path.exists( os.path.join( EmergeStandardDirs.emergeRoot(), "tmp" ) ):
        os.makedirs( os.path.join( EmergeStandardDirs.emergeRoot(), "tmp" ) )

    if os.path.exists( tempdbpath1 ):
        os.remove( tempdbpath1 )
    if os.path.exists( tempdbpath2 ):
        os.remove( tempdbpath2 )

    db_temp = InstallDB( tempdbpath1 )
    db = InstallDB( tempdbpath2 )

    EmergeDebug.debug('testing installation database')

    # in case the package is still installed, remove it first silently
    if db.isInstalled( 'win32libs', 'dbus-src', '1.4.0' ):
        packageList = db.getInstalledPackages( 'win32libs', 'dbus-src' )
        # really commit uninstall
        for package in packageList:
            package.uninstall()
    EmergeDebug.debug_line()

    EmergeDebug.new_line()
    # add a package
    EmergeDebug.debug('installing package win32libs/dbus-src-1.4.0 (release)')
    package = db.addInstalled( 'win32libs', 'dbus-src', '1.4.0', 'release' )
    package.addFiles( dict().fromkeys( [ 'test', 'test1', 'test2' ], 'empty hash' ) )
    # now really commit the package
    package.install()

    # add another package in a different prefix
    EmergeDebug.debug('installing package win32libs/dbus-src-1.4.0 (debug)')
    package = db.addInstalled( 'win32libs', 'dbus-src', '1.4.0', 'debug' )
    package.addFiles( dict().fromkeys( [ 'test', 'test1', 'test2' ], 'empty hash' ) )
    # now really commit the package
    package.install()
    EmergeDebug.debug_line()

    EmergeDebug.new_line()
    EmergeDebug.debug('checking installed packages')
    EmergeDebug.debug('get installed package (release): %s' % db.getInstalled('win32libs', 'dbus-src', 'release'))
    EmergeDebug.debug('get installed package (debug):   %s' % db.getInstalled('win32libs', 'dbus-src', 'debug'))

    EmergeDebug.new_line()
    EmergeDebug.debug('now trying to remove package & revert it again later')
    # remove the package again
    packageList = db.getInstalledPackages( 'win32libs', 'dbus-src' )
    for pac in packageList:
        for line in pac.getFiles(): # pylint: disable=W0612
            # we could remove the file here
            # print line
            pass
    EmergeDebug.debug_line()

    EmergeDebug.new_line()
    EmergeDebug.debug('checking installed packages')
    EmergeDebug.debug('get installed package (release): %s' % db.getInstalled('win32libs', 'dbus-src', 'release'))
    EmergeDebug.debug('get installed package (debug):   %s' % db.getInstalled('win32libs', 'dbus-src', 'debug'))
    EmergeDebug.debug_line()

    EmergeDebug.new_line()
    EmergeDebug.debug('reverting removal')
    # now instead of completing the removal, revert it
    for pac in packageList:
        pac.revert()

    EmergeDebug.debug('checking installed packages')
    EmergeDebug.debug('get installed package (release): %s' % db.getInstalled('win32libs', 'dbus-src', 'release'))
    EmergeDebug.debug('get installed package (debug):   %s' % db.getInstalled('win32libs', 'dbus-src', 'debug'))
    EmergeDebug.debug_line()

    db.getInstalled()
    db.getInstalled( category='win32libs', prefix='debug' )
    db.getInstalled( package='dbus-src' )

    EmergeDebug.new_line()
    EmergeDebug.debug('now really remove the package')
    packageList = db.getInstalledPackages( 'win32libs', 'dbus-src' )
    for pac in packageList:
        EmergeDebug.debug('removing %s files' % len(pac.getFilesWithHashes()))
        pac.uninstall()

    EmergeDebug.debug('get installed package (release): %s' % db.getInstalled('win32libs', 'dbus-src', 'release'))
    EmergeDebug.debug('get installed package (debug):   %s' % db.getInstalled('win32libs', 'dbus-src', 'debug'))
    EmergeDebug.debug_line()

    # test the import from the old style (manifest based) databases
    EmergeDebug.new_line()
    print("getInstalled:", db_temp.getInstalled())

if __name__ == '__main__':
    main()
