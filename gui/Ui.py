from PyQt5 import QtWidgets, uic

from Cnc import CNC


class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()  # Call the inherited classes __init__ method
        uic.loadUi('ui.ui', self)

        self.doubleSpinBoxXPosition.editingFinished.connect(self.__x_position_changed)
        self.doubleSpinBoxYPosition.editingFinished.connect(self.__y_position_changed)
        self.doubleSpinBoxZPosition.editingFinished.connect(self.__z_position_changed)

        self.disable_position_signal = False # if true the spinboxes will not trigger cnc moves

        self.doubleSpinBoxXSteps.valueChanged.connect(self.__x_position_steps_changed)
        self.doubleSpinBoxYSteps.valueChanged.connect(self.__y_position_steps_changed)
        self.doubleSpinBoxZSteps.valueChanged.connect(self.__z_position_steps_changed)

        self.pushButtonSendInit.clicked.connect(self.__send_init_clicked)
        self.pushButtonMoveToZero.clicked.connect(self.__move_to_zero_clicked)

        self.cnc = CNC()
        self.cnc.send_command.connect(self.__send_command_handler)


        self.show()

    def __x_position_changed(self):
        if not self.disable_position_signal:
            self.__move_absolute()

    def __y_position_changed(self):
        if not self.disable_position_signal:
            self.__move_absolute()

    def __z_position_changed(self):
        if not self.disable_position_signal:
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

    def __move_absolute(self):
        self.cnc.move_absolute(self.doubleSpinBoxXPosition.value(), self.doubleSpinBoxYPosition.value(), self.doubleSpinBoxZPosition.value())

    def __send_command_handler(self, command):
        """
        Listens to the cnc command send signal
        """
        self.plainTextEditTerminal.appendPlainText(command)
