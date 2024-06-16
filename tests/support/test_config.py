# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Name: tests/support/test_config.py
# Purpose: Testing harness for support/config.py
# Author: Lindsay Bradford, Truii.com, 2024, based heaviy on syncSurvey
# Release History:
# ---------------------------------------------------------------------------
# V1: Initial release

from support.parameters import *
from support.config import *

import pytest

@pytest.mark.usefixtures("useTestDataDirectory")    
class TestConfig:
    def test_Init_CONFIG_MissingFile(self):
        # given

        configUnderTest = Config().withConfigMap({ 
            CONFIG_FILE_PATH: "configNotPresent.ini",
            CONFIG_FILE_SECTION: "SanitarySurvey"
        })

        #when/then

        with pytest.raises(SystemExit, match=r'Invalid config file \[configNotPresent\.ini\]') as info:
            configUnderTest.map()
        
        print(f'Exception message = [{info.value}]')


    def test_Init_CONFIG_MissingParameter(self):
        # given

        configUnderTest = Config().withConfigMap({ 
            CONFIG_FILE_PATH: "missingParamConfig.ini",
            CONFIG_FILE_SECTION: "SanitarySurvey"
        })

        #when/then

        with pytest.raises(SystemExit, match=r'\[\'portal\'\] missing') as info:
            configUnderTest.map()
        
        print(f'Exception message = [{info.value}]')


    def test_Init_CONFIG_MissingSection(self):
            # given

            configUnderTest = Config().withConfigMap({
                CONFIG_FILE_PATH: "fullValidConfig.ini", 
                CONFIG_FILE_SECTION: "NotValidSection"
            })
            
            #when/then

            with pytest.raises(SystemExit, match=r'Invalid section \[NotValidSection\]') as info:
                configUnderTest.map()
        
            print(f'Exception message = [{info.value}]')


    def test_Init_CONFIG_MimimalIsValid(self):
        # given

        configUnderTest = Config().withConfigMap({
            CONFIG_FILE_PATH: "minimalValidConfig.ini",
            CONFIG_FILE_SECTION: "SanitarySurvey"
        })
        
        # when

        actualConfigMap = configUnderTest.map()
 
        #then

        for parameter in actualConfigMap:
            print(f'Config parameter [{parameter}] = [{actualConfigMap[parameter]}]')

        assert len(actualConfigMap) == 6
        assert actualConfigMap[PREFIX] == 'min'
        assert actualConfigMap[SERVICE_URL] == 'https://yaddayaddayadda.com/rest-of-url'

    
    def test_Init_CONFIG_FullIsValid(self):
        # given

        configUnderTest = Config().withConfigMap({ 
            CONFIG_FILE_PATH: "fullValidConfig.ini",
            CONFIG_FILE_SECTION: "SanitarySurvey"
        })
        
        # when

        actualConfigMap = configUnderTest.map()
 
        #then

        for parameter in actualConfigMap:
            print(f'Config parameter [{parameter}] = [{actualConfigMap[parameter]}]')

        assert len(actualConfigMap) == 8

        assert actualConfigMap[PREFIX] == 'myprefix'
        assert actualConfigMap[PORTAL_USER_NAME] == 'TheUser'
        assert actualConfigMap[PORTAL_PASSWORD] == 'NopeNopeNopeNope'
        assert actualConfigMap[SERVICE_URL] == 'https://yaddayaddayadda.com/rest-of-url'

