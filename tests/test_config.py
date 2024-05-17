from xml.dom import UserDataHandler
import arcpy
import sys

from support.parameters import *
from support.config import *
import pytest

@pytest.mark.usefixtures("useTestDataDirectory")    
class TestConfig:

    def test_Init_CONFIG_MissingFile(self):
        # given

        arcpy.SetParameterAsText(0,"CONFIG")
        arcpy.SetParameterAsText(1,"configNotPresent.ini")
        arcpy.SetParameterAsText(2,"SanitarySurvey")

        #when/then

        with pytest.raises(SystemExit, match=r'configNotPresent\.ini') as info:
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

        

