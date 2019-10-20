import serial

class Sender:

    def __init__(self, port_name):
        self.serial = serial.Serial()
        self.serial.baudrate = 19200
        self.serial.port = port_name
        self.serial.open()

    def send(self, commands):
        self.serial.timeout = None

        for cmd in commands:
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
            self.serial.write(cmd)
            cmd_ok = self.serial.read() # we ignore the return because we ask for it again using OE anyway


            if cmd_ok == "0":
                # the only thing that "OE" can reply is "!0 OK" but we dont know when
                cmd_ok = self.serial.read(size=len("!0 OK"))
                if cmd_ok != "!0 OK":
                    print("ERROR while sending. Answer should have been OK but was: " + cmd_ok)
                    return
            else:
                # we dont know what OE might reply, but it will be replied within the next second
                # ans we know that it will be an error
                self.serial.timeout = 1.0 # wait max one second
                error = self.serial.read(len("!2 L_OVERFLOW")) # longest possible answer is "!2 L_OVE RFLOW", all other errors are shorter
                print("ERROR response: " + error)
                return