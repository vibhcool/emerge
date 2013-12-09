# -*- coding: utf-8 -*-
# config parser
#    by Ralf Habacker <ralf.habacker@freenet.de>

import configparser
import os
import utils

def readConfig(filename):
    config = configparser.RawConfigParser()
    config.optionxform = lambda option: option
    config.read(filename)
    for key in config.sections():
        for item in config.items(key):
            os.environ[item[0]] = item[1]

    # replace ${key} by related environment variable
    for key in os.environ:
        value = os.environ[key]
        start = value.find('${');
        if start > -1:
            end = value.find('}', start)
            if end == -1:
                continue
            search = value[start:end-start+1]
            replacekey = value[start+2:end-start]
            if replacekey in os.environ:
                os.environ[key] = value.replace(search, os.environ[replacekey])

# example
#import config
#config.readConfig('../etc/kdesettings.ini')
#import utils
#utils.system("sh -c set")
