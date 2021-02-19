#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5 import QtCore as qtc
from PyQt5 import QtGui as qtg
from datetime import datetime
import numpy as np


class WellDataModel(qtc.QAbstractTableModel):
    '''Model to populate the Well Data Table'''

    def __init__(self, data, samplePositions, colors):
        super().__init__()
        self._data = data
        self._samplePositions = samplePositions
        self._numOfSamples = len(samplePositions)
        self._colors = colors

    def data(self, index, role):
        if role == qtc.Qt.DisplayRole:
            value = self._data.iloc[index.column(), index.row()]
            if np.isnan(value):
                return ''
            else:
                return str(value)
        if role == qtc.Qt.TextAlignmentRole:
            return qtc.Qt.AlignCenter

    def setData(self, index, value, role):
        if role == qtc.Qt.EditRole:
            try:
                self._data.iloc[index.column(), index.row()] = float(value)
                self.dataChanged.emit(index, index)
                return True
            except ValueError:
                return False

    def rowCount(self, index):
        return 6

    def columnCount(self, index):
        return 10

    def headerData(self, section, orientation, role):
        if role == qtc.Qt.DisplayRole:
            if orientation == qtc.Qt.Horizontal:
                return str(section + 1)
            if orientation == qtc.Qt.Vertical:
                return self._data.columns[section] + ' ug/mL'
        if role == qtc.Qt.BackgroundRole:
            if orientation == qtc.Qt.Horizontal:
                for i in range(self._numOfSamples):
                    if self._samplePositions[i][0] is not None and self._samplePositions[i][0] <= section + 1 <= self._samplePositions[i][1]:
                        return qtg.QColor(self._colors[i])
                if self._samplePositions[-1][0] is not None and section + 1 > self._samplePositions[-1][1]:
                    return qtg.QColor(self._colors[-1])

    def flags(self, index):
        return qtc.Qt.ItemIsEnabled | qtc.Qt.ItemIsSelectable | qtc.Qt.ItemIsEditable


class AvailableAssaysModel(qtc.QAbstractTableModel):
    '''Model to populate the Well Data Table'''

    def __init__(self, data):
        super().__init__()
        self._data = data

    def data(self, index, role):
        if role == qtc.Qt.DisplayRole or role == qtc.Qt.EditRole:
            if index.column() == 0:
                return self._data[index.row()].name
            elif index.column() == 1:
                return self._data[index.row()].type
            elif index.column() == 2:
                return self._data[index.row()].numOfSamples
            elif index.column() == 3:
                return self._data[index.row()].conc[0]
            elif index.column() == 4:
                return str(self._data[index.row()].date)

    def setData(self, index, value, role):
        if role == qtc.Qt.EditRole:
            try:
                if index.column() == 0:
                    self._data[index.row()].name = value
                elif index.column() == 1:
                    self._data[index.row()].type = value
                elif index.column() == 2:
                    self._data[index.row()].numOfSamples = value
                elif index.column() == 3:
                    self._data[index.row()].conc = [str(float(value) / 2 ** i) for i in range(6)]
                elif index.column() == 4:
                    self._data[index.row()].date = datetime.fromisoformat(value)
                self.dataChanged.emit(index, index)
                return True
            except ValueError:
                return False

    def rowCount(self, index):
        return len(self._data)

    def columnCount(self, index):
        return 5

    def headerData(self, section, orientation, role):
        if role == qtc.Qt.DisplayRole:
            if orientation == qtc.Qt.Vertical:
                return str(section + 1)
            if orientation == qtc.Qt.Horizontal:
                if section == 0:
                    return 'Name'
                elif section == 1:
                    return 'Type'
                elif section == 2:
                    return 'Number of Samples'
                elif section == 3:
                    return 'Conc. (ug/mL)'
                elif section == 4:
                    return 'Date'

    def flags(self, index):
        return qtc.Qt.ItemIsEnabled | qtc.Qt.ItemIsSelectable | qtc.Qt.ItemIsEditable
