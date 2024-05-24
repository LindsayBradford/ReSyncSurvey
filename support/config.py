# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# support/config.py
# Author: Lindsay Bradford, Truii.com, 2024.
# Release History:
# ---------------------------------------------------------------------------
# V1: Initial release

from support.parameters import *

import configparser

import arcpy

DEFAULT_SECTION = 'DEFAULT'
CONFIG = 'CONFIG'

class Config:

    def __init__(self) :
        self.configMap = {}
            
        if arcpy.GetParameterAsText(0) == CONFIG:
            self.deriveParametersFromConfigFile()
        else:
            self.deriveParametersFromCommandLine()


    def deriveParametersFromConfigFile(self):
        self.filepath = arcpy.GetParameterAsText(1)
        self.section = arcpy.GetParameterAsText(2)
        
        self.parseConfig()


    def parseConfig(self):
        self.parseConfigFile()
     
        self.parseMandatoryParameters()
        self.parseOptionalParameters()


    def parseConfigFile(self):
        self.parser = configparser.ConfigParser(default_section = DEFAULT_SECTION)
        filesParsed = self.parser.read(self.filepath)

        if self.filepath not in filesParsed:
            raise SystemExit(f"Invalid config file [{self.filepath}] passed as config parser parameter")

        if self.section not in self.parser.sections():
            raise SystemExit(f"Invalid section [{self.section}] for config file [{self.filepath}] passed as config parser parameter")
        

    def parseMandatoryParameters(self):
        misingParameters = []
        for option in MANDATORY_PARAMETERS:            
            if option not in self.parser[self.section]:
                misingParameters.append(option)
            else:
                self.configMap[option] = self.parser.get(self.section, option)

        if len(misingParameters) > 0:
            raise SystemExit(f"Expected parameter(s) {misingParameters} missing from config file [{self.filepath}]")

        
    def parseOptionalParameters(self):
        for option in OPTIONAL_PARAMETERS:
            if option in self.parser[self.section]:
                self.configMap[option] = self.parser.get(self.section, option)
        

    def deriveParametersFromCommandLine(self):
        self.configMap[SDE_CONNECTION] = arcpy.GetParameterAsText(0)
        self.configMap[PREFIX] = arcpy.GetParameterAsText(1)
        self.configMap[SERVICE_URL] = arcpy.GetParameterAsText(2)
        self.configMap[TIMEZONE] = arcpy.GetParameterAsText(3)
        self.configMap[PORTAL] = arcpy.GetParameterAsText(4)
        self.configMap[USER_NAME] = arcpy.GetParameterAsText(5)
        self.configMap[PASSWORD] = arcpy.GetParameterAsText(6)
        self.configMap[REPROJECT_CODE] = arcpy.GetParameterAsText(7)  # TODO: check syncsurvey, maybe this should go before credentials?
        
        
    def map(self):
        return self.configMap

