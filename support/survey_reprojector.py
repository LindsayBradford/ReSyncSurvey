# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Name: support/survey_reprojector.py
# Purpose: To reproject an AGOL survey, then save to target geodatabase
# Author: Lindsay Bradford, Truii.com, 2024, based heaviy on syncSurvey
# Release History:
# ---------------------------------------------------------------------------
# V1: Initial release

from support.parameters import *
import support.time as time
import support.survey_replicator as replicator
import support.transformer as transformer
import support.appender as appender
from support.messenger import Messenger

import arcpy

class SurveyReprojector:
    def __init__(self, parametersSupplied):
        self.parameters = parametersSupplied
        self.messenger = Messenger()

        self.initialiseContext()
        
        self.replicator = \
            replicator.NullSurveyReplicator(parametersSupplied).withContext(self.context)
        
        self.reprojector = \
            transformer.NullTransformer(parametersSupplied).withContext(self.context)

        self.appender = \
            appender.NullAppender(parametersSupplied).withContext(self.context)


    def initialiseContext(self):
        self.context = {}
        self.context[PROCESS_TIME] = time.getUTCTimestamp(self.parameters[TIMEZONE])
        self.context[SECTION] = 'Unspecified'
        self.context[LAST_SYNC_TIME] = None
        self.context[CLEANUP_OPERATIONS] = {}
        self.messenger.debug(f'Context: [{self.context}]')

    def usingSurveyReplicator(self, replicator):
        self.replicator = replicator.withContext(self.context)
        return self


    def usingReprojector(self, transformer):
        self.reprojector = transformer.withContext(self.context)
        return self


    def usingAppender(self, appender):
        self.appender = appender.withContext(self.context)
        return self


    def reproject(self):
        try:
            self.tryReprojection()
        except Exception as ex:
            self.handleException(ex)
        finally:
            self.cleanup()


    def tryReprojection(self):
        self.context[SECTION] = 'Extraction'
        surveyGDB = self.replicator.replicate()

        self.context[SECTION] = 'Transformation'
        self.reprojector.transform(surveyGDB)

        self.context[SECTION] = 'Loading'
        self.appender.appendFrom(surveyGDB)


    def handleException(self, ex):
        arcpy.AddMessage('======================')
        arcpy.AddMessage(f'FAIL: {self.context[SECTION]}')
        arcpy.AddMessage('exception:')
        arcpy.AddMessage(ex)
        arcpy.AddMessage(ex.args)
        arcpy.AddMessage(ex.exc_info()[0])
        arcpy.AddMessage(ex.exc_info()[2].tb_lineno)
        arcpy.AddMessage('----------------------')
        arcpy.AddMessage('arcpy messages:')
        arcpy.AddMessage(arcpy.GetMessages(1))
        arcpy.AddMessage(arcpy.GetMessages(2))
        arcpy.AddMessage('======================')


    def cleanup(self):
        # TODO: delegate cleanup to the ETL objects
        operations = self.context[CLEANUP_OPERATIONS].keys()
        if 'append' in operations:
            self.cleanupAppends(operations['append'])
        if 'createTables' in operations:
            self.cleanupCreatedTables()


    def cleanupAppends(self, tables):
        arcpy.env.workspace = self.parameters[SDE_CONNECTION]
        timestamp = time.createTimestampText(self.processTime)

        i = 0
        for table in tables:
            i = i + 1
            thisName = f'layerOrView{str(i)}'
            whereStatment = f"sys_transfer_date = timestamp'{timestamp}'"
            dsc = arcpy.Describe(table)
            if dsc.datatype == u'FeatureClass':
                arcpy.MakeFeatureLayer_management(table, thisName, whereStatment)
                arcpy.DeleteFeatures_management(thisName)
            else:
                arcpy.MakeTableView_management(table, thisName, whereStatment)
                arcpy.DeleteRows_management(thisName)
            # arcpy.Delete_management(view) -- What was this meant to do in syncSurvey originally?


    def cleanupCreatedTables(self):
        for table in self.getSurveyTables():
            arcpy.Delete_management(table)


    def getSurveyTables(self):
        originalWorkspace = arcpy.env.workspace
        
        arcpy.env.workspace = self.parameters[SDE_CONNECTION]
        prefix = self.parameters[PREFIX]        

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


