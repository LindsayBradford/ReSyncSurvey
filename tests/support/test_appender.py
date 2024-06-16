# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Name: tests/support/test_appender.py
# Purpose: Testing harness for support/appender.py
# Author: Lindsay Bradford, Truii.com, 2024, based heaviy on syncSurvey
# Release History:
# ---------------------------------------------------------------------------
# V1: Initial release

from support.parameters import *
import support.time as time

import pytest
from unittest.mock import patch

from support.appender import SDEAppender


class FakeArcpy():
    def __init__(self):
        self.spatialReferenceInputs = []

    def SpatialReference(self, crsCode):
        self.spatialReferenceInputs.append(crsCode)


@pytest.mark.usefixtures("useTestDataDirectory", "resetArcpy", "resetMessengerSingleton")    
class TestSDEAppender:

    def test_SDEAppender_appendFrom_no_attachments(self):
        # given
           
        parameters = {
            PORTAL: 'https://www.not.really.arcgis.com',
            USER_NAME: 'TheUser',
            PASSWORD: 'NopeNopeNopeNope',
            SERVICE_URL: 'https://yaddayaddayadda.com/rest-of-url',

            PREFIX: 'myprefix',
            TIMEZONE: 'Australia/Brisbane',
            SDE_CONNECTION: 'c:/tmp/some_destination.gdb',
            REPROJECT_CODE: 'GDA2020 MGA Zone 56',
        }
        
        context = {
            PROCESS_TIME: time.getUTCTimestamp(parameters[TIMEZONE]),
            EXISTING_TABLES: []
        }
        
        fakeReplicatedGeodatabase = 'fakeReplicant.gdb'
        fakeArcpy = FakeArcpy()
        
        transformerUnderTest = SDEAppender(parameters).withContext(context)
        
        with patch('support.appender.arcpy.SpatialReference', fakeArcpy.SpatialReference):
            transformerUnderTest.appendFrom(fakeReplicatedGeodatabase)

        assert len(fakeArcpy.spatialReferenceInputs) == 2
        assert fakeArcpy.spatialReferenceInputs[0] == parameters[REPROJECT_CODE] # General env projection/transformation
        assert fakeArcpy.spatialReferenceInputs[1] == parameters[REPROJECT_CODE] # Explicit feature class creation
