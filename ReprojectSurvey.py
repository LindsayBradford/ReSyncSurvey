# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# ReprojectSurvey.py
# Author: Lindsay Bradford, Truii.com, 2024.
# Release History:
# ---------------------------------------------------------------------------
# V1: Initial release
# ---------------------------------------------------------------------------


import arcpy

import configparser
DEFAULT_SECTION = 'DEFAULT'

CONFIG = 'CONFIG'

context = {}

# context keys

PARAMETERS = 'Parameters'
SDE_CONNECTION = 'SDE_Connection'
FEATURE_SERVICE = 'FeatureService'
PREFIX = 'Prefix'
TIMEZONE = 'TimeZone'
PORTAL = 'Portal'
USER_NAME = 'UserName'
PASSWORD = 'Password'


def processParameters():
    parameters = context[PARAMETERS]
    for parameter in parameters:
        arcpy.AddMessage(f'Parameter [{parameter}] supplied = [{parameters[parameter]}]')


def deriveParametersFromConfigFile(filepath, section):
    parser = configparser.ConfigParser(default_section=DEFAULT_SECTION)

    parser.read(filepath)

    for option in parser[section]:
        context[PARAMETERS][option] = parser.get(section, option)


def deriveParametersFromCommandLine():
    context[PARAMETERS][SDE_CONNECTION] = arcpy.GetParameterAsText(0)
    context[PARAMETERS][PREFIX] = arcpy.GetParameterAsText(1)
    context[PARAMETERS][FEATURE_SERVICE] = arcpy.GetParameterAsText(2)
    context[PARAMETERS][TIMEZONE] = arcpy.GetParameterAsText(3)
    context[PARAMETERS][PORTAL] = arcpy.GetParameterAsText(4)
    context[PARAMETERS][USER_NAME] = arcpy.GetParameterAsText(5)
    context[PARAMETERS][PASSWORD] = arcpy.GetParameterAsText(6)


def deriveParameters():
    context[PARAMETERS] = {}
     
    if arcpy.GetParameterAsText(0) == CONFIG:
        filepath = arcpy.GetParameterAsText(1)
        section = arcpy.GetParameterAsText(2)

        deriveParametersFromConfigFile(filepath, section)
    else:
        deriveParametersFromCommandLine()


def main():
    deriveParameters()        
    processParameters()


if __name__ == '__main__':
    main()