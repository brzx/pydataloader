#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup
import py2exe

setup(
    windows = ["iLoad.py"],
    console = ["scheduleLoad.py", "multiScheduleLoad.py"],
    options = { "py2exe": { "dll_excludes": ["MSVCP90.dll"] } }
    
)
