#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
from PyQt5 import QtWidgets as qtw
from PyQt5 import uic
from Models import WellDataModel


class WellProcessor(qtw.QWidget):
    def __init__(self, conc):
        super().__init__()
        uic.loadUi('uiWellProcessor.ui', self)
        data = pd.DataFrame(np.zeros((10, 6), dtype=float), columns=conc)
        # concentrations = [self.uiC1Label, self.uiC2Label, self.uiC3Label, self.uiC4Label]
        # [i.setText(j + ' ug/mL') for i, j in zip(concentrations, conc)]
        self.model = WellDataModel(data)
        self.uiWellTableView.setModel(self.model)
        self.model.layoutChanged.emit()
