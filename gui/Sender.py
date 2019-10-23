import serial
from PyQt5.QtCore import QObject, pyqtSignal, QThread


class Sender(QThread):
    command_sent_successful = pyqtSignal(str)
    command_send_fail = pyqtSignal(str, str)

    def __init__(self, port_name, cmds):
        super().__init__()
        self.port_name = port_name
        self.cmds = cmds

    def __del__(self):
        self.wait()

    def run(self):
        try:
            self.send_commands(self.port_name, self.cmds)
        except RuntimeError as e:
            print(str(e))

    def send_command(self, port_name, cmd):
        """
        Send a single command
        """
        port = serial.Serial()
        port.baudrate = 19200
        port.port = port_name
        port.timeout = None
        with port as s:
            self.__send_cmd(s, cmd)

    def __send_cmd(self, s, cmd):
        # append nonesense command to get another "ok" response after the first command has been executed
        # this is done because the cnc will acknowlede the command immediately, i.e. before it has finished
        # executing the command. However we need to know when the command has actually finished before
        # sending the next command.
        # Therefore we append the "OE" command. "OE" asks for the explanation of the last error code.
        # "OE" will be execute after the move command has finished. The answer to "OE" inidicates that
        # all commands have finished.
        cmd += "OE;"
        cmd += "\n"
        print(cmd)
        s.write(cmd.encode())
        cmd_ok = s.read()

        if cmd_ok == "0".encode():
            # the only thing that "OE" can reply is "!0 OK" but we dont know when, we wait forever
            s.timeout = None
            cmd_ok = s.read(size=len("!0 OK"))
            if cmd_ok != "!0 OK".encode():
                self.command_send_fail.emit(cmd, cmd_ok.decode())
                raise RuntimeError(cmd + " -- " + cmd_ok.decode())
            else:
                self.command_sent_successful.emit(cmd)
        else:
            # we dont know what OE might reply, but it will be replied within the next second
            # and we know that it will be an error
            s.timeout = 1.0  # wait max one second
            error = s.read(
                len("!2 L_OVERFLOW"))  # longest possible answer is "!2 L_OVE RFLOW", all other errors are shorter
            self.command_send_fail.emit(cmd, error.decode())
            raise RuntimeError(cmd + " -- " + error.decode())


    def send_commands(self, port_name, commands):
        port = serial.Serial()
        port.baudrate = 19200
        port.port = port_name
        port.timeout = None

        with port as s:
            for cmd in commands:
                self.__send_cmd(s, cmd)
