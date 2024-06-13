

class Editor():
    # https://pro.arcgis.com/en/pro-app/latest/arcpy/data-access/editor.htm
    def __init__(self, workspace):
        pass
    
    def __enter__(self):
        return self
    
    def __exit__(self, exception_type, exception_value, exception_traceback):
        pass


class Cursor():
    def __init__(self):
        pass
    
    def updateRow(self, value):
        pass

    def __enter__(self):
        return self
    
    def __exit__(self, exception_type, exception_value, exception_traceback):
        pass
    
    def __iter__(self):
        self.a = 1
        return self

    def __next__(self):
        x = self.a
        self.a += 1
        if self.a < 4:
            return x
        else:
            raise StopIteration


def UpdateCursor(FQtable, where_clause):
    return Cursor()

def SearchCursor(table, columnList):
    return Cursor()
