#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
from io import StringIO
import csv
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc
from PyQt5 import QtGui as qtg
from PyQt5 import uic
from Models import WellDataModel


class WellProcessor(qtw.QWidget):

    submitted = qtc.pyqtSignal(list, list, list, object, object)

    def __init__(self, name, conc, samplesPerPlate, replicas):
        super().__init__()
        uic.loadUi('Views/uiWellProcessor.ui', self)
        self.setWindowTitle(f'Adding samples to {name} assay')
        self.uiSubmitT0Button.setVisible(False)
        self.uiSubmitSampleButton.setVisible(False)
        self.uiCalculateButton.setVisible(False)
        self.samplesPerPlate = samplesPerPlate
        self.conc = conc
        self.ResetDataFrame('Tf')
        self.samplePositions = [
            [(replicas * i) + 1, (replicas * i) + replicas] for i in range(samplesPerPlate)
        ]
        missingSamples = 4 - samplesPerPlate
        [self.samplePositions.append([None, None]) for _ in range(missingSamples) if missingSamples != 0]
        lastSample = sorted([i[-1] for i in self.samplePositions if i[0] is not None])
        self.samplePositions.append([lastSample[-1] + 1, 10])
        self.samples, self.sampleRanges = self.SetSamples(self.df, self.samplePositions)
        self.sampleNames = ['' for _ in range(self.samplesPerPlate)]
        self.colors = [
            '#ff0000', '#0000ff', '#ffff00', '#00ff00', '#ffffff'
        ]
        self.sampleButtons = [
            self.uiSample1Button,
            self.uiSample2Button,
            self.uiSample3Button,
            self.uiSample4Button,
            self.uiBlankButton
        ]
        self.sampleNameLabels = [
            self.uiSample1NameLine,
            self.uiSample2NameLine,
            self.uiSample3NameLine,
            self.uiSample4NameLine,
        ]
        [self.sampleButtons[i].setStyleSheet('background-color: ' + self.colors[i]) for i in range(5)]
        [self.sampleNameLabels[i].setStyleSheet('color: ' + self.colors[i]) for i in range(4)]
        [self.sampleButtons[i].setVisible(False) for i in range(4) if i >= self.samplesPerPlate]
        [self.sampleNameLabels[i].setVisible(False) for i in range(4) if i >= self.samplesPerPlate]
        self.model = WellDataModel(self.df, self.samplePositions, self.colors)
        self.uiWellTableView.setModel(self.model)
        self.uiWellTableView.verticalHeader().setDefaultAlignment(qtc.Qt.AlignRight)
        self.model.layoutChanged.emit()
        self.uiWellTableView.installEventFilter(self)
        self.sampleNameLabels[0].setFocus()
        # ---------------SIGNALS-----------------
        self.sampleButtons[0].clicked.connect(lambda: self.SampleSelection(0))
        self.sampleButtons[1].clicked.connect(lambda: self.SampleSelection(1))
        self.sampleButtons[2].clicked.connect(lambda: self.SampleSelection(2))
        self.sampleButtons[3].clicked.connect(lambda: self.SampleSelection(3))
        self.sampleButtons[4].clicked.connect(lambda: self.SampleSelection(4))
        self.sampleNameLabels[0].textChanged.connect(lambda: self.SetNames(0))
        self.sampleNameLabels[1].textChanged.connect(lambda: self.SetNames(1))
        self.sampleNameLabels[2].textChanged.connect(lambda: self.SetNames(2))
        self.sampleNameLabels[3].textChanged.connect(lambda: self.SetNames(3))
        self.uiSubmitTfButton.clicked.connect(self.SubmitTf)
        self.uiSubmitT0Button.clicked.connect(self.SubmitT0)
        self.uiCalculateButton.clicked.connect(self.Calculate)
        self.uiSubmitSampleButton.clicked.connect(self.SubmitSample)

    def eventFilter(self, source, event):
        if event.type() == qtc.QEvent.KeyPress and event.matches(qtg.QKeySequence.Copy):
            self.CopySelection()
            return True
        elif event.type() == qtc.QEvent.KeyPress and event.matches(qtg.QKeySequence.Paste):
            self.PasteSelection()
            return True
        return super().eventFilter(source, event)

    def CopySelection(self):
        selection = self.uiWellTableView.selectedIndexes()
        if selection:
            rows = sorted(index.row() for index in selection)
            columns = sorted(index.column() for index in selection)
            rowcount = rows[-1] - rows[0] + 1
            colcount = columns[-1] - columns[0] + 1
            table = [[''] * colcount for _ in range(rowcount)]
            for index in selection:
                row = index.row() - rows[0]
                column = index.column() - columns[0]
                table[row][column] = index.data()
            stream = StringIO()
            csv.writer(stream).writerows(table)
            qtw.qApp.clipboard().setText(stream.getvalue())

    def PasteSelection(self):
        selection = self.uiWellTableView.selectedIndexes()
        if selection:
            buffer = qtw.qApp.clipboard().text()
            rows = sorted(index.row() for index in selection)
            columns = sorted(index.column() for index in selection)
            reader = csv.reader(StringIO(buffer), delimiter='\t')
            for i, line in enumerate(reader):
                if rows[0] + i <= 5:
                    for j, cell in enumerate(line):
                        if columns[0] + j <= 9:
                            self.df.iloc[columns[0] + j, rows[0] + i] = float(cell.replace(',', '.'))
            self.model.layoutChanged.emit()

    def ResetDataFrame(self, step):
        if step == 'Tf':
            theTime = 'Final Time'
        elif step == 'T0':
            theTime = 'Time 0'
        self.df = pd.DataFrame([6 * [np.nan] for _ in range(10)], columns=self.conc)
        self.df['line'] = range(1, 11)
        self.df = self.df.set_index('line')
        self.uiMessageLabel.setStyleSheet('color: red')
        self.uiMessageLabel.setText(
            f'Please enter the data from your assay at {theTime}'
        )

    def SetSamples(self, data, positions):
        ranges = []
        for i, j in positions:
            if i is not None:
                ranges.append(range(i, j + 1))
            else:
                ranges.append([None, None])
        samples = [data.loc[i:j].copy() if i is not None else None for i, j in positions]
        return samples, ranges

    def SetNames(self, sampleIdx):
        self.sampleNames[sampleIdx] = self.sampleNameLabels[sampleIdx].text()

    def SampleSelection(self, sampleIdx):
        indexes = self.uiWellTableView.selectedIndexes()
        if indexes:
            first = indexes[0].column() + 1
            last = indexes[-1].column() + 1
            self.samplePositions[sampleIdx] = [first, last]
            self.samples, self.sampleRanges = self.SetSamples(self.df, self.samplePositions)
            for idx, i in enumerate(self.sampleRanges):
                if (first in i or last in i) and idx != sampleIdx:
                    self.samplePositions[idx] = [None, None]
                    self.samples[idx] = [None, None]
            self.model.layoutChanged.emit()

    def SubmitTf(self):
        if '' in self.sampleNames[:self.samplesPerPlate + 1]:
            qtw.QMessageBox.warning(
                self, 'Missing Name(s)', 'Please enter the name of all samples before continue',
                qtw.QMessageBox.Ok
            )
        elif isinstance(self.samples[-1], pd.DataFrame) is False:
            qtw.QMessageBox.warning(
                self, 'Missing Blank(s)', 'You may have not selected the Blank',
                qtw.QMessageBox.Ok
            )
        else:
            self.Tf = self.df.copy()
            self.ResetDataFrame('T0')
            self.uiTimeLabel.setText('T0')
            self.uiTimeLabel.setStyleSheet('color: red')
            self.model = WellDataModel(self.df, self.samplePositions, self.colors)
            self.uiWellTableView.setModel(self.model)
            self.model.layoutChanged.emit()
            self.uiSubmitTfButton.setVisible(False)
            self.uiSubmitT0Button.setVisible(True)
            [self.sampleButtons[i].setVisible(False) for i in range(5)]

    def SubmitT0(self):
        if '' in self.sampleNames[:self.samplesPerPlate + 1]:
            qtw.QMessageBox.warning(
                self, 'Missing Name(s)', 'Please enter the name of all samples before continue',
                qtw.QMessageBox.Ok
            )
        else:
            self.T0 = self.df.copy()
            self.TfminusT0 = self.Tf - self.T0
            self.uiTimeLabel.setText('TF-T0')
            self.samples, self.sampleRanges = self.SetSamples(self.TfminusT0, self.samplePositions)
            self.model = WellDataModel(self.TfminusT0, self.samplePositions, self.colors)
            self.uiWellTableView.setModel(self.model)
            self.model.layoutChanged.emit()
            self.uiSubmitT0Button.setVisible(False)
            self.uiCalculateButton.setVisible(True)

    def Calculate(self):
        if '' in self.sampleNames[:self.samplesPerPlate + 1]:
            qtw.QMessageBox.warning(
                self, 'Missing Name(s)', 'Please enter the name of all samples before continue',
                qtw.QMessageBox.Ok
            )
        else:
            self.uiMessageLabel.setText('')
            self.uiTimeLabel.setText('')
            self.uiCalculateButton.setVisible(False)
            self.uiSubmitSampleButton.setVisible(True)
            blankMean = self.samples[-1].stack().mean()
            blankStd = self.samples[-1].stack().std()
            self.uiBlankMeanLabel.setText(f'Blank Mean: {str(round(blankMean, 3))}')
            self.uiBlankStdLabel.setText(f'Blank Standard dev.: {str(round(blankStd, 3))}')
            self.uiBlankMeanLabel.setStyleSheet('background-color: #037272;\ncolor: #ffffff')
            self.uiBlankStdLabel.setStyleSheet('background-color: #720303;\ncolor: #ffffff')
            inhibit = []
            for i, sample in enumerate(self.samples[:-1]):
                if sample is not None:
                    self.samples[i] = sample.applymap(lambda x: (blankMean - x) * 100 / blankMean)
                    means = self.samples[i].mean()
                    desvest = self.samples[i].std()
                    self.samples[i].loc['Mean'] = means
                    self.samples[i].loc['Std'] = desvest
                    inhibit.append(self.samples[i])
            self.percentInhib = inhibit[0].append(inhibit[1:])
            self.model = WellDataModel(self.percentInhib, self.samplePositions, self.colors)
            self.uiWellTableView.setModel(self.model)
            self.model.layoutChanged.emit()
            self.uiMessageLabel.setText(
                'Verify your data and edit it befor Sample Submission'
            )

    def SubmitSample(self):
        self.submitted.emit(
            self.samples, self.sampleNames, self.samplePositions, self.Tf, self.T0
        )
        # antes de cerrar, pedir confirmación de la información que se va a guardar
        self.close()

