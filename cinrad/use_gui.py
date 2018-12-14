import sys
from gui import Ui_MainWindow
from PyQt5 import QtCore, QtGui, QtWidgets

app = QtWidgets.QApplication(sys.argv)
Form = QtWidgets.QMainWindow()
ui = Ui_MainWindow()
ui.setupUi(Form)
Form.show()
sys.exit(app.exec_())