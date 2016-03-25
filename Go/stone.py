class stone():
    def __init__(self, color, left=None, right=None, up=None, down=None, board=None, coord=(None,None)):
        self.color = color
        if color == 'white':
            self.opposite_color = 'black'
        elif color == 'black':
            self.opposite_color = 'white'
        self.left = left
        if left:
            self.left.right = self
        self.right = right
        if right:
            self.right.left = self
        self.up = up
        if up:
            self.up.down = self
        self.down = down
        if down:
            self.down.up = self
        self.board = board
        self.coord = coord
        
    def __repr__(self):
        string = "<" + self.color + " stone:"
        if self.coord != (None, None):
            string += " coords=" + str(self.coord)
        string += " liberties=" + str(self.liberties())
        if self.left:
            string += " left=" + self.left.color
        if self.right:
            string += " right=" + self.right.color
        if self.up:
            string += " up=" + self.up.color
        if self.down:
            string += " down=" + self.down.color
        return string + ">"
    
    def __del__(self):
        self.cleanup()

    def neighbors(self):
        n = []
        if self.left:
            n += [self.left]
        if self.right:
            n += [self.right]
        if self.up:
            n += [self.up]
        if self.down:
            n += [self.down]
        return n

    def neighboring_enemies(self):
        n = []
        if self.left and self.left.color != self.color:
            n += [self.left]
        if self.right and self.right.color != self.color:
            n += [self.right]
        if self.up and self.up.color != self.color:
            n += [self.up]
        if self.down and self.down.color != self.color:
            n += [self.down]
        return n
            
    def liberties(self):
        return 4 - len(self.neighbors())
    
    def connected(self, so_far=[]):
        conn = so_far + [self]
        for i in self.neighbors():
            if i and i.color == self.color and i not in conn:
                conn = i.connected(so_far=conn)
        return conn
    
    def thickness(self):
        return len(self.connected())
    
    def is_captured(self):
        for i in self.connected():
            if i.liberties():
                return False
        return True
    
    def capture(self, override=False):
        if self.is_captured() or override:
            count = 0
            for i in self.connected():
                count += 1
                if i.board:
                    i.board.remove(*i.coord)
                else:
                    i.__del__()
            return count
        return 0

    def cleanup(self):
        if self.left:
            if self.left.color == "edge":
                del self.left
            else:
                self.left.right = None
        if self.right:
            if self.right.color == "edge":
                del self.right
            else:
                self.right.left = None
        if self.up:
            if self.up.color == "edge":
                del self.up
            else:
                self.up.down = None
        if self.down:
            if self.down.color == "edge":
                del self.down
            else:
                self.down.up = None

    def empty_neighbors(self):
        if self.coord != (None, None):
            ret = []
            if not self.left:
                ret.append((self.coord[0] - 1, self.coord[1]))
            if not self.right:
                ret.append((self.coord[0] + 1, self.coord[1]))
            if not self.up:
                ret.append((self.coord[0], self.coord[1] - 1))
            if not self.down:
                ret.append((self.coord[0], self.coord[1] + 1))
            return ret
        return False

    def is_capturable(self):
        if self.num_eyes() >= 2:
            return False
        # Otherwise try asking the board
        elif self.board:
            stones = self.connected()
            tests = set()
            for stone in stones:
                for i in stone.empty_neighbors():
                    tests.add(i)
            count = 0
            for test in tests:
                try:
                    if not self.board.test_placement(self.opposite_color, test[0], test[1]):
                        count += 1
                except:
                    count += 1
            return count < 2
        else:
            return True        

    def num_eyes(self):
        stones = self.connected()
        count = 0
        to_check = set()
        for stone in stones:
            for coord in stone.empty_neighbors():
                to_check.add(coord)
        for coord in to_check:
            if self.is_eye(coord, stones):
                count += 1
        return count

    def is_eye(self, coord, stones=None):
        # Begin setup
        if not stones:
            stones = self.connected()
        right_edge, down_edge = 0, 0
        if self.board:
            right_edge = self.board.sizex + 2
            down_edge = self.board.sizey + 2
        else:
            for stone in stones:
                if stone.right and stone.right.color == 'edge':
                    right_edge = stone.right.coord[0]
                    break
                elif stone.coord[0] > right_edge:
                    right_edge = stone.coord[0]
            for stone in stones:
                if stone.down and stone.down.color == 'edge':
                    down_edge = stone.down.coord[1]
                    break
                elif stone.coord[1] > down_edge:
                    down_edge = stone.coord[1]
        neighbors = [(coord[0] - 1, coord[1]),
                     (coord[0] + 1, coord[1]),
                     (coord[0], coord[1] - 1),
                     (coord[0], coord[1] + 1)]
        good = []
        # Begin checking
        for i in neighbors:
            if i in [s.coord for s in stones]:
                good.append(i)
        if len(good) == 4:
            return True
        elif len(good) < 2:
            return False
        else:
            for i in good:
                neighbors.remove(i)
            if len(neighbors) == 2 and (neighbors[0][0] == neighbors[1][0] or neighbors[0][1] == neighbors[1][1]):
                return False
            for i in neighbors:
                if i[0] not in range(-1, right_edge + 1) or i[1] not in range(-1, down_edge + 1):
                    return False
                elif i[0] in range(0, right_edge) and i[1] in range(0, down_edge):
                    return False
        return True
