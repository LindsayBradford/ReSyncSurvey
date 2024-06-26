# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# support/arc_proxy.py  -Keeps components from calling arcpy directoy.
# Author: Lindsay Bradford, Truii.com, 2024.
# Release History:
# ---------------------------------------------------------------------------
# V1: Initial release


import support.time as time

import arcpy

def runningWithinToolbox():
    if arcpy.GetParameterInfo():
        return True
    return False


def raiseExecuteError(message, baseException = None):
    raise arcpy.ExecuteError(message, baseException)
    

def cleanupAppends(sdeConnection, processTime, tables):
    arcpy.env.workspace = sdeConnection
    timestamp = time.createTimestampText(processTime)

    i = 0
    for table in tables:
        i = i + 1
        thisName = f'layerOrView{str(i)}'
        whereStatment = f"sys_transfer_date = timestamp'{timestamp}'"
        dsc = arcpy.Describe(table)
        if dsc.datatype == u'FeatureClass':
            arcpy.MakeFeatureLayer_management(table, thisName, whereStatment)
            arcpy.management.DeleteFeatures(thisName)
        else:
            arcpy.MakeTableView_management(table, thisName, whereStatment)
            arcpy.DeleteRows_management(thisName)
            

def cleanupCreatedTables(sdeConnection, prefix):
    for table in getSurveyTables(sdeConnection, prefix):
        arcpy.management.Delete(table)
        

def getSurveyTables(sdeConnection, prefix):
    originalWorkspace = arcpy.env.workspace
        
    arcpy.env.workspace = sdeConnection

    #This is used in 2 contexts:
    #Downloaded GDB - tables have no prefix
    #Enterprise GDB - prefix is added to table name
    #The full table name (i.e. GDB.SCHEMA.NAME) is returned, so prefix is in the middle
    wildcard = '*{0}*'.format(prefix) if prefix != '' else '*'
    #List the Feature Classes & Tables
    #Tables also returns Attachment tables
    featureClasses = arcpy.ListFeatureClasses(wildcard)
    tables = arcpy.ListTables(wildcard)

    #Loop through the tables, checking for:
    #1) Is this an attachment table?
    #2) Does the prefix actually match the prefix term exactly?
    allTables = featureClasses
    allTables.extend(tables)
    outTables = []
    for t in allTables:
        tableName = t.split('.')[-1]
        nameParts = tableName.split('_')
        if '__ATTACH' not in t:
            if nameParts[0] == prefix or prefix == '':
                outTables.append(t)

    arcpy.env.workspace = originalWorkspace
    return outTables


def GetMessages(severity):
    return arcpy.GetMessages(severity)

def isExecuteError(exception):
    if isinstance(exception, arcpy.ExecuteError):
        return True
    return False