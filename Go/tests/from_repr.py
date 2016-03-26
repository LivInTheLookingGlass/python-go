from ..board import board

def test_from_repr():
    status = test_from_repr_setting()
    status = status and test_from_repr_inequality()
    return status

def test_from_repr_setting():
    f = board(13, 13)
    f.place('black', 1, 0)
    f.place('white', 2, 0)
    f.place('black', 0, 1)
    f.place('white', 3, 1)
    f.place('black', 2, 1)
    f.place('white', 1, 2)
    f.place('black', 0, 2)
    f.place('white', 1, 1)
    f.place('black', 3, 2)
    f.place('white', 5, 5)
    g = board.from_repr(str(f))
    status = f.komi == g.komi
    status = status and f.prisoners == g.prisoners
    status = status and f.__pos__() == g.__pos__()
    status = status and f.turn == g.turn
    status = status and f.size == g.size
    return status

def test_from_repr_inequality():
    f = board(13, 13)
    f.place('black', 1, 0)
    f.place('white', 2, 0)
    f.place('black', 0, 1)
    f.place('white', 3, 1)
    f.place('black', 2, 1)
    f.place('white', 1, 2)
    f.place('black', 0, 2)
    f.place('white', 1, 1)
    f.place('black', 3, 2)
    f.place('white', 5, 5)
    g = board.from_repr(str(f))
    return g != f and g is not f
