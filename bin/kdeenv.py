# -*- coding: utf-8 -*-
# this file sets some environment variables that are needed
# for finding programs and libraries etc.
# 
# by Holger Schroeder <schroder@kde.org>
# by Patrick Spendrin <ps_ml@gmx.de>
# by Ralf Habacker <ralf.habacker@freenet.de>

# you should copy kdesettings-example.ini to ..\etc\kdesettings.ini
# and adapt it to your needs (see that file for more info)

# this file should contain all path settings - and provide thus an environment
# to build and run kde programs
# this file sources the kdesettings.ini file automatically

import config
import os
import sys
import utils

verbose = 1
build_type = ''
application = ''

if verbose:
    utils.setVerbose(3)

if sys.argv[1] in ['debug', 'release', 'relwithdebinfo']:
    build_type = sys.argv[1]
elif sys.argv[1]:
    application = sys.argv[1]

os.environ['EMERGE_BUILDTYPE'] = build_type
os.environ['APPLICATION'] = application

# On win64 we have both %ProgramFiles% and %ProgramFiles(x86)%,
# but the latter is actually used for most of the paths (e.g. for Visual Studio)
# so we create a wrapper to use the right variable on both win32 and win64
if 'ProgramFiles(x86)' in os.environ: 
    PROGRAM_FILES=os.environ['ProgramFiles(x86)']
elif 'ProgramFiles' in os.environ:
    PROGRAM_FILES=os.environ['ProgramFiles']

# import kdesettings.ini
current_path= os.path.dirname(__file__)

for dir in ['../etc/kdesettings.ini', 'etc/kdesettings.ini', '../kdesettings.ini']:
    path = os.path.join(current_path, dir)
    if verbose:
        print(path)
    if os.path.exists(path):
        config.readConfig(path)
        break

# find python 
# FIXME: need to be set in bat wrapper
for dir in ['../python', 'python', 'emerge/python', os.environ['PYTHONPATH']]:
    python_path = os.path.join(current_path, dir)
    if verbose:
        print(python_path)
    if os.path.exists(python_path):
        os.environ['EMERGE_PYTHON_PATH'] = python_path
        print("Using Python from: %s" % python_path)

# handle drive substitution
#
# check for unversioned kdesettings.ini,
# in that case drive substition already took place
if 'EMERGE_SETTINGS_VERSION' in os.environ:
    # Make sure download/svn/git directories exist
    if not os.path.exists(os.environ['DOWNLOADDIR']):
        utils.createDir(os.environ['DOWNLOADDIR'])
    if not os.path.exists(os.environ['KDESVNDIR']):
        utils.createDir(os.environ['KDESVNDIR'])
    if not os.path.exists(os.environ['KDEGITDIR']):
        utils.createDir(os.environ['KDEGITDIR'])

    if os.environ['EMERGE_USE_SHORT_PATH'] == '1':
        os.environ['ROOT_SET'] = 'FALSE'
        os.environ['SVN_SET'] = 'FALSE'
        os.environ['DOWNLOAD_SET'] = 'FALSE'
        os.environ['GIT_SET'] = 'FALSE'
        # FIXME
        # Check if drives are already os.environ['up correctly
        #FOR /F "tokens=1,2,3* delims= " '] + ['i in ('subst') DO (
            #if /I "'] + ['i" == "!EMERGE_ROOT_DRIVE!\:" (
                #if /I "'] + ['k" == "!KDEROOT!" (
                    #os.environ['ROOT_SET=TRUE
                #)
            #)
            #if /I "'] + ['i" == "!EMERGE_SVN_DRIVE!\:" (
                #if /I "'] + ['k" == "!KDESVNDIR!" (
                    #os.environ['SVN_SET=TRUE
                #)
            #)
            #if /I "'] + ['i" == "!EMERGE_DOWNLOAD_DRIVE!\:" (
                #if /I "'] + ['k" == "!DOWNLOADDIR!" (
                    #os.environ['DOWNLOAD_SET=TRUE
                #)
            #)
            #if /I "'] + ['i" == "!EMERGE_GIT_DRIVE!\:" (
                #if /I "'] + ['k" == "!KDEGITDIR!" (
                    #os.environ['GIT_SET=TRUE
                #)
            #)
        #)
        if os.environ['ROOT_SET'] != 'TRUE':
            if os.path.exists(os.environ['EMERGE_ROOT_DRIVE']):
                utils.system('subst %s /D' % os.environ['EMERGE_ROOT_DRIVE'])
                utils.system('subst %s %s' % (os.environ['EMERGE_ROOT_DRIVE'], os.environ['KDEROOT']))

        if os.environ['DOWNLOAD_SET'] != 'TRUE':
            if os.path.exists(os.environ['EMERGE_DOWNLOAD_DRIVE']):
                utils.system('subst %s /D' % os.environ['EMERGE_DOWNLOAD_DRIVE'])
                utils.system('subst %s %s' % (os.environ['EMERGE_DOWNLOAD_DRIVE'], os.environ['DOWNLOADDIR']))

        if os.environ['SVN_SET'] != 'TRUE':
            if os.path.exists(os.environ['EMERGE_SVN_DRIVE']):
                utils.system('subst %s /D' % os.environ['EMERGE_SVN_DRIVE'])
                utils.system('subst %s %s' % (os.environ['EMERGE_SVN_DRIVE'], os.environ['KDESVNDIR']))

        if os.environ['GIT_SET'] != 'TRUE':
            if os.path.exists(os.environ['EMERGE_GIT_DRIVE']):
                utils.system('subst %s /D' % os.environ['EMERGE_GIT_DRIVE'])
                utils.system('subst %s %s' % (os.environ['EMERGE_GIT_DRIVE'], os.environ['KDEGITDIR']))

        os.environ['KDEROOT'] = os.environ['EMERGE_ROOT_DRIVE']
        os.environ['KDESVNDIR'] = os.environ['EMERGE_SVN_DRIVE']
        os.environ['DOWNLOADDIR'] = os.environ['EMERGE_DOWNLOAD_DRIVE']
        os.environ['KDEGITDIR'] = os.environ['EMERGE_GIT_DRIVE']
        #!EMERGE_ROOT_DRIVE!



