from Cnc import CNC
from nose.tools import assert_equals, assert_raises, raises, assert_greater, assert_true
import numpy as np


def test_build_moves():
    c = CNC()
    c.single_move_limit = 10

    start = np.array([1, 3, 7])
    end = np.array([30, 19, 12])

    moves = c._CNC__calc_moves(start, end)
    result = c._CNC__build_absolute_move_commands(moves)
    print(result)


def test_build_multiple_moves():
    c = CNC()
    c.single_move_limit = 1000

    start = np.array([0, 0, 0])
    end = np.array([100000, 19000, 12000])

    moves = c._CNC__calc_moves(start, end)
    result = c._CNC__build_absolute_move_commands(moves)
    print(result)


def test_mark3d2d():
    c = CNC()
    c.single_move_limit = 1000

    moves = np.array([[1, 1, 1],
                      [1, 1, 1],
                      [1, 1, 2],
                      [1, 1, 2],
                      [1, 1, 2],
                      [1, 1, 3],
                      [1, 1, 4],
                      [1, 1, 5],
                      [1, 1, 6],
                      [1, 1, 7],
                      [1, 1, 7],
                      [1, 1, 7]])

    marked_moves = c._CNC__mark3d2d(moves)

    assert_equals(len(marked_moves), 6)

    for i, move in enumerate(marked_moves):
        if i % 2 == 0:
            assert_equals(move[0], 3)
        else:
            assert_equals(move[0], 2)

    assert_equals(len(marked_moves[0][1]), 1)
    assert_equals(len(marked_moves[1][1]), 1)
    assert_equals(len(marked_moves[2][1]), 1)
    assert_equals(len(marked_moves[3][1]), 2)
    assert_equals(len(marked_moves[4][1]), 5)
    assert_equals(len(marked_moves[5][1]), 2)


    assert_true(np.array_equal(marked_moves[0][1][0], np.array([1,1,1])))

    assert_true(np.array_equal(marked_moves[1][1][0], np.array([1, 1, 1])))

    assert_true(np.array_equal(marked_moves[2][1][0], np.array([1, 1, 2])))

    assert_true(np.array_equal(marked_moves[3][1][0], np.array([1, 1, 2])))
    assert_true(np.array_equal(marked_moves[3][1][1], np.array([1, 1, 2])))

    assert_true(np.array_equal(marked_moves[4][1][0], np.array([1, 1, 3])))
    assert_true(np.array_equal(marked_moves[4][1][1], np.array([1, 1, 4])))
    assert_true(np.array_equal(marked_moves[4][1][2], np.array([1, 1, 5])))
    assert_true(np.array_equal(marked_moves[4][1][3], np.array([1, 1, 6])))
    assert_true(np.array_equal(marked_moves[4][1][4], np.array([1, 1, 7])))

    assert_true(np.array_equal(marked_moves[5][1][0], np.array([1, 1, 7])))


def test_mark3d2d_empty():
    c = CNC()
    c.single_move_limit = 1000
    moves = np.array([])
    marked_moves = c._CNC__mark3d2d(moves)
    assert_equals(len(marked_moves), 0)


def test_mark3d2d_simple():
    c = CNC()
    c.single_move_limit = 1000
    moves = np.array([[1,2,3]])
    marked_moves = c._CNC__mark3d2d(moves)
    assert_equals(len(marked_moves), 1)
    assert_equals(marked_moves[0][0], 3)
    assert_true(np.array_equal(marked_moves[0][1][0],  np.array([1,2,3])))


def test_convert2d_moves_empty():
    c = CNC()
    moves = np.array([])
    cmds = c._CNC__convert_2d_moves_to_commands(moves)
    assert_equals(len(cmds), 0)


def test_convert2d_moves_simple():
    c = CNC()
    moves = np.array([[1,2,3]])
    cmds = c._CNC__convert_2d_moves_to_commands(moves)
    assert_equals(len(cmds), 1)
    assert_equals(cmds[0], "PA1,2;")


def test_convert2d_moves():
    c = CNC()
    moves = np.array([[1,2,3],
                      [2,3,4],
                      [4,5,3],
                      [5,6,3],
                      [6,7,3],
                      [7,8,3],
                      [8,9,3]])
    cmds = c._CNC__convert_2d_moves_to_commands(moves)
    assert_equals(len(cmds), 1)
    assert_equals(cmds[0], "PA1,2,2,3,4,5,5,6,6,7,7,8,8,9;")

