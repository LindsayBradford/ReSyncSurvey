# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# support/time.py
# Author: Lindsay Bradford, Truii.com, 2024.
# Release History:
# ---------------------------------------------------------------------------
# V1: Initial release

import datetime, pytz

TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"

def createTimestampText(datetimeInstance):
    return datetimeInstance.strftime(TIMESTAMP_FORMAT)


def getUTCTimestamp(inputTimezone):
    timezone = pytz.timezone(inputTimezone)
    now = datetime.datetime.now()

    inputTimezoneNow = timezone.localize(now)
    utcNow = inputTimezoneNow.astimezone(pytz.utc)

    return utcNow

def dummyTimestamp():
    return datetime.datetime.fromtimestamp(0)