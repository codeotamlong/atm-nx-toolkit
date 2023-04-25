#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pyunpack import Archive

Archive("./db/titles.rar").extractall("./db")