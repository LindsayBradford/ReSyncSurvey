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

class ArcpyProxy():
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ArcpyProxy, cls).__new__(cls)
            cls._instance.reset()
        return cls._instance    

    def reset(self):
        self.messenger = Messenger()

    def runningWithinToolbox(self):
        if arcpy.GetParameterInfo():
            return True
        return False

    def raiseExecuteError(self, message, baseException = None):
        raise arcpy.ExecuteError(message, baseException)

    def cleanupAppends(self, sdeConnection, processTime, tables):
        arcpy.env.workspace = sdeConnection
        timestamp = time.createTimestampText(processTime)
        whereStatment = f"sys_transfer_date = timestamp'{timestamp}'"

        self.messenger.indent()
        self.messenger.info(f'Applying where statement ["{whereStatment}"] for isolating newly added rows')

        i = 0
        for table in tables:
            i = i + 1
            thisName = f'layerOrView{str(i)}'
            dsc = arcpy.Describe(table)
            if dsc.datatype == u'FeatureClass':
                arcpy.management.MakeFeatureLayer(table, thisName, whereStatment)
                self.messenger.debug(f'Deleting matching rows from feature class [{table}]')
                arcpy.management.DeleteFeatures(thisName)
            else:
                arcpy.management.MakeTableView(table, thisName, whereStatment)
                self.messenger.debug(f'Deleting matching rows from table [{table}]')
                arcpy.management.DeleteRows(thisName)

        self.messenger.outdent()

    def cleanupCreatedTables(self, sdeConnection, prefix):
        self.messenger.indent()

        for table in self.getSurveyTables(sdeConnection, prefix):
            self.messenger.debug(f'Deleting table [{table}]')
            arcpy.management.Delete(table)

        self.messenger.outdent()

    def getSurveyTables(self, workspace, prefix=''):
        originalWorkspace = arcpy.env.workspace
        arcpy.env.workspace = workspace
        
        tables = self.getSurveyTablesFromCurrentWorkspace(prefix)

        arcpy.env.workspace = originalWorkspace
        return tables

    def getSurveyTablesFromCurrentWorkspace(self, prefix=''):
        #This is used in 2 contexts:
        #Downloaded GDB - tables have no prefix
        #Enterprise GDB - prefix is added to table name
        #The full table name (i.e. GDB.SCHEMA.NAME) is returned, so prefix is in the middle
        wildcard = f'*{prefix}*' if prefix != '' else '*'
        #List the Feature Classes & Tables
        #Tables also returns Attachment tables
        
        self.messenger.info(f'Applying pattern match ["{wildcard}"] for table search at [{arcpy.env.workspace}]')

        featureClasses = arcpy.ListFeatureClasses(wildcard)
        tables = arcpy.ListTables(wildcard)

        self.messenger.indent()
        if featureClasses != None:
            self.messenger.debug(f'Found {len(featureClasses)} matching feature classes')
        if tables != None:
            self.messenger.debug(f'Found {len(tables)} matching tables')
        self.messenger.outdent()

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

    def GetMessages(self, severity):
        return arcpy.GetMessages(severity)

    def Delete(self, dataElement):
        self.messenger.info(f'Deleting [{dataElement}]')
        arcpy.management.Delete(dataElement)

    def isExecuteError(self, exception):
        if isinstance(exception, arcpy.ExecuteError):
            return True
        return False
