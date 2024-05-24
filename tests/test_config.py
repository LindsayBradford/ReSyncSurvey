# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# test/test_config.py
# Author: Lindsay Bradford, Truii.com, 2024.
# Release History:
# ---------------------------------------------------------------------------
# V1: Initial release

import arcpy
import sys

from support.parameters import *
from support.config import *

import pytest
from unittest.mock import patch

@pytest.mark.usefixtures("useTestDataDirectory")    
class TestConfig:

    @patch('support.config.configparser.ConfigParser')
    def test_Init_CONFIG_MissingFile_ViaMock(self, mockParser):
        # given
 
        mockParser.read.return_value = [] # this is default, but explicitly stating here what the key mock behaviour should be.
        
        arcpy.SetParameterAsText(0,"CONFIG")
        arcpy.SetParameterAsText(1,"fullValidConfig.ini")  # file is valid (present and readable), but mock will pretend otherwise.
        arcpy.SetParameterAsText(2,"SanitarySurvey")
        
        #when/then

        with pytest.raises(SystemExit, match=r'Invalid config file \[fullValidConfig\.ini\]') as info:
            Config()
        
        print(f'Exception message = [{info.value}]')


    def test_Init_CONFIG_MissingFile(self):
        # given

        arcpy.SetParameterAsText(0,"CONFIG")
        arcpy.SetParameterAsText(1,"configNotPresent.ini")
        arcpy.SetParameterAsText(2,"SanitarySurvey")

        #when/then

        with pytest.raises(SystemExit, match=r'Invalid config file \[configNotPresent\.ini\]') as info:
            configUnderTest = Config()
        
        print(f'Exception message = [{info.value}]')


    def test_Init_CONFIG_MissingParameter(self):
        # given

        arcpy.SetParameterAsText(0,"CONFIG")
        arcpy.SetParameterAsText(1,"missingParamConfig.ini")
        arcpy.SetParameterAsText(2,"SanitarySurvey")

        #when/then

        with pytest.raises(SystemExit, match=r'\[\'portal\'\] missing') as info:
            configUnderTest = Config()
        
        print(f'Exception message = [{info.value}]')


    def test_Init_CONFIG_MissingSection(self):
            # given

            arcpy.SetParameterAsText(0,"CONFIG")
            arcpy.SetParameterAsText(1,"fullValidConfig.ini")
            arcpy.SetParameterAsText(2,"NotValidSection")

            #when/then

            with pytest.raises(SystemExit, match=r'Invalid section \[NotValidSection\]') as info:
                configUnderTest = Config()
        
            print(f'Exception message = [{info.value}]')


    def test_Init_CONFIG_MimimalIsValid(self):
        # given


        arcpy.SetParameterAsText(0,"CONFIG")
        arcpy.SetParameterAsText(1,"minimalValidConfig.ini")
        arcpy.SetParameterAsText(2,"SanitarySurvey")
        
        # when

        configUnderTest = Config()
 
        #then

        actualConfigMap = configUnderTest.map()

        for parameter in actualConfigMap:
            print(f'Config parameter [{parameter}] = [{actualConfigMap[parameter]}]')

        assert len(actualConfigMap) == 6
        assert actualConfigMap[PREFIX] == 'min'
        assert actualConfigMap[SERVICE_URL] == 'https://yaddayaddayadda.com/rest-of-url'

    
    def test_Init_CONFIG_FullIsValid(self):
        # given

        arcpy.SetParameterAsText(0,"CONFIG")
        arcpy.SetParameterAsText(1,"fullValidConfig.ini")
        arcpy.SetParameterAsText(2,"SanitarySurvey")
        
        # when

        configUnderTest = Config()
 
        #then

        actualConfigMap = configUnderTest.map()

        for parameter in actualConfigMap:
            print(f'Config parameter [{parameter}] = [{actualConfigMap[parameter]}]')

        assert len(actualConfigMap) == 8

        assert actualConfigMap[PREFIX] == 'myprefix'
        assert actualConfigMap[USER_NAME] == 'TheUser'
        assert actualConfigMap[PASSWORD] == 'NopeNopeNopeNope'
        assert actualConfigMap[SERVICE_URL] == 'https://yaddayaddayadda.com/rest-of-url'

        

