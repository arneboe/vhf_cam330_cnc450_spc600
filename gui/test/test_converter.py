from nose.tools import assert_equals, assert_raises, raises, assert_greater, assert_true
import numpy as np

from Converter import Converter, G0, EU


def test_to_machine():
    c = Converter(rapid_move_speed_mm_min=1500)
    result = c.convert("C:\\git\\test_vhf_cnc.cnc")
    print(result)
    f = open("C:\\git\\cnc.txt", "w+")

    for line in result[0]:
        f.write(line + "\n")
    f.close()


def test_g_code_parser_G0():
    c = Converter(rapid_move_speed_mm_min=1500)
    cmd = c._parse_g_code_line("G0 X1000.42 Y2000.44 Z3300")
    assert_true(type(cmd) is G0)
    assert_equals(cmd.X, 1000.42)
    assert_equals(cmd.Y, 2000.44)
    assert_equals(cmd.Z, 3300.0)

@raises(RuntimeError)
def test_g_code_parser_G0_2():
    c = Converter(rapid_move_speed_mm_min=1500)
    cmd = c._parse_g_code_line("G0 X1000.42 Y2000.44")

@raises(RuntimeError)
def test_g_code_parser_G0_3():
    c = Converter(rapid_move_speed_mm_min=1500)
    cmd = c._parse_g_code_line("G0 X1000.42 Z2000.44")

@raises(RuntimeError)
def test_g_code_parser_G0_4():
    c = Converter(rapid_move_speed_mm_min=5000)
    cmd = c._parse_g_code_line("G0")

@raises(ValueError)
def test_g_code_parser_G0_5():
    c = Converter(rapid_move_speed_mm_min=5000)
    cmd = c._parse_g_code_line("G0 X Y300 Z030")

@raises(RuntimeError)
def test_g_code_parser_G0_5():
    c = Converter(rapid_move_speed_mm_min=5000)
    cmd = c._parse_g_code_line("G0 X1 X2 Z3 Y4")

@raises(RuntimeError)
def test_g_code_parser_G0_7():
    c = Converter(rapid_move_speed_mm_min=5000)
    cmd = c._parse_g_code_line("G0 X1 X2 X3")


def test_remove_duplicate_speed():
    c = Converter(rapid_move_speed_mm_min=5000)

    cmds = [EU(10),EU(10),EU(10),EU(0), EU(20), EU(20), EU(10), EU(0), EU(42),EU(42),EU(3)]
    removed_cmds = c._remove_duplicate_speed_commands(cmds)

    assert_equals(removed_cmds[0], EU(10))
    assert_equals(removed_cmds[1], EU(0))
    assert_equals(removed_cmds[2], EU(20))
    assert_equals(removed_cmds[3], EU(10))
    assert_equals(removed_cmds[4], EU(0))
    assert_equals(removed_cmds[5], EU(42))
    assert_equals(removed_cmds[6], EU(3))

if __name__ == '__main__':
    import nose

    nose.runmodule()

# uncomment for coverage report
#    file_path = os.path.abspath(__file__)
#    tests_path =os.path.abspath(os.path.dirname(file_path))
#    result = nose.run(
#        argv=[os.path.abspath(__file__), "--cover-package=xdbi", "--with-cov", "--verbosity=3", "--cover-html", "--cover-html-dir=" + tests_path + "/html", tests_path])
