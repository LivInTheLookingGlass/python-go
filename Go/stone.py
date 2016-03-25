class stone():
    def __init__(self, color, left=None, right=None, up=None, down=None, board=None, coord=(None,None)):
        self.color = color
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
