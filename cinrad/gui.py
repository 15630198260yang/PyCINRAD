# -*- coding: utf-8 -*-

from cinrad.io import *
from cinrad.visualize.ppi import norm_plot, cmap_plot
from cinrad.visualize.basicfunc import add_shp

from PyQt5 import QtCore, QtGui, QtWidgets
import matplotlib.pyplot as plt
#matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import cartopy.crs as ccrs

_translate = QtCore.QCoreApplication.translate

class MyMplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=5, dpi=70):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = plt.axes(projection=ccrs.PlateCarree())
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self, QtWidgets.QSizePolicy.Expanding,
                                   QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

class Ui_MainWindow(object):

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(863, 635)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.graphicsView = QtWidgets.QGraphicsView(self.centralwidget)
        self.graphicsView.setGeometry(QtCore.QRect(150, 10, 701, 571))
        self.graphicsView.setObjectName("graphicsView")
        self.graphicsView.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.button_group = QtWidgets.QButtonGroup()
        self.plainTextEdit = QtWidgets.QPlainTextEdit(self.centralwidget)
        self.plainTextEdit.setGeometry(QtCore.QRect(10, 30, 81, 31))
        self.plainTextEdit.setObjectName("plainTextEdit")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(10, 10, 72, 15))
        self.label.setObjectName("label")
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(100, 30, 41, 31))
        self.pushButton.setObjectName("pushButton")
        self.pushButton.clicked.connect(self.on_click_update_radius)
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(10, 460, 131, 121))
        self.label_2.setObjectName("label_2")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 863, 26))
        self.menubar.setObjectName("menubar")
        self.menu = QtWidgets.QMenu(self.menubar)
        self.menu.setObjectName("menu")
        self.menu_2 = QtWidgets.QMenu(self.menubar)
        self.menu_2.setObjectName("menu_2")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionOpen = QtWidgets.QAction(MainWindow, triggered=self._open)
        self.actionOpen.setObjectName("actionOpen")
        self.actionClose = QtWidgets.QAction(MainWindow)
        self.actionClose.setObjectName("actionClose")
        self.actionBase_Reflectivity = QtWidgets.QAction(MainWindow)
        self.actionBase_Reflectivity.setObjectName("actionBase_Reflectivity")
        self.actionBase_Velocity = QtWidgets.QAction(MainWindow)
        self.actionBase_Velocity.setObjectName("actionBase_Velocity")
        self.menu.addAction(self.actionOpen)
        self.menu.addAction(self.actionClose)
        self.menu_2.addAction(self.actionBase_Reflectivity)
        self.menu_2.addAction(self.actionBase_Velocity)
        self.menubar.addAction(self.menu.menuAction())
        self.menubar.addAction(self.menu_2.menuAction())
        self.set_radio_button(range(12))
        l = QtWidgets.QVBoxLayout(self.graphicsView)
        self.canvas = MyMplCanvas(self.centralwidget, width=5, height=4, dpi=100)
        self.mpl_toolbar = NavigationToolbar(self.canvas, self.centralwidget)
        l.addWidget(self.canvas)
        l.addWidget(self.mpl_toolbar)
        self.retranslateUi(MainWindow)
        #QtCore.QMetaObject.connectSlotsByName(MainWindow)
        self.drange = 230
        self.dtype = 'REF'

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "CINRAD Radar Display"))
        self.label.setText(_translate("MainWindow", "绘图半径"))
        self.pushButton.setText(_translate("MainWindow", "更新"))
        self.label_2.setText(_translate("MainWindow", "Geoinfo"))
        self.menu.setTitle(_translate("MainWindow", "文件"))
        self.menu_2.setTitle(_translate("MainWindow", "数据"))
        self.actionOpen.setText(_translate("MainWindow", "打开"))
        self.actionClose.setText(_translate("MainWindow", "关闭"))
        self.actionBase_Reflectivity.setText(_translate("MainWindow", "Base Reflectivity"))
        self.actionBase_Velocity.setText(_translate("MainWindow", "Base Velocity"))

    def _open(self):
        fp = QtWidgets.QFileDialog.getOpenFileName()[0]
        try:
            self.cinrad = CinradReader(fp)
        except Exception:
            try:
                self.cinrad = StandardData(fp)
            except Exception:
                self.cinrad = NexradL2Data(fp)
        for i in self.radio_button_list[len(self.cinrad.el):]:
            i.setEnabled(False)

    def close(self):
        if hasattr(self, 'cinrad'):
            del self.cinrad
        for i in self.radio_button_list:
            i.setEnabled(True)

    def set_radio_button(self, elevation_list):
        self.radio_button_list = list()
        for idx in elevation_list:
            radioButton = QtWidgets.QRadioButton("Tilt {}".format(idx + 1), self.centralwidget)
            #radioButton.move(10, 70 + 20 * idx)
            radioButton.setGeometry(QtCore.QRect(10, 70 + 20 * idx, 115, 19))
            radioButton.setText(_translate("MainWindow", "Tilt {}".format(idx + 1)))
            radioButton.toggled.connect(lambda x=idx: self.on_click_update_tilt(x))
            self.button_group.addButton(radioButton, idx)
            self.radio_button_list.append(radioButton)

    def on_click_update_radius(self):
        rad = self.plainTextEdit.toPlainText()
        self.radius = float(rad)
        print('Radius: {}'.format(self.radius))

    def on_click_update_tilt(self, tilt):
        self.tilt = tilt
        print('Tilt: {}'.format(tilt))
        self.draw(tilt)

    def draw(self, tilt):
        data = self.cinrad.get_data(tilt, self.drange, self.dtype)
        _ax = self.canvas.axes
        _ax.background_patch.set_fill(False)
        if not isinstance(data.data, (tuple, list)):
            _ax.pcolormesh(data.lon, data.lat, data.data, cmap=cmap_plot[data.dtype], norm=norm_plot[data.dtype])
        else:
            _ax.pcolormesh(data.lon, data.lat, data.data[0], cmap=cmap_plot[data.dtype], norm=norm_plot[data.dtype])
            _ax.pcolormesh(data.lon, data.lat, data.data[1], cmap=cmap_plot['RF'], norm=norm_plot['RF'])
        add_shp(_ax)
        self.canvas.draw()