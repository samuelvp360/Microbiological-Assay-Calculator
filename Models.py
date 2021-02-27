#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5 import QtCore as qtc
from PyQt5 import QtGui as qtg
from PyQt5.QtWidgets import QApplication, QStyle
from datetime import datetime
import numpy as np


class WellDataModel(qtc.QAbstractTableModel):
    '''Model to populate the Well Data Table'''

    def __init__(self, data, samplePositions, colors, inhibition=False):
        super().__init__()
        self._data = data
        self._samplePositions = samplePositions
        self._numOfSamples = len(samplePositions)
        self._inhibition = inhibition
        self._colors = colors
        self._indexes = self._data.index.values.tolist()

    def data(self, index, role):
        if role == qtc.Qt.DisplayRole or role == qtc.Qt.EditRole:
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
        return self._data.shape[1]

    def columnCount(self, index):
        return self._data.shape[0]

    def headerData(self, section, orientation, role):
        if role == qtc.Qt.DisplayRole:
            if orientation == qtc.Qt.Horizontal:
                return str(self._indexes[section])
            if orientation == qtc.Qt.Vertical:
                return self._data.columns[section] + u' \u00B5g/mL'
        if role == qtc.Qt.BackgroundRole:
            if orientation == qtc.Qt.Horizontal:
                column = self._indexes[section]
                if column == 'Mean':
                    return qtg.QColor('#037272')
                elif column == 'Std':
                    return qtg.QColor('#720303')
                else:
                    for i in range(self._numOfSamples):
                        if self._samplePositions[i][0] is not None and \
                           self._samplePositions[i][0] <= int(column) <= self._samplePositions[i][1]:
                            return qtg.QColor(self._colors[i])
        if role == qtc.Qt.ForegroundRole:
            if orientation == qtc.Qt.Horizontal:
                column = self._indexes[section]
                if column == 'Mean':
                    return qtg.QColor('#ffffff')
                elif column == 'Std':
                    return qtg.QColor('#ffffff')

    def flags(self, index):
        return qtc.Qt.ItemIsEnabled | qtc.Qt.ItemIsSelectable | qtc.Qt.ItemIsEditable


class AssaysModel(qtc.QAbstractTableModel):
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

        if role == qtc.Qt.DecorationRole:
            style = QApplication.style()
            if self._data[index.row()].stored and index.column() == 0:
                return qtg.QIcon(style.standardIcon(QStyle.SP_DriveHDIcon))

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
                    return u'Conc. (\u00B5g/mL)'
                elif section == 4:
                    return 'Date'

    def flags(self, index):
        return qtc.Qt.ItemIsEnabled | qtc.Qt.ItemIsSelectable


class SamplesModel(qtc.QAbstractTableModel):
    def __init__(self, data, conc):
        super().__init__()
        self._data = data
        self._conc = conc
        self._names = [i['Name'] for i in self._data]

    def data(self, index, role):
        if role == qtc.Qt.DisplayRole:
            thisConc = self._conc[index.column()]
            inhibition = self._data[index.row()]['Inhibition'].loc['Mean', thisConc]
            std = self._data[index.row()]['Inhibition'].loc['Std', thisConc]
            return str(round(inhibition, 3)) + u' \u00B1 ' + str(round(std, 3))

    def rowCount(self, index):
        return len(self._data)

    def columnCount(self, index):
        return len(self._conc)

    def headerData(self, section, orientation, role):
        if role == qtc.Qt.DisplayRole:
            if orientation == qtc.Qt.Vertical:
                return self._names[section]
            if orientation == qtc.Qt.Horizontal:
                return self._conc[section] + u' \u00B5g/mL'

    def flags(self, index):
        return qtc.Qt.ItemIsEnabled | qtc.Qt.ItemIsSelectable

