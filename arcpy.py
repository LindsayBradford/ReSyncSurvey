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

def GetSigninToken():
    tokenPkg = {
        'token': 'randomTokenString',
        'referer': '127.0.0.1',
        'expires': '60',
        'messages': 'here is a token message'
    }
    return tokenPkg

def AddMessage(message):
    print(message)


def GetParameterCount():
    argCount = 0
    while(sys.argv[argCount] != ''):
        argCount = argCount + 1
#    print(sys.argv[:argCount])
    return argCount - 1



def GetParameterAsText(parmeterIndex):
    return sys.argv[parmeterIndex + 1]


def SetParameterAsText(parmeterIndex, text):
    sys.argv[parmeterIndex + 1] = text
    