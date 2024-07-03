# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# support/messemger.py  - Singleton messenger, wrapping arcpy messaging
# Author: Lindsay Bradford, Truii.com, 2024.
# Release History:
# ---------------------------------------------------------------------------
# V1: Initial release

from datetime import datetime
import arcpy


def __reload__(state):
    Messenger().reset()


TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"

class Messenger(object):
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Messenger, cls).__new__(cls)
            cls._instance.reset()
        return cls._instance
   
    def reset(self):
        self._indentCount = 0

    def indent(self):
        self._indentCount +=  1

    def outdent(self):
        if self._indentCount > 0:
            self._indentCount -= 1

    def debug(self,msgText):
        if not __debug__:
            return
        self.msg(msgText, 'DEBUG')

    def info(self,msgText):
        self.msg(msgText, ' INFO')

    def warn(self,msgText):
        self.msg(msgText, ' WARN')

    def error(self,msgText):
        self.msg(msgText, 'ERROR')

    def msg(self,msgText, msgType='UNDEFINED'):
        arcpy.AddMessage(f'{self.timestamp(msgType)}{self.indentSpace()}{msgText}')

    def timestamp(self, msgType='INFO'):
        formattedMsg = f'[{datetime.now().strftime(TIMESTAMP_FORMAT)}|{msgType}] '
        return formattedMsg


    def indentSpace(self):
        indentWhitespace = '  ' * self._indentCount
        return indentWhitespace
        
        