# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# arcpy.da  -- Test stub stamding in for ESRI arcpy sub-module.
# Author: Lindsay Bradford, Truii.com, 2024.
# Release History:
# ---------------------------------------------------------------------------
# V1: Initial release
# ---------------------------------------------------------------------------
# 

import sys
from . import env
from . import da
from . import management

messages = []


def TestReset():
    messages.clear()


def AddFieldDelimiters(datasource, field):
    # https://pro.arcgis.com/en/pro-app/latest/arcpy/functions/addfielddelimiters.htm
    pass


def AddMessage(message):
    messages.append(message)
    print(message)


class Describe():
    # https://pro.arcgis.com/en/pro-app/latest/arcpy/functions/describe.htm
    # https://pro.arcgis.com/en/pro-app/latest/arcpy/functions/describe-object-properties.htm

    def __init__(self, value, dataType = None):
        self.name = value
        self.workspaceType = 'LocalDatabase'
        self.datatype = u'Workspace'
        self.children = []
        self.domains = []

    def __iter__(self):
        self.currentChildIndex  = 0
        return self

    def __next__(self):
        self.currentChildIndex += 1
        if self.currentChildIndex < len(self.children):
            return self.children[self.currentChildIndex]
        else:
            raise StopIteration


def Exists(workspace):
    return False


class Field():
    def __init__(self, name):
        self.name = name
        self.domain = self.name
        self.editable = True
        self.required = True
        pass


class FieldMap():
    # https://pro.arcgis.com/en/pro-app/latest/arcpy/classes/fieldmap.htm
    def __init__(self):
        self.outputField = Field('outputField')
        pass
 
    def addInputField(self, tableName, fieldName):
        pass


class FieldMappings():
    # https://pro.arcgis.com/en/pro-app/latest/arcpy/classes/fieldmappings.htm
    def __init__(self):
        self.maps = []
        
    def addFieldMap(self, fieldMap):
        self.maps.append(fieldMap)


def GetArgumentCount():
    argCount = 0
    while(sys.argv[argCount] != ''):
        argCount = argCount + 1
#    print(sys.argv[:argCount])
    return argCount - 1

def GetMessages(type):
    if type == 1:
        return 'warning one\nwarning two'
    if type == 2:
        return 'error one\nerror two'
    return ''


def GetMessage(index):
    return messages[index]


def GetMessageCount():
    return len(messages)


def GetParameterAsText(parmeterIndex):
    return sys.argv[parmeterIndex + 1]


def SetParameterAsText(parmeterIndex, text):
    sys.argv[parmeterIndex + 1] = text

def GetParameterInfo():
    return None

def GetSigninToken():
    return None


def ListFeatureClasses(wild_card = None):
    return ["featureClass1", "featureClass2"]


def ListTables(wild_card = None, table_type = None):
    # https://pro.arcgis.com/en/pro-app/latest/arcpy/functions/listtables.htm
    return ["table1", "table2"]


def ListFields(table):
    # https://pro.arcgis.com/en/pro-app/latest/arcpy/functions/listfields.htm
    return [Field('oid')]


def SpatialReference(CRS):
    pass


def Statistics_analysis(tableName, workspace, analysisType):
    return None

class ExecuteError(Exception):
    '''Raise some random ExecuteError'''