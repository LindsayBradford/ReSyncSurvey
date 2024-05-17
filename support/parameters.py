# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# support/parameters.py
# Author: Lindsay Bradford, Truii.com, 2024.
# Release History:
# ---------------------------------------------------------------------------
# V1: Initial release

SDE_CONNECTION = 'sde_conn'
PREFIX = 'prefix'
TIMEZONE = 'timezone'
PORTAL = 'portal'
USER_NAME = 'username'
PASSWORD = 'password'
REPROJECT_CODE = 'reprojection'
SERVICE_URL = 'service_url'

MANDATORY_PARAMETERS = [
    SDE_CONNECTION,
    PREFIX,
    TIMEZONE,
    PORTAL,
    REPROJECT_CODE,
    SERVICE_URL
]

OPTIONAL_PARAMETERS = [
    USER_NAME,
    PASSWORD
]
