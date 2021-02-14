#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.gridspec import GridSpec
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


class PlotCanvas(FigureCanvasQTAgg):
    """
    docstring
    """
    def __init__(self, parent=None):
        self.fig = Figure(figsize=(6, 4), dpi=100, facecolor='#2d2a2e')
        self.grid = GridSpec(17, 1, left=0.1, bottom=0.15, right=0.94, top=0.94, wspace=0.3, hspace=0.3)
        self.ax = self.fig.add_subplot(self.grid[0:, 0])
        self.ax2 = self.ax.twinx()
        super().__init__(self.fig)


