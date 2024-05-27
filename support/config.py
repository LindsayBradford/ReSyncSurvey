# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# support/config.py
# Author: Lindsay Bradford, Truii.com, 2024.
# Release History:
# ---------------------------------------------------------------------------
# V1: Initial release

from support.parameters import *

import configparser

DEFAULT_SECTION = 'DEFAULT'
CONFIG = 'CONFIG'

class Config:

    def __init__(self):
        self.withConfigMap(None)
        self.withParser(None)

            
    def withConfigMap(self, configMap):
        self.configMap = configMap
        return self

    
    def withParser(self,parser):
        if parser == None:
            self.parser = configparser.ConfigParser(default_section = DEFAULT_SECTION)
        else:
            self.parser = parser
        return self


    def map(self):
        if self.configMap == None:
            self.configMap = produceParameters()

        if CONFIG_FILE_PATH in self.configMap.keys():
            self.deriveMapFromConfigFile()
            
        return self.configMap


    def deriveMapFromConfigFile(self):
        self.parseConfigFile()
     
        self.parseMandatoryParameters()
        self.parseOptionalParameters()

        del self.configMap[CONFIG_FILE_PATH]
        del self.configMap[CONFIG_FILE_SECTION]


    def parseConfigFile(self):
        if self.configMap == {}:
            raise SystemExit(f"No configuration supplied before attempting to specify a parser.")

        if CONFIG_FILE_PATH not in self.configMap.keys():
            raise SystemExit(f"Configuration supplied doesn't need a parser.")

        filesParsed = self.parser.read(self.configMap[CONFIG_FILE_PATH])

        if self.configMap[CONFIG_FILE_PATH] not in filesParsed:
            raise SystemExit(f"Invalid config file [{self.configMap[CONFIG_FILE_PATH]}] passed as config parser parameter")

        if self.configMap[CONFIG_FILE_SECTION] not in self.parser.sections():
            raise SystemExit(f"Invalid section [{self.configMap[CONFIG_FILE_SECTION]}] for config file [{self.configMap[CONFIG_FILE_PATH]}] passed as config parser parameter")


    def parseMandatoryParameters(self):
        misingParameters = []
        for option in MANDATORY_PARAMETERS:            
            if option not in self.parser[self.configMap[CONFIG_FILE_SECTION]]:
                misingParameters.append(option)
            else:
                self.configMap[option] = self.parser.get(self.configMap[CONFIG_FILE_SECTION], option)

        if len(misingParameters) > 0:
            raise SystemExit(f"Expected parameter(s) {misingParameters} missing from config file [{self.configMap[CONFIG_FILE_PATH]}]")

        
    def parseOptionalParameters(self):
        for option in OPTIONAL_PARAMETERS:
            if option in self.parser[self.configMap[CONFIG_FILE_SECTION]]:
                self.configMap[option] = self.parser.get(self.configMap[CONFIG_FILE_SECTION], option)
