from dataclasses import MISSING
from optparse import Option
from support.parameters import *

import configparser
import os

import arcpy

DEFAULT_SECTION = 'DEFAULT'
CONFIG = 'CONFIG'

class Config:
    def __init__(self):
        self.configMap = {}
        if arcpy.GetParameterAsText(0) == CONFIG:
            filepath = arcpy.GetParameterAsText(1)
            section = arcpy.GetParameterAsText(2)

            self.deriveParametersFromConfigFile(filepath, section)
        else:
            self.deriveParametersFromCommandLine()


    def deriveParametersFromConfigFile(self, filepath, section):
        parser = configparser.ConfigParser(default_section=DEFAULT_SECTION)

        if not os.access(filepath, os.R_OK):
            raise SystemExit(f"Invalid config file [{filepath}] passed as config parser parameter")
        
        parser.read(filepath)

        misingParameters = []
        for option in MANDATORY_PARAMETERS:            
            if option not in parser[section]:
                misingParameters.append(option)
            else:
                self.configMap[option] = parser.get(section, option)

        if len(misingParameters) > 0:
            raise SystemExit(f"Expected parameter(s) {misingParameters} missing from config file [{filepath}]")
                
        for option in OPTIONAL_PARAMETERS:            
            if option in parser[section]:
                self.configMap[option] = parser.get(section, option)


    def deriveParametersFromCommandLine(self):
        self.configMap[SDE_CONNECTION] = arcpy.GetParameterAsText(0)
        self.configMap[PREFIX] = arcpy.GetParameterAsText(1)
        self.configMap[SERVICE_URL] = arcpy.GetParameterAsText(2)
        self.configMap[TIMEZONE] = arcpy.GetParameterAsText(3)
        self.configMap[PORTAL] = arcpy.GetParameterAsText(4)
        self.configMap[USER_NAME] = arcpy.GetParameterAsText(5)
        self.configMap[PASSWORD] = arcpy.GetParameterAsText(6)
        self.configMap[REPROJECT_CODE] = arcpy.GetParameterAsText(7)
        
        
    def map(self):
        return self.configMap

