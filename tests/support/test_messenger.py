from support.messenger import *

import pytest

@pytest.mark.usefixtures("useTestDataDirectory", "resetArcpy", "resetMessengerSingleton")    
class TestMessenger:
    def test_Init_IsSingleton(self):
        # when

        messengerOne = Messenger()
        messengerTwo = Messenger()
        
        # then
        assert messengerOne == messengerTwo


    def test_simpleMessage(self):
        # given
        messengerUnderTest = Messenger()
        # when
        messengerUnderTest.info('hello')
        #then
        lastMsg = arcpy.GetMessage(0)
        assert lastMsg.endswith('] hello')


    def test_indentMessage(self):
        # given
        messengerUnderTest = Messenger()

        # when
        messengerUnderTest.info('unindented')
        messengerUnderTest.indent()
        messengerUnderTest.info('indented')

        #then
        lastMsg = arcpy.GetMessage(1)
        assert lastMsg.endswith(']   indented')


    def test_outdentMessage(self):
        # given
        messengerUnderTest = Messenger()
        # when
        messengerUnderTest.info('first unindented')
        messengerUnderTest.indent()
        messengerUnderTest.info('second indented')
        messengerUnderTest.outdent()
        messengerUnderTest.info('third unindented')
        
        #then
        lastMsg = arcpy.GetMessage(2)
        assert lastMsg.endswith('] third unindented')


    def test_tooManyOutdentMessage(self):
        # given
        messengerUnderTest = Messenger()
        # when
        messengerUnderTest.info('first unindented')
        messengerUnderTest.outdent()
        messengerUnderTest.info('second outdented')
        
        #then
        lastMsg = arcpy.GetMessage(1)
        assert lastMsg.endswith('] second outdented')