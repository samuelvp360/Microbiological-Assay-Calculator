#!/usr/bin/env python3
# -*- coding: utf-8 -*-


class Assay():
    def __init__(self, typeOfAssay, name, conc, date):
        self.type = typeOfAssay
        self.name = name
        self.conc = conc
        self.date = date
        self.numOfSamples = 0
