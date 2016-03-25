colors = ["white", "black", "edge"]
from stone import stone

class board():
    def __init__(self, sizex, sizey, komi=5.5):
        """Initializes a board of a specified size. To enter a known state, use board.from_repr() or board.from_history()"""
        self.sizex = sizex - 1
        self.sizey = sizey - 1
        self.size = str(sizex) + 'x' + str(sizey)
        self.__field__ = []
        for i in range(sizey):
            self.__field__ += [[None for j in range(sizex)]]
        self.turn = 1
        self.prisoners = {'black': 0, 'white': 0}
        self.komi = komi
        self.ko = False
        self.move_history = [(sizex, sizey, komi)]

    @classmethod
    def from_repr(cls, string):
        """Given a string representation of a board, reproduce that board and return it"""
        string = str(string).replace("\r", "")
        lines = string.split("\n")
        meta = lines[len(lines) - 1].split(" ")
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
        b.turn = int(meta[1])
        b.komi = float(meta[3])
        return b

    @classmethod
    def from_history(cls, hist):
        """Given a list of moves and metadata, reconstruct a board. Format: [(sizex, sizey, komi), (color_move_one, x_move_one, y_move_one), ...]"""
        size = hist[0]
        hist = hist[1:]
        b = board(*size)
        for move in hist:
            b.place(*move)
        return b

    def __eq__(self, comp):
        """Compare move histories, if possible; Otherwise return False"""
        try:
            return self.move_history == comp.move_history
        except:
            return False

    def __getitem__(self, coords):
        """Get a stone from a given x/y coordinate. format: board[x, y]"""
        if not isinstance(coords, tuple) or len(coords) != 2:
            raise ValueError("Coordinates must be given as x, y")
        x = coords[0]
        y = coords[1]
        return self.__field__[y][x]

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
        string += "\nTurn: " + str(self.turn) + " Komi: " + str(self.komi) + \
                   " Dead: " + str(self.prisoners['black']) + "," + \
                               str(self.prisoners['white']) + \
                   " Ko: " + str(self.ko)
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
        self.__field__[y][x] = stone(color, left=left, right=right, up=up, 
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
        elif piece.is_captured() and True not in [n.is_captured() for n in piece.neighboring_enemies()]:
            self.remove(x, y)
            raise IndexError("Illegal move--this is suicidal")
        elif self.test_ko(x, y):
            self.remove(x, y)
            raise IndexError("Illegal move--ko prevents board loops")
        for i in piece.neighboring_enemies():
            self.prisoners[self.whos_turn()] += i.capture(override=False)
        self.move_history += [(piece.color, x, y)]
        self.turn += 1
        return True

    def test_placement(self, color, x, y):
        """Forks the board to test a placement without affecting the match"""
        brd = board.from_history(self.move_history)
        return brd.place(color, x, y)

    def remove(self, x, y):
        """Remove the piece at the given coordinates"""
        if self[x, y]:
            self[x, y].cleanup()
            self.__field__[y][x] = None
            return True
        return False

    def whos_turn(self):
        """Returns the color who's turn it is"""
        return colors[self.turn % 2]

    def score(self, territory=False):
        """Attempts to score the board, and returns a dictionary keyed by color"""
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

    def territory_score(self):
        """Scores (incorrectly) by territory, and returns a dictionary keyed by color"""
        grid = [['-' for y in range(self.sizey + 1)] for x in range(self.sizex + 1)]
        for x in range(self.sizex + 1):
            for y in range(self.sizey + 1):
                if self[x, y]:
                    grid[x][y] = self[x, y].color[0]
        for count in range(len(grid) * 2):
            for x in range(len(grid)):
                for y in range(len(grid[0])):
                    if grid[x][y] == "-":
                        neighbors = []
                        neighbors.append(grid[max(0, x-1)][y])                 # left
                        neighbors.append(grid[min(len(grid)-1, x+1)][y])       # right
                        neighbors.append(grid[x][max(0, y-1)])                 # up
                        neighbors.append(grid[x][min(len(grid[0])-1, y+1)])    # down
                        if 'w' in neighbors and 'b' in neighbors:
                            continue
                        elif not ('w' in neighbors or 'b' in neighbors):
                            continue
                        elif 'w' in neighbors:
                            grid[x][y] = 'w'
                        else:
                            grid[x][y] = 'b'
        s = self.prisoners.copy()
        s['white'] += self.komi
        for x in range(len(grid)):
            for y in range(len(grid)):
                if grid[x][y] == 'w':
                    s['white'] += 1
                elif grid[x][y] == 'b':
                    s['black'] += 1
        return s

    def test_ko(self, x, y):
        """Tests whether the ko rule is triggered"""
        if self[x, y].is_captured() and True in [piece.is_captured() and piece.thickness() == 1 for piece in self[x,y].neighboring_enemies()]:
            if self.ko:
                return True
            else:
                self.ko = True
                return False
        self.ko = False
        return False
