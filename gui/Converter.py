import math
from recordclass import recordclass
import re

# X/Y/Z in mm, F in mm/s
G1 = recordclass('G1', 'X Y Z F')

# cX/cY in mm, A in rad, F in mm/s
G2 = recordclass('G2', 'cX cY A F')

# X/Y/Z in machine units (multiples of TODO !!)
MA = recordclass('MA', 'X Y Z')

# cX/cY in machine units, A in TODO (probably deg.deg?)
AA = recordclass('AA', 'cX cY A')

# F in steps/second
EU = recordclass('EU', 'F')

# X/Y in machine units
PA = recordclass('PA', 'X Y')


class Converter:

    def convert(self, path, params: {}):
        """
        :param path: Path to input file
        :param params: parameters for the conversion
                - 'spindel_pitch' in um
                - 'maximum_line_length' in machine units (depend in spindel_pitch)

        :return:
        """
        g_codes = self._load_file(path)
        g_codes_in_machine = self._to_machine_coordinates(g_codes)
        vhf_codes = self._to_machine_commands(g_codes_in_machine)
        vhf_codes_opt_1 = self._remove_duplicate_speed_commands(vhf_codes)
        vhf_codes_opt_2 = self._convert_MA_to_PA(vhf_codes_opt_1)
        # vhf_codes_opt_3 = self._convert_MA_to_ZA(vhf_codes_opt_2)
        # vhf_codes_opt_4 = self._combine_PA(vhf_codes_opt_3)
        vhf_strings = self._convert_to_string(vhf_codes_opt_2)

    def _load_file(self, path):
        """
        Load G Codes from file
        :param path: path to input file
        :return: list of commands G1 and G2
        """
        file = open(path, 'r')
        g_code = file.readlines()
        result = []
        for line in g_code:
            result.append(self._parse_g_code_line(line))
        return result

    def _to_machine_coordinates(self, g_codes):
        """
        Convert coordinates in g_codes to machine coordinates.
        :return: commands converted to machine coordinate system (but still in mm).
        """
        return [G1(10.0, 20.0, 1.0, 25.5), G2(11.0, 21.5, 1.425, 5.05)]

    def _to_machine_commands(self, g_codes):
        """
        Converts g codes to vhf commands.
        G1 -> EU & MA
        G2 -> EU & AA
        :return: vhf commands
        """

        # Converts the units and inserts EU everywhere.
        # No optimization is done whatsoever
        return [EU(2040), MA(10000, 20000, 100), EU(2040), AA(11000, 21500, 1500)]

    def _remove_duplicate_speed_commands(self, vhf_codes):
        """
        Removes all unnecessary (i.e. duplicate) speed commands
        """
        current_speed = -10000000  # illegal speed
        result = []
        for cmd in vhf_codes:
            if type(cmd) is EU:
                if current_speed != cmd.F:
                    result.append(cmd)
                current_speed = cmd.F
            else:
                result.append(cmd)
        return result

    def _convert_MA_to_PA(self, vhf_codes):
        """
        Replace MA with PA where possible (i.e. when only X and Y change)
        """
        return [EU(2040), MA(10000, 20000, 100), PA(3000, 4000), AA(11000, 21500, 1500)]

    def _convert_to_string(self, vhf_codes_opt_2):
        """
        Convert commands to strings
        :param vhf_codes_opt_2:
        :return:
        """
        return ["EU2040;", "MA10000,20000,100;", "PA3000,4000;", "AA11000,21500,1500;"]

    def _parse_g_code_line(self, line):
        splitted = line.split(" ")

        if len(splitted) == 0:
            raise RuntimeError("malformed G Code: " + line)

        if splitted[0] == "G1":
            if len(splitted) != 5:
                raise RuntimeError("malformed G1 code: " + line)
            g1 = G1(float('nan'), float('nan'), float('nan'), float('nan'))
            for value in splitted[1:]:
                if value.startswith("X"):
                    g1.X = float(value[1:])
                elif value.startswith("Y"):
                    g1.Y = float(value[1:])
                elif value.startswith("Z"):
                    g1.Z = float(value[1:])
                elif value.startswith("F"):
                    g1.F = float(value[1:])
                else:
                    raise RuntimeError("unknown G1 code element: '" + value + "' in line: " + line)
            self._check_not_nan(g1)
            return g1
        elif splitted[0] == G2:
            if len(splitted) != 5:
                raise RuntimeError("malformed G2 code: " + line)
            g2 = G2(float('nan'), float('nan'), float('nan'), float('nan'))
            for value in splitted[1:]:
                if value.startswith("cX"):
                    g2.cX = float(value[2:])
                elif value.startswith("cY"):
                    g2.cY = float(value[2:])
                elif value.startswith("A"):
                    g2.A = float(value[1:])
                elif value.startswith("F"):
                    g2.F = float(value[1:])
                else:
                    raise RuntimeError("unknown G1 code element: '" + value + "' in line: " + line)
            self._check_not_nan(g2)
            return g2
        else:
            raise RuntimeError("unknown G Code: " + line)

    def _check_not_nan(self, value):
        for x in value:
            if math.isnan(x):
                raise RuntimeError("Value is NaN")
