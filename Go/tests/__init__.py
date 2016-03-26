from . import capturable
from . import from_history
from . import from_repr
from . import ko
from . import nonterritory_score
from . import num_eyes
from . import relative_positions
from . import suicide

__all__ = ["capturable", "from_history", "from_repr", "ko", 
           "nonterritory_score", "num_eyes", "relative_positions", "suicide"]

def run():
    import multiprocessing
    tests = [from_history.test_from_history,
             from_repr.test_from_repr,
             ko.test_ko]
    status = False not in multiprocessing.Pool().map(wrapper, tests)
    return status

def wrapper(func):
    return func()
