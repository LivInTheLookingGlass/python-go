colors = ["white", "black", "edge"]
from .stone import stone

class board():
    def __init__(self, sizex, sizey):
        """Initializes a board of a specified size. To enter a known state, use board.from_repr()"""
        self.sizex = sizex - 1
        self.sizey = sizey - 1
        self.size = str(sizex) + 'x' + str(sizey)
        self.field = []
        for i in range(sizey):
            self.field += [[None for j in range(sizex)]]
        self.ko = (None, None)
        self.next_ko = (None, None)
        self.turn = 1
        self.prisoners = {'black': 0, 'white': 0}
        self.komi = 5.5
        self.prev_board = ""
        self.prev_prev_board = ""

    @classmethod
    def from_repr(cls, string):
        """Given a string representation of a board, reproduce that board and return it"""
        string = str(string).replace("\r", "")
        lines = string.split("\n")
        turn = int(lines[len(lines) - 1][5:])
        lines = lines[:-1]
        lenx = len(lines[0])
        for line in lines:
            if len(line) != lenx:
                raise Exception("string is not in correct format")
        sizey = len(lines)
        sizex = lenx / 2
        b = cls(sizex, sizey)
        for x in range(sizex):
            for y in range(sizey):
                if lines[y][x * 2] == "W":
                    b.__place__("white", x, y)
                elif lines[y][x * 2] == "B":
                    b.__place__("black", x, y)
        b.turn = turn
        return b

    def __eq__(self, comp):
        """Since these are string reconstructable, compare their strings"""
        return str(self) == str(comp)

    def __getitem__(self, coords):
        """Get a stone from a given x/y coordinate. format: board[x, y]"""
        if not isinstance(coords, tuple) or len(coords) != 2:
            raise ValueError("Coordinates must be given as x, y")
        x = coords[0]
        y = coords[1]
        return self.field[y][x]

    def __pos__(self):
        """Returns a visual, partially-serialized representation of the board positions"""
        string = ""
        for y in range(self.sizey + 1):
            for x in range(self.sizex + 1):
                if not self[x, y]:
                    string += "- "
                elif self[x, y].color == "white":
                    string += "W "
                elif self[x, y].color == "black":
                    string += "B "
            string += "\n"
        return string[:-1]  # exclude the last endline

    def __repr__(self):
        """Returns a visual, serialized representation of the board"""
        string = self.__pos__()
        string += "\nTurn: " + str(self.turn)
        return string

    def __place__(self, color, x, y):
        """Place a stone without considering rules"""
        if self[x, y]:
            raise IndexError("Illegal move--there's already a piece there")
        if x > 0:
            left = self[x-1, y]
        else:
            left = stone("edge")
        if x < self.sizex:
            right = self[x+1, y]
        else:
            right = stone("edge")
        if y > 0:
            up = self[x, y-1]
        else:
            up = stone("edge")
        if y < self.sizey:
            down = self[x, y+1]
        else:
            down = stone("edge")
        self.field[y][x] = stone(color, left=left, right=right, up=up, 
                                  down=down, board=self, coord=(x, y))

    def place(self, color, x, y, turn_override=False):
        """Place a stone of a specific color on the board"""
        self.__place__(color, x, y)
        return self.process(x, y, turn_override)

    def process(self, x, y, turn_override=False):
        """Process the rules for a specific move"""
        piece = self[x, y]
        if piece.color != self.whos_turn() and not turn_override:
            self.remove(x, y)
            raise Exception("Illegal move--it's not your turn")
        elif self.test_ko(x, y):
            self.remove(x, y)
            raise IndexError("Illegal move--ko prevents board loops")
        elif piece.is_captured() and True not in [n.is_captured() for n in piece.neighboring_enemies()]:
            self.remove(x, y)
            raise IndexError("Illegal move--this is suicidal")
        for i in piece.neighboring_enemies() + [piece]:
            self.prisoners[self.whos_turn()] += i.capture(override=False)
        self.ko = self.next_ko
        self.next_ko = (x, y)
        self.prev_prev_board = self.prev_board
        self.prev_board = self.__pos__()
        self.turn += 1
        return True

    def remove(self, x, y):
        """Remove the piece at the given coordinates"""
        if self[x, y]:
            self[x, y].cleanup()
            self.field[y][x] = None
            return True
        return False

    def whos_turn(self):
        """Returns the color who's turn it currently is"""
        return colors[self.turn % 2]

    def score(self, territory=False):
        """Returns the current score"""
        if territory:
            print("Territory scoring is not fully supported, but we'll count what's on the board")
            s = self.score(False)
            for x in range(self.sizex + 1):
                for y in range(self.sizey + 1):
                    if self[x, y]:
                        s[self[x, y].color] += 1
            return s
        else:
            s = self.prisoners.copy()
            s['white'] += self.komi
            return s

    def test_ko(self, x, y):
        """Tests to see if the Ko rule has been violated on a safe copy of the board"""
        b = board.from_repr(str(self))
        piece = b[x, y]
        if piece.color != b.whos_turn() and not turn_override:
            b.remove(x, y)
            raise Exception("Illegal move--it's not your turn")
        elif piece.is_captured() and True not in [n.is_captured() for n in piece.neighbors()]:
            b.remove(x, y)
            raise IndexError("Illegal move--this is suicidal")
        for i in piece.neighbors() + [piece]:
            self.prisoners[b.whos_turn()] += i.capture(override=False)
        return b.__pos__() == self.prev_prev_board
