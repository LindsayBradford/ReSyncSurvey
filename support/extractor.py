# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Name: support/extractor.py
# Purpose: To extract a survey out of AGOL into a temp FGDB via replication
# Author: Lindsay Bradford, Truii.com, 2024, based heaviy on syncSurvey
# Release History:
# ---------------------------------------------------------------------------
# V1: Initial release


from support.parameters import *
from support.messenger import Messenger
import support.time as time

import os
import urllib, urllib.parse, urllib.request
import getpass
import json
import tempfile
import uuid
import zipfile

import arcpy

# Context keys

TOKEN = 'Token'
SERVICE_INFO = 'ServiceInfo'
SECTION = 'ProcessSection'

TOKEN_EXPIRY_MINUTES = 60
POLL_WAIT_SECONDS = 10

from abc import ABC, abstractmethod


class Extractor(ABC):
    @abstractmethod
    def withContext(self, context):
        pass

    @abstractmethod
    def extract(self):
        return None


class NullSurveyReplicator(Extractor):
    def __init__(self, parametersSupplied):
        self.context = {}
        self.parameters = parametersSupplied

    def withContext(self, context):
        self.context = context
        return self
    
    def extract(self):
        return "<Nothing Replicated>"
    

class AGOLSurveyReplicator(Extractor):
    def __init__(self, parametersSupplied):
        self.context = {}
        self.messenger = Messenger()
        self.parameters = parametersSupplied


    def withContext(self, context):
        self.context = context
        return self


    def extract(self):        
        self.messenger.info(f'Replicating survey at [{self.parameters[SERVICE_URL]}]')
        self.messenger.indent()

        self.logIntoSurvey()
        replicatedSurveyPath = self.downloadSurvey() 

        self.messenger.outdent()
        self.messenger.info(f'Done replicating survey at [{self.parameters[SERVICE_URL]}]')

        return replicatedSurveyPath
 

    def logIntoSurvey(self):
        self.retrieveLoginToken()
        self.checkServiceHasSyncEnabled()


    def checkServiceHasSyncEnabled(self):
        self.messenger.info(f'Checking service has Sync capability...')
        self.messenger.indent()

        self.deriveServiceDefinition()
        if 'Sync' not in self.context[SERVICE_INFO]['capabilities']:
            errorMsg = f'Sync Capabilities not enabled for survey [{self.parameters[SERVICE_URL]}]'
            self.messenger.error(errorMsg)
            raise Exception(errorMsg)

        self.messenger.info(f'Service confirmed as having Sync capability.')
        self.messenger.outdent()
        

    def retrieveLoginToken(self):
        self.messenger.info(f'Retrieving login token for [{self.parameters[SERVICE_URL]}]')
        self.messenger.indent()
        
        tokenTest = arcpy.GetSigninToken()
        token = None
        if tokenTest == None:
            token = self.getPortalToken()
        else:
            token = tokenTest['token']
            
        self.context[TOKEN] = token
        self.messenger.info(f'Login token [{self.context[TOKEN]}] retrieved')
        
        self.messenger.outdent()


    def getPortalToken(self):
        '''Gets a token from ArcGIS Online/Portal with the given username/password'''
        params = self.parameters
        
        tokenURL = f'{params[PORTAL]}/sharing/rest/generateToken?'
        
        self.messenger.info(f'Requesting login token via [{tokenURL}]')
        
        requestParams = self.generateTokenRequestParams()
        response = urllib.request.urlopen(tokenURL, requestParams).read()
        parsedResponse = json.loads(response)
        if 'token' in parsedResponse.keys():
            return parsedResponse['token']
        
        errorMessage = f'No login token returned from [{tokenURL}] for the credentials supplied'
        self.messenger.debug(f'Response returned [{response}]')
        self.messenger.error(errorMessage)
        raise Exception(errorMessage)

    def deriveServiceDefinition(self):
        requestUrl = f"{self.parameters[SERVICE_URL]}?f=json&token={self.context[TOKEN]}"
        self.messenger.info(f'Requesting service definition via [{requestUrl}]')
        
        response = urllib.request.urlopen(requestUrl).read()
        self.messenger.debug(f'Service definition response [{response}]')

        self.context[SERVICE_INFO] = json.loads(response)


    def generateTokenRequestParams(self):
        params = self.parameters

        if params[PORTAL_PASSWORD] == None:
            params[PORTAL_PASSWORD]= getpass.getpass()

        parameters = urllib.parse.urlencode({
            'username': params[PORTAL_USER_NAME],
            'password': params[PORTAL_PASSWORD],
            'client': 'referer',
            'referer': params[PORTAL_USER_NAME],
            'expiration': TOKEN_EXPIRY_MINUTES,
            'f': 'json'
        }).encode('utf-8')
        
        return parameters


    def downloadSurvey(self):
        self.messenger.info(f'Downloading survey replica...')
        self.messenger.indent()
        
        replicationRequestUrl = self.generateReplicateRequestUrl()
        resultUrl = self.pollForResponseUrl(replicationRequestUrl)
        replicaFileGeodatabasePath = self.downloadReplicaFileGeodatabase(resultUrl)

        self.messenger.info(f'Survey replica downloaded to file path [{replicaFileGeodatabasePath}]')
        self.messenger.outdent()

        return replicaFileGeodatabasePath


    def generateReplicateRequestUrl(self):
        # See https://developers.arcgis.com/rest/services-reference/enterprise/create-replica/
        createReplicaURL = f'{self.parameters[SERVICE_URL]}/createReplica/?f=json&token={self.context[TOKEN]}'
        self.messenger.info(f'Requesting Replica via [{createReplicaURL}]')

        replicaParameters = {
            "geometry": "-180,-90,180,90",
            "geometryType": "esriGeometryEnvelope",
            "inSR":4326,
            "transportType":"esriTransportTypeUrl",
            "returnAttachments":True,
            "returnAttachmentsDatabyURL":False,
            "async":True,
            "syncModel":"none",
            "dataFormat":"filegdb",
        }

        if "syncCapabilities" in self.context[SERVICE_INFO]:
            if self.context[SERVICE_INFO]["syncCapabilities"]["supportsAttachmentsSyncDirection"] == True:
                replicaParameters["attachmentsSyncDirection"] = "bidirectional"
                
        layerList = [str(l["id"]) for l in self.context[SERVICE_INFO]["layers"]]
        tableList = [str(t["id"]) for t in self.context[SERVICE_INFO]["tables"]]
        layerList.extend(tableList)
        replicaParameters["layers"] = ", ".join(layerList)
        layerQueries = {}
        
        encodedUrlParams = urllib.parse.urlencode(replicaParameters).encode('utf-8')
        
        createReplStream = urllib.request.urlopen(createReplicaURL, encodedUrlParams)
        return createReplStream


    def pollForResponseUrl(self, createReplStream):
        # This is asynchronous, so we get a jobId to check periodically for completion
        resultUrl = None
        
        thisJob = json.loads(createReplStream.read())
        self.messenger.debug(f'Response received = [{thisJob}]')

        if not "statusUrl" in thisJob:
            raise Exception(f"invalid job: {thisJob}")

        jobUrl = thisJob["statusUrl"]
        self.messenger.info(f'Watching replica job via = [{jobUrl}]')
        self.messenger.indent()

        resultUrl = ""

        tokenExpirySeconds = TOKEN_EXPIRY_MINUTES * 60
        maxPollAttempts = int(tokenExpirySeconds / POLL_WAIT_SECONDS)
        pollCounter = 1
        while resultUrl == "":
            jobPollUrl = f"{jobUrl}?f=json&token={self.context[TOKEN]}"
            self.messenger.debug(f'Polling replica job via = [{jobPollUrl}]')
            checkReq = urllib.request.urlopen(jobPollUrl)

            statusText = checkReq.read()

            status = json.loads(statusText)
            self.messenger.debug(f'Poll check #{pollCounter}, response = [{statusText}] ')

            if "resultUrl" in status.keys():
                resultUrl = status["resultUrl"]
            if pollCounter > maxPollAttempts:
                raise Exception('Took too long finish replica job')
            if status["status"] == "Failed" or status["status"] == "CompletedWithErrors":
                raise Exception(f'Create Replica Issues: [{status["status"]}]')
            if status["status"] != "Completed":
                pollCounter += 1
                time.sleep(POLL_WAIT_SECONDS)  # TODO: Random expontantial backoff instead?

        self.messenger.info(f'Result URL [{resultUrl}] obtained after [{pollCounter}] poll attempts')
                
        self.messenger.outdent()
        return resultUrl


    def downloadReplicaFileGeodatabase(self, resultUrl):
        tokenisedResultUrl = f"{resultUrl}?token={self.context[TOKEN]}"
        self.messenger.info(f'Retrieving cooked replica via [{tokenisedResultUrl}]')
        self.messenger.indent()

        resultRequestUrl = urllib.request.urlopen(tokenisedResultUrl)
        
        outDir = tempfile.mkdtemp()
        outFile = os.path.join(outDir, f"{uuid.uuid4()}.zip")

        self.messenger.info(f'Writing replica bytestream to filepath [{outFile}]')
        with open(outFile, 'wb') as output:
            output.write(resultRequestUrl.read())
        del(output) # force freeing of memory held by output variable. Is this important?

        surveyGDB = ''
        with zipfile.ZipFile(outFile, 'r') as zipGDB:
            # Get the name of the gdb directory by splitting the first part of the path of a zipped file
            surveyGDB = zipGDB.namelist()[0].split(r'/')[0]
            zipGDB.extractall(outDir)
            
        unzippedSurveyGDBpath = os.path.join(outDir, surveyGDB)   
        self.messenger.info(f'Survey geodatabase unzipped to [{unzippedSurveyGDBpath}]')

        os.remove(outFile) 
        self.messenger.info(f'Removed zipped replica file [{outFile}]')

        self.messenger.outdent()
        return unzippedSurveyGDBpath
        