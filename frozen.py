#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Sep  2 16:56:59 2017

@author: ivan
"""

from flask_frozen import Freezer
from webapp import app

freezer = Freezer(app)

if __name__ == '__main__':
    freezer.freeze()