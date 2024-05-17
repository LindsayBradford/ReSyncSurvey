# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# support.arcpy.py -- Test stub for ESRI arcpy library.
# Author: Lindsay Bradford, Truii.com, 2024.
# Release History:
# ---------------------------------------------------------------------------
# V1: Initial release
# ---------------------------------------------------------------------------
# 

import sys

def AddMessage(message):
    print(message)


def GetParameterCount():
    return len(sys.argv)


def GetParameterAsText(parmeterIndex):
    return sys.argv[parmeterIndex + 1]


def SetParameterAsText(parmeterIndex, text):
    sys.argv[parmeterIndex + 1] = text
    