colors = ["white", "black", "edge"]
from .stone import stone


class board():
    def __init__(self, sizex, sizey, komi=6.5):
        """Initializes a board of a specified size."""
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
        sizex = int(lenx / 2)
        b = cls(sizex, sizey)
        for x in range(sizex):
            for y in range(sizey):
                if lines[y][x * 2] == "W":
                    b.__place__("white", x, y, True)
                elif lines[y][x * 2] == "B":
                    b.__place__("black", x, y, True)
        b.turn = int(meta[1])
        b.komi = float(meta[3])
        b.prisoners['black'], b.prisoners['white'] = map(int, meta[5].split(','))
        return b

    @classmethod
    def from_history(cls, hist):
        size = hist[0]
        hist = hist[1:]
        b = board(*size)
        for move in hist:
            if move[0] == "add":
                b.__place__(*move[1:])
            elif move[0] == "remove":
                b.__remove__(*move[1:])
            else:
                b.place(*move)
        return b

    @classmethod
    def from_sgf(cls, f):
        try:
            f.read
        except:
            f = open(f, 'r')
        lines = f.read().replace('\r', '').replace('\n', '').split(';')
        meta = lines[1]
        size = meta.split('SZ[')[1].split(']')[0]
        komi = meta.split('KM[')[1].split(']')[0]
        if "Japanese" not in meta or "japanese" not in meta or "JAPANESE" not in meta:
            print("Warning: This game may have been in a different ruleset")
        b = cls(int(size), int(size), float(komi))

        def translate_coord(string):
            grid = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
            x = string[0]
            y = string[1]
            return (grid.index(x), grid.index(y))

        for line in lines:
            if 'AB[' == line[:3]:
                coord = translate_coord(line[3:5])
                b.__place__('black', *coord)
                b.move_history += ("add", "black", coord[0], coord[1])
            elif 'AW[' == line[:3]:
                coord = translate_coord(line[3:5])
                b.__place__('white', *coord)
                b.move_history += ("add", "white", coord[0], coord[1])
            elif 'B[' == line[:2]:
                b.place('black', *translate_coord(line[2:4]))
            elif 'W[' == line[:2]:
                b.place('white', *translate_coord(line[2:4]))
            elif 'AE[' == line[:3]:
                coord = translate_coord(line[3:5])
                b.__remove__(*coord)
                b.move_history += ("remove", coord[0], coord[1])
        return b

    def copy(self):
        return board.from_history(self.move_history)

    def __hash__(self):
        """Returns a unique integer for each possible board configuration"""
        return hash((self.__pos__(), tuple(self.move_history)))

    def __eq__(self, comp):
        """Compare move histories, if possible"""
        return hash(self) == hash(comp) and isinstance(comp, type(self))

    def __getitem__(self, coords):
        """Get a stone from a given x/y coordinate. format: board[x, y]"""
        if not isinstance(coords, tuple) or len(coords) != 2:
            raise ValueError("Coordinates must be given as x, y")
        x = coords[0]
        y = coords[1]
        return self.__field__[y][x]

    def __pos__(self):
        """Returns a visual, partly serialized representation of the board positions"""
        string = ""
        symbols = {"white": "W ", "black": "B "}
        for y in range(self.sizey + 1):
            for x in range(self.sizex + 1):
                if not self[x, y]:
                    string += "- "
                else:
                    string += symbols[self[x, y].color]
            string += "\n"
        return string[:-1]  # exclude the last endline

    def __repr__(self, string=None):
        """Returns a visual, mostly serialized representation of the board"""
        if string is None:
            string = self.__pos__()
        string += "\nTurn: " + str(self.turn) + " Komi: " + str(self.komi) + \
                   " Dead: " + str(self.prisoners['black']) + "," + \
                               str(self.prisoners['white'])
        return string

    def highlight(self, group=[]):
        string = self.__pos__().replace('W', 'w').replace('B', 'b')
        lines = string.split('\n')
        high = {"w": "W", "b": "B", "-": "#"}
        for coord in group:
            x = coord[0]
            y = coord[1]
            lines[y] = lines[y][:x*2] + high[lines[y][x*2]] + lines[y][x*2+1:]
        string = ""
        for line in lines:
            string += line + "\n"
        return self.__repr__(string[:-1])

    def __place__(self, color, x, y, turn_override=False):
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
        self.move_history += [(color, x, y, turn_override)]

    def place(self, color, x, y, turn_override=False):
        """Place a stone of a specific color on the board"""
        self.__place__(color, x, y, turn_override)
        return self.process(x, y, turn_override)

    def process(self, x, y, turn_override=False):
        """Process the rules for a specific move"""
        piece = self[x, y]
        exception, msg = None, None
        if piece.color != self.whos_turn() and not turn_override:
            exception, msg = True, "Illegal move--it's not your turn"
        elif piece.is_captured() and True not in [n.is_captured() for n in piece.neighboring_enemies()]:
            exception, msg = True, "Illegal move--this is suicidal"
        elif self.test_ko(x, y):
            exception, msg = True, "Illegal move--ko prevents board loops"
        if exception:
            self.__remove__(x, y)
            self.move_history = self.move_history[:-1]
            raise Exception(msg)
        for i in piece.neighboring_enemies():
            self.prisoners[self.whos_turn()] += i.capture(override=False)
        self.turn += 1
        return True

    def test_placement(self, color, x, y):
        try:
            brd = board.from_history(self.move_history)
            if brd.place(color, x, y, turn_override=True):
                return {'white': brd.prisoners['white'] - self.prisoners['white'],
                        'black': brd.prisoners['black'] - self.prisoners['black']}
            else:
                return False
        except:
            return False

    def __remove__(self, x, y):
        """Remove the piece at the given coordinates"""
        if self[x, y]:
            self[x, y].cleanup()
            self.__field__[y][x] = None
            return True
        return False

    def whos_turn(self):
        return colors[self.turn % 2]

    def score(self, territory=False):
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
        if self[x, y].is_captured() and True in [piece.is_captured() and piece.thickness() == 1 for piece in self[x, y].neighbors()]:
            if self.ko:
                return True
            else:
                self.ko = True
                return False
        self.ko = False
        return False

    def is_surrounded(self, x, y):
        """If a blank group is surrounded, and does not touch three sides, return the set of coordinates. Otherwise return False"""
        if isinstance(self[x, y], stone):
            raise TypeError("Checking stones is not yet supported. Use stone.group_liberties as a proxy")
        to_check = set([(x, y)])
        group = set([(x, y)])
        # First gather a set of the blank stones in question
        while len(to_check):
            next_round = set()
            for test in to_check:
                x = test[0]
                y = test[1]
                for coord in [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]:
                    if coord in group or \
                       coord[0] not in range(0, self.sizex + 1) or \
                       coord[1] not in range(0, self.sizey + 1) or \
                       self[coord]:
                        continue
                    next_round.add(coord)
                group.add(test)
            to_check = next_round
        # If the group touches more than three edges, return False
        xs = [coord[0] for coord in group]
        ys = [coord[1] for coord in group]
        if [0 in xs, self.sizex in xs, 0 in ys, self.sizey in ys].count(True) > 2:
            return False
        del xs, ys
        # Otherwise check all the stones around this group for their color
        to_check = set(group)
        colors = set()
        for test in to_check:
            x = test[0]
            y = test[1]
            for coord in [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]:
                if coord[0] not in range(0, self.sizex + 1) or \
                   coord[1] not in range(0, self.sizey + 1) or \
                   not self[coord]:
                    continue
                colors.add(self[coord].color)
        # Return False if there's multiple colors touching it
        if len(colors) != 1:
            return False
        return group

    def is_eye(self, x, y):
        if self[x, y]:
            return False
        for pos in [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]:
            if pos[0] not in range(0, self.sizex + 1):
                break
            if pos[1] not in range(0, self.sizey + 1):
                break
            if self[pos] and self[pos].is_eye((x, y)):
                return True
        return False

    def get_easily_scored(self):
        group = set()
        for y in range(self.sizey + 1):
            for x in range(self.sizex + 1):
                if (x, y) not in group:
                    if not self[x, y] and self.is_surrounded(x, y):
                        group.update(self.is_surrounded(x, y))
                    elif self[x, y] and not self[x, y].can_be_uncapturable(1, silent=True):
                        group.update([s.coord for s in self[x, y].connected()])
        return group

    def print_easily_scored(self):
        print(self.highlight(self.get_easily_scored()))

    def get_difficult_to_score(self):
        anti_group = self.get_easily_scored()
        group = set()
        for y in range(self.sizey + 1):
            for x in range(self.sizex + 1):
                if (x, y) not in anti_group:
                    group.add((x, y))
        return group

    def print_difficult_to_score(self):
        print(self.highlight(self.get_difficult_to_score()))
