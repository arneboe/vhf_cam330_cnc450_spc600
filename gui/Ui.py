from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QFileDialog

from Cnc import CNC


class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()  # Call the inherited classes __init__ method
        uic.loadUi('ui.ui', self)

        self.doubleSpinBoxXPosition.valueChanged.connect(self.__x_position_changed)
        self.doubleSpinBoxYPosition.valueChanged.connect(self.__y_position_changed)
        self.doubleSpinBoxZPosition.valueChanged.connect(self.__z_position_changed)

        self.disable_position_signal = False # if true the spinboxes will not trigger cnc moves

        self.doubleSpinBoxXSteps.valueChanged.connect(self.__x_position_steps_changed)
        self.doubleSpinBoxYSteps.valueChanged.connect(self.__y_position_steps_changed)
        self.doubleSpinBoxZSteps.valueChanged.connect(self.__z_position_steps_changed)

        self.pushButtonSendInit.clicked.connect(self.__send_init_clicked)
        self.pushButtonMoveToZero.clicked.connect(self.__move_to_zero_clicked)
        self.pushButtonSendPosition.clicked.connect(self.__send_position_clicked)
        self.pushButtonUsePositionAsOrigin.clicked.connect(self.__use_current_position_as_origin_clicked)
        self.pushButtonChooseFile.clicked.connect(self.__choose_g_code_file_clicked)

        self.cnc = CNC()
        self.cnc.send_command.connect(self.__send_command_handler)

        self.show()

    def __x_position_changed(self):
        if not self.disable_position_signal and self.checkBoxUpdatePositionLive.isChecked():
            self.__move_absolute()

    def __y_position_changed(self):
        if not self.disable_position_signal and self.checkBoxUpdatePositionLive.isChecked():
            self.__move_absolute()

    def __z_position_changed(self):
        if not self.disable_position_signal and self.checkBoxUpdatePositionLive.isChecked():
            self.__move_absolute()

    def __x_position_steps_changed(self, new_value):
        self.doubleSpinBoxXPosition.setSingleStep(new_value)

    def __y_position_steps_changed(self, new_value):
        self.doubleSpinBoxYPosition.setSingleStep(new_value)

    def __z_position_steps_changed(self, new_value):
        self.doubleSpinBoxZPosition.setSingleStep(new_value)

    def __send_init_clicked(self):
        self.cnc.initialize()
        self.disable_position_signal = True
        self.doubleSpinBoxXPosition.setValue(0)
        self.doubleSpinBoxYPosition.setValue(0)
        self.doubleSpinBoxZPosition.setValue(0)
        self.disable_position_signal = False

    def __move_to_zero_clicked(self):
        self.disable_position_signal = True
        self.doubleSpinBoxXPosition.setValue(0)
        self.doubleSpinBoxYPosition.setValue(0)
        self.doubleSpinBoxZPosition.setValue(0)
        self.__move_absolute()
        self.disable_position_signal = False

    def __send_position_clicked(self):
        self.__move_absolute()

    def __choose_g_code_file_clicked(self):
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.AnyFile)

        if dlg.exec_():
            file_names = dlg.selectedFiles()
            f = open(file_names[0], 'r')
            with f:
                commands = self.cnc.load_g_code(f)
                self.plainTextEditLoadedCommands.clear()
                for cmd in commands:
                    self.plainTextEditLoadedCommands.appendPlainText(cmd)


    def __use_current_position_as_origin_clicked(self):
        self.doubleSpinBoxOriginX.setValue(self.doubleSpinBoxXPosition.value())
        self.doubleSpinBoxOriginY.setValue(self.doubleSpinBoxYPosition.value())
        self.doubleSpinBoxOriginZ.setValue(self.doubleSpinBoxZPosition.value())

    def __move_absolute(self):
        self.cnc.move_absolute(self.doubleSpinBoxXPosition.value(), self.doubleSpinBoxYPosition.value(), self.doubleSpinBoxZPosition.value())

    def __send_command_handler(self, command):
        """
        Listens to the cnc command send signal
        """
        self.plainTextEditTerminal.appendPlainText(command)
