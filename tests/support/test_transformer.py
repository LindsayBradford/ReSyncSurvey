from support.parameters import *
import support.time as time


import pytest
# from unittest.mock import patch

from support.transformer import FGDBReprojectionTransformer

@pytest.mark.usefixtures("useTestDataDirectory", "resetArcpy", "resetMessengerSingleton")    
class TestFGDReprojectionTransformer:

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
            PROCESS_TIME: time.getUTCTimestamp(parameters[TIMEZONE])    
        }
        
        fakeReplicatedGeodatabase = 'fakeReplicant.gdb'
        
        transformerUnderTest = FGDBReprojectionTransformer(parameters).withContext(context)
        transformerUnderTest.transform(fakeReplicatedGeodatabase)

        assert True

@pytest.mark.skip(reason="just exploring <list>.extend() behaviour")
class TestListExtend():
    
    def test_list_extend(self):
        #given    
        listUnderTest = ['one','two']
        
        #when
        listUnderTest.extend(['three'])
        
        #then
        assert len(listUnderTest) == 3
        assert listUnderTest[0] == 'one'
        assert listUnderTest[2] == 'three'

    def test_list_extend_empty(self):
        #given    
        listUnderTest = []
        
        #when
        listUnderTest.extend(['three'])
        
        #then
        assert len(listUnderTest) == 1
        assert listUnderTest[0] == 'three'

    def test_list_extend_None_errors(self):
        #given    
        listUnderTest = None
        
        #when
        with pytest.raises(Exception) as e_info:
            listUnderTest.extend(['three'])
        
        #then
        assert str(e_info.value) == "'NoneType' object has no attribute 'extend'"

    def test_list_extend_empty_with_None(self):
        #given    
        listUnderTest = []
        
        #when
        with pytest.raises(Exception) as e_info:
            listUnderTest.extend(None)
        
        #then
        assert len(listUnderTest) == 0
