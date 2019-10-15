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



if __name__ == '__main__':
    import nose

    nose.runmodule()

# uncomment for coverage report
#    file_path = os.path.abspath(__file__)
#    tests_path =os.path.abspath(os.path.dirname(file_path))
#    result = nose.run(
#        argv=[os.path.abspath(__file__), "--cover-package=xdbi", "--with-cov", "--verbosity=3", "--cover-html", "--cover-html-dir=" + tests_path + "/html", tests_path])
