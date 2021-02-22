#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from persistent import Persistent
import transaction


class Assay(Persistent):
    def __init__(self, typeOfAssay, name, conc, date):
        self.type = typeOfAssay
        self.name = name
        self.conc = conc
        self.date = date
        self.samplesDict = {}
        self.numOfSamples = 0
        self.stored = False
        self._p_changed = False

