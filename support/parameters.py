# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# support/parameters.py
# Author: Lindsay Bradford, Truii.com, 2024.
# Release History:
# ---------------------------------------------------------------------------
# V1: Initial release

import arcpy
from support.messenger import Messenger

# Context keys

TOKEN = 'Token'
SERVICE_INFO = 'ServiceInfo'
LAST_SYNC_TIME = 'LastSynchronisationTime'
PROCESS_TIME = 'ProcessTime'
SECTION = 'ProcessSection'
CLEANUP_OPERATIONS = 'CleanupOperations'
EXISTING_TABLES = 'ExistingTables'

# parameter keys

MAP_CONTENT = 'CONFIG'
CONFIG_FILE_PATH = 'filepath'
CONFIG_FILE_SECTION = 'section'

SDE_CONNECTION = 'sde_conn'
PREFIX = 'prefix'
TIMEZONE = 'timezone'
PORTAL = 'portal'
USER_NAME = 'username'
PASSWORD = 'password'
REPROJECT_CODE = 'reprojection'
SERVICE_URL = 'service_url'

MANDATORY_PARAMETERS = [
    SDE_CONNECTION,
    PREFIX,
    TIMEZONE,
    PORTAL,
    REPROJECT_CODE,
    SERVICE_URL
]

OPTIONAL_PARAMETERS = [
    USER_NAME,
    PASSWORD
]

def produceParameters():
    rawParams = []

    for index in range(arcpy.GetArgumentCount()):
        rawParams.append(arcpy.GetParameterAsText(index))
        
    params = {}
    if arcpy.GetArgumentCount() >= 3 and arcpy.GetParameterAsText(0) == MAP_CONTENT:
        params[CONFIG_FILE_PATH] = arcpy.GetParameterAsText(1)
        params[CONFIG_FILE_SECTION] = arcpy.GetParameterAsText(2)
    elif arcpy.GetArgumentCount() >= 6:
        params[SDE_CONNECTION] = arcpy.GetParameterAsText(0)
        params[PREFIX] = arcpy.GetParameterAsText(1)
        params[SERVICE_URL] = arcpy.GetParameterAsText(2)
        params[TIMEZONE] = arcpy.GetParameterAsText(3)
        params[PORTAL] = arcpy.GetParameterAsText(4)
        params[REPROJECT_CODE] = arcpy.GetParameterAsText(5)  # TODO: check syncsurvey, maybe this should go before credentials?
        params[USER_NAME] = arcpy.GetParameterAsText(6)
        params[PASSWORD] = arcpy.GetParameterAsText(7)
    else:
        raise SystemExit(f"Expected parameter(s) [{arcpy.GetArgumentCount()}] were not supplied")
    
    Messenger().info(f'Parameters supplied: [{params}]')

    return params
        
        
