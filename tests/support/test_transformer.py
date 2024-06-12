from support.parameters import *
import support.time as time


import pytest
from unittest.mock import patch

from support.transformer import FGDBReprojectionTransformer

@pytest.mark.usefixtures("useTestDataDirectory", "resetArcpy", "resetMessengerSingleton")    
class TestFGDReprojectionTransformer:
    
    def test_FGDBReprojectionTransformer_transform_no_existing_data(self):
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
        
        context = {
            PROCESS_TIME: time.getUTCTimestamp(parameters[TIMEZONE])    
        }
        
        fakeReplicatedGeodatabase = 'fakeReplicant.gdb'
        
        with patch('support.transformer.arcpy.ListFeatureClasses', result=[]),\
             patch('support.transformer.arcpy.ListTables', result=[]):

            transformerUnderTest = FGDBReprojectionTransformer(parameters).withContext(context)
            transformerUnderTest.transform(fakeReplicatedGeodatabase)

        assert True


    def test_FGDBReprojectionTransformer_transform_no_attachments(self):
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
        
        context = {
            PROCESS_TIME: time.getUTCTimestamp(parameters[TIMEZONE]),
        }
        
        fakeReplicatedGeodatabase = 'fakeReplicant.gdb'
        
        transformerUnderTest = FGDBReprojectionTransformer(parameters).withContext(context)
        transformerUnderTest.transform(fakeReplicatedGeodatabase)

        assert True