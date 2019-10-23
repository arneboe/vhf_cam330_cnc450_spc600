from time import sleep

import serial
if __name__ == '__main__':
    port = serial.Serial()
    port.baudrate = 19200
    port.port = "/dev/pts/14"
    port.timeout = None

    i = 0

    with port as s:
        while True:
            i = i + 1
            cmd = s.read_until("\n".encode())
            print(cmd)

            if (i % 10) == 0:
                s.write("3".encode())
                s.write("!3 SYNTAX".encode())
            else:
                s.write("0".encode())
                sleep(0.5)
                s.write("!0 OK".encode())