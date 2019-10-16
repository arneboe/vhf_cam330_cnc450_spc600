import collections

import math
import numpy as np

from PyQt5.QtCore import QObject, pyqtSignal


class CNC(QObject):
    send_command = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.position = np.array([0, 0, 0])  # in machine units
        self.single_move_limit = 5000  # in machine units


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
                new_split_num = math.ceil(d / self.single_move_limit) + 1
                split_num = max(new_split_num, split_num)

        if split_num > 1:
            xs = np.linspace(start[0], goal[0], split_num)
            ys = np.linspace(start[1], goal[1], split_num)
            zs = np.linspace(start[2], goal[2], split_num)
            return np.column_stack((xs,ys,zs))[1:]
        else:
            return np.array([goal])

    def __build_absolute_move_commands(self, moves, cmd_string="MA", ignore_z=False):

        cmds = []
        cmd = cmd_string

        while len(moves) > 0:
            next_goal = moves[0]
            x, y, z = next_goal
            if ignore_z:
                next_goal_str = str(int(x)) + "," + str(int(y))
            else:
                next_goal_str = str(int(x)) + "," + str(int(y)) + "," + str(int(z))

            #does the goal fit?
            if len(next_goal_str) + len(cmd) + 2 > 76:
                # no it does not
                # end command and start a new one
                cmd = cmd + ";"
                cmds.append(cmd)
                cmd = cmd_string
            else:
                # yes it does
                # remove it from moves
                moves = np.delete(moves, 0, 0)
                if len(moves) == 0:
                    if cmd == cmd_string:
                        cmd = cmd + next_goal_str + ";"
                    else:
                        cmd = cmd + "," + next_goal_str + ";"

                    cmds.append(cmd)
                else:
                    if cmd == cmd_string:
                        cmd = cmd + next_goal_str
                    else:
                        cmd = cmd + "," + next_goal_str
        return cmds

    def move_absolute(self, x_mm, y_mm, z_mm):

        moves = self.__calc_moves(self.position, self.__get_xyz_in_machine_units(x_mm, y_mm, z_mm))
        cmds = self.__build_absolute_move_commands(moves)

        # TODO hier sollte man auch immer auf eine antwort warten vorher
        for cmd in cmds:
            self.__send(cmd)

        self.position = self.__get_xyz_in_machine_units(x_mm, y_mm, z_mm)

    def __send(self, command):
        self.send_command.emit(command)

    def __mark3d2d(self, positions):
        """
        Split the positions into a sequence of 3d and 2d moves
        :param positions: np.array(n,3)
        :return: a list of 3d and 2d chunks. One chunk is a tuple (dim, [data]) where dim=2 or dim=3
        """

        current_dim = 3
        current_positions = []
        result = []

        for i, pos in enumerate(positions):

            if not current_positions:
                current_positions.append(pos)
            else:
                curr_z = pos[2]
                old_z = current_positions[-1][2]

                if current_dim == 3:
                    # are we still a 3d move?
                    if curr_z == old_z:
                        # no we are not, end chunk
                        result.append((current_dim, current_positions))
                        current_positions = [pos]
                        current_dim = 2
                        # figure out dimension of the next chunk
                    else:
                        # yes we are
                        current_positions.append(pos)
                elif current_dim == 2:
                    # are we still a 2d move?
                    if curr_z != old_z:
                        # no we are not, end chunk
                        result.append((current_dim, current_positions))
                        current_positions = [pos]
                        current_dim = 3
                    else:
                        # yes we are
                        current_positions.append(pos)
                else:
                    pass

        if current_positions:
            result.append((current_dim, current_positions))

        return result

    def __convert_3d_moves_to_commands(self, moves):

        # 1. split moves to fit the step length limit
        split_moves = []
        if len(moves) > 1:
            for i, move in enumerate(moves):
                if i == len(moves) - 1:
                    pass
                else:
                    start = move
                    if i == 0:
                        split_moves.append(start) #FIXME das geht nicht beim ersten element wenn gesplitted wurde
                    end = moves[i + 1]
                    splitted = self.__calc_moves(start, end)
                    split_moves.extend(splitted)
        elif len(moves) == 1:
            split_moves.append(moves[0])



        # 2. convert to maximum line length commands
        cmds = self.__build_absolute_move_commands(split_moves, cmd_string="MA", ignore_z=False)
        return cmds

    def __convert_2d_moves_to_commands(self, moves):
        cmds = self.__build_absolute_move_commands(moves, cmd_string="PA", ignore_z=True)
        return cmds

    def __convert_marked_moves_to_commands(self, marked_moves):
        commands = []

        for dim, moves in marked_moves:
            if dim == 3:
                commands.extend(self.__convert_3d_moves_to_commands(moves))
            elif dim == 2:
                commands.extend(self.__convert_2d_moves_to_commands(moves))
            else:
                pass
        return commands

    def __coordinate_transformation(self, positions):
        """
        :param positions: in working coordinate system (in mm)
        :return positions in machine coordinate system
        """

        result = []

        x_offset = 10.0 #TODO use real offset
        y_offset = 10.0 # TODO use real offset
        z_offset = 10.0 # TODO ....

        # TODO implement rotation

        for x, y, z in positions:
            x += x_offset
            y += y_offset
            z *= -1.0  # this works around a bug in fusion360
            z += z_offset
            # TODO do real transformation here
            result.append(np.array([x, y, z]))

        return result


    def __convert_positions_to_commands(self, positions):
        """
        :param positions: in work space coordinates (in mm).
        :param coordinate_offset: offset of the work space coordinate system from the machine system (np.array([x,y,z]))
        """
        commands = []
        # insert origin. otherwise calculations break ATTENTION this assumes that the origin is 0/0/0, this should
        # be fine because the machine offset is always 0/0/0

        # TODO do coordinate transformation
        #machine_positions = self.__coordinate_transformation(positions)
        machine_positions =positions

        # generate linear path from origin to first position
        if not np.array_equal(machine_positions[0], np.array([0, 0, 0])):
            first_positions = [np.array([0, 0, 0]), machine_positions[0]]
            first_marked_positions = self.__mark3d2d(first_positions)
            # TODO MA0,0,0 should not be in here, it will break if we dont start at zero anyway
            commands = self.__convert_marked_moves_to_commands(first_marked_positions)

        # TODO duplicate position, the last of initial and the first of the real ones are duplicate, doesnt matter much
        marked_positions = self.__mark3d2d(machine_positions)
        commands.extend(self.__convert_marked_moves_to_commands(marked_positions))
        return commands


    def load_g_code(self, gcode):
        """
        Format:
        Move absolut:  G1 Xnnn Ynnnn Znnn Fnnn
            X pos in mm
            Y pos in mm
            Z pos in mm
            F feedrate in mm/s
        :return:
        """
        positions = []

        for line in gcode:
            line = line.strip()
            entries = line.split(" ")
            if len(entries) != 5:
                raise RuntimeError("gcode illegal line")

            if not entries[0].startswith("G1"):
                raise RuntimeError("unknown gcode:" + entries[0])

            if not entries[1].startswith("X"):
                raise RuntimeError("first entry has to be 'X' but was:" + entries[1])
            x = float(entries[1][1:])

            if not entries[2].startswith("Y"):
                raise RuntimeError("second entry has to be 'Y' but was:" + entries[2])
            y = float(entries[2][1:])

            if not entries[3].startswith("Z"):
                raise RuntimeError("third entry has to be 'Z' but was:" + entries[3])
            z = float(entries[3][1:])

            if not entries[4].startswith("F"):
                raise RuntimeError("fourth entry has to be 'F' but was:" + entries[4])
            f = float(entries[4][1:])

            # TODO use feed rate for anything
            positions.append(np.array([x, y, z]))

        return self.__convert_positions_to_commands(positions)
