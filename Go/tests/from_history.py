from ..board import board

def test_from_history():
    status = test_from_history_equality()
    return status

def test_from_history_equality():
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
    g = board.from_history(f.move_history)
    return g == f and g is not f
