from . import capturable
from . import from_history
from . import from_repr
from . import ko
from . import nonterritory_score
from . import num_eyes
from . import relative_positions
from . import suicide

__all__ = ["capturable", "from_history", "from_repr", "ko", "nonterritory_score",
           "num_eyes", "relative_positions", "suicide"]

def run():
    status = from_history.test_from_history()
    status = status and ko.test_ko()
    return status