def test_convert2d_moves_long():
    c = CNC()
    moves = np.array([[100000,200000,3],
                      [200000,300000,3],
                      [400000,500000,3],
                      [500000,600000,3],
                      [600000,700000,3],
                      [700000,800000,3],
                      [800000,900000,3],
                      [900000,1000000,3],
                      [1000000,1100000,3],
                      [1100000,1200000,3],
                      [1200000,1300000,3],
                      [1300000,1400000,3],
                      [1400000,1500000,3]])
    cmds = c._CNC__convert_2d_moves_to_commands(moves)
    assert_equals(len(cmds), 3)
    for cmd in cmds:
        assert_true(len(cmd) <= 77)

    assert_equals(cmds[0], 'PA100000,200000,200000,300000,400000,500000,500000,600000,600000,700000;')
    assert_equals(cmds[1], 'PA700000,800000,800000,900000,900000,1000000,1000000,1100000;')
    assert_equals(cmds[2], 'PA1100000,1200000,1200000,1300000,1300000,1400000,1400000,1500000;')




def test_convert3d_moves_empty():
    c = CNC()
    c.single_move_limit = 5000

    moves = np.array([])
    cmds = c._CNC__convert_3d_moves_to_commands(moves)
    assert_equals(len(cmds), 0)


def test_convert3d_moves_simple():
    c = CNC()
    c.single_move_limit = 5000

    moves = np.array([[10,20,330]])
    cmds = c._CNC__convert_3d_moves_to_commands(moves)
    assert_equals(len(cmds), 1)
    assert_equals(cmds[0], "MA10,20,330;")


def test_convert3d_moves_long():
    c = CNC()
    c.single_move_limit = 5000

    moves = np.array([[1000,2000,330],
                      [3000,5000,700],
                      [4000,7000,900],
                      [5000,9000,1200],
                      [7000,10000,1500],
                      [8000,9000,2200],
                      [10000,8000,2500]
                      ])
    cmds = c._CNC__convert_3d_moves_to_commands(moves)
    assert_equals(len(cmds), 2)
    assert_equals(cmds[0], 'MA1000,2000,330,3000,5000,700,4000,7000,900,5000,9000,1200,7000,10000,1500;')
    assert_equals(cmds[1], 'MA8000,9000,2200,10000,8000,2500;')

def test_convert3d_moves_long_split():
    c = CNC()
    c.single_move_limit = 1000

    moves = np.array([[0,0,0],
                      [1000,2000,330],
                      [3000,5000,700],
                      [4000,7000,900],
                      [5000,9000,1200],
                      [7000,10000,1500],
                      [8000,9000,2200],
                      [10000,8000,2500]
                      ])
    cmds = c._CNC__convert_3d_moves_to_commands(moves)
    assert_equals(len(cmds), 4)
    # TODO do real asserts


def test_convert_positions_to_commands():
    c = CNC()
    c.single_move_limit = 1000

    moves = np.array([[1000,2000,330],
                      [3000,5000,700],
                      [4000,7000,900],
                      [5000,9000,900],
                      [7000,10000,900],
                      [8000,9000,2500],
                      [10000,8000,2500]
                      ])
    cmds = c._CNC__convert_positions_to_commands(moves)
    print(cmds)

def test_load_g_code():
    c = CNC()

    gcode = [
        'G1 X12.34 Y34.56 Z42.42 F300.42',
        'G1 X22.24 Y35.56 Z43.42 F301.42',
        'G1 X32.34 Y36.56 Z44.42 F302.4233',
        'G1 X42.44 Y37.56 Z45.42 F303.4222',

    ]

    positions = c.load_g_code(gcode)
    print(positions)

if __name__ == '__main__':
    import nose

    nose.runmodule()

# uncomment for coverage report
#    file_path = os.path.abspath(__file__)
#    tests_path =os.path.abspath(os.path.dirname(file_path))
#    result = nose.run(
#        argv=[os.path.abspath(__file__), "--cover-package=xdbi", "--with-cov", "--verbosity=3", "--cover-html", "--cover-html-dir=" + tests_path + "/html", tests_path])