# print pathes 
if 'EMERGE_SETTINGS_VERSION' in os.environ:
    print('KDEROOT     : %s' % os.environ['KDEROOT'])
    print('KDECOMPILER : %s' % os.environ['KDECOMPILER'])
    print('KDESVNDIR   : %s' % os.environ['KDESVNDIR'])
    print('KDEGITDIR   : %s' % os.environ['KDEGITDIR'])
    print('DOWNLOADDIR : %s' % os.environ['DOWNLOADDIR'])
    if os.name == 'nt':
        utils.system("title %s %s" % (os.environ['KDEROOT'], os.environ['KDECOMPILER']))

# handle multiple merge roots
# FIXME: check logic 
if not build_type:
    if os.environ['EMERGE_MERGE_ROOT_WITH_BUILD_TYPE'] == 'True':
        os.environ['SUBDIR'] = os.environ['EMERGE_BUILDTYPE']
else:
    os.environ['SUBDIR'] = os.environ['EMERGE_BUILDTYPE']


os.environ['PATH'] = os.path.join(os.environ['KDEROOT'], os.environ['SUBDIR'], 'bin') + ';' + os.environ['PATH']
os.environ['KDEDIRS'] = os.path.join(os.environ['KDEROOT'], os.environ['SUBDIR'])
os.environ['QT_PLUGIN_PATH'] = os.path.join(os.environ['KDEDIRS'], 'plugins') + ';' + os.path.join(os.environ['KDEDIRS'], 'lib', 'kde4',',plugins')
os.environ['XDG_DATA_DIRS'] = os.path.join(os.environ['KDEDIRS'], 'share')

# for emerge
os.environ['PATH'] = os.path.join(os.environ['KDEROOT'], 'emerge', 'bin') + ';' + os.environ['PATH']

# for dev-utils
os.environ['PATH'] = os.path.join(os.environ['KDEROOT'], 'dev-utils','bin') + ';' + os.environ['PATH']

# for old packages
os.environ['PATH'] = os.path.join(os.environ['KDEROOT'], 'bin') + ';' + os.environ['PATH']

# for python
if 'EMERGE_PYTHON_PATH' in os.environ:
   os.environ['PATH'] = os.environ['EMERGE_PYTHON_PATH'] + ';' + os.environ['PATH']
   if os.path.exists(os.path.join(os.environ['EMERGE_PYTHON_PATH'],'Scripts')):
        os.environ['PATH'] = os.path.join(os.environ['EMERGE_PYTHON_PATH'],'Scripts') + ';' + os.environ['PATH']

if 'EMERGE_USE_CCACHE' in os.environ and os.environ['EMERGE_USE_CCACHE'] == 'True':
   os.environ['CCACHE_DIR'] = os.path.join(os.environ['KDEROOT'], 'build', 'CCACHE')

if os.name == 'nt':
	utils.system("cmd.exe")
else:
	utils.system("/bin/bash --noprofile")
