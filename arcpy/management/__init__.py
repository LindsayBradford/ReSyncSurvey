def Append(table, destination, schemaType, field_mapping):
    # See: https://pro.arcgis.com/en/pro-app/latest/tool-reference/data-management/append.htm
    pass

def CopyRows(in_rows, out_table, config_keyword = None):
    # See: https://pro.arcgis.com/en/pro-app/latest/tool-reference/data-management/copy-rows.htm
    pass


def CreateFileGDB(pathOnly, dbName):
    pass


def GetCount(*tableNames):
    counts = []
    for tableName in tableNames:
        counts.append(int(0))
    return counts


def Project(inputFC, outputFC, out_coordinate_system):
    pass


def Copy(sourceWorkspace, destWorkspace):
    pass

def Delete(workspace):
    pass