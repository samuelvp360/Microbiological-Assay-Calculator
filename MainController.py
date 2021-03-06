#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from datetime import datetime
from PyQt5 import QtCore as qtc
# from PyQt5 import QtGui as qtg
from PyQt5 import QtWidgets as qtw
from PyQt5 import uic
# import pandas as pd
import numpy as np
from Models import AssaysModel, SamplesModel
from DB.AssaysDB import MyZODB
import matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from WellProcessor import WellProcessor
from Assay import Assay

matplotlib.use('Qt5Agg')


class PlotCanvas(FigureCanvasQTAgg):
    """
    docstring
    """
    def __init__(self, parent=None):
        self.fig = Figure(
            figsize=(6, 4), dpi=100, facecolor='#2d2a2e', tight_layout=True
        )
        self.ax = self.fig.add_subplot(111)
        super().__init__(self.fig)


class MainWindow(qtw.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('Views/uiMainWindow.ui', self)
        self.database = MyZODB()
        self.canvas = PlotCanvas(self)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.uiToolbarLayout.addWidget(self.toolbar)
        self.uiPlotLayout.addWidget(self.canvas)
        self.assaysList = self.LoadAssays()
        self.assaysToRemove = []
        self.model = AssaysModel(self.assaysList)
        self.uiAssaysTableView.setModel(self.model)
        self.uiAssaysTableView.resizeColumnsToContents()
        self.uiAssaysTableView.resizeRowsToContents()
        self.selectedAssay = None
        self.selectedSamples = None
        # ---------------- SIGNALS ---------------
        self.uiCommitButton.clicked.connect(self.StoreChanges)
        self.uiAddAssayButton.clicked.connect(self.AddAssay)
        self.uiDelAssayButton.clicked.connect(self.RemoveAssay)
        self.uiAddSampleButton.clicked.connect(self.AddSample)
        self.uiDelSampleButton.clicked.connect(self.RemoveSample)
        self.uiDiscardButton.clicked.connect(self.DiscardChanges)
        self.uiAssaysTableView.selectionModel().selectionChanged.connect(self.SetSelectedAssay)

    def Plot(self):
        assay = self.assaysList[self.selectedAssay]
        samples = [assay.samples[i] for i in self.selectedSamples]
        n = len(samples)
        x = np.arange(len(assay.conc))
        limit = 0.4
        width = 2 * limit / n
        if n == 1:
            factor = np.zeros(1)
        else:
            factor = np.linspace(-limit + width / 2, limit - width / 2, n)
            print(factor)
        self.canvas.ax.clear()
        for i, sample in enumerate(samples):
            mean = sample['Inhibition'].loc['Mean']
            std = sample['Inhibition'].loc['Std']
            self.canvas.ax.bar(x + factor[i], mean, width, label=sample['Name'])
        self.canvas.ax.set_title(assay.name, color='#ae81ff')
        self.canvas.ax.set_xlabel(u'Concentrations (\u00B5g/mL)', color='#f92672')
        self.canvas.ax.set_ylabel('%Inhibition', color='#f92672')
        self.canvas.ax.set_xticks(x)
        self.canvas.ax.set_xticklabels(assay.conc)
        self.canvas.ax.tick_params(axis='x', colors='#66d9ef')
        self.canvas.ax.tick_params(axis='y', colors='#66d9ef')
        self.canvas.ax.legend()
        self.canvas.draw()

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

    def LoadAssays(self):
        DB = self.database.FetchDB()
        if not len(DB):
            return []
        else:
            assayNames = DB.keys()
            return [DB.get(i) for i in assayNames]

    def SetSelectedAssay(self):
        indexes = self.uiAssaysTableView.selectedIndexes()
        if indexes:
            self.selectedAssay = indexes[0].row()
            assay = self.assaysList[self.selectedAssay]
            self.samplesModel = SamplesModel(assay.samples, assay.conc)
            self.uiSamplesTableView.setModel(self.samplesModel)
            self.uiSamplesTableView.resizeColumnsToContents()
            self.samplesModel.layoutChanged.emit()
            self.uiSamplesTableView.selectionModel().selectionChanged.connect(self.SetSelectedSamples)
        else:
            self.selectedAssay = None

    def SetSelectedSamples(self):
        indexes = self.uiSamplesTableView.selectedIndexes()
        if indexes:
            self.selectedSamples = tuple(set([i.row() for i in indexes]))
            self.Plot()
        else:
            self.selectedSamples = None

    def SetConcentrations(self):
        value, ok = qtw.QInputDialog.getText(
            self, 'Concentrations', 'Please enter the highest concentration'
        )
        if ok:
            try:
                # el número 6 se puede cambiar según sea el número de
                # diluciones seriadas
                conc = [str(float(value.replace(',', '.')) / 2 ** i) for i in range(6)]
                return conc
            except ValueError:
                qtw.QMessageBox.warning(
                    self, 'Not a valid number!',
                    'You have not enter a valid number, please try again'
                )
                return False

    def AddAssay(self):
        items = ('MIC', 'MTT')
        typeOfAssay, ok = qtw.QInputDialog.getItem(
            self, 'Type of Assay', 'Choose the type of assay to add',
            items, 0, False
        )
        name = self.SetAssayName()
        conc = self.SetConcentrations()
        while not conc:
            conc = self.SetConcentrations()
        date = datetime.now()
        assay = Assay(typeOfAssay, name, conc, date)
        self.assaysList.append(assay)
        self.model.layoutChanged.emit()
        self.uiAssaysTableView.resizeColumnsToContents()
        self.uiAssaysTableView.resizeRowsToContents()

    def AddSample(self):
        items = ['1', '2', '3', '4']
        if self.selectedAssay is not None:
            numOfSamples, ok1 = qtw.QInputDialog.getItem(
                self, 'Number of Samples', 'Choose the number of samples per plate',
                items, 0, False
            )
            if int(numOfSamples) == 3:
                del items[3]
            elif int(numOfSamples) == 4:
                del items[2:]
            replicas, ok2 = qtw.QInputDialog.getItem(
                self, 'Number of Samples', 'Choose the number of replicas',
                items, 0, False
            )
            if ok1 and ok2:
                self.wellProcessor = WellProcessor(
                    self.assaysList[self.selectedAssay].name,
                    self.assaysList[self.selectedAssay].conc,
                    int(numOfSamples), int(replicas)
                )
                self.wellProcessor.submitted.connect(self.SampleProcessor)
                self.wellProcessor.show()
            else:
                return False
        else:
            qtw.QMessageBox.warning(
                self, 'No Assay Selection',
                'You have not selected an assay, please choose one assay before adding a sample'
            )

    def RemoveAssay(self):
        if self.selectedAssay is not None:
            self.assaysToRemove.append(self.assaysList[self.selectedAssay].name)
            if self.assaysList[self.selectedAssay].stored:
                self.database.RemoveAssay(self.assaysList[self.selectedAssay].name)
            del self.assaysList[self.selectedAssay]
            self.selectedAssay = self.selectedAssay - 1 if self.selectedAssay - 1 >= 0 else 0
            if len(self.assaysList) > 0:
                index = self.uiAssaysTableView.model().index(self.selectedAssay, 0, qtc.QModelIndex())
                self.uiAssaysTableView.setCurrentIndex(index)
            self.model.layoutChanged.emit()

    def RemoveSample(self):
        if self.selectedAssay is not None and self.selectedSamples is not None:
            self.assaysList[self.selectedAssay].RemoveSample(self.selectedSamples)
            self.selectedSamples = [self.selectedSamples[0] - 1 if self.selectedSamples[0] - 1 >= 0 else 0]
            if len(self.assaysList[self.selectedAssay].samples) > 0:
                index = self.uiSamplesTableView.model().index(self.selectedSamples[0], 0, qtc.QModelIndex())
                self.uiSamplesTableView.setCurrentIndex(index)
            self.model.layoutChanged.emit()
            assay = self.assaysList[self.selectedAssay]
            self.samplesModel = SamplesModel(assay.samples, assay.conc)
            self.uiSamplesTableView.setModel(self.samplesModel)
            self.samplesModel.layoutChanged.emit()

    @qtc.pyqtSlot(list, list, list, object, object)
    def SampleProcessor(self, samples, sampleNames, samplesPositions, Tf, T0):
        assay = self.assaysList[self.selectedAssay]
        assay.StoreSamples(samples, sampleNames, samplesPositions, Tf, T0)
        self.samplesModel = SamplesModel(assay.samples, assay.conc)
        self.uiSamplesTableView.setModel(self.samplesModel)
        self.samplesModel.layoutChanged.emit()
        self.uiSamplesTableView.resizeColumnsToContents()

    def SetAssayName(self):
        text, ok = qtw.QInputDialog.getText(
            self, 'Assay Name', 'Please enter the name of the assay'
        )
        if ok:
            return text

    def TrackChanges(self):
        assaysToStore = [index for index, assay in enumerate(self.assaysList) if not assay.stored]
        assaysToUpdate = [index for index, assay in enumerate(self.assaysList) if assay._p_changed]
        assaysToRemove = self.assaysToRemove
        return assaysToStore, assaysToUpdate, assaysToRemove

    def StoreChanges(self):
        assaysToStore, assaysToUpdate, assaysToRemove = self.TrackChanges()
        toStore = len(assaysToStore)
        toUpdate = len(assaysToUpdate)
        toRemove = len(assaysToRemove)
        message = qtw.QMessageBox()
        message.setWindowTitle('Changes to save')
        message.setStandardButtons(qtw.QMessageBox.Ok | qtw.QMessageBox.Cancel)
        text = []
        if toStore > 0:
            text1 = ['\nTo Store: ' + self.assaysList[i].name for i in assaysToStore]
            text.extend(text1)
        if toUpdate > 0:
            text2 = ['\nTo Update: ' + self.assaysList[i].name for i in assaysToUpdate]
            text.extend(text2)
        if toRemove > 0:
            text3 = ['\nTo Remove: ' + name for name in assaysToRemove]
            text.extend(text3)
        if toStore + toUpdate + toRemove > 0:
            message.setText(
                'The following assays will be stored, removed or updated:{}'.format(''.join(text))
            )
            returnValue = message.exec()
            if returnValue == qtw.QMessageBox.Ok:
                for index in assaysToStore:
                    self.database.StoreAssay(self.assaysList[index])
                if len(assaysToStore) == 0 and len(assaysToUpdate) > 0:
                    self.database.Commit()
                if len(assaysToStore) == 0 and len(assaysToRemove) > 0:
                    self.database.Commit()
            else:
                self.database.Abort()
        else:
            message2 = qtw.QMessageBox()
            message2.setText('There are no changes to be saved')
            message2.exec()

    def DiscardChanges(self):
        assay = self.assaysList[self.selectedAssay]
        self.database.Abort()
        self.LoadAssays()
        self.model.layoutChanged.emit()
        self.samplesModel = SamplesModel(assay.samples, assay.conc)
        self.uiSamplesTableView.setModel(self.samplesModel)
        self.samplesModel.layoutChanged.emit()
        self.uiAssaysTableView.resizeColumnsToContents()
        self.uiSamplesTableView.resizeColumnsToContents()

    def closeEvent(self, event):
        try:
            assaysToStore, assaysToUpdate, assaysToRemove = self.TrackChanges()
            toStore = len(assaysToStore)
            toUpdate = len(assaysToUpdate)
            toRemove = len(assaysToRemove)
            if toStore + toUpdate + toRemove > 0:
                reply = qtw.QMessageBox.question(
                    self, 'Window Close',
                    'Some changes have not been stored yet, do you want to save them',
                    qtw.QMessageBox.Yes | qtw.QMessageBox.No | qtw.QMessageBox.Cancel,
                    qtw.QMessageBox.No
                )
                if reply == qtw.QMessageBox.Yes:
                    self.StoreChanges()
                    self.database.Close()
                    event.accept()
                    print('Window closed')
                elif reply == qtw.QMessageBox.No:
                    self.database.Abort()
                    self.database.Close()
                    event.accept()
                    print('Window closed')
                else:
                    event.ignore()
            else:
                self.database.Close()
                event.accept()
        except AttributeError:
            self.database.Close()
            event.accept()


if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


# TODO:
    # 1. Implementar el botón Discard changes
    # 2. La selección múltiple de muestras para poder borrarlas en combo
    # 3. 

