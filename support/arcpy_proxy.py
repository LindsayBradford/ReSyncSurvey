# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# support/arc_proxy.py  -Keeps components from calling arcpy directoy.
# Author: Lindsay Bradford, Truii.com, 2024.
# Release History:
# ---------------------------------------------------------------------------
# V1: Initial release


import support.time as time
from support.messenger import Messenger
import arcpy

messenger = Messenger()

def runningWithinToolbox():
    if arcpy.GetParameterInfo():
        return True
    return False


def raiseExecuteError(message, baseException = None):
    raise arcpy.ExecuteError(message, baseException)
    

def cleanupAppends(sdeConnection, processTime, tables):
    arcpy.env.workspace = sdeConnection
    timestamp = time.createTimestampText(processTime)
    whereStatment = f"sys_transfer_date = timestamp'{timestamp}'"

    messenger.indent()
    messenger.info(f'Applying where statement ["{whereStatment}"] for isolating newly added rows')

    i = 0
    for table in tables:
        i = i + 1
        thisName = f'layerOrView{str(i)}'
        dsc = arcpy.Describe(table)
        if dsc.datatype == u'FeatureClass':
            arcpy.management.MakeFeatureLayer(table, thisName, whereStatment)
            messenger.debug(f'Deleting matching rows from feature class [{table}]')
            arcpy.management.DeleteFeatures(thisName)
        else:
            arcpy.management.MakeTableView(table, thisName, whereStatment)
            messenger.debug(f'Deleting matching rows from table [{table}]')
            arcpy.management.DeleteRows(thisName)

    messenger.outdent()
            

def cleanupCreatedTables(sdeConnection, prefix):
    messenger.indent()

    for table in getSurveyTables(sdeConnection, prefix):
        messenger.debug(f'Deleting table [{table}]')
        arcpy.management.Delete(table)

    messenger.outdent()
        

def getSurveyTables(workspace, prefix=''):
    originalWorkspace = arcpy.env.workspace
    arcpy.env.workspace = workspace
        
    tables = getSurveyTablesFromCurrentWorkspace(prefix)

    arcpy.env.workspace = originalWorkspace
    return tables


def getSurveyTablesFromCurrentWorkspace(prefix=''):
    #This is used in 2 contexts:
    #Downloaded GDB - tables have no prefix
    #Enterprise GDB - prefix is added to table name
    #The full table name (i.e. GDB.SCHEMA.NAME) is returned, so prefix is in the middle
    wildcard = f'*{prefix}*' if prefix != '' else '*'
    #List the Feature Classes & Tables
    #Tables also returns Attachment tables
        
    messenger.info(f'Applying pattern match ["{wildcard}"] for table search at [{arcpy.env.workspace}]')

    featureClasses = arcpy.ListFeatureClasses(wildcard)
    tables = arcpy.ListTables(wildcard)

    if featureClasses != None:
        messenger.debug(f'Found {len(featureClasses)} matching feature classes')
    if tables != None:
        messenger.debug(f'Found {len(tables)} matching tables')

    #Loop through the tables, checking for:
    #1) Is this an attachment table?
    #2) Does the prefix actually match the prefix term exactly?
        
    allTables = []
    if featureClasses != None:
        allTables.extend(featureClasses)
    if tables != None:
        allTables.extend(tables)
        
    outTables = []
    for t in allTables:
        tableName = t.split('.')[-1]
        nameParts = tableName.split('_')
        if '__ATTACH' not in t:
            if nameParts[0] == prefix or prefix == '':
                outTables.append(t)

    return outTables


def GetMessages(severity):
    return arcpy.GetMessages(severity)

def Delete(dataElement):
    messenger.info(f'Deleting [{dataElement}] via arcpy')
    arcpy.management.Delete(dataElement)

def isExecuteError(exception):
    if isinstance(exception, arcpy.ExecuteError):
        return True
    return False
