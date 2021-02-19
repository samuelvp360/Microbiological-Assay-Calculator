#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from datetime import datetime
# from PyQt5 import QtCore as qtc
# from PyQt5 import QtGui as qtg
from PyQt5 import QtWidgets as qtw
from PyQt5 import uic
# import pandas as pd
# import numpy as np
from Models import AvailableAssaysModel
from Plotter import PlotCanvas
from WellProcessor import WellProcessor
from Assay import Assay


class MainWindow(qtw.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('uiMainWindow.ui', self)
        self.assaysDict = {}
        self.model = AvailableAssaysModel(self.assaysDict)
        self.uiAvailableAssaysTableView.setModel(self.model)
        self.uiAvailableAssaysTableView.resizeColumnsToContents()
        self.uiAvailableAssaysTableView.resizeRowsToContents()
        # ---------------- SIGNALS ---------------
        self.uiActionMIC.triggered.connect(lambda: self.AddAssay('MIC'))
        self.uiActionMTT.triggered.connect(lambda: self.AddAssay('MTT'))
        self.uiAddSampleButton.clicked.connect(self.AddSample)

    def AddAssay(self, typeOfAssay):
        position = len(self.assaysDict)
        name = self.SetAssayName()
        conc = self.SetConcentrations()
        while conc is False:
            conc = self.SetConcentrations()
        date = datetime.now()
        self.assaysDict[position] = Assay(typeOfAssay, name, conc, date)
        self.model.layoutChanged.emit()
        self.uiAvailableAssaysTableView.resizeColumnsToContents()
        self.uiAvailableAssaysTableView.resizeRowsToContents()

    def AddSample(self):
        position = self.SetSelectedAssay()
        items = ['1', '2', '3', '4']
        if position is not None:
            samples, ok1 = qtw.QInputDialog.getItem(
                self, 'Number of Samples', 'Choose the number of samples per plate',
                items, 0, False
            )
            if int(samples) == 3:
                del items[3]
            elif int(samples) == 4:
                del items[2:]
            replicas, ok2 = qtw.QInputDialog.getItem(
                self, 'Number of Samples', 'Choose the number of replicas',
                items, 0, False
            )
            if ok1 and ok2:
                self.wellProcessor = WellProcessor(
                    self.assaysDict[position].conc, int(samples), int(replicas)
                )
                self.wellProcessor.show()
            else:
                return False
        else:
            qtw.QMessageBox.warning(
                self, 'No Assay Selection',
                'You have not selected an assay, please choose one assay before adding a sample'
            )

    def SetSelectedAssay(self):
        indexes = self.uiAvailableAssaysTableView.selectedIndexes()
        if indexes:
            index = indexes[0]
            return index.row()
        else:
            return None

    def SetAssayName(self):
        text, ok = qtw.QInputDialog.getText(
            self, 'Assay Name', 'Please enter the name of the assay'
        )
        if ok:
            return text

    def SetConcentrations(self):
        value, ok = qtw.QInputDialog.getText(
            self, 'Concentrations', 'Please enter the highest concentration'
        )
        if ok:
            try:
                conc = [str(float(value.replace(',', '.')) / 2 ** i) for i in range(6)]
                return conc
            except ValueError:
                qtw.QMessageBox.warning(
                    self, 'Not a valid number!',
                    'You have not enter a valid number, please try again'
                )
                return False


if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


# labels = ['G1', 'G2', 'G3', 'G4', 'G5']
# C1 = np.array([.049, .052, .054, .051])
# df = pd.read_csv('Gen_6,25.csv')
# df = df.set_index('Pocillo')
# first = 'B 2'
# last = 'B 5'
# C1 = df.loc[first:last, 'Absorbancia en bruto']
# print(C1, C1.mean(), C1.std())
# men_means = [20, 34, 30, 35, 27]
# women_means = [25, 32, 34, 20, 25]

# x = np.arange(len(labels))  # the label locations
# width = 0.35  # the width of the bars

# fig, ax = plt.subplots()
# rects1 = ax.bar(x - width / 2, men_means, width, label='Men')
# rects2 = ax.bar(x + width / 2, women_means, width, label='Women')

# # Add some text for labels, title and custom x-axis tick labels, etc.
# ax.set_ylabel('Scores')
# ax.set_title('Scores by group and gender')
# ax.set_xticks(x)
# ax.set_xticklabels(labels)
# ax.legend()


# def autolabel(rects):
    # """Attach a text label above each bar in *rects*, displaying its height."""
    # for rect in rects:
        # height = rect.get_height()
        # ax.annotate('{}'.format(height),
                    # xy=(rect.get_x() + rect.get_width() / 2, height),
                    # xytext=(0, 3),  # 3 points vertical offset
                    # textcoords="offset points",
                    # ha='center', va='bottom')


# autolabel(rects1)
# autolabel(rects2)

# fig.tight_layout()

# plt.show()

