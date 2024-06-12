# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Name: support/survey_replicator.py
# Purpose: To replicate a survey out of AGOL into a temporary file geodatabase
# Author: Lindsay Bradford, Truii.com, 2024, based heaviy on syncSurvey
# Release History:
# ---------------------------------------------------------------------------
# V1: Initial release

from support.parameters import *
from support.survey_reprojector import SurveyReprojector
from support.survey_replicator import NullSurveyReplicator

import pytest
# from unittest.mock import patch

DUMMY_ENTRY = 'dummyentry'

class FakeReplicator(NullSurveyReplicator):
    def replicate(self):
        self.context[DUMMY_ENTRY] = DUMMY_ENTRY


@pytest.mark.usefixtures("useTestDataDirectory", "resetArcpy", "resetMessengerSingleton")    
class TestSurveyReplicator:

    def test_SurveyReprojector_context_available_across_ETL(self):
        # given
           
        parameters = {
            PORTAL: 'https://www.not.really.arcgis.com',
            USER_NAME: 'TheUser',
            PASSWORD: 'NopeNopeNopeNope',
            SERVICE_URL: 'https://yaddayaddayadda.com/rest-of-url',

            PREFIX: 'myprefix',
            TIMEZONE: 'Australia/Brisbane',
            SDE_CONNECTION: 'some_destination.gdb',
            REPROJECT_CODE: 'WSG84-to-GDA2020-standin',
        }
       
        # when

        fakeReplicator = FakeReplicator(parameters)
        reprojectorUnderTest = SurveyReprojector(parameters).usingSurveyReplicator(fakeReplicator)
        reprojectorUnderTest.reproject()
        
        # then
        
        assert DUMMY_ENTRY in reprojectorUnderTest.context.keys()
        assert reprojectorUnderTest.context[DUMMY_ENTRY] == DUMMY_ENTRY

        assert DUMMY_ENTRY in reprojectorUnderTest.replicator.context.keys()
        assert reprojectorUnderTest.replicator.context[DUMMY_ENTRY] == DUMMY_ENTRY

        assert DUMMY_ENTRY in reprojectorUnderTest.reprojector.context.keys()
        assert reprojectorUnderTest.reprojector.context[DUMMY_ENTRY] == DUMMY_ENTRY
        
        assert DUMMY_ENTRY in reprojectorUnderTest.appender.context.keys()
        assert reprojectorUnderTest.appender.context[DUMMY_ENTRY] == DUMMY_ENTRY
         
 



