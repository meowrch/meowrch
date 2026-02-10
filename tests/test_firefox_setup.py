#!/usr/bin/env python3
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from Builder.managers.custom_apps.firefox import FirefoxConfigurer

firefox = FirefoxConfigurer(
    darkreader=True,
    ublock=True,
    twp=True,
    unpaywall=True,
    vot=True
)

firefox.setup()
