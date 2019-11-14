#################################
############ Authors ############
# ---# Amine_ID / Hamza_BEN #---#
#################################

import csv
import os
import sys
import re

import itertools
import Lab1
from Lab1 import Point, Segment
import numpy as np
import pandas as pd
import pyqtgraph as pg
import pyqtgraph.exporters
from PyQt5 import QtWidgets, uic, QtGui, QtCore
import sqlite3
import time

connection = None
process = None
df = []
df_filtered = []
plotted = []
vLine = None
hLine = None
Enabled_RTP = False
Enabled_MT = False
Enabled_ZM = False
Enabled_IM = False
Enabled_WM = False
img = None
id_str = ''
Gate_item = None
cGate = Segment()
items = None
Intersection_arr = []
newItems = None
added = False
Gated = False
ls = []
X_dict = {}
Y_dict = {}
ids = []

csv.register_dialect('StdCSV', delimiter=';', quoting=csv.QUOTE_NONE, skipinitialspace=True)


def velocity(pt1: Point, pt2: Point):
    import math
    return math.sqrt((pt1.x - pt2.x)**2 + (pt1.y - pt2.y)**2)


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        uic.loadUi('main1.ui', self)

        self.img = pg.ImageItem()
        global vLine
        vLine = pg.InfiniteLine(angle=90, movable=False)
        global hLine
        hLine = pg.InfiniteLine(angle=0, movable=False)
        self.graphPlot.addItem(vLine, ignoreBounds=True)
        self.graphPlot.addItem(hLine, ignoreBounds=True)
        self.graphPlot.setBackground('w')
        self.graphPlot.showGrid(x=True, y=True)
        self.graphPlot.setMouseEnabled(x=False, y=False)
        self.graphPlot.setMenuEnabled(False)
        self.graphPlot.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

        self.ids.setStyleSheet("QComboBox { combobox-popup: 0; }")
        self.pBar = QtWidgets.QProgressBar()
        self.statusBar().addPermanentWidget(self.pBar)
        self.pBar.setGeometry(320, 643, 20, 240)
        self.pBar.hide()
        self.statusBar().showMessage('Ready.')

        # Handlers-connection
        self.graphPlot.customContextMenuRequested.connect(self.customContextMenu)
        self.importCsv.triggered.connect(self.onClicked_Import)
        self.actionPoint_csv.triggered.connect(self.ExportCSV)
        self.actionGraph_png.triggered.connect(self.ExportIMG)
        self.action_Exit.triggered.connect(self.onClicked_Exit)
        self.plotBtn.clicked.connect(self.onCLicked_Plot)
        self.plotBtn.setEnabled(False)
        self.plotAllBtn.clicked.connect(self.cmdPlotAll)
        self.tb_id.currentTextChanged.connect(self.onChangedVal)
        self.Gate_P1_x.textChanged.connect(self.onTextChanged)
        self.Gate_P1_y.textChanged.connect(self.onTextChanged)
        self.Gate_P2_x.textChanged.connect(self.onTextChanged)
        self.Gate_P2_y.textChanged.connect(self.onTextChanged)
        self.graphPlot.scene().sigMouseMoved.connect(self.mouseMoved)
        self.cmdVal.clicked.connect(self.onCLickedVal)
        self.dateTimeEdit.setEnabled(Enabled_RTP)
        self.dateTimeEdit.stepBy(15)
        self.reelTimeCheck.stateChanged.connect(self.Enable_RealTimePlot)
        self.dateTimeEdit.dateTimeChanged.connect(self.ReelTimePlot)

    # Handlers
    def cmdPlotAll(self):
        global plotted
        obj = self.sender()
        if obj.text() == "Plot all":
            obj.setText("Delete all")
            self.graphPlot.clear()
            self.graphPlot.addItem(vLine, ignoreBounds=True)
            self.graphPlot.addItem(hLine, ignoreBounds=True)
            plotted = []
            cursor = connection.cursor()

            for id in ids:
                id_ = [str(s) for s in id[0] if s.isdigit()]
                id_ = str("".join(id_))
                self.statusBar().showMessage('Plotting ID: ' + str(id[0]) + ' ...')
                X = []
                Y = []
                color = list(np.random.choice(range(256), size=3))
                pen = pg.mkPen(color=color, width=2)
                brush = pg.mkBrush(color=color)
                cursor.execute("SELECT latitude FROM TAB WHERE id LIKE " + str(id_))
                X = cursor.fetchall()
                X = list(itertools.chain(*X))
                cursor.execute("SELECT longitude FROM TAB WHERE id LIKE " + str(id_))
                Y = cursor.fetchall()
                Y = list(itertools.chain(*Y))
                self.tb_id.addItem(str(id_))
                self.tb_id.setCurrentIndex(self.tb_id.findData(str(id_)))
                self.graphPlot.plot(X, Y, pen=pen, symbol='o', symbolSize=4, symbolBrush=brush)

            self.statusBar().showMessage('Ready.')

        elif obj.text() == "Delete all":
            obj.setText("Plot all")
            self.graphPlot.clear()
            self.graphPlot.addItem(vLine, ignoreBounds=True)
            self.graphPlot.addItem(hLine, ignoreBounds=True)
            plotted = []
            self.Table_Point.clear()
            self.tb_id.clear()
            self.Table_Point.setHorizontalHeaderLabels(ls)

    def customContextMenu(self, p):
        global added
        Menu = QtWidgets.QMenu(self.graphPlot)

        mouse_tracking = QtWidgets.QAction('Enable mouse tracking')
        mouse_tracking.setCheckable(True)
        mouse_tracking.setChecked(Enabled_MT)
        mouse_tracking.triggered.connect(self.Enable_MTracking)
        wheelie_zoom = QtWidgets.QAction('Enable wheelie zoom')
        wheelie_zoom.setCheckable(True)
        wheelie_zoom.setChecked(Enabled_ZM)
        wheelie_zoom.triggered.connect(self.Enable_WZoom)
        world_map = QtWidgets.QAction('Enable world map')
        world_map.setCheckable(True)
        world_map.setChecked(Enabled_WM)
        world_map.triggered.connect(self.Enable_WorldMap)
        sep = QtWidgets.QAction()
        sep.setSeparator(True)
        RemoveLastPlotted = QtWidgets.QAction('Remove last plotted')
        RemoveLastPlotted.triggered.connect(self.Remove_last)
        IntersectionMode = QtWidgets.QAction('Intersection mode')
        IntersectionMode.setCheckable(True)
        IntersectionMode.setChecked(Enabled_IM)
        IntersectionMode.triggered.connect(self.Intersection_Mode)
        ExportIntersection = QtWidgets.QAction('Export intersections')
        ExportIntersection.triggered.connect(self.ExportIntersection)

        Menu.addAction(wheelie_zoom)
        Menu.addAction(mouse_tracking)
        Menu.addAction(world_map)
        Menu.addAction(sep)
        Menu.addAction(RemoveLastPlotted)
        if Gated:
            Menu.addAction(IntersectionMode)

        if Enabled_IM:
            Menu.addAction(ExportIntersection)
            added = True
        else:
            if added:
                Menu.removeAction(ExportIntersection)
                added = False

        Menu.exec_(self.graphPlot.mapToGlobal(p))

    def Intersection_Mode(self):
        global Enabled_IM
        global newItems
        global items
        if Enabled_IM:
            Enabled_IM = False
            self.graphPlot.setBackground('w')
            for itm in newItems.items:
                self.graphPlot.removeItem(itm)

            for i in range(2, len(items)):
                self.graphPlot.plotItem.items[i].show()

            self.graphPlot.update()

            newItems.clear()

            self.graphPlot.getPlotItem().items[0].setPen(pg.mkPen(color=(0, 0, 0)))
            self.graphPlot.getPlotItem().items[1].setPen(pg.mkPen(color=(0, 0, 0)))
            self.graphPlot.getPlotItem().items[plotted.index('Gate') + 2].setPen(pg.mkPen(color=(0, 0, 0), width=2))
            self.graphPlot.autoRange()
        else:
            Enabled_IM = True
            newItems = pg.PlotItem()
            self.graphPlot.setBackground((0, 0, 0))
            self.graphPlot.getPlotItem().items[0].setPen(pg.mkPen(color=(255, 255, 255)))
            self.graphPlot.getPlotItem().items[1].setPen(pg.mkPen(color=(255, 255, 255)))
            self.graphPlot.getPlotItem().items[plotted.index('Gate') + 2].setPen(
                pg.mkPen(color=(255, 255, 255), width=2))
            items = self.graphPlot.getPlotItem().items
            self.pBar.show()
            self.statusBar().showMessage('Busy...')

            ind = []
            global Intersection_arr
            arr = []
            for elt in df_filtered.iterrows():
                ind.append(elt[0])

            i = 0
            while i < len(ind) - 1:
                self.pBar.setValue(int((i / len(ind)) * 100))
                Pt1 = Point(df.iloc[ind[i]].id, df.iloc[ind[i]].date, df.iloc[ind[i]].x, df.iloc[ind[i]].y)
                Pt2 = Point(df.iloc[ind[i + 1]].id, df.iloc[ind[i + 1]].date, df.iloc[ind[i + 1]].x,
                            df.iloc[ind[i + 1]].y)
                Seg1 = Segment(Pt1, Pt2)
                Seg1.IsInBoth(cGate, arr)
                i += 1

            i = 0
            tmp_list = []
            for pt in arr:
                tmp_list.append([pt.id, pt.date, pt.x, pt.y])
                self.pBar.setValue(int((i / len(arr)) * 100))
                color = list(np.random.choice(range(256), size=3))
                item_pen = pg.mkPen(color=color)
                item_brush = pg.mkBrush(color=color)
                scatterPoint = pg.ScatterPlotItem([pt.x], [pt.y], pen=item_pen, symbol='o', symbolSize=8,
                                                  symbolBrush=item_brush)
                newItems.addItem(scatterPoint)
                self.graphPlot.plot([pt.x], [pt.y], pen=item_pen, symbol='o', symbolSize=8, symbolBrush=item_brush)
                i += 1

            Intersection_arr = pd.DataFrame(tmp_list, columns=list(df))

            xRange = [min(cGate.Pt1.x, cGate.Pt2.x), max(cGate.Pt1.x, cGate.Pt2.x)]
            yRange = [min(cGate.Pt1.y, cGate.Pt2.y), max(cGate.Pt1.y, cGate.Pt2.y)]
            self.graphPlot.setRange(xRange=xRange, yRange=yRange)
            for i in range(2, len(items) - len(arr)):
                if i != plotted.index('Gate') + 2:
                    self.graphPlot.plotItem.items[i].hide()
                    self.pBar.setValue(int(i / (len(items) - 2) * 100))

            self.graphPlot.update()
            self.pBar.hide()
            self.statusBar().showMessage('Ready.')

    def Remove_last(self):
        item = self.graphPlot.getPlotItem().items[-1]
        self.graphPlot.removeItem(item)
        del plotted[-1]
        self.tb_id.clear()
        for _id in plotted:
            if _id[0] != 'Gate':
                self.tb_id.addItem(str(_id[0]))

    def Enable_RealTimePlot(self):
        global Enabled_RTP, plotted
        obj = self.sender()
        if obj.isChecked():
            Enabled_RTP = True
            self.graphPlot.clear()
            self.graphPlot.addItem(vLine, ignoreBounds=True)
            self.graphPlot.addItem(hLine, ignoreBounds=True)
            plotted = []
            self.dateTimeEdit.setEnabled(Enabled_RTP)
        else:
            Enabled_RTP = False
            self.graphPlot.clear()
            self.graphPlot.addItem(vLine, ignoreBounds=True)
            self.graphPlot.addItem(hLine, ignoreBounds=True)
            plotted = []
            self.dateTimeEdit.setEnabled(Enabled_RTP)

    def Enable_WorldMap(self):
        global Enabled_WM, img
        if Enabled_WM:
            Enabled_WM = False
            self.graphPlot.removeItem(self.img)
            self.graphPlot.autoRange()
        else:
            Enabled_WM = True
            image = QtGui.QImage("World.jpg")
            # image = image.convertToFormat(QtGui.QImage.Format_ARGB32_Premultiplied)
            imgArray = pg.imageToArray(image, copy=True)
            self.img = pg.ImageItem(imgArray)
            self.img.setImage(imgArray)
            self.img.translate(-638, 494.6)
            self.graphPlot.addItem(self.img)
            self.img.setZValue(-100)
            self.img.scale(1, -1)
            self.graphPlot.autoRange()

    def Enable_WZoom(self):
        global Enabled_ZM
        if Enabled_ZM:
            Enabled_ZM = False
            self.graphPlot.autoRange()
        else:
            Enabled_ZM = True
        self.graphPlot.setMouseEnabled(x=Enabled_ZM, y=Enabled_ZM)

    def Enable_MTracking(self):
        global Enabled_MT
        if Enabled_MT:
            Enabled_MT = False
            self.statusBar().showMessage('Ready.')
            global vLine
            vLine.setPos(0)
            global hLine
            hLine.setPos(0)
        else:
            Enabled_MT = True

    def onChangedVal(self):
        global df_filtered
        if self.tb_id.currentText() != '':
            if process == "csv":
                df_filtered = Lab1.Filtering_Data(df, self.tb_id.currentText(), mode=True)
            elif process == "sql":
                cursor = connection.cursor()
                cursor.execute("SELECT * FROM TAB WHERE id LIKE " + self.tb_id.currentText())
                df_filtered = cursor.fetchall()
            self.TableFill()

    def onCLicked_Plot(self):
        self.statusBar().showMessage('Plotting ID: ' + str(self.ids.currentText() + ' ...'))
        X = []
        Y = []
        color = list(np.random.choice(range(256), size=3))
        pen = pg.mkPen(color=color, width=2)
        brush = pg.mkBrush(color=color)
        global df_filtered, id_str, plotted
        temp = [str(s) for s in self.ids.currentText() if s.isdigit()]
        id_str = str("".join(temp))
        if process == "csv":
            X, Y, df_filtered = Lab1.Filtering_Data(df, id_str)
        elif process == "sql":
            cursor = connection.cursor()
            cursor.execute("SELECT latitude FROM TAB WHERE id LIKE " + id_str)
            X = cursor.fetchall()
            X = list(itertools.chain(*X))
            cursor.execute("SELECT longitude FROM TAB WHERE id LIKE " + id_str)
            Y = cursor.fetchall()
            Y = list(itertools.chain(*Y))

        plotted.append(id_str)

        self.tb_id.addItem(id_str)
        self.tb_id.setCurrentIndex(self.tb_id.findData(id_str))
        self.graphPlot.plot(X, Y, pen=pen, symbol='o', symbolSize=4, symbolBrush=brush)
        self.statusBar().showMessage('Ready.')

    def onCLickedVal(self):
        global Gated
        X_pts = np.array([self.Gate_P1_x.text(), self.Gate_P2_x.text()]).astype('float')
        Y_pts = np.array([self.Gate_P1_y.text(), self.Gate_P2_y.text()]).astype('float')
        Gate_pen = pg.mkPen(color=(0, 0, 0), width=2)
        global Gate_item
        if Gate_item is None:
            Gate_item = pg.PlotDataItem(X_pts, Y_pts)
            Gate_item.setPen(Gate_pen)
            self.graphPlot.addItem(Gate_item)
            plotted.append('Gate')
        else:
            Gate_item.setData(X_pts, Y_pts)
            Gate_item.setPen(Gate_pen)
            self.graphPlot.removeItem(Gate_item)
            plotted.remove('Gate')
            self.graphPlot.addItem(Gate_item)
            plotted.append('Gate')
        global cGate
        cGate.setPoints(Point(x_=X_pts[0], y_=Y_pts[0]), Point(x_=X_pts[1], y_=Y_pts[1]))
        Gated = True

    def onClicked_Import(self):
        global ls
        self.importCSV()
        self.statusBar().showMessage('Generating tabs ...')
        if process == "csv":
            self.Table_Point.setColumnCount(len(list(df.columns)) + 1)
            ls = ['iloc_index'] + list(df.columns)
            self.Table_Point.setColumnHidden(0, True)
        elif process == "sql":
            cursor = connection.cursor()
            cursor.execute("PRAGMA table_info(TAB)")
            clmns = cursor.fetchall()
            for clmn in clmns:
                ls.append(clmn[1])

            self.Table_Point.setColumnCount(len(ls))

            cursor.execute("SELECT MIN(date) FROM TAB")
            minDate = cursor.fetchall()
            minDate = minDate[0][0]

            cursor.execute("SELECT MAX(date) FROM TAB")
            maxDate = cursor.fetchall()
            maxDate = maxDate[0][0]

            self.dateTimeEdit.setMinimumDateTime(QtCore.QDateTime.fromString(minDate, "dd/MM/yyyy hh:mm"))
            self.dateTimeEdit.setMaximumDateTime(QtCore.QDateTime.fromString(maxDate, "dd/MM/yyyy hh:mm"))

        self.Table_Point.setHorizontalHeaderLabels(ls)
        self.plotBtn.setEnabled(True)
        self.statusBar().showMessage('Ready.')

    def onClicked_Exit(self):
        """
        Static
        """
        QtWidgets.QApplication.quit()

    def onTextChanged(self):
        obj = self.sender()
        pal = QtGui.QPalette()
        if obj is not None:
            if not str(obj.text()).lstrip('-+').isnumeric():
                pal.setColor(QtGui.QPalette.Base, QtCore.Qt.red)
                pal.setColor(QtGui.QPalette.WindowText, QtCore.Qt.white)
                obj.setStyleSheet("background-color: red;")
                self.cmdVal.setEnabled(False)
            else:
                pal.setColor(QtGui.QPalette.Base, QtCore.Qt.white)
                pal.setColor(QtGui.QPalette.Text, QtCore.Qt.black)
                obj.setStyleSheet("background-color: white;")
                self.cmdVal.setEnabled(True)

    # Not Handlers
    def ReelTimePlot(self):
        if Enabled_RTP:
            self.statusBar().showMessage('Real time plotting ... (this may take a while)')
            global X_dict, Y_dict
            obj = self.sender()
            date = obj.text()
            cursor = connection.cursor()
            minDate = obj.minimumDateTime()
            minDate = minDate.toString('dd/MM/yyyy hh:mm')

            self.statusBar().showMessage('Real time plotting ... (retrieving coordinates)')
            i = 0
            for id in sorted(ids):
                self.pBar.setValue(int((i / len(ids)) * 100))
                cursor.execute(
                    "SELECT latitude FROM TAB WHERE date BETWEEN " + "'{}'".format(minDate) + " AND " + "'{}'".format(
                        date) + " AND id LIKE " + str("".join([str(s) for s in id[0] if s.isdigit()])))
                tmp = cursor.fetchall()
                X_dict[id[0]] = list(itertools.chain(*tmp))
                cursor.execute(
                    "SELECT longitude FROM TAB WHERE date BETWEEN " + "'{}'".format(minDate) + " AND " + "'{}'".format(
                        date) + " AND id LIKE " + str("".join([str(s) for s in id[0] if s.isdigit()])))
                tmp = cursor.fetchall()
                Y_dict[id[0]] = list(itertools.chain(*tmp))
                i += 1

            if len(self.graphPlot.getPlotItem().items) == 2:
                self.statusBar().showMessage('Real time plotting ... (plotting targets)')
                i = 0
                for id in sorted(ids):
                    self.pBar.setValue(int((i / len(ids)) * 100))
                    color = list(np.random.choice(range(256), size=3))
                    pen = pg.mkPen(color=color, width=2)
                    brush = pg.mkBrush(color=color)
                    self.graphPlot.plot(X_dict[id[0]], Y_dict[id[0]], pen=pen, symbol='o', symbolSize=4, symbolBrush=brush)
                    plotted.append(str("".join([str(s) for s in id[0] if s.isdigit()])))
                    i += 1

            else:
                self.statusBar().showMessage('Real time plotting ... (updating targets)')
                for id in sorted(ids):
                    items = self.graphPlot.getPlotItem().items
                    for i in range(2, len(items)):
                        self.pBar.setValue(int((i-2) / (len(items)-2) * 100))
                        items[i].setData(X_dict[ids[i - 2][0]], Y_dict[ids[i - 2][0]])

                    self.graphPlot.update()

            self.statusBar().showMessage('Ready.')

    def TableFill(self):
        global df_filtered
        numRows = self.Table_Point.rowCount()
        if numRows > 0:
            self.Table_Point.clearContents()
            self.Table_Point.setRowCount(0)
            numRows = 0

        if process == "csv":
            for i in df_filtered.iterrows():
                self.Table_Point.insertRow(numRows)
                self.Table_Point.setItem(numRows, 0, QtWidgets.QTableWidgetItem(str(i[0])))
                item = QtWidgets.QTableWidgetItem(str(df.iloc[i[0]].id))
                item.setFlags(QtCore.Qt.ItemIsEnabled)
                self.Table_Point.setItem(numRows, 1, item)
                self.Table_Point.setItem(numRows, 2, QtWidgets.QTableWidgetItem(str(df.iloc[i[0]].date)))
                self.Table_Point.setItem(numRows, 3, QtWidgets.QTableWidgetItem(str(df.iloc[i[0]].x)))
                self.Table_Point.setItem(numRows, 4, QtWidgets.QTableWidgetItem(str(df.iloc[i[0]].y)))
                numRows = self.Table_Point.rowCount()
        elif process == "sql":
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM TAB WHERE id LIKE " + str(self.tb_id.currentText()))
            df_filtered = cursor.fetchall()
            for i in df_filtered:
                self.Table_Point.insertRow(numRows)
                item = QtWidgets.QTableWidgetItem(str(i[0]))
                item.setFlags(QtCore.Qt.ItemIsEnabled)
                self.Table_Point.setItem(numRows, 0, item)
                self.Table_Point.setItem(numRows, 1, QtWidgets.QTableWidgetItem(str(i[1])))
                self.Table_Point.setItem(numRows, 2, QtWidgets.QTableWidgetItem(str(i[2])))
                self.Table_Point.setItem(numRows, 3, QtWidgets.QTableWidgetItem(str(i[3])))
                numRows = self.Table_Point.rowCount()

    def ExportIMG(self):
        file = "ECG_%d.png" % time.time()
        exp = pg.exporters.ImageExporter(self.graphPlot.plotItem)
        exp.parameters()['width'] = 1000
        exp.export(file)

    def ExportIntersection(self):
        file = 'points for intersection.csv'
        with open(file, 'w') as writingF:
            csvw = csv.writer(writingF, dialect='StdCSV')
            for row in Intersection_arr:
                csvw.writerow([row.id, row.date, row.x, row.y])

    def ExportCSV(self):
        if self.tb_id.currentText() == '':
            QtWidgets.QMessageBox.warning(self, 'Error retrieving ID', 'Please select an ID.', QtWidgets.QMessageBox.Ok)
            self.tb_id.setFocus()
        else:
            file = 'points for id(' + str(self.tb_id.currentText()) + ').csv'
            with open(file, 'w') as writingF:
                csvw = csv.writer(writingF, dialect='StdCSV')
                for row in range(0, self.Table_Point.rowCount()):
                    line = []
                    for col in range(0, self.Table_Point.columnCount()):
                        cell = self.Table_Point.item(row, col).text().strip()
                        line.append(cell)
                    csvw.writerow(line)

    def importCSV(self):
        separation = None
        file = QtWidgets.QFileDialog.getOpenFileName(QtWidgets.QFileDialog(),
                                                     'Select dataset',
                                                     os.getcwd(),
                                                     "Comma-separated values (*.csv) ;; SQlite database (*.db *.sdb *.sqlite *.db3 *.s3db *.sqlite3 *.db2 *.s2db *.sqlite2 *.sl2)")
        self.statusBar().showMessage('Importing ' + str(file[0]) + ', please wait...')
        global df, process, connection, ids
        if file[0].endswith(".csv"):
            process = 'csv'
            sep, ok = QtWidgets.QInputDialog.getText(self, 'CSV separator', 'Enter separator:')
            if ok:
                separation = sep
            else:
                separation = ''

            if separation == '':
                with open(file[0]) as csvFile:
                    delimiter = csv.Sniffer().sniff(csvFile.read(1024)).delimiter
            else:
                delimiter = separation

            df = pd.read_csv(file[0], sep=delimiter)
            ids = Lab1.getIDs(df)

            for id in sorted(ids):
                self.ids.addItem(str(id))

        elif file[0].endswith(".db") or file[0].endswith(".sdb") or file[0].endswith(".sqlite") or file[0].endswith(
                ".db3") or file[0].endswith(".s3db") or file[0].endswith(".sqlite3") or file[0].endswith(".db2") or \
                file[0].endswith(".s2db") or file[0].endswith(".sqlite2") or file[0].endswith(".sl2"):
            connection = None
            try:
                connection = sqlite3.connect(file[0])
            except Error as e:
                print(e)
            process = 'sql'
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM TAB")
            df = cursor.fetchall()
            cursor.execute("SELECT DISTINCT nom FROM TAB2")
            ids = cursor.fetchall()

            for id in sorted(ids):
                self.ids.addItem(str(id[0]))

    def mouseMoved(self, evt):
        global vLine, hLine
        if Enabled_MT:
            pos = evt
            vb = self.graphPlot.plotItem.vb
            if self.graphPlot.sceneBoundingRect().contains(pos):
                dist = 0
                mousePoint = vb.mapSceneToView(pos)
                if process == "csv":
                    if Enabled_IM:
                        nearest_list = Intersection_arr.iloc[
                            (Intersection_arr.x - float(mousePoint.x())).abs().argsort()[:2]]
                        dataframe = Intersection_arr
                    else:
                        nearest_list = df_filtered.iloc[
                            (df_filtered.x - float(mousePoint.x())).abs().argsort()[:2]]
                        dataframe = df

                    for row in nearest_list.iterrows():
                        if dist == 0:
                            dist = abs(dataframe.iloc[row[0]].x - mousePoint.x())
                            r = row[0]
                        else:
                            tmp = abs(dataframe.iloc[row[0]].x - mousePoint.x())
                            if tmp < dist:
                                r = row[0]

                    x = dataframe.iloc[r].x
                    y = dataframe.iloc[r].y
                    pt_id = dataframe.iloc[r].id

                elif process == "sql":
                    cursor = connection.cursor()
                    if Enabled_RTP:
                        minDate = self.dateTimeEdit.minimumDateTime()
                        minDate = minDate.toString("dd/MM/yyyy hh:mm")
                        date = self.dateTimeEdit.text()

                        cursor.execute("SELECT latitude FROM TAB WHERE date BETWEEN " + "'{}'".format(minDate) + " AND " + "'{}'".format(date) +
                                       " ORDER BY ABS(" + str(mousePoint.x()) + "- latitude" + ")" + " ASC LIMIT 1")
                        x = cursor.fetchall()
                        x = x[0][0]

                        cursor.execute("SELECT longitude FROM TAB WHERE latitude LIKE " + str(x))
                        y = cursor.fetchall()
                        y = y[0][0]

                        cursor.execute("SELECT id FROM TAB WHERE latitude LIKE " + str(x) + " AND longitude LIKE " + str(y))
                        plt_id = cursor.fetchall()
                        plt_id = plt_id[0][0]

                        cursor.execute("SELECT nom FROM TAB2 WHERE id LIKE " + str(plt_id))
                        plt_id = cursor.fetchall()
                        plt_id = plt_id[0][0]

                        self.statusBar().showMessage('x:' + str(x) + ', y:' + str(y) + ', ID: ' + str(plt_id))

                        vLine.setPos(float(x))
                        hLine.setPos(float(y))

                    else:
                        plt = str("".join([str(s) for s in self.ids.currentText() if s.isdigit()]))
                        if plt in plotted:
                            cursor.execute("SELECT latitude FROM TAB WHERE id LIKE " + plt + " ORDER BY ABS(" +
                                           str(mousePoint.x()) + "- latitude" + ")" + " ASC LIMIT 1")

                            x = cursor.fetchall()

                            cursor.execute("SELECT longitude FROM TAB WHERE id LIKE " + plt + " AND latitude LIKE " + str(x[0][0]))

                            y = cursor.fetchall()
                            if len(y) > 0 and len(x) > 0:
                                y = y[0][0]
                                x = x[0][0]

                                self.statusBar().showMessage('x:' + str(x) + ', y:' + str(y) + ', ID: mobile ' + str(plt))

                                vLine.setPos(float(x))
                                hLine.setPos(float(y))

                        else:
                            self.statusBar().showMessage(
                                "ID " + "'{}'".format(self.ids.currentText()) + " not plotted yet.")


def main():
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
