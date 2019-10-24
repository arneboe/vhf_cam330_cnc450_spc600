from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QFileDialog, QProgressBar

import Sender
from Converter import Converter


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
        self.pushButtonChooseFile.clicked.connect(self.__choose_g_code_file_clicked)
        self.pushButtonExecuteCode.clicked.connect(self.__execute_commands_clicked)
        self.pushButtonConnect.clicked.connect(self.__connect_clicked)

        self.progressBar = QProgressBar()
        self.statusBar().addPermanentWidget(self.progressBar)

        self.current_cmds = []

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
        self.disable_position_signal = True
        self.doubleSpinBoxXPosition.setValue(0)
        self.doubleSpinBoxYPosition.setValue(0)
        self.doubleSpinBoxZPosition.setValue(0)
        self.disable_position_signal = False

        init_cmds= ["^s0;",
                    "AP5000,5000,5000;",
                    "CO790000,1024000,160000;",
                    "VB200,200,200;",
                    "RV2500,300;",
                    "RF;",
                    "SO1,0;SO2,0;",
                    "EU3000,3000,3000;"]

        self.send_async(init_cmds)

    def __connect_clicked(self):
        self.sender = Sender.Sender(self.lineEditComPort.text())
        self.sender.command_sent_successful.connect(self.__cmd_sent_successful_handler)
        self.sender.error.connect(self.__print_error_handler)
        self.sender.finished.connect(self.__cmd_sender_finished_handler)
        self.sender.send_status.connect(self.__cmd_sender_send_status_handler)
        self.sender.start()
        self.__set_ui_enabled(True)

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
            c = Converter(self.doubleSpinBoxRapidMoveSpeed.value())
            cmds, bounds = c.convert(file_names[0])
            self.plainTextEditLoadedCommands.clear()
            for cmd in cmds:
                self.plainTextEditLoadedCommands.appendPlainText(cmd)

            self.current_cmds = cmds

    def __move_absolute(self):
        cmd = Converter.build_move_command(self.doubleSpinBoxXPosition.value(),
                                           self.doubleSpinBoxYPosition.value(),
                                           self.doubleSpinBoxZPosition.value())
        self.sender.enqeue_cmd(cmd)


    def __execute_commands_clicked(self):
        self.send_async(self.current_cmds)

    def send_async(self, cmds):
        for cmd in cmds:
            self.sender.enqeue_cmd(cmd)

    def __cmd_sent_successful_handler(self, cmd):
        self.plainTextEditTerminal.appendHtml("<font color=\"green\">" + cmd + "</font>")

    def __print_error_handler(self, error_msg):
        self.plainTextEditTerminal.appendHtml("<font color=\"red\"> ERROR: " + error_msg + "</font>")

    def __cmd_sender_finished_handler(self):

        self.__set_ui_enabled(False)

    def __send_command_handler(self, command):
        """
        Listens to the cnc command send signal
        """
        self.plainTextEditTerminal.appendPlainText(command)

    def __set_ui_enabled(self, enabled):
        """
        Enable/Disable ui while sending
        """
        self.doubleSpinBoxXPosition.setEnabled(enabled)
        self.doubleSpinBoxYPosition.setEnabled(enabled)
        self.doubleSpinBoxZPosition.setEnabled(enabled)


        self.doubleSpinBoxXSteps.setEnabled(enabled)
        self.doubleSpinBoxYSteps.setEnabled(enabled)
        self.doubleSpinBoxZSteps.setEnabled(enabled)

        self.pushButtonSendInit.setEnabled(enabled)
        self.pushButtonMoveToZero.setEnabled(enabled)
        self.pushButtonSendPosition.setEnabled(enabled)
        self.pushButtonChooseFile.setEnabled(enabled)
        self.pushButtonExecuteCode.setEnabled(enabled)

    def __cmd_sender_send_status_handler(self, num_cmds):
        if num_cmds == 0:
            self.statusBar().showMessage("")
            self.progressBar.hide()
            self.progressBar.setMaximum(0)
        else:
            self.statusBar().showMessage("Sending (" + str(num_cmds) + " commands left)")

            if self.progressBar.maximum() < num_cmds:
                # new maximum
                self.progressBar.setMaximum(num_cmds)
            self.progressBar.setValue(self.progressBar.maximum() - num_cmds)
            self.progressBar.show()

    def closeEvent(self, event):
        if self.sender.isRunning():
            self.sender.stop()
        event.accept()
