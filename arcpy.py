
# Test stub to be turfed in live env for actual ESRI arcpy library.

import sys

def AddMessage(message):
    print(message)


def GetParameterAsText(parmeterIndex):
    return sys.argv[parmeterIndex + 1]
    