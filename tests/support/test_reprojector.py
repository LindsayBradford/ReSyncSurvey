# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Name: tests/support/test_reprojector.py
# Purpose: Testing harness for support/reprojector.py
# Author: Lindsay Bradford, Truii.com, 2024, based heaviy on syncSurvey
# Release History:
# ---------------------------------------------------------------------------
# V1: Initial release

from support.parameters import *
from support.reprojector import SurveyReprojector
from support.extractor import NullSurveyReplicator
from support.loader import NullLoader
import support.time as time

import pytest
from unittest.mock import patch

import arcpy

DUMMY_ENTRY = 'dummyentry'

class FakeArcpyProxy():
    def __init__(self):
        self.cleanupAppendsCalled = 0
        self.cleanupCreatedTablesCalled = 0

    def cleanupAppends(self, sdeConnection, processTime, tables):
        self.cleanupAppendsCalled += 1

    def cleanupCreatedTables(self, sdeConnection, prefix):
        self.cleanupCreatedTablesCalled += 1
        

class FakeReplicator(NullSurveyReplicator):
    def extract(self):
        self.context[DUMMY_ENTRY] = DUMMY_ENTRY
        return 'FakeReplicant.gdb'


class FakeAttributeErrorReplicator(NullSurveyReplicator):
    def extract(self):
        raise AttributeError("Here's a randon attribute error")

class FakeExecuteErrorReplicator(NullSurveyReplicator):
    def extract(self):
        raise arcpy.ExecuteError("Failed to execute. Parameters are not valid.")
    
def FakeArcpyGetParameterInfo():
    return ['param1value', 'param2value']

class FakeLoader(NullLoader):
    def loadFrom(self, surveyGDB):
         self.context[PROCESS_TIME] = time.dummyTimestamp()
         self.context[LAST_SYNC_TIME] = self.context[PROCESS_TIME]
        
         self.context[CLEANUP_OPERATIONS] = {}
         self.context[CLEANUP_OPERATIONS]['createTables'] = True
         self.context[CLEANUP_OPERATIONS]['append'] = ['appendTable1', 'appendTable2']

         raise arcpy.ExecuteError('some fake error')


