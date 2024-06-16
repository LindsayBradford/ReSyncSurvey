# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Name: tests/support/test_transformer.py
# Purpose: Testing harness for support/transformer.py
# Author: Lindsay Bradford, Truii.com, 2024, based heaviy on syncSurvey
# Release History:
# ---------------------------------------------------------------------------
# V1: Initial release

from support.parameters import *
import support.time as time

from enum import Enum
import pytest
from unittest.mock import patch

from support.transformer import FGDBReprojectionTransformer

ResponseType = Enum('ResponseType', \
                    ['NO_TABLES', 'NO_DESTINATION_TABLES', \
                     'NO_REPLICA_TABLES', 'MATCHING_REPLICA_DESTINATION_TABLES'])

class FakeCursor(arcpy.da.Cursor):
    def __init__(self):
        self.a = 1
        self.timestamp = None

    def __next__(self):
        self.a += 1
        if self.a < 4:
            return [self.timestamp]
        else:
            raise StopIteration


class FakeArcpyBridge():
    def __init__(self, params):
        self.params = params

        self.responseType = ResponseType.NO_TABLES
        self.ListTablesCalled = 0
        self.tables = []

        self.ListFeatureClassesCalled = 0
        self.featureClasses = []

        self.GetCountCalled = 0

    
    def usingReplicaGeodatabase(self, replicaGeodatabase):
        self.params['replica'] = replicaGeodatabase
        return self

    def withNoTables(self):
        self.responseType = ResponseType.NO_TABLES
        return self
    
    def withNoDestinationTables(self):
        self.responseType = ResponseType.NO_DESTINATION_TABLES
        return self
    
    def withNoReplicaTables(self):
        self.responseType = ResponseType.NO_REPLICA_TABLES
        return self

    def withMatchingTables(self):
        self.responseType = ResponseType.MATCHING_REPLICA_DESTINATION_TABLES
        return self


    def ListTables(self, wildcard):
        self.ListTablesCalled += 1
        if arcpy.env.workspace == self.params['replica']:
            if self.responseType == ResponseType.MATCHING_REPLICA_DESTINATION_TABLES or\
                self.responseType == ResponseType.NO_DESTINATION_TABLES:
                return ['table1', 'table2']
        if arcpy.env.workspace == self.params[SDE_CONNECTION]:
            if self.responseType == ResponseType.MATCHING_REPLICA_DESTINATION_TABLES:
                return [self.params[PREFIX] + '_table1', self.params[PREFIX] + '_table2']
        return []

    def ListFeatureClasses(self, wildcard):
        self.ListFeatureClassesCalled += 1

        if arcpy.env.workspace == self.params['replica']:
            if self.responseType == ResponseType.MATCHING_REPLICA_DESTINATION_TABLES or\
                self.responseType == ResponseType.NO_DESTINATION_TABLES:
                return ['featureClass1', 'featureClass2']
        if arcpy.env.workspace == self.params[SDE_CONNECTION]:
            if self.responseType == ResponseType.MATCHING_REPLICA_DESTINATION_TABLES:
                return [self.params[PREFIX] + '_featureClass1', self.params[PREFIX] + '_featureClass2']
        return []
    
    def GetCount(self, tableName):
        self.GetCountCalled += 1
        if arcpy.env.workspace == self.params['replica']:
            if self.responseType == ResponseType.MATCHING_REPLICA_DESTINATION_TABLES or\
                self.responseType == ResponseType.NO_DESTINATION_TABLES:
                return [2]
        if arcpy.env.workspace == self.params[SDE_CONNECTION]:
            if self.responseType == ResponseType.MATCHING_REPLICA_DESTINATION_TABLES:
                return [2]
        return [0]
    
    def SearchCursor(self, tableName, columns):
        cursor = FakeCursor()
        cursor.timestamp = self.params['destinationTimestamp']
        return cursor

    
    def Statistics_analysis(self, tableName, workspace, analysisType):
        if arcpy.env.workspace == self.params[SDE_CONNECTION]:
            if self.responseType == ResponseType.MATCHING_REPLICA_DESTINATION_TABLES:
                return [f'in_memory\stat_{self.params[PREFIX] + "_featureClass1"}', f'in_memory\stat_{self.params[PREFIX] + "_featureClass2"}']
        return None


@pytest.mark.usefixtures("useTestDataDirectory", "resetArcpy", "resetMessengerSingleton") 
class TestFGDReprojectionTransformer:
    
    def test_FGDBReprojectionTransformer_transform_no_existing_data(self):
        # given
           
        parameters = {
            PORTAL: 'https://www.not.really.arcgis.com',
            PORTAL_USER_NAME: 'TheUser',
            PORTAL_PASSWORD: 'NopeNopeNopeNope',
            SERVICE_URL: 'https://yaddayaddayadda.com/rest-of-url',

            PREFIX: 'myprefix',
            TIMEZONE: 'Australia/Brisbane',
            SDE_CONNECTION: 'some_destination.gdb',
            DESTINATION_CRS: 'GDA2020 MGA Zone 56',
        }
        
        context = {
            PROCESS_TIME: time.getUTCTimestamp(parameters[TIMEZONE])    
        }
        
        fakeReplicatedGeodatabase = 'fakeReplicant.gdb'

        fakeBridge = FakeArcpyBridge(parameters).\
                        usingReplicaGeodatabase(fakeReplicatedGeodatabase).\
                        withNoTables()
        
        with patch('support.transformer.arcpy.ListFeatureClasses', fakeBridge.ListFeatureClasses),\
             patch('support.transformer.arcpy.ListTables', fakeBridge.ListTables):

            transformerUnderTest = FGDBReprojectionTransformer(parameters).withContext(context)
            transformerUnderTest.transform(fakeReplicatedGeodatabase)
            
        assert fakeBridge.ListTablesCalled == 3
        assert fakeBridge.ListFeatureClassesCalled == 3


    def test_FGDBReprojectionTransformer_transform_no_destination_data(self):
        # given
           
        parameters = {
            PORTAL: 'https://www.not.really.arcgis.com',
            PORTAL_USER_NAME: 'TheUser',
            PORTAL_PASSWORD: 'NopeNopeNopeNope',
            SERVICE_URL: 'https://yaddayaddayadda.com/rest-of-url',

            PREFIX: 'myprefix',
            TIMEZONE: 'Australia/Brisbane',
            SDE_CONNECTION: 'some_destination.gdb',
            DESTINATION_CRS: 'GDA2020 MGA Zone 56',
        }
        
        context = {
            PROCESS_TIME: time.getUTCTimestamp(parameters[TIMEZONE])    
        }
        
        fakeReplicatedGeodatabase = 'fakeReplicant.gdb'

        fakeBridge = FakeArcpyBridge(parameters).\
                        usingReplicaGeodatabase(fakeReplicatedGeodatabase).\
                        withNoDestinationTables()
        
        with patch('support.transformer.arcpy.ListFeatureClasses', fakeBridge.ListFeatureClasses),\
             patch('support.transformer.arcpy.ListTables', fakeBridge.ListTables),\
             patch('support.transformer.arcpy.management.GetCount', fakeBridge.GetCount),\
             patch('support.transformer.arcpy.da.SearchCursor', fakeBridge.SearchCursor):

            transformerUnderTest = FGDBReprojectionTransformer(parameters).withContext(context)
            transformerUnderTest.transform(fakeReplicatedGeodatabase)
            
        assert fakeBridge.ListTablesCalled == 3
        assert fakeBridge.ListFeatureClassesCalled == 3


    def test_FGDBReprojectionTransformer_transform_matching_tables(self):
        # given
           
        parameters = {
            PORTAL: 'https://www.not.really.arcgis.com',
            PORTAL_USER_NAME: 'TheUser',
            PORTAL_PASSWORD: 'NopeNopeNopeNope',
            SERVICE_URL: 'https://yaddayaddayadda.com/rest-of-url',

            PREFIX: 'myprefix',
            TIMEZONE: 'Australia/Brisbane',
            SDE_CONNECTION: 'some_destination.gdb',
            DESTINATION_CRS: 'GDA2020 MGA Zone 56',
            'destinationTimestamp': time.dummyTimestamp()
        }
        
        context = {
            PROCESS_TIME: time.getUTCTimestamp(parameters[TIMEZONE])    
        }
        
        fakeReplicatedGeodatabase = 'fakeReplicant.gdb'

        fakeBridge = FakeArcpyBridge(parameters).\
                        usingReplicaGeodatabase(fakeReplicatedGeodatabase).\
                        withMatchingTables()
        
        with patch('support.transformer.arcpy.ListFeatureClasses', fakeBridge.ListFeatureClasses),\
             patch('support.transformer.arcpy.ListTables', fakeBridge.ListTables),\
             patch('support.transformer.arcpy.management.GetCount', fakeBridge.GetCount),\
             patch('support.transformer.arcpy.da.SearchCursor', fakeBridge.SearchCursor):

            transformerUnderTest = FGDBReprojectionTransformer(parameters).withContext(context)
            transformerUnderTest.transform(fakeReplicatedGeodatabase)
            
        assert fakeBridge.ListTablesCalled == 3
        assert fakeBridge.ListFeatureClassesCalled == 3
