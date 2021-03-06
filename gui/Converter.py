import math
import sys

from collections import namedtuple
import re

# rapid move. X/Y/Z in mm
G0 = namedtuple('G0', 'X Y Z')
# X/Y/Z in mm, F in mm/s
G1 = namedtuple('G1', 'X Y Z F')

# arc absolut, center x/y in mm, angle in deg, F in mm/s
GAA = namedtuple('GAA', 'cX cY A F')

BEGIN_SECTION = namedtuple('BEGIN_SECTION', '')
END_SECTION = namedtuple('END_SECTION', '')

# X/Y/Z in machine units
MA = namedtuple('MA', 'X Y Z')

# cX/cY in machine units, A in degree
AA = namedtuple('AA', 'cX cY A')

# F in steps/second
EU = namedtuple('EU', 'F')

# X/Y in machine units
PA = namedtuple('PA', 'X Y')

# X in mchine units
XA = namedtuple('XA', 'X')

# Y in machine units
YA = namedtuple('YA', 'Y')

# Z in machine units
ZA = namedtuple('ZA', 'Z')

Boundaries = namedtuple("Boundaries", "min_z max_z")

class Converter:

    def __init__(self, rapid_move_speed_mm_min):
        """
        :param rapid_move_speed_mm_min: rapid move speed in mm/min
        """
        self.rapid_move_speed_steps = self._convert_speed_to_machine(rapid_move_speed_mm_min)
        print("rapid move speed in steps/s: " + str(self.rapid_move_speed_steps))
        # TODO validate rapid move speed!

    def convert(self, path):
        """
        :param path: Path to input file
        :return:
        """
        g_codes = self._load_file(path)
        # g_codes_in_machine = self._to_machine_coordinates(g_codes)
        vhf_codes = self._to_machine_commands(g_codes)
        vhf_codes_with_lead_in = self._add_lead_in(vhf_codes)
        vhf_codes_opt_1 = self._remove_duplicate_speed_commands(vhf_codes_with_lead_in)
        vhf_codes_opt_2 = self._convert_MA_to_ZA(vhf_codes_opt_1)
        vhf_codes_opt_3 = self._convert_MA_to_PA(vhf_codes_opt_2)
        # vhf_codes_opt_3 = self._convert_MA_to_ZA(vhf_codes_opt_2)
        # vhf_codes_opt_4 = self._combine_PA(vhf_codes_opt_3)

        self._validate(vhf_codes_opt_2)


        vhf_strings = self._convert_to_string(vhf_codes_opt_3)
        bounds = self._calculate_bounds(vhf_codes_opt_3)

        return vhf_strings, bounds

    def _load_file(self, path):
        """
        Load G Codes from file
        :param path: path to input file
        :return: list of commands G1 and G2
        """
        file = open(path, 'r')
        g_code = file.readlines()

        if g_code[0] != "THIS_IS_VHF330_G_CODE_DIALECT\n":
            raise RuntimeError("Unknown file format")

        result = []
        for line in g_code[1:]:
            result.append(self._parse_g_code_line(line))
        return result

    def _to_machine_commands(self, g_codes):
        """
        Converts g codes to vhf commands, converts units to machine units
        :return: vhf commands
        """
        result = []
        for g_code in g_codes:
            if type(g_code) is G0:
                result.extend(self._convert_G0_to_vhf(g_code))
            elif type(g_code) is G1:
                result.extend(self._convert_G1_to_vhf(g_code))
            elif type(g_code) is GAA:
                result.extend(self._convert_GAA_to_vhf(g_code))
            elif type(BEGIN_SECTION):
                result.append(BEGIN_SECTION())
            elif type(END_SECTION):
                result.append(END_SECTION)
            else:
                raise RuntimeError("Unknown g code: " + g_code)
        return result


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
        current_z = sys.maxsize

        for i, cmd in enumerate(vhf_codes):
            if type(cmd) is ZA:
                current_z = cmd.Z
            elif type(cmd) is MA:
                if current_z == cmd.Z:
                    # this is a MA that does not change Z. replace with PA
                    vhf_codes[i] = PA(cmd.X, cmd.Y)
                else:
                    # this is MA that also changes Z. keep and update tracking z
                    current_z = cmd.Z
        return vhf_codes

    @staticmethod
    def __convert_MA_to_string(cmd):
        za = ZA(cmd.Z)
        pa = PA(cmd.X, cmd.Y)
        return Converter.__convert_ZA_to_string(za) + Converter.__convert_PA_to_string(pa)


    #    return "MA" + str(cmd.X) + "," + str(cmd.Y) + "," + str(cmd.Z) + ";"

    @staticmethod
    def __convert_PA_to_string(cmd):
        return "PA" + str(cmd.X) + "," + str(cmd.Y) + ";"

    @staticmethod
    def __convert_ZA_to_string(cmd):
        return "ZA" + str(cmd.Z) + ";"

    @staticmethod
    def __convert_XA_to_string(cmd):
        return "XA" + str(cmd.X) + ";"

    @staticmethod
    def __convert_YA_to_string(cmd):
        return "YA" + str(cmd.Y) + ";"

    def _convert_to_string(self, vhf_codes):
        """
        Convert commands to strings
        :param vhf_codes_opt_2:
        :return:
        """
        result = []

        for cmd in vhf_codes:
            if type(cmd) is MA:
                za = ZA(cmd.Z)
                pa = PA(cmd.X, cmd.Y)
              #  return Converter.__convert_ZA_to_string(za) + Converter.__convert_PA_to_string(pa)

                result.append(Converter.__convert_ZA_to_string(za))
                result.append(Converter.__convert_PA_to_string(pa))

            elif type(cmd) is PA:
                result.append(Converter.__convert_PA_to_string(cmd))
            elif type(cmd) is ZA:
                result.append(Converter.__convert_ZA_to_string(cmd))
            elif type(cmd) is AA:
                result.append("AA" + str(cmd.cX) + "," + str(cmd.cY) + "," + str(cmd.A) + ";")
            elif type(cmd) is EU:
                result.append("EU" + str(cmd.F) + ";")
            elif type(cmd) is BEGIN_SECTION:
                pass
            elif type(cmd) is END_SECTION:
                pass
            else:
                raise RuntimeError("Uknown command: " + str(cmd))
        return result

    def _parse_g_code_line(self, line):

        if line.startswith("BEGIN_SECTION"):
            return BEGIN_SECTION()
        if line.startswith("END_SECTION"):
            return END_SECTION()

        splitted = line.split(" ")
        if len(splitted) == 0:
            raise RuntimeError("malformed G Code: " + line)

        if splitted[0] == "G0":
            return self._parse_G0(splitted)
        if splitted[0] == "G1":
            return self._parse_G1(splitted)
        if splitted[0] == "GAA":
            return self._parse_GAA(splitted)
        else:
            raise RuntimeError("unknown G Code: " + line)

    def _check_not_nan(self, value):
        for x in value:
            if math.isnan(x):
                raise RuntimeError("Value is NaN")

    def _parse_G0(self, splitted):
        if len(splitted) != 4:
            raise RuntimeError("malformed G0 code: " + str(splitted))
        x = float('nan')
        y = float('nan')
        z = float('nan')

        for value in splitted[1:]:
            if value.startswith("X"):
                x = float(value[1:])
            elif value.startswith("Y"):
                y = float(value[1:])
            elif value.startswith("Z"):
                z = float(value[1:])
            else:
                raise RuntimeError("unknown G0 code element: '" + value + "' in line: " + splitted)
        g0 = G0(x, y, z)
        self._check_not_nan(g0)
        return g0

    def _parse_G1(self, splitted):
        if len(splitted) != 5:
            raise RuntimeError("malformed G1 code: " + splitted)
        x = float('nan')
        y = float('nan')
        z = float('nan')
        f = float('nan')
        for value in splitted[1:]:
            if value.startswith("X"):
                x = float(value[1:])
            elif value.startswith("Y"):
                y = float(value[1:])
            elif value.startswith("Z"):
                z = float(value[1:])
            elif value.startswith("F"):
                f = float(value[1:])
            else:
                raise RuntimeError("unknown G1 code element: '" + value + "' in line: " + splitted)
        g1 = G1(x, y, z, f)
        self._check_not_nan(g1)
        return g1

    def _parse_GAA(self, splitted):
        if len(splitted) != 5:
            raise RuntimeError("malformed G2 code: " + splitted)
        x = float('nan')
        y = float('nan')
        a = float('nan')
        f = float('nan')
        for value in splitted[1:]:
            if value.startswith("cX"):
                x = float(value[2:])
            elif value.startswith("cY"):
                y = float(value[2:])
            elif value.startswith("A"):
                a = float(value[1:])
            elif value.startswith("F"):
                f = float(value[1:])
            else:
                raise RuntimeError("unknown G1 code element: '" + value + "' in line: " + splitted)
        gaa = GAA(x, y, a, f)
        self._check_not_nan(gaa)
        return gaa

    def _validate(self, vhf_codes):
        #TODO implement
        # this method should to coordinate validation, check software endstops, etc.
        # find all kinds of mistakes before they break the cnc :D

        # check z
        for cmd in vhf_codes:
            if hasattr(cmd, "Z"):
                if cmd.Z < 0:
                    raise RuntimeError("Z Coordinates < 0 not allowed")


    def _add_lead_in(self, vhf_codes):
        target_x = float('nan')
        target_y = float('nan')
        target_z = float('nan')

        for cmd in vhf_codes:
            if type(cmd) is MA:
                if math.isnan(target_x):
                    target_x = cmd.X
                if math.isnan(target_y):
                    target_y = cmd.Y
                target_z = cmd.Z
                break
            elif type(cmd) is PA:
                target_x = cmd.X
                target_y = cmd.Y
            elif type(cmd) is BEGIN_SECTION or EU:
                continue
            else:
                raise RuntimeError("Encounterd '" + str(cmd) + "' before all coordinates where known.")

        vhf_codes.insert(0, ZA(target_z))
        vhf_codes.insert(0, PA(target_x, target_y))
        vhf_codes.insert(0, ZA(0))
        vhf_codes.insert(0, EU(self.rapid_move_speed_steps))

        # todo in theroy we could remove the first  command now?!

        return vhf_codes

    def _convert_G0_to_vhf(self, g_code):
        result = []
        result.append(EU(self.rapid_move_speed_steps))
        x = Converter._convert_mm_to_machine(g_code.X)
        y = Converter._convert_mm_to_machine(g_code.Y)
        z = Converter._convert_mm_to_machine(g_code.Z)
        result.append(MA(x, y, z))
        return result

    def _convert_G1_to_vhf(self, g_code):
        result = []
        f = self._convert_speed_to_machine(g_code.F)
        result.append(EU(f))
        x = Converter._convert_mm_to_machine(g_code.X)
        y = Converter._convert_mm_to_machine(g_code.Y)
        z = Converter._convert_mm_to_machine(g_code.Z)
        result.append(MA(x, y, z))
        return result

    def _convert_GAA_to_vhf(self, g_code):
        result = []
        f = self._convert_speed_to_machine(g_code.F)
        result.append(EU(f))
        cx = Converter._convert_mm_to_machine(g_code.cX)
        cy = Converter._convert_mm_to_machine(g_code.cY)
        result.append(AA(cx, cy, g_code.A))
        return result

    def _convert_speed_to_machine(self, speed_mm_min):
        mm_sec = speed_mm_min / 60.0
        steps_sec = mm_sec * 80.0 # 1mm = 80 steps
        return int(round(steps_sec))

    @staticmethod
    def _convert_mm_to_machine(distance):
        # converts distance from mm to machine units (micrometer)
        return int(round(distance * 1000.0))

    def _convert_MA_to_ZA(self, vhf_codes):
        current_x = sys.maxsize
        current_y = sys.maxsize

        for i, cmd in enumerate(vhf_codes):
            if type(cmd) is PA:
                current_x = cmd.X
                current_y = cmd.Y
            elif type(cmd) is MA:
                if cmd.X == current_x and cmd.Y == current_y:
                    # this is a MA command that only affects the z axis, can be replaced by ZA
                    vhf_codes[i] = ZA(cmd.Z)
                else:
                    # this is a MA that changes x/y, just update our tracking position
                    current_x = cmd.X
                    current_y = cmd.Y

        return vhf_codes

    def _calculate_bounds(self, vhf_codes):
        min_z=99999999
        max_z=-9999999999
        for cmd in vhf_codes:
            if type(cmd) is MA:
                min_z = min(min_z, cmd.Z)
                max_z = max(max_z, cmd.Z)
            elif type(cmd) is ZA:
                min_z = min(min_z, cmd.Z)
                max_z = max(max_z, cmd.Z)
        return Boundaries(min_z, max_z)

    @staticmethod
    def build_PA_command(x_mm, y_mm):
        x = Converter._convert_mm_to_machine(x_mm)
        y = Converter._convert_mm_to_machine(y_mm)
        pa = PA(x, y)
        return Converter.__convert_PA_to_string(pa)

    @staticmethod
    def build_ZA_command(z_mm):
        z = Converter._convert_mm_to_machine(z_mm)
        za = ZA(z)
        return Converter.__convert_ZA_to_string(za)

    @staticmethod
    def build_XA_command(x_mm):
        x = Converter._convert_mm_to_machine(x_mm)
        xa = XA(x)
        return Converter.__convert_XA_to_string(xa)

    @staticmethod
    def build_YA_command(y_mm):
        y = Converter._convert_mm_to_machine(y_mm)
        return Converter.__convert_YA_to_string(YA(y))

    @staticmethod
    def build_MA_command(x_mm, y_mm, z_mm):
        """
        Creates a single MA command from x/y/z
        """
        x = Converter._convert_mm_to_machine(x_mm)
        y = Converter._convert_mm_to_machine(y_mm)
        z = Converter._convert_mm_to_machine(z_mm)
        za = ZA(z)
        pa = PA(x, y)

        ma = MA(x, y, z)
        return Converter.__convert_ZA_to_string(za) + Converter.__convert_PA_to_string(pa)

    @staticmethod
    def build_begin_init_command():
        return "^s0;"

    @staticmethod
    def build_spindel_gradient_command(x_mm, y_mm, z_mm):
        x = Converter._convert_mm_to_machine(x_mm)
        y = Converter._convert_mm_to_machine(y_mm)
        z = Converter._convert_mm_to_machine(z_mm)

        return "AP" + str(x) + "," + str(y) + "," + str(z) + ";"

    @staticmethod
    def build_table_dimensions_command(x_mm, y_mm, z_mm):
        x = Converter._convert_mm_to_machine(x_mm)
        y = Converter._convert_mm_to_machine(y_mm)
        z = Converter._convert_mm_to_machine(z_mm)

        return "CO" + str(x) + "," + str(y) + "," + str(z) + ";"


    def build_spindel_speed_command(self, rpm):
        """
         vhf spc600 (copy paste from cenon 3.3):
         port 1, bits 0-7 and port 2, bits 0-1: revolution
         input, bit 0: rotation achieved
         input, bit 1: spindle stop
         input, bit 2: spindel error
        """

        min_rpm = 800
        max_rpm = 20000

        # min and max values that we can send to the controller
        min_value = 1
        max_value = 1023


        "SO1,0;SO2,0;"

    def __encoden_spindel_to_byte(self, spindel_value):
        """
        param: spindel_value range(0, 1023)h
        return: (byte1, byte2)
        """
        b0 = int(spindel_value / 255.0)