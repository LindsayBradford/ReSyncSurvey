# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# support.arcpy.py -- Test stub for ESRI arcpy library.
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


def GetSigninToken():
    return None

def Exists(workspace):
    return False

def AddMessage(message):
    messages.append(message)
    print(message)


def GetMessage(index):
    return messages[index]


def GetMessageCount():
    return len(messages)


def GetArgumentCount():
    argCount = 0
    while(sys.argv[argCount] != ''):
        argCount = argCount + 1
#    print(sys.argv[:argCount])
    return argCount - 1


def GetParameterAsText(parmeterIndex):
    return sys.argv[parmeterIndex + 1]


def SetParameterAsText(parmeterIndex, text):
    sys.argv[parmeterIndex + 1] = text
    

def ListFeatureClasses(wild_card = None):
    return ["featureClass1", "featureClass2"]


def ListTables(wild_card = None, table_type = None):
    # https://pro.arcgis.com/en/pro-app/latest/arcpy/functions/listtables.htm
    return ["table1", "table2"]

def AddFieldDelimiters(datasource, field):
    # https://pro.arcgis.com/en/pro-app/latest/arcpy/functions/addfielddelimiters.htm
    pass

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


def MakeFeatureLayer_management(table, thisName, excludeStatement):
    pass

def DeleteFeatures_management(tableName):
    pass

def DeleteRows_management(tableName):
    pass

def Delete_management(tableName):
    pass

def DisableEditorTracking_management(table):
    pass

def AddField_management(table , field_name, field_type):
    # https://pro.arcgis.com/en/pro-app/latest/tool-reference/data-management/add-field.htm
    pass

def MakeTableView_management(in_table, out_view, where_clause = None, workspace = None, field_info = None):
    # https://pro.arcgis.com/en/pro-app/latest/tool-reference/data-management/make-table-view.htm
    pass

def CreateTable_management(outWorkspace, newTableName, template=None):
    pass

def AssignDomainToField_management(tableName, fieldName, domainName):
    pass

def Append_management(table, destination, schemaType, field_mapping):
    # https://pro.arcgis.com/en/pro-app/latest/tool-reference/data-management/append.htm
    pass

class FieldMappings():
    # https://pro.arcgis.com/en/pro-app/latest/arcpy/classes/fieldmappings.htm
    def __init__(self):
        self.maps = []
        
    def addFieldMap(self, fieldMap):
        self.maps.append(fieldMap)

class FieldMap():
    # https://pro.arcgis.com/en/pro-app/latest/arcpy/classes/fieldmap.htm
    def __init__(self):
        self.outputField = Field('outputField')
        pass
 
    def addInputField(self, tableName, fieldName):
        pass
    

class Field():
    def __init__(self, name):
        self.name = name
        self.domain = self.name
        self.editable = True
        self.required = True
        pass

def ListFields(table):
    # https://pro.arcgis.com/en/pro-app/latest/arcpy/functions/listfields.htm
    return [Field('oid')]

def CreateFileGDB_management(pathOnly, dbName):
    pass




def SpatialReference(CRS):
    pass