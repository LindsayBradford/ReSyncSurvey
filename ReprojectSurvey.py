# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# ReprojectSurvey.py
# Author: Lindsay Bradford, Truii.com, 2024.
# Release History:
# ---------------------------------------------------------------------------
# V1: Initial release
# ---------------------------------------------------------------------------


from support.config import Config
from support.reprojection import Reprojection


def main():
    configSupplied = Config().map()

    reprojection = Reprojection(configSupplied)
    reprojection.reproject()


if __name__ == '__main__':
    main()