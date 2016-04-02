from ..board import board

standard =  [(13, 13, 6.5), ('black', 1, 0), ('white', 2, 0), ('black', 0, 1), ('white', 3, 1), 
                            ('black', 1, 2), ('white', 2, 2), ('black', 2, 1), ('white', 1, 1)]
exception = [(13, 13, 6.5), ('black', 1, 0), ('white', 2, 0), ('black', 0, 1), ('white', 3, 1), 
                            ('black', 2, 1), ('white', 1, 2), ('black', 0, 2), ('white', 1, 1),
                            ('black', 3, 2), ('white', 5, 5), ('black', 1, 3), ('white', 4, 5), 
                            ('black', 2, 3)]

def test_ko():
    status = test_ko_activation()
    status = status and test_ko_resolution()
    status = status and test_ko_exception()
    return status

def test_ko_activation():
    f = board.from_history(standard)
    try:
        f.place('black', 2, 1)
    except Exception as e:
        return e.args[0] == "Illegal move--ko prevents board loops"
    return False

def test_ko_resolution():
    f = board.from_history(standard)
    f.place('black', 5, 5)
    f.place('white', 4, 5)
    try:
        f.place('black', 2, 1)
    except Exception as e:
        return e.args[0] != "Illegal move--ko prevents board loops"
    return True

def test_ko_exception():
    f = board.from_history(exception)
    try:
        f.place('white', 2, 2)
        f.place('black', 2, 1)
    except Exception as e:
        return e.args[0] != "Illegal move--ko prevents board loops"
    return True
