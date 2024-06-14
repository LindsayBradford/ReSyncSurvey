# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Name: support/appender.py
# Purpose: To append data from a temp file geodatabase into an SDE geodatabase
# Author: Lindsay Bradford, Truii.com, 2024, based heaviy on syncSurvey
# Release History:
# ---------------------------------------------------------------------------
# V1: Initial release

from support.parameters import *
from support.messenger import Messenger

from abc import ABC, abstractmethod
import re

import arcpy
import os

# Context keys

SECTION = 'ProcessSection'
CLEANUP_OPERATIONS = 'CleanupOperations'
EXISTING_TABLES = 'ExistingTables'

class Appender(ABC):
    @abstractmethod
    def withContext(self, context):
        pass

    @abstractmethod
    def appendFrom(self, surveyGDB):
        return None


class NullAppender(Appender):
    def __init__(self, parametersSupplied):
        self.context = {}
        self.parameters = parametersSupplied


    def withContext(self, context):
        self.context = context
        return self


    def appendFrom(self, surveyGDB):
        return f"<Nothing appended from Survey geodatabase {surveyGDB}>"


class SDEAppender(Appender):
    def __init__(self, parametersSupplied):
        self.context = {}
        self.parameters = parametersSupplied
        self.messenger = Messenger()


    def withContext(self, context):
        self.context = context
        return self


    def appendFrom(self, surveyGDB):
        self.context[CLEANUP_OPERATIONS] = {}

        self.messenger.info(f'Appending data from [{surveyGDB}] to [{self.parameters[SDE_CONNECTION]}]...')
        self.messenger.indent()

        self.createDestinationDatabaseIfNeeded()
        self.createDestinationTablesIfNeeded(surveyGDB)
        self.updateDestinationTables(surveyGDB)

        self.messenger.outdent()
        self.messenger.info(f'Done appending data from [{surveyGDB}] to [{self.parameters[SDE_CONNECTION]}]')


    def createDestinationDatabaseIfNeeded(self):
        destinationDB = self.parameters[SDE_CONNECTION]
        if not destinationDB.endswith('.gdb'):
            return
        
        if not arcpy.Exists(destinationDB):
            self.messenger.info(f'Destinaion file geodatabase [{destinationDB}] does not exist. Creating...')
            split = os.path.split(destinationDB)

            pathOnly = split[0]
            if pathOnly == {}:
                pathOnly = '.'

            dbName = split[1]

            arcpy.management.CreateFileGDB(pathOnly, dbName)
            self.messenger.info(f'Destinaion file geodatabase [{destinationDB}] created')


    def createDestinationTablesIfNeeded(self, surveyGDB):
        if len(self.context[EXISTING_TABLES]) > 0:
            self.messenger.info('Tables were found in destination workspace. Skipping table creation')
            return

        self.context[SECTION] = 'Making Tables'
        self.createTablesAtDestination(surveyGDB)
        
        #TODO:  get a better bead on CLEANUP_OPEERATIONS usage...
        self.context[CLEANUP_OPERATIONS]['createTables'] = True


    def createTablesAtDestination(self, surveyGDB):
        arcpy.env.workspace = surveyGDB

        self.messenger.info('Creating needed tables in destination workspace...')

        surveyGDBdesc = arcpy.Describe(arcpy.env.workspace)
        


        self.migrateDomainsToDestination(surveyGDB, surveyGDBdesc)
        self.createDestinationFeatureClassesAndTables(surveyGDB, surveyGDBdesc)
        self.createDestinationRelationships(surveyGDBdesc)

        self.messenger.info('Done creating needed tables in destination workspace')


    def migrateDomainsToDestination(self, surveyGDB, dscW):
        self.messenger.indent()
        self.messenger.info('Migrating domains...')

        destWorkspace = self.parameters[SDE_CONNECTION]

        self.messenger.indent()
        for domainName in dscW.domains:
            if domainName[0:3] == 'cvd':
                self.messenger.debug(f'Creating domain [{domainName}]')
                tempTable = f'in_memory\{domainName}'
                arcpy.DomainToTable_management(surveyGDB, domainName, tempTable,'CODE', 'DESC')
                arcpy.TableToDomain_management(tempTable, 'CODE', 'DESC', destWorkspace, domainName, update_option='REPLACE')
                arcpy.Delete_management(tempTable)
        self.messenger.outdent()

        self.messenger.info('Done migrating domains')
        self.messenger.outdent()


    def createDestinationFeatureClassesAndTables(self, surveyGDB, surveyGDBdesc):
        self.messenger.indent()
        self.messenger.info("Creating feature classes & tables...")

        self.messenger.indent()

        destWorkspace = self.parameters[SDE_CONNECTION]  
        prefix = self.parameters[PREFIX]
        
        # TODO: Does this force the CRS transformation? James Tedrick (syncSurvey author, ESRI employee, email 27/03/24, says yes)
        # https://pro.arcgis.com/en/pro-app/latest/tool-reference/environment-settings/geographic-transformations.htm
        # arcpy.env.outputCoordinateSystem = arcpy.SpatialReference("WGS 1984 UTM Zone 18N")
        # arcpy.env.geographicTransformations = "Arc_1950_To_WGS_1984_5; PSAD_1956_To_WGS_1984_6"
        # https://epsg.io/7856s

        self.messenger.info(f'Applying CRS [{self.parameters[REPROJECT_CODE]}] as output coordinate system')
        arcpy.env.outputCoordinateSystem = arcpy.SpatialReference(self.parameters[REPROJECT_CODE])

        geographicTransform = "WGS_1984_To_GDA2020_3"
        self.messenger.info(f'Applying geographic transformation [{geographicTransform}] as output coordinate transformation')
        arcpy.env.geographicTransformations = geographicTransform

        allTables = self.getSurveyTables(surveyGDB)
        for table in allTables:
            dsc = arcpy.Describe(table)
            newTableName = f"{prefix}_{table}"
            templateTable = os.path.join(surveyGDB, table)

            if dsc.datatype == u'FeatureClass':
                self.messenger.debug(f"Creating Feature Classes [{newTableName}]...")
                newTable = arcpy.CreateFeatureclass_management(destWorkspace, newTableName, "POINT", template=templateTable, spatial_reference=dsc.spatialReference)
            else:
                self.messenger.debug(f"Creating Table [{newTableName}]...")
                newTable = arcpy.CreateTable_management(destWorkspace, newTableName, template=templateTable)
            
            self.messenger.indent()

            # Attach domains to fields

            self.messenger.debug("Attaching field domains to table...")
            self.messenger.indent()
            tableFields = arcpy.ListFields(table)
            for field in tableFields:
                if field.domain != '':
                    self.messenger.debug(f"Field [{newTableName}.{field.name}] being assigned domain [{field.domain}]")
                    arcpy.AssignDomainToField_management(newTable, field.name, field.domain)
            self.messenger.outdent()

            if surveyGDBdesc.workspaceType == "RemoteDatabase":
                self.messenger.debug(f"Registering new table [{newTableName}] as versioned...")
                arcpy.RegisterAsVersioned_management(newTable)
    
            self.messenger.outdent()
            
        self.messenger.outdent()

        self.messenger.info("Done creating feature classes & tables")
        self.messenger.outdent()


    def createDestinationRelationships(self, surveyGDBdesc):
        self.messenger.indent()
        self.messenger.info("Creating Relationships...")

        #Reconnect Relationship classes, checking for attachments
        CARDINALITIES = {
        'OneToOne': "ONE_TO_ONE",
        'OneToMany': "ONE_TO_MANY",
        'ManyToMany': "MANY_TO_MANY"
        }

        destWorkspace = self.parameters[SDE_CONNECTION]
        prefix = self.parameters[PREFIX]

        for child in [(c.name, c.datatype) for c in surveyGDBdesc.children if c.datatype == u'RelationshipClass']:
            self.messenger.indent()

            dscRC = arcpy.Describe(child[0])
            
            RCOriginTable = dscRC.originClassNames[0]
            RCDestTable = dscRC.destinationClassNames[0]
            
            newOriginTable = f"{prefix}_{RCOriginTable}"
            newOriginPath = os.path.join(destWorkspace, newOriginTable)

            if dscRC.isAttachmentRelationship:
                #Simple case - attachments have a dedicated tool
                self.messenger.info(f"Enabling attachment relationship for [{newOriginTable}]...")
                arcpy.EnableAttachments_management(newOriginPath)
            else:
                newDestTable = f"{prefix}_{RCDestTable}"
                newDestPath = os.path.join(destWorkspace, newDestTable)
                newRC = os.path.join(destWorkspace, f"{prefix}_{child[0]}")
                relationshipType = "COMPOSITE" if dscRC.isComposite else "SIMPLE"
                fwd_label = dscRC.forwardPathLabel if dscRC.forwardPathLabel != '' else 'Repeat'
                bck_label = dscRC.backwardPathLabel if dscRC.backwardPathLabel != '' else 'MainForm'
                msg_dir = dscRC.notification.upper()
                cardinality = CARDINALITIES[dscRC.cardinality]
                attributed = "ATTRIBUTED" if dscRC.isAttributed else "NONE"
                originclassKeys = dscRC.originClassKeys
                originclassKeys_dict = {}
                for key in originclassKeys:
                    originclassKeys_dict[key[1]] = key[0]
                originPrimaryKey = originclassKeys_dict[u'OriginPrimary']
                originForiegnKey = originclassKeys_dict[u'OriginForeign']

                #Regular Relation

                self.messenger.info(f"Enabling [{relationshipType}] relationship between [{newOriginTable}] and [{newDestTable}]...")
                arcpy.CreateRelationshipClass_management(newOriginPath, newDestPath, newRC, relationshipType, fwd_label, bck_label, msg_dir, cardinality, attributed, originPrimaryKey, originForiegnKey)

            self.messenger.outdent()

        self.messenger.info("Done creating relationships")
        self.messenger.outdent()


    # TODO: copied from transformer.py... consolidate.
    def getSurveyTables(self, workspace, prefix=''):
        originalWorkspace = arcpy.env.workspace
        arcpy.env.workspace = workspace
        
        tables = self.getSurveyTablesFromCurrentWorkspace(prefix)

        arcpy.env.workspace = originalWorkspace
        return tables


    def getSurveyTablesFromCurrentWorkspace(self, prefix):
        #This is used in 2 contexts:
        #Downloaded GDB - tables have no prefix
        #Enterprise GDB - prefix is added to table name
        #The full table name (i.e. GDB.SCHEMA.NAME) is returned, so prefix is in the middle
        wildcard = '*{0}*'.format(prefix) if prefix != '' else '*'
        #List the Feature Classes & Tables
        #Tables also returns Attachment tables
        featureClasses = arcpy.ListFeatureClasses(wildcard)
        tables = arcpy.ListTables(wildcard)

        #Loop through the tables, checking for:
        #1) Is this an attachment table?
        #2) Does the prefix actually match the prefix term exactly?
        allTables = featureClasses
        allTables.extend(tables)
        outTables = []
        for t in allTables:
            tableName = t.split('.')[-1]
            nameParts = tableName.split('_')
            if '__ATTACH' not in t:
                if nameParts[0] == prefix or prefix == '':
                    outTables.append(t)

        return outTables


    def updateDestinationTables(self, surveyGDB):
        self.context[SECTION] = 'Updating Tables'

        appendTables = {}
        if EXISTING_TABLES in self.context.keys():
            appendTables = self.context[EXISTING_TABLES]
        self.context[CLEANUP_OPERATIONS]['append'] = appendTables

        self.appendTables(surveyGDB)

        self.context[CLEANUP_OPERATIONS].pop('append', None)
        self.context[CLEANUP_OPERATIONS].pop('createTables', None)


    def appendTables(self, surveyGDB):
        self.messenger.info('Appending new data to destination workspace tables...')
        self.messenger.indent()

        arcpy.env.workspace = surveyGDB
        
        tableList = self.getSurveyTables(surveyGDB)
        attachmentList = self.getTablesWithAttachments(self.parameters[SDE_CONNECTION], self.parameters[PREFIX])

        for table in tableList:
            #Normalize table fields to get schemas in alignmnet- enable all editing, make nonrequired
            fields = arcpy.ListFields(table)
            for field in fields:
                if not field.editable:
                    field.editable = True
                if field.required:
                    field.required = False
            destinationName = f"{self.parameters[PREFIX]}_{table}"
            destinationFC = os.path.join(self.parameters[SDE_CONNECTION], destinationName)

            self.messenger.debug(f'Processing replica [{table}] -> SDE [{destinationName}]...')

            originFieldNames = [f.name for f in arcpy.ListFields(table)]
            destFieldNames = [f.name for f in arcpy.ListFields(destinationFC)]
            fieldMap = self.createFieldMap(table, originFieldNames, destFieldNames)

            arcpy.management.Append(table, destinationFC, 'NO_TEST', fieldMap)

            if destinationName in attachmentList:
                self.appendAttachments(table, destinationFC)

        self.messenger.outdent()
        self.messenger.info('Done appending new data to destination workspace tables')


    def getTablesWithAttachments(self, workspace, prefix):
        '''Lists the tables that have attachments, so that we can seperately process the attachments during migration'''
        self.messenger.info('Finding tables with attachments...')

        originalWorkspace = arcpy.env.workspace
        arcpy.env.workspace = workspace
        dscW = arcpy.Describe(workspace)
        tableList = []
        relClasses = [c.name for c in dscW.children if c.datatype == u'RelationshipClass']
        for child in relClasses:
            dbNameParts = child.split(".")
            childParts = dbNameParts[-1].split("_")
            if childParts[0] == prefix:
                dscRC = arcpy.Describe(child)
                if dscRC.isAttachmentRelationship:
                    originTable = dscRC.originClassNames[0]
                    originParts = originTable.split(".")
                    tableList.append(originParts[-1])
        arcpy.env.workspace = originalWorkspace

        self.messenger.info('Done finding tables with attachments')
        return tableList

 
    def createFieldMap(self, originTable, originFieldNames, destinationFieldNames):
        '''Matches up fields between tables, even if some minor alteration (capitalization, underscores) occured during creation'''
        self.messenger.indent()
        self.messenger.debug(f'Creating field map for table [{originTable}]...')

        fieldMappings = arcpy.FieldMappings()
        for field in originFieldNames:
            if field != 'SHAPE':
                thisFieldMap = arcpy.FieldMap()
                thisFieldMap.addInputField(originTable, field)
                if field in destinationFieldNames:
                    #Easy case- it came over w/o issue
                    outField = thisFieldMap.outputField
                    outField.name = field
                    thisFieldMap.outputField = outField
                    #arcpy.AddMessage("\t".join([field, field]))
                else:
                    #Use regular expression to search case insensitve and added _ to names
                    candidates = [x for i, x in enumerate(destinationFieldNames) if re.search('{0}\W*'.format(field), x, re.IGNORECASE)]
                    if len(candidates) == 1:
                        outField = thisFieldMap.outputField
                        outField.name = candidates[0]
                        thisFieldMap.outputField = outField
                fieldMappings.addFieldMap(thisFieldMap)

        self.messenger.debug(f'Done creating field map for table [{originTable}]')
        self.messenger.outdent()

        return fieldMappings


    def appendAttachments(self, inFC, outFC, keyField='rowid', valueField = 'globalid'):
        self.messenger.indent()
        self.messenger.debug(f'Appending attachments for [{outFC}]...')
        
        # 1) scan through both GlobalID and rowID of the old and new features and build a conversion dictionary
        GUIDFields = [keyField, valueField]
        inDict = {}
        outDict = {}
        lookup = {}
        
        inAttachTable = f"{inFC}__ATTACH"
        with arcpy.da.SearchCursor(inFC, GUIDFields) as inputSearch:
            for row in inputSearch:
                inDict[row[0]] = row[1]

        outAttachTable = f"{outFC}__ATTACH"
        with arcpy.da.SearchCursor(outFC, GUIDFields) as outputSearch:
            for row in outputSearch:
                outDict[row[0]] = row[1]
        for key, inValue in inDict.items():
            if key not in outDict.keys():
                raise Exception(f'missing key: {key}')
            lookup[inValue] = outDict[key]

        # 2) Copy the attachment table to an in-memory layer
        tempTableName = r'in_memory\AttachTemp'
        
        self.messenger.debug(f'Copying attachment table [{inAttachTable}] rows to [{tempTableName}]...')
        tempTable = arcpy.management.CopyRows(inAttachTable, tempTableName)

        # 3) update the attachment table with new GlobalIDs
        self.messenger.debug(f'Updating table [{tempTableName}] with new GlobalIDs...')
        with arcpy.da.UpdateCursor(tempTable, ['REL_GLOBALID']) as uRows:
            for uRow in uRows:
                uRow[0] = lookup[uRow[0]]
                uRows.updateRow(uRow)

        # 4) Append to destination attachment table
        self.messenger.debug(f'Appending table [{tempTableName}] to [{outAttachTable}]...')
        
        arcpy.management.Append(tempTable, outAttachTable, 'NO_TEST')

        self.messenger.debug(f'Deleting table [{tempTableName}]...')
        arcpy.Delete_management(tempTable)

        self.messenger.debug(f'Done appending attachments for [{outFC}]...')
        self.messenger.outdent()