@pytest.mark.usefixtures("useTestDataDirectory", "resetArcpy", "resetMessengerSingleton")    
class TestSurveyReprojecor:

    def test_SurveyReprojector_context_available_across_ETL(self):
        # given
           
        parameters = {
            PORTAL: 'https://www.not.really.arcgis.com',
            PORTAL_USER_NAME: 'TheUser',
            PORTAL_PASSWORD: 'NopeNopeNopeNope',
            SERVICE_URL: 'https://yaddayaddayadda.com/rest-of-url',

            PREFIX: 'myprefix',
            TIMEZONE: 'Australia/Brisbane',
            SDE_CONNECTION: 'some_destination.gdb',
            DESTINATION_CRS: 'WSG84-to-GDA2020-standin',
        }
       
        # when

        fakeReplicator = FakeReplicator(parameters)
        reprojectorUnderTest = SurveyReprojector(parameters).usingExtractor(fakeReplicator)
        reprojectorUnderTest.reproject()
        
        # then
        
        assert DUMMY_ENTRY in reprojectorUnderTest.context.keys()
        assert reprojectorUnderTest.context[DUMMY_ENTRY] == DUMMY_ENTRY

        assert DUMMY_ENTRY in reprojectorUnderTest.extractor.context.keys()
        assert reprojectorUnderTest.extractor.context[DUMMY_ENTRY] == DUMMY_ENTRY

        assert DUMMY_ENTRY in reprojectorUnderTest.transformer.context.keys()
        assert reprojectorUnderTest.transformer.context[DUMMY_ENTRY] == DUMMY_ENTRY
        
        assert DUMMY_ENTRY in reprojectorUnderTest.loader.context.keys()
        assert reprojectorUnderTest.loader.context[DUMMY_ENTRY] == DUMMY_ENTRY

        
    def test_SurveyReprojector_CmdLine_ExecuteError_handled(self):
        # given
           
        parameters = {
            PORTAL: 'https://www.not.really.arcgis.com',
            PORTAL_USER_NAME: 'TheUser',
            PORTAL_PASSWORD: 'NopeNopeNopeNope',
            SERVICE_URL: 'https://yaddayaddayadda.com/rest-of-url',

            PREFIX: 'myprefix',
            TIMEZONE: 'Australia/Brisbane',
            SDE_CONNECTION: 'some_destination.gdb',
            DESTINATION_CRS: 'WSG84-to-GDA2020-standin',
        }
       
        # when

        fakeExecuteErrrorReplicator = FakeExecuteErrorReplicator(parameters)
        reprojectorUnderTest = SurveyReprojector(parameters).usingExtractor(fakeExecuteErrrorReplicator)
        
        with pytest.raises(SystemExit) as sysExitInfo:
            reprojectorUnderTest.reproject()
            
        # then
        
        assert str(sysExitInfo.value).startswith('Failed to execute')


    def test_SurveyReprojector_CmdLine_AttributeError_handled(self):
        # given
           
        parameters = {
            PORTAL: 'https://www.not.really.arcgis.com',
            PORTAL_USER_NAME: 'TheUser',
            PORTAL_PASSWORD: 'NopeNopeNopeNope',
            SERVICE_URL: 'https://yaddayaddayadda.com/rest-of-url',

            PREFIX: 'myprefix',
            TIMEZONE: 'Australia/Brisbane',
            SDE_CONNECTION: 'some_destination.gdb',
            DESTINATION_CRS: 'WSG84-to-GDA2020-standin',
        }
       
        # when

        fakeAttributeErrrorReplicator = FakeAttributeErrorReplicator(parameters)
        reprojectorUnderTest = SurveyReprojector(parameters).usingExtractor(fakeAttributeErrrorReplicator)
        
        with pytest.raises(SystemExit) as sysExitInfo:
            reprojectorUnderTest.reproject()
            
        # then
        
        assert str(sysExitInfo.value).startswith("Here's a randon attribute error")


    def test_SurveyReprojector_ArcGISPro_ExecuteError_handled(self):
        # given
           
        parameters = {
            PORTAL: 'https://www.not.really.arcgis.com',
            PORTAL_USER_NAME: 'TheUser',
            PORTAL_PASSWORD: 'NopeNopeNopeNope',
            SERVICE_URL: 'https://yaddayaddayadda.com/rest-of-url',

            PREFIX: 'myprefix',
            TIMEZONE: 'Australia/Brisbane',
            SDE_CONNECTION: 'some_destination.gdb',
            DESTINATION_CRS: 'WSG84-to-GDA2020-standin',
        }
       
        # when

        fakeExecuteErrrorReplicator = FakeExecuteErrorReplicator(parameters)
        reprojectorUnderTest = SurveyReprojector(parameters).usingExtractor(fakeExecuteErrrorReplicator)
        
        with patch('support.loader.arcpy.GetParameterInfo', FakeArcpyGetParameterInfo),\
            pytest.raises(arcpy.ExecuteError) as exInfo:

            reprojectorUnderTest.reproject()
            
        # then
        
        assert str(exInfo.value).startswith("('Aborting script")
        
    def test_SurveyReprojector_context_triggers_deep_cleanup(self):
        # given
           
        parameters = {
            PORTAL: 'https://www.not.really.arcgis.com',
            PORTAL_USER_NAME: 'TheUser',
            PORTAL_PASSWORD: 'NopeNopeNopeNope',
            SERVICE_URL: 'https://yaddayaddayadda.com/rest-of-url',

            PREFIX: 'myprefix',
            TIMEZONE: 'Australia/Brisbane',
            SDE_CONNECTION: 'some_destination.gdb',
            DESTINATION_CRS: 'WSG84-to-GDA2020-standin',
        }
        
        fakeProxy = FakeArcpyProxy()

        fakeLoader = FakeLoader(parameters)
        reprojectorUnderTest = SurveyReprojector(parameters).usingLoader(fakeLoader)
       
        # when
        with patch('support.reprojector.arcpy_proxy.cleanupAppends', fakeProxy.cleanupAppends), \
            patch('support.reprojector.arcpy_proxy.cleanupCreatedTables', fakeProxy.cleanupCreatedTables), \
            pytest.raises(SystemExit) as sysExitInfo:

            reprojectorUnderTest.reproject()

        # then
        
        assert str(sysExitInfo.value).startswith("some fake error")

        fakeProxy.cleanupCreatedTablesCalled = 1
        fakeProxy.cleanupAppendsCalled = 1
        