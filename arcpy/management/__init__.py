# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# arcpy.managemnt -- Test stub stamding in for ESRI arcpy sub-module
# Author: Lindsay Bradford, Truii.com, 2024.
# Release History:
# ---------------------------------------------------------------------------
# V1: Initial release
# ---------------------------------------------------------------------------
# 

def AddField(table , field_name, field_type):
    # https://pro.arcgis.com/en/pro-app/latest/tool-reference/data-management/add-field.htm
    pass


def Append(table, destination, schemaType, field_mapping):
    # See: https://pro.arcgis.com/en/pro-app/latest/tool-reference/data-management/append.htm
    pass


def AssignDomainToField(tableName, fieldName, domainName):
    pass


def Copy(sourceWorkspace, destWorkspace):
    pass


def CopyRows(in_rows, out_table, config_keyword = None):
    # See: https://pro.arcgis.com/en/pro-app/latest/tool-reference/data-management/copy-rows.htm
    pass


def CreateFileGDB(pathOnly, dbName):
    pass


def CreateTable(outWorkspace, newTableName, template=None):
    pass


def Delete(workspace):
    pass


def DeleteRows(tableName):
    pass


def DeleteFeatures(tableName):
    pass


def DisableEditorTracking(table):
    pass


def GetCount(*tableNames):
    counts = []
    for tableName in tableNames:
        counts.append(int(0))
    return counts


def MakeFeatureLayer(table, thisName, excludeStatement):
    pass


def MakeTableView(in_table, out_view, where_clause = None, workspace = None, field_info = None):
    # https://pro.arcgis.com/en/pro-app/latest/tool-reference/data-management/make-table-view.htm
    pass


def Project(inputFC, outputFC, out_coordinate_system):
    pass


