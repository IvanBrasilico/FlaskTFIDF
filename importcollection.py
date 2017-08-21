# -*- coding: utf-8 -*-
"""
Created on Mon Aug 21 10:01:05 2017

@author: ivan
"""


from tecmodels import db
db.create_all()

from tecmodels import Collection
Collection1 = Collection("TEC")
db.session.add(Collection1)

db.session.commit()

