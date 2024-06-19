# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Name: tests/support/test_loader.py
# Purpose: Testing harness for support/loader.py
# Author: Lindsay Bradford, Truii.com, 2024, based heaviy on syncSurvey
# Release History:
# ---------------------------------------------------------------------------
# V1: Initial release

from support.parameters import *
import support.time as time

import pytest
from unittest.mock import patch

from support.loader import ReprojectingSDEAppender


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
            PORTAL_USER_NAME: 'TheUser',
            PORTAL_PASSWORD: 'NopeNopeNopeNope',
            SERVICE_URL: 'https://yaddayaddayadda.com/rest-of-url',

            PREFIX: 'myprefix',
            TIMEZONE: 'Australia/Brisbane',
            SDE_CONNECTION: 'c:/tmp/some_destination.gdb',
            DESTINATION_CRS: 'GDA2020_MGA_Zone_56',
            DESTINATION_GEOGRAPHIC_TRANSFORMATIONS: "WGS_1984_2_To_GDA2020"
        }
        
        context = {
            PROCESS_TIME: time.getUTCTimestamp(parameters[TIMEZONE]),
            EXISTING_TABLES: []
        }
        
        fakeReplicatedGeodatabase = 'fakeReplicant.gdb'
        fakeArcpy = FakeArcpy()
        
        transformerUnderTest = ReprojectingSDEAppender(parameters).withContext(context)
        
        with patch('support.loader.arcpy.SpatialReference', fakeArcpy.SpatialReference):
            transformerUnderTest.loadFrom(fakeReplicatedGeodatabase)

        assert len(fakeArcpy.spatialReferenceInputs) == 2
        assert fakeArcpy.spatialReferenceInputs[0] == parameters[DESTINATION_CRS] # General env projection/transformation
        assert fakeArcpy.spatialReferenceInputs[1] == parameters[DESTINATION_CRS] # Explicit feature class creation
        
        assert arcpy.env.geographicTransformations == parameters[DESTINATION_GEOGRAPHIC_TRANSFORMATIONS] # General env projection/transformation
