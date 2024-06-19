# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# ReSyncSurvey.py  - SyncSurvey with Reprojection
# Author: Lindsay Bradford, Truii.com, 2024.
# Release History:
# ---------------------------------------------------------------------------
# V1: Initial release
# ---------------------------------------------------------------------------

from importlib import reload

import support.config as config
import support.reprojector as reprojector
import support.extractor as extractor
import support.transformer as transformer
import support.loader as loader
import support.messenger as messenger

NAME='ReprojectSurvey'
VERSION = '1.0'

def buildReprojector(configSupplied):
    # ETL sub-component dependenct injection
    return reprojector.SurveyReprojector(configSupplied).\
                usingExtractor(extractor.AGOLSurveyReplicator(configSupplied)).\
                usingTransformer(transformer.FGDBReprojectionTransformer(configSupplied)).\
                usingLoader(loader.ReprojectingSDEAppender(configSupplied))


def main():
    mainMessenger = messenger.Messenger()
    mainMessenger.info(f'{NAME} version {VERSION}')

    configSupplied = config.Config().map()
    mainMessenger.info(f'Parameters supplied: {configSupplied}')
    
    reprojector = buildReprojector(configSupplied)
    reprojector.reproject()


def reloadModulesForArcGISPro():
    # https://gis.stackexchange.com/questions/91112/refreshing-imported-modules-in-arcgis-python-toolbox
    reload(messenger)
    reload(config)
    reload(reprojector)
    reload(extractor)
    reload(transformer)
    reload(loader)


if __name__ == '__main__':
    reloadModulesForArcGISPro()       
    main()