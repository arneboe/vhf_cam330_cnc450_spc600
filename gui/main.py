import sys

from PyQt5 import QtWidgets
from Ui import Ui

if __name__== "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    app.exec_()