# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Name: support/reprojector.py
# Purpose: To reproject an AGOL surveyinto a target geodatabase
# Author: Lindsay Bradford, Truii.com, 2024, based heaviy on syncSurvey
# Release History:
# ---------------------------------------------------------------------------
# V1: Initial release

from support.parameters import *
import support.arcpy_proxy as arcpy_proxy
import support.extractor as extractor
import support.transformer as transformer
import support.loader as loader
import support.time as time
from support.messenger import Messenger

import sys
import traceback

class SurveyReprojector:
    def __init__(self, parametersSupplied):
        self.parameters = parametersSupplied
        self.messenger = Messenger()
        self.abortingException = None

        self.initialiseContext()
        
        self.extractor = \
            extractor.NullSurveyReplicator(parametersSupplied).withContext(self.context)
        
        self.transformer = \
            transformer.NullTransformer(parametersSupplied).withContext(self.context)

        self.loader = \
            loader.NullLoader(parametersSupplied).withContext(self.context)


    def initialiseContext(self):
        self.context = {}
        self.context[PROCESS_TIME] = time.getUTCTimestamp(self.parameters[TIMEZONE])
        self.context[SECTION] = 'Unspecified'
        self.context[LAST_SYNC_TIME] = None
        self.context[CLEANUP_OPERATIONS] = {}
        self.messenger.debug(f'Context: [{self.context}]')


    def usingExtractor(self, extractor):
        self.extractor = extractor.withContext(self.context)
        return self


    def usingTransformer(self, transformer):
        self.transformer = transformer.withContext(self.context)
        return self


    def usingLoader(self, loader):
        self.loader = loader.withContext(self.context)
        return self

    def reproject(self):
        try:
            self.tryReprojection()
            self.noDestinationCleanupRequired()
        except Exception as ex:
            self.handleException(ex)
        finally:
            self.cleanup()
            self.abortIfRequired()
            
    def noDestinationCleanupRequired(self):
        self.context[CLEANUP_OPERATIONS].pop('append', None)
        self.context[CLEANUP_OPERATIONS].pop('createTables', None)

    def abortIfRequired(self):
        if self.abortingException == None:
            return

        message = f'Aborting script due to unrecoverable error [{self.abortingException}]'
        if arcpy_proxy.runningWithinToolbox():
            arcpy_proxy.raiseExecuteError(message, self.abortingException)
        else:
            self.messenger.error(message)
            sys.exit(self.abortingException)


    def tryReprojection(self):
        self.context[SECTION] = 'Extraction'
        surveyGDB = self.extractor.extract()

        self.context[SECTION] = 'Transformation'
        self.transformer.transform(surveyGDB)

        self.context[SECTION] = 'Loading'
        self.loader.loadFrom(surveyGDB)

        arcpy_proxy.Delete(surveyGDB)    
        

    def handleException(self, ex):
        exceptionType = type(ex).__name__
        self.messenger.error(f'Handling exception of type [{exceptionType}] in section [{self.context[SECTION]}]')

        self.messenger.indent()
        self.messenger.error(f'Exception: [{ex}]')
        self.messenger.error(f'Arguments: [{ex.args}]')

        if arcpy_proxy.isExecuteError(ex): 
            warnings = arcpy_proxy.GetMessages(1)
            splitWarnings = warnings.split('\n')
            if len(splitWarnings) > 0:
                self.messenger.error('arcpy warning messages:')
                self.messenger.indent()
                for warning in splitWarnings:
                    self.messenger.error(warning)
                self.messenger.outdent()
            
            errors = arcpy_proxy.GetMessages(2)  
            splitErrors = errors.split('\n')
            if len(splitErrors) > 0:
                self.messenger.error('arcpy error messages:')
                self.messenger.indent()
                for error in splitErrors:
                    self.messenger.error(error)
                self.messenger.outdent()

        self.messenger.error(f'Traceback: [{traceback.format_exc()}]')

        self.messenger.outdent()
        self.abortingException = ex


    def cleanup(self):
        self.messenger.info(f'Cleaning up...')
        self.messenger.indent()

        operations = self.context[CLEANUP_OPERATIONS].keys()
        if 'append' in operations:
            self.messenger.info(f'Cleaning up appended rows...')
            self.cleanupAppends(self.context[CLEANUP_OPERATIONS]['append'])
        if 'createTables' in operations:
            self.messenger.info(f'Cleaning up created tables...')
            self.cleanupCreatedTables()
        

        self.messenger.outdent()
        self.messenger.info(f'Done cleaning up')
        
        

    def cleanupAppends(self, tables):
        arcpy_proxy.cleanupAppends(self.parameters[SDE_CONNECTION], self.context[PROCESS_TIME], tables)


    def cleanupCreatedTables(self):
        arcpy_proxy.cleanupCreatedTables(self.parameters[SDE_CONNECTION], self.parameters[PREFIX])




