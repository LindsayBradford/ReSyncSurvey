# ---------------------------------------------------------------------------
# config.py
# Scope:  Supplies config dictionary to be shared across multiple scripts
# Author: Lindsay Bradford, Truii.com, 2022.
# Release History:
# ---------------------------------------------------------------------------
# V1: Initial release
# ---------------------------------------------------------------------------

import argparse
import json
import os
import sys

# config should contain external or setup-wide constant data only. 

class Config(dict):
    def __init__(self):
        self['Version'] = '1.0'
        
        self.extractCommandLineArguments()
        self.loadConfigFromArguments()


    def extractCommandLineArguments(self):
        self.defineCommandLineArguments()
        self.retrieveArguments()
        
        
    def defineCommandLineArguments(self):
        self._parser = argparse.ArgumentParser(prog=os.path.basename(sys.argv[0]), usage='%(prog)s [options]', argument_default='--help')

        self._parser.add_argument('--version', action='version', version=f'%(prog)s {self["Version"]}')
        self._parser.add_argument('--configFile', nargs='?', required=True, type=argparse.FileType('r'),  help='relative path to the setup configuration file')
        
        
    def retrieveArguments(self):
        args = self._parser.parse_args()
        self._arguments = vars(args)
    

    def loadConfigFromArguments(self):
        configFileHandle = self._arguments['configFile']
        loadedConfig = json.load(configFileHandle)
        self.update(loadedConfig)

        self.configureLogFile(configFileHandle)
        
        configFileHandle.close()

    def configureLogFile(self,configFileHandle):
        newWorkingDirectory = os.path.dirname(configFileHandle.name)
        os.chdir(newWorkingDirectory)
        
config = Config()