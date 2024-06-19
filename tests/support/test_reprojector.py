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

import pytest
# from unittest.mock import patch

DUMMY_ENTRY = 'dummyentry'

class FakeReplicator(NullSurveyReplicator):
    def extract(self):
        self.context[DUMMY_ENTRY] = DUMMY_ENTRY


@pytest.mark.usefixtures("useTestDataDirectory", "resetArcpy", "resetMessengerSingleton")    
class TestSurveyReplicator:

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