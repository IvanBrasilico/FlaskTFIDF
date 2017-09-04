#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep  3 18:35:40 2017

@author: ivan
Run all interface AND json urls at once
For development purposes
In production, they could be separate apps or
frozen.py can be used to generate static html for the front-end
"""
from webapp import app
import jsonapp

if __name__ == '__main__':
    app.run()
