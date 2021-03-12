#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from persistent import Persistent


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

    def StoreSample(self, sample, index, sampleNames, samplesPositions, TF, T0):
        self.samples.append({
            'Name': sampleNames[index],
            'TF': TF,
            'T0': T0,
            'Positions': samplesPositions,
            'Name of samples': sampleNames,
            'Inhibition': sample
        })
        self.numOfSamples += 1
        self._p_changed = True

    def RemoveSample(self, samplesIndexes):
        for i, sampleIndex in enumerate(samplesIndexes):
            del self.samples[sampleIndex - i]
            self.numOfSamples -= 1
        self._p_changed = True

