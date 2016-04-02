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
        n = [self.left, self.right, self.up, self.down]
        while n.count(None):
            n.remove(None)
        return n

    def neighboring_enemies(self):
        n = self.neighbors()
        remove = []
        for stone in n:
            if stone.color != self.color:
                remove.append(stone)
        for stone in remove:
            n.remove(stone)
        return n
            
    def liberties(self):
        return 4 - len(self.neighbors())
    
    def connected(self, so_far=[]):
        conn = so_far + [self]
        for i in self.neighbors():
            if i and i.color == self.color and i not in conn:
                conn = i.connected(so_far=conn)
        return conn

    def all_connected(self, so_far=[]):
        conn = so_far + [self]
        for i in self.neighbors():
            if i not in conn:
                conn = i.all_connected(so_far=conn)
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
                    i.board.__remove__(*i.coord)
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
        if self.coord == (None, None):
            self.map_relative_positions()
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

    def is_capturable(self):
        if self.num_eyes() >= 2:
            # Groups with two+ eyes are not capturable
            return False
        elif self.board:
            # Otherwise try asking the board if the capturing placements are suicidal/legal
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

    def map_relative_positions(self, first=True, set_origin=True, start_pos=(0, 0)):
        """When there isn't a board in place, set relative coordinates according to the stone network"""
        if self.board:
            # If there's a board, they'll manage this
            return
        if first:
            # First reset the coordinates of all stones
            for stone in self.all_connected():
                stone.coord = (None, None)
        if set_origin:
            # Set yourself as the origin
            self.coord = start_pos
        if self.left:
            # If the stone to your left is an edge, make yourself x = 0
            if self.left.color == 'edge':
                self.coord = (0, self.coord[1])
            # If the stone to your left has the wrong coordinates, correct it and recurse
            if self.left.coord != (self.coord[0] - 1, self.coord[1]):
                self.left.coord = (self.coord[0] - 1, self.coord[1])
                self.left.map_relative_positions(first=False, set_origin=False)
        if self.right:
            # If the stone to your right has the wrong coordinates, correct it and recurse
            if self.right.coord != (self.coord[0] + 1, self.coord[1]):
                self.right.coord = (self.coord[0] + 1, self.coord[1])
                self.right.map_relative_positions(first=False, set_origin=False)
        if self.up:
            # If the stone above you is an edge, make yourself y = 0
            if self.up.color == 'edge':
                self.coord = (self.coord[0], 0)
            # If the stone above you has the wrong coordinates, correct it and recurse
            if self.up.coord != (self.coord[0], self.coord[1] - 1):
                self.up.coord = (self.coord[0], self.coord[1] - 1)
                self.up.map_relative_positions(first=False, set_origin=False)
        if self.down:
            # If the stone below you has the wrong coordinates, correct it and recurse
            if self.down.coord != (self.coord[0], self.coord[1] + 1):
                self.down.coord = (self.coord[0], self.coord[1] + 1)
                self.down.map_relative_positions(first=False, set_origin=False)
        if first:
            # If you were the first, make sure the left and upward edges are 0
            leftmost = self
            upmost = self
            for stone in self.all_connected():
                if leftmost.coord[0] > stone.coord[0]:
                    leftmost = stone
                if upmost.coord[1] > stone.coord[1]:
                    upmost = stone
            if leftmost.color != 'edge' and leftmost.coord[0] != 0:
                # Unless it's already correct...
                leftmost.map_relative_positions(first=False, set_origin=True, start_pos=(0, leftmost.coord[1]))
            if upmost.color != 'edge' and upmost.coord[1] != 0:
                # Unless it's already correct...
                upmost.map_relative_positions(first=False, set_origin=True, start_pos=(upmost.coord[0], 0))

    def num_eyes(self):
        return len(self.get_eyes())

    def get_eyes(self):
        stones = self.connected()
        eyes = set()
        to_check = set()
        # If you aren't associated with a board, make sure coords are correct
        if not self.board:
            self.map_relative_positions()
        # Collect a list of all empty positions next to/within your grouping
        for stone in stones:
            for coord in stone.empty_neighbors():
                to_check.add(coord)
        # For each of the unique candidates, count if they're an eye
        for coord in to_check:
            if self.is_eye(coord, stones):
                eyes.add(coord)
        return list(eyes)

    def is_eye(self, coord, stones=None):
        # Begin setup
        if not stones:
            stones = self.connected()
        right_edge, down_edge = 0, 0
        if self.board:
            # If there's a board, it knows the edges
            right_edge = self.board.sizex + 2
            down_edge = self.board.sizey + 2
        else:
            # Otherwise, map your relative positions
            self.map_relative_positions()
            for stone in stones:
                # Then find the stones farthest to the right and downward
                if stone.coord[0] > right_edge:
                    right_edge = stone.coord[0]
                if stone.coord[1] > down_edge:
                    down_edge = stone.coord[1]
        # Now that we have the coordinates and bounds, grab the eye's neighbors
        neighbors = [(coord[0] - 1, coord[1]),
                     (coord[0] + 1, coord[1]),
                     (coord[0], coord[1] - 1),
                     (coord[0], coord[1] + 1)]
        good = []
        # Begin checking
        for i in neighbors:
            if i in [s.coord for s in stones]:
                # If there's a connected stone in the neighboring spot, mark the spot as good
                good.append(i)
        if len(good) == 4:
            # If all four are good, it's an eye for sure
            return True
        elif len(good) < 2:
            # If there's fewer than two surrounding stones of the same color, it's for sure not
            return False
        else:
            # Otherwise we need to check edges
            for i in good:
                neighbors.remove(i)
            if len(neighbors) == 2 and (neighbors[0][0] == neighbors[1][0] or neighbors[0][1] == neighbors[1][1]):
                return False
            for i in neighbors:
                # Short version: If the position is not just outside the board, return False
                # This returns false positives if the stones are not on a board and have no connected edge
                if i[0] not in range(-1, right_edge + 1) or i[1] not in range(-1, down_edge + 1):
                    return False
                elif i[0] in range(0, right_edge) and i[1] in range(0, down_edge):
                    return False
        return True

    def can_be_uncapturable(self, moves, passed_board=None, silent=False):
        """Serially brute forces every combination of moves up to x to see if a group can be made uncapturable
        Warning: This is blocking, and can take a long time at depths >= 4
        Warning: This makes a copy of the board for each level of depth"""
        if not passed_board:
            # Inherit the object's board
            passed_board = self.board
        if not passed_board:
            # If the object has no board...
            raise ValueError("You can't call this without an associated board")
        if not passed_board[self.coord].is_capturable():
            # If the current configuration is uncapturable, you're done
            if not silent:
                print(passed_board)
            return True
        if moves > 0:
            # If you have moves left, recurse for every move to a direct neighbor
            from .board import board
            coords = set()
            for s in passed_board[self.coord].connected():
                for coord in s.empty_neighbors():
                    coords.add(coord)
            for coord in coords:
                b = board.from_history(passed_board.move_history)
                try:
                    b.place(self.color, coord[0], coord[1], turn_override=True)
                except:
                    return False
                if self.can_be_uncapturable(moves - 1, b, silent):
                    return True
        # Otherwise return False
        return False
