import queue

import serial
from PyQt5.QtCore import QObject, pyqtSignal, QThread


class Sender(QThread):
    command_sent_successful = pyqtSignal(str)
    error = pyqtSignal(str)
    send_status = pyqtSignal(int) # num commands

    def __init__(self, port_name):
        super().__init__()
        self.port_name = port_name
        self.cmds = queue.Queue()
        self.running = False

    def __del__(self):
        self.wait()

    def enqeue_cmd(self, cmd):
        if self.isRunning():
            self.cmds.put(cmd)
        else:
            raise RuntimeError("Sender is not running")

    def run(self):
        port = serial.Serial()
        port.baudrate = 19200
        port.port = self.port_name
        port.timeout = None
        self.running = True
        try:
            with port as s:
                while self.running:

                    # get cmd from queue
                    try:
                        cmd = self.cmds.get(timeout=0.1)  # block until cmd is available
                    except queue.Empty:
                        continue

                    # execute cmd
                    try:
                        self.__send_cmd(s, cmd)
                    except RuntimeError as e:
                        # discard all following commands on error
                        while not self.cmds.empty():
                            cmd = self.cmds.get()
                            self.cmds.task_done()
                        self.error.emit(str(e) + " Discarding command queue!")

                    self.cmds.task_done()
                    self.send_status.emit(self.cmds.qsize())

        except FileNotFoundError as e:
            self.error.emit(str(e))
        except serial.SerialException as e:
            self.error.emit(str(e))

    def stop(self):
        self.running = False
        self.wait()

    def __send_cmd(self, s, cmd):
        # append nonesense command to get another "ok" response after the first command has been executed
        # this is done because the cnc will acknowlede the command immediately, i.e. before it has finished
        # executing the command. However we need to know when the command has actually finished before
        # sending the next command.
        # Therefore we append the "OE" command. "OE" asks for the explanation of the last error code.
        # "OE" will be execute after the move command has finished. The answer to "OE" inidicates that
        # all commands have finished.

        print(cmd)
        s.write(cmd.encode())
        cmd_ok = s.read()

        if cmd_ok == "0".encode():
            self.command_sent_successful.emit(cmd)
        else:
            raise RuntimeError(cmd + " | Error Code: " + cmd_ok.decode())


