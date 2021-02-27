#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5 import QtCore as qtc
from persistent import Persistent
import transaction


class Assay(Persistent):
    def __init__(self, typeOfAssay, name, conc, date):
        self.type = typeOfAssay
        self.name = name
        self.conc = conc
        self.date = date
        self.samples = []
        self.numOfSamples = 0
        self.stored = False
        self._p_changed = False

    def StoreSamples(self, samples, sampleNames, samplesPositions, Tf, T0):
        for index, name in enumerate(sampleNames):
            self.samples.append({
                'Name': name,
                'Tf': Tf,
                'T0': T0,
                'Positions': samplesPositions,
                'Name of samples': sampleNames,
                'Inhibition': samples[index]
            })
        self.numOfSamples += len(sampleNames)
        self._p_changed = True


