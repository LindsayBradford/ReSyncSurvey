# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Name: tests/support/test_messenger.py
# Purpose: Testing harness for support/messenger.py
# Author: Lindsay Bradford, Truii.com, 2024, based heaviy on syncSurvey
# Release History:
# ---------------------------------------------------------------------------
# V1: Initial release

from support.messenger import *

from importlib import reload
import pytest

@pytest.mark.usefixtures("useTestDataDirectory", "resetArcpy", "resetMessengerSingleton")    
class TestMessenger:
    def test_InitReload_IsSingleton(self):
        # when

        import support.messenger as messenger

        reload(messenger)

        messengerOne = messenger.Messenger()
        messengerTwo = messenger.Messenger()
        
        # then
        assert messengerOne == messengerTwo


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