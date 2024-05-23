# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# tests/conftest.py
# Author: Lindsay Bradford, Truii.com, 2024.
# Release History:
# ---------------------------------------------------------------------------
# V1: Initial release

import pytest
import os
from pathlib import Path

@pytest.fixture
def useTestDataDirectory():
    print(f'Absolute path of module [{__file__}]')
    path = Path(__file__).parents[0]

    testPath = path.joinpath('test_data')
    print(f'Test working directory: [{testPath}]')
    os.chdir(testPath)