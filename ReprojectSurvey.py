# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# ReprojectSurvey.py
# Author: Lindsay Bradford, Truii.com, 2024.
# Release History:
# ---------------------------------------------------------------------------
# V1: Initial release
# ---------------------------------------------------------------------------

from importlib import reload

import support.config as config
import support.survey_reprojector as reprojector
import support.survey_replicator as replicator
import support.transformer as transformer
import support.appender as appender
import support.messenger as messenger

NAME='ReprojectSurvey'
VERSION = '1.0'

def buildReprojector(configSupplied):
    return reprojector.SurveyReprojector(configSupplied).\
                usingSurveyReplicator(replicator.AGOLSurveyReplicator(configSupplied)).\
                usingReprojector(transformer.FGDBReprojectionTransformer(configSupplied)).\
                usingAppender(appender.SDEAppender(configSupplied))


def main():
    messenger.Messenger().info(f'{NAME} version {VERSION}')

    configSupplied = config.Config().map()
    reprojector = buildReprojector(configSupplied)
    reprojector.reproject()


def reloadModulesForArcGISPro():
    # https://gis.stackexchange.com/questions/91112/refreshing-imported-modules-in-arcgis-python-toolbox
    reload(messenger)
    reload(config)
    reload(reprojector)
    reload(replicator)
    reload(transformer)
    reload(appender)


if __name__ == '__main__':
    reloadModulesForArcGISPro()       
    main()