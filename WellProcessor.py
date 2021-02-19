#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
from PyQt5 import QtWidgets as qtw
from PyQt5 import uic
from Models import WellDataModel


class WellProcessor(qtw.QWidget):
    def __init__(self, conc, samplesPerPlate, replicas):
        super().__init__()
        uic.loadUi('uiWellProcessor.ui', self)
        self.samplesPerPlate = samplesPerPlate
        self.df = pd.DataFrame([6 * [np.nan] for _ in range(10)], columns=conc)
        self.df['line'] = range(1, 11)
        self.df = self.df.set_index('line')
        self.samplePositions = [
            [(replicas * i) + 1, (replicas * i) + replicas] for i in range(samplesPerPlate)
        ]
        self.samples, self.sampleRanges = self.SetSamples(self.samplePositions)
        self.colors = [
            '#ff0000', '#0000ff', '#ffff00', '#00ff00', '#ff00ff', '#ffffff'
        ]
        self.sampleButtons = [
            self.uiSample1Button,
            self.uiSample2Button,
            self.uiSample3Button,
            self.uiSample4Button,
            self.uiSample5Button
        ]
        [self.sampleButtons[i].setStyleSheet('background-color: ' + self.colors[i]) for i in range(5)]
        [self.sampleButtons[i].setVisible(False) for i in range(5) if i >= self.samplesPerPlate]
        self.model = WellDataModel(self.df, self.samplePositions, self.colors)
        self.uiWellTableView.setModel(self.model)
        self.model.layoutChanged.emit()
        # ---------------SIGNALS-----------------
        self.sampleButtons[0].clicked.connect(lambda: self.SampleSelection(1))
        self.sampleButtons[1].clicked.connect(lambda: self.SampleSelection(2))
        self.sampleButtons[2].clicked.connect(lambda: self.SampleSelection(3))
        self.sampleButtons[3].clicked.connect(lambda: self.SampleSelection(4))
        self.sampleButtons[4].clicked.connect(lambda: self.SampleSelection(5))

    def SetSamples(self, positions):
        ranges = [range(i, j + 1) for i, j in positions]
        samples = {f'Sample {k + 1}': self.df.loc[i:j] for k, [i, j] in enumerate(positions)}
        return samples, ranges

    def SampleSelection(self, sampleIdx):
        indexes = self.uiWellTableView.selectedIndexes()
        if indexes:
            first = indexes[0].column() + 1
            last = indexes[-1].column() + 1
            self.samplePositions[sampleIdx - 1] = [first, last]
            self.samples, self.sampleRanges = self.SetSamples(self.samplePositions)
            for idx, i in enumerate(self.sampleRanges, start=1):
                if (first in i or last in i) and idx != sampleIdx:
                    self.samplePositions[idx - 1] = [None, None]
                    self.samples[f'Sample {idx}'] = [None, None]
            self.model.layoutChanged.emit()

