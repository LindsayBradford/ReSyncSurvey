# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# support/time.py
# Author: Lindsay Bradford, Truii.com, 2024.
# Release History:
# ---------------------------------------------------------------------------
# V1: Initial release

import datetime, pytz, time

TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"

def createTimestampText(datetimeInstance):
    return datetimeInstance.strftime(TIMESTAMP_FORMAT)


def getUTCTimestamp(inputTimezone):
    inputTimezoneNow = getLocalisedTimestamp(inputTimezone)
    utcNow = inputTimezoneNow.astimezone(pytz.utc)

    return utcNow


def getLocalisedTimestamp(inputTimezone):
    now = datetime.datetime.now()

    timezone = pytz.timezone(inputTimezone)
    inputTimezoneNow = timezone.localize(now)
    
    return inputTimezoneNow


def dummyTimestamp():
    return datetime.datetime.fromtimestamp(0)


def sleep(seconds):
    time.sleep(seconds)