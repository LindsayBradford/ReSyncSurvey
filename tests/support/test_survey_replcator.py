# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Name: support/survey_replicator.py
# Purpose: To replicate a survey out of AGOL into a temporary file geodatabase
# Author: Lindsay Bradford, Truii.com, 2024, based heaviy on syncSurvey
# Release History:
# ---------------------------------------------------------------------------
# V1: Initial release

from io import BytesIO
from os import replace

import uuid

from support.parameters import *

import pytest
from unittest.mock import patch

import json
from urllib.request import HTTPSHandler
from urllib.parse import unquote
from pathlib import Path
from support.survey_replicator import AGOLSurveyReplicator

# https://developers.arcgis.com/rest/services-reference/enterprise/feature-service/

class FakeZipFile():
    def __init__(self):
        self.extracted = 0
        self.namelistReturned = 0
        pass
    
    def namelist(self):
        self.namelistReturned = self.namelistReturned + 1
        return ['someFakeFileGeodatabase.gdb/garbagePartOfPath']
    
    def extractall(self, outdir = None):
        self.extracted = self.extracted + 1
        pass


class FakeGoodCredentialsHttpsHandler(HTTPSHandler):

    def __init__(self):
        self.generateTokenCallCount = 0
        self.serviceInfoCallCount = 0
        self.replicateJobCallCount = 0
        self.jobPollCallCount = 0
        self.resultCallCount = 0
        
        HTTPSHandler.__init__(self)
        
    def forParameters(self, params):
        self.params = params
        
        self.tokenUUID = str(uuid.uuid4())
        self.jobUrl = f'{self.params[SERVICE_URL]}/createReplica/{uuid.uuid4()}'
        self.jobStatusUrl = self.jobUrl + f'?statusId={uuid.uuid4()}'
        self.resultFileUrl = f'{self.params[SERVICE_URL]}/replicafiles/{uuid.uuid4()}.json'

        return self

    def withServiceInfo(self, serviceInfo):
        self.serviceInfo = serviceInfo
        return self

    def open(self,url, prameters = None):
        if url.startswith(f'{self.params[PORTAL]}/sharing/rest/generateToken?'):
            tokenJson = '{ "token": "' +self.tokenUUID + '" }' 
            responseUtf8 = tokenJson.encode('utf-8')
            self.generateTokenCallCount = self.generateTokenCallCount + 1
        elif url == f"{self.params[SERVICE_URL]}?f=json&token={self.tokenUUID}":
            self.serviceInfoCallCount = self.serviceInfoCallCount + 1
            responseUtf8 = self.serviceInfo.encode('utf-8')
        elif url == f'{self.params[SERVICE_URL]}/createReplica/?f=json&token={self.tokenUUID}':
            jobJson = '{ "statusUrl": "' + self.jobUrl + '" }'
            self.replicateJobCallCount = self.replicateJobCallCount + 1
            responseUtf8 = jobJson.encode('utf-8')
        elif url ==  f'{self.jobUrl}?f=json&token={self.tokenUUID}':
            jobBodyJson = '{"resultUrl":"' + self.resultFileUrl + '","status":"Completed"}'
            self.jobPollCallCount = self.jobPollCallCount + 1
            responseUtf8 = jobBodyJson.encode('utf-8')
        elif url ==  f'{self.resultFileUrl}?token={self.tokenUUID}':
            self.resultCallCount = self.resultCallCount + 1 
            responseUtf8 = Path('fakeFileGeodatabase.zip').read_bytes()
        else:
            responseUtf8 = '{}'.encode('utf-8')
        return BytesIO(responseUtf8)


class FakeBadCredentialsHttpsHandler(HTTPSHandler):

    def __init__(self):
        self.generateTokenCallCount = 0
        HTTPSHandler.__init__(self)
        
    def forParameters(self, params):
        self.params = params
        
        return self

    def withServiceInfo(self, serviceInfo):
        self.serviceInfo = serviceInfo
        return self

    def open(self,url, prameters = None):
        if url.startswith(f'{self.params[PORTAL]}/sharing/rest/generateToken?'):
            responseText =  '{"error":{"code":400,"message":"Unable to generate token.","details":["Invalid username or password."]}}'
            responseUtf8 = responseText.encode('utf-8')  
            self.generateTokenCallCount = self.generateTokenCallCount + 1
        else:
            responseUtf8 = '{}'.encode('utf-8')
        return BytesIO(responseUtf8)


@pytest.mark.usefixtures("useTestDataDirectory", "resetArcpy", "resetMessengerSingleton")    
class TestAGOLSurveyReplicator:

    def test_AGOLSurveyReplicator_replicate(self):
        # given
           
        parameters = {
            PORTAL: 'https://www.not.really.arcgis.com',
            USER_NAME: 'TheUser',
            PASSWORD: 'NopeNopeNopeNope',
            SERVICE_URL: 'https://yaddayaddayadda.com/rest-of-url',

            PREFIX: 'myprefix',
            TIMEZONE: 'Australia/Brisbane',
            SDE_CONNECTION: 'blob.gdb',
            REPROJECT_CODE: 'WSG84-to-GDA2020-standin',
        }

        
        validServiceInfo = Path('syncEnabledFeatureServiceInfo.json').read_text()
        fakeHandler = FakeGoodCredentialsHttpsHandler().forParameters(parameters).withServiceInfo(validServiceInfo)

        fakeZipFile = FakeZipFile()

        #TODO:  Can I shrink this to just referencing fakeZipFile once?
        with patch('support.survey_replicator.urllib.request.urlopen', fakeHandler.open),\
             patch('support.survey_replicator.zipfile.ZipFile.namelist', fakeZipFile.namelist),\
             patch('support.survey_replicator.zipfile.ZipFile.extractall', fakeZipFile.extractall):
            
            replicatorUnderTest = AGOLSurveyReplicator(parameters)

            # when

            replicatorUnderTest.replicate()

            # then

            assert fakeHandler.generateTokenCallCount == 1
            assert fakeHandler.serviceInfoCallCount == 1
            assert fakeHandler.replicateJobCallCount == 1
            assert fakeHandler.jobPollCallCount == 1
            assert fakeHandler.resultCallCount == 1                

            assert fakeZipFile.namelistReturned == 1
            assert fakeZipFile.extracted == 1

            
    def test_AGOLSurveyReplicator_replicate_bad_credentials(self):
        # given
           
        parameters = {
            PORTAL: 'https://www.not.really.arcgis.com',
            USER_NAME: 'BadUser',
            PASSWORD: 'BadPassword',
            SERVICE_URL: 'https://yaddayaddayadda.com/rest-of-url',

            PREFIX: 'myprefix',
            TIMEZONE: 'Australia/Brisbane',
            SDE_CONNECTION: 'blob.gdb',
            REPROJECT_CODE: 'WSG84-to-GDA2020-standin',
        }

        validServiceInfo = Path('syncEnabledFeatureServiceInfo.json').read_text()
        fakeHandler = FakeBadCredentialsHttpsHandler().forParameters(parameters).withServiceInfo(validServiceInfo)

        with patch('support.survey_replicator.urllib.request.urlopen', fakeHandler.open):
            with pytest.raises(Exception) as e_info:
                replicatorUnderTest = AGOLSurveyReplicator(parameters)

                # when

                replicatorUnderTest.replicate()

            # then

            assert fakeHandler.generateTokenCallCount == 1
            assert str(e_info.value).startswith('No login token returned from ')
