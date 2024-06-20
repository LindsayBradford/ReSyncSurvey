# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Name: support/transformer.py
# Purpose: To transorm data in a temp file geodatabase via uniform interface
# Author: Lindsay Bradford, Truii.com, 2024, based heaviy on syncSurvey
# Release History:
# ---------------------------------------------------------------------------
# V1: Initial release

from support.parameters import *
from support.messenger import Messenger


from abc import ABC, abstractmethod
import support.time as time
import os
import uuid
import arcpy

# Context keys

LAST_SYNC_TIME = 'LastSynchronisationTime'
PROCESS_TIME = 'ProcessTime'
SECTION = 'ProcessSection'
EXISTING_TABLES = 'ExistingTables'

class Transformer(ABC):
    def withContext(self, context):
        self.context = context
        return self

    @abstractmethod
    def transform(self, surveyGDB):
        return None


class NullTransformer(Transformer):
    def __init__(self, parametersSupplied):
        self.context = {}
        self.parameters = parametersSupplied
        
    def transform(self, surveyGDB):
        return f"<Nothing transformed in Survey geodatabase {surveyGDB}>"


class FGDBReprojectionTransformer(Transformer):
    def __init__(self, parametersSupplied):
        self.context = {}
        self.messenger = Messenger()
        self.parameters = parametersSupplied


    def transform(self, surveyGDB):
        self.messenger.info(f'Transforming survey at [{surveyGDB}]...')
        self.messenger.indent()

        self.checkExistingData()
        self.filterRecords(surveyGDB)
        self.addTimeStamp(surveyGDB)
        self.addKeyFields(surveyGDB)

        self.messenger.outdent()
        self.messenger.info(f'Done transforming survey at [{surveyGDB}]')


    def checkExistingData(self):
        self.messenger.info(f'Checking existing data via [{self.parameters[SDE_CONNECTION]}]')
        self.messenger.indent()

        existingTables = self.getSurveyTables(self.parameters[SDE_CONNECTION], self.parameters[PREFIX])
        if len(existingTables) > 0:
            self.getLastSynchronizationTime(existingTables)
            if self.context[LAST_SYNC_TIME] != None:
                self.messenger.info(f'Last synchronisation time established [{time.createTimestampText(self.context[LAST_SYNC_TIME])}]')
            else:
                self.messenger.warn(f'No last synchronisation time establised, despite [{len(existingTables)}] tables found.')
        else:
            self.messenger.info(f'No existing tables with prefix [{self.parameters[PREFIX]}] found in [{self.parameters[SDE_CONNECTION]}]')
            
        self.context[EXISTING_TABLES] = existingTables

        self.messenger.outdent()
        self.messenger.info(f'Done checking existing data via [{self.parameters[SDE_CONNECTION]}]')


    def getSurveyTables(self, workspace, prefix=''):
        originalWorkspace = arcpy.env.workspace
        arcpy.env.workspace = workspace
        
        tables = self.getSurveyTablesFromCurrentWorkspace()

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

        if featureClasses != None:
            self.messenger.debug(f'Found {len(featureClasses)} matching feature classes')
        if tables != None:
            self.messenger.debug(f'Found {len(tables)} matching tables')

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


    def getLastSynchronizationTime(self, tableList):
        # Looks at the existing records in the SDE and returns the latest synchronization time
        originalWorkspace = arcpy.env.workspace
        arcpy.env.workspace = self.parameters[SDE_CONNECTION]

        statTables = []
        #Dummy value to compare time
        lastSync = time.dummyTimestamp()
        
        self.messenger.indent()

        for table in tableList:
            #Skip if empty table (i.e., no rows)
            self.messenger.debug(f'Checking sync on table [{table}]')
            #Just use the last part of the table name
            tableName = FGDBReprojectionTransformer.lastPartOfTableName(table)
            rowCheck = arcpy.management.GetCount(tableName)
            rowCount = int(rowCheck[0])
            if rowCount > 0:
                statTable = arcpy.Statistics_analysis(tableName, f'in_memory\stat_{tableName}', "SYS_TRANSFER_DATE MAX")
                statTables.append(statTable)

        for s in statTables:
            with arcpy.da.SearchCursor(s, ['MAX_sys_transfer_date']) as rows:
                for row in rows:
                    thisDate = row[0]
                    if thisDate > lastSync:
                        lastSync = thisDate

        for s in statTables:
            arcpy.management.Delete(s)

        if lastSync == time.dummyTimestamp():
            self.context[LAST_SYNC_TIME] =  None
        else:
            self.context[LAST_SYNC_TIME] = lastSync

        arcpy.env.workspace = originalWorkspace
        self.messenger.outdent()


    def lastPartOfTableName(table):
        return table.split(".")[-1]


    def filterRecords(self, surveyGDB):
        '''Filter the records to those that need to be updated'''
        #Note - This excludes new entries that are *after* the timestamp
        #       Depending on how active the survey is, there may have been new submissions
        #           after the start of the script
        #       We put in a max time to ensure consistency in operation from run to run and
        #           table to table
        
        self.messenger.info(f'Filtering records to new set since last synchronised...')
        self.messenger.indent()
        
        arcpy.env.workspace = surveyGDB
        
        nowText = time.createTimestampText(self.context[PROCESS_TIME])
        tableList = self.getSurveyTables(surveyGDB)
        dateField = arcpy.AddFieldDelimiters(surveyGDB, "CreationDate")
        excludeStatement = "CreationDate > date '{1}'".format(dateField, nowText)
        if LAST_SYNC_TIME in self.context.keys() and self.context[LAST_SYNC_TIME] != None:
            lastSyncText = time.createTimestampText(self.context[LAST_SYNC_TIME])
            excludeStatement = f"{excludeStatement} OR CreationDate <= date '{lastSyncText}'"

        self.messenger.info(f'Using filter view exclude statement [{excludeStatement}]')

        i = 0
        for table in tableList:
            i = i + 1
            thisName = f'filterView{str(i)}'
            dsc = arcpy.Describe(table)
            if dsc.datatype == u'FeatureClass' or dsc.datatype == u'FeatureLayer':
                arcpy.management.MakeFeatureLayer(table, thisName, excludeStatement)
                arcpy.management.DeleteFeatures(thisName)
            else:
                arcpy.management.MakeTableView(table, thisName, excludeStatement)
                arcpy.management.DeleteRows(thisName)
            arcpy.management.Delete(thisName)
        
        self.messenger.outdent()
        self.messenger.info(f'Done filtering records to new set since last synchronised...')



    def addTimeStamp(self, surveyGDB):
        # Disables editor tracking, adds and populates the timestamp field

        self.messenger.info(f'Adding syncronization time to tables...')
        self.messenger.indent()

        arcpy.env.workspace = surveyGDB
        tableList = self.getSurveyTables(surveyGDB)
        self.messenger.debug(f'Survey table list: {tableList}')

        self.addSynchronisationFields(surveyGDB, tableList)
        self.setTimestampOnTables(surveyGDB, tableList)
        
        self.messenger.outdent()
        self.messenger.info(f'Done adding syncronization time to tables...')


    def addSynchronisationFields(self, surveyGDB, tableList):
        self.messenger.info(f'Adding synchronisation fields on tables...')
        self.messenger.indent()

        for table in tableList:
            FQtable = os.path.join(surveyGDB, table)
            
            self.messenger.debug(f'Disabling Editor Tracking on table [{table}]')
            arcpy.management.DisableEditorTracking(FQtable)

            self.messenger.debug(f'Adding synchronisation field on table [{table}]')
            arcpy.management.AddField(FQtable, 'SYS_TRANSFER_DATE', 'DATE')

        self.messenger.outdent()
        self.messenger.info(f'Done adding synchronisation fields on tables')


    def setTimestampOnTables(self, surveyGDB, tableList):
        timestamp = self.context[PROCESS_TIME]

        self.messenger.info(f'Setting timestamp [{time.createTimestampText(timestamp)}] on tables...')
        self.messenger.indent()

        with arcpy.da.Editor(surveyGDB) as edit:
            for table in tableList:
                FQtable = os.path.join(surveyGDB, table)
                self.messenger.debug(f'Setting Timestamp on table [{table}]...')
                with arcpy.da.UpdateCursor(FQtable, ['SYS_TRANSFER_DATE']) as rows:
                    for row in rows:
                        rows.updateRow([timestamp])
        del(edit)

        self.messenger.outdent()
        self.messenger.info(f'Done setting timestamps on tables')
 

    def addKeyFields(self, workspace):
        '''To enable transfer of attachments with repeats, we need an additional GUID field to serve as a lookup'''
        arcpy.env.workspace = workspace
        dscW = arcpy.Describe(workspace)
        tableList = []
        relClasses = [c.name for c in dscW.children if c.datatype == u'RelationshipClass']
        for child in relClasses:
            dscRC = arcpy.Describe(child)
            if dscRC.isAttachmentRelationship:
                originTable = dscRC.originClassNames[0]
                originFieldNames = [f.name for f in arcpy.ListFields(originTable)]
                if 'rowid' not in originFieldNames:
                    arcpy.management.AddField(originTable, 'rowid', 'GUID')
                    with arcpy.da.Editor(workspace) as edit:
                        with arcpy.da.UpdateCursor(originTable, ['rowid']) as urows:
                            for urow in urows:
                                urow[0] = '{' + str(uuid.uuid4()) + '}'
                                urows.updateRow(urow)
                    del(edit)
