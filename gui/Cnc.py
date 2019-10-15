import collections

import math
import numpy as np

from PyQt5.QtCore import QObject, pyqtSignal


class CNC(QObject):
    send_command = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.position = np.array([0, 0, 0]) #in machine units
        self.single_move_limit = 5000 # in machine units


    def initialize(self):
        command = "^s0;AP5000,5000,5000;CO790000,1024000,160000;VB200,200,200;RV2500,300;RF;SO1,0;SO2,0;"
        self.__send(command)

    def __get_xyz_in_machine_units(self, x_mm, y_mm, z_mm):
        # TODO use real converstion instead of conversion to um
        x = int(x_mm * 1000)
        y = int(y_mm * 1000)
        z = int(z_mm * 1000)
        return np.array([x, y, z])

    def __calc_moves(self, start, goal):
        diff = goal - start

        split_num = 1
        for d in diff:
            if d > self.single_move_limit:
                split_num = math.ceil(d / self.single_move_limit) + 1

        if split_num > 1:
            xs = np.linspace(start[0], goal[0], split_num)
            ys = np.linspace(start[1], goal[1], split_num)
            zs = np.linspace(start[2], goal[2], split_num)
            return np.column_stack((xs,ys,zs))[1:]
        else:
            return np.array([goal])

    def __build_absolute_move_commands(self, moves):

        cmds = []
        cmd = "MA"

        while len(moves) > 0:
            next_goal = moves[0]
            x, y, z = next_goal
            next_goal_str = str(int(x)) + "," + str(int(y)) + "," + str(int(z))

            #does the goal fit?
            if len(next_goal_str) + len(cmd) + 2 > 76:
                # no it does not
                # end command and start a new one
                cmd = cmd + ";"
                cmds.append(cmd)
                cmd = "MA"
            else:
                # yes it does
                # remove it from moves
                moves = np.delete(moves, 0, 0)
                if len(moves) == 0:
                    if cmd == "MA":
                        cmd = cmd + next_goal_str + ";"
                    else:
                        cmd = cmd + "," + next_goal_str + ";"

                    cmds.append(cmd)
                else:
                    if cmd == "MA":
                        cmd = cmd + next_goal_str
                    else:
                        cmd = cmd + "," + next_goal_str
        return cmds





    def move_absolute(self, x_mm, y_mm, z_mm):

        moves = self.__calc_moves(self.position, self.__get_xyz_in_machine_units(x_mm, y_mm, z_mm))
        cmds = self.__build_absolute_move_commands(moves)

        #TODO hier sollte man auch immer auf eine antwort warten vorher
        for cmd in cmds:
            self.__send(cmd)

        self.position = self.__get_xyz_in_machine_units(x_mm, y_mm, z_mm)

    def __send(self, command):
        self.send_command.emit(command)
