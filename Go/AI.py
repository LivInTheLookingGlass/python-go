from .Neural_Network import *
from .player import player
from .server import server

class AI():
	def __init__(self, x, y):
		self.color = "black"
		self.x = x
		self.y = y
		arch = []
		mult = 39
		arch.append((x, y * mult))
		# arch.append(input_len * 2)
		# arch.append(input_len * 5)
		# arch.append((input_len * 5) / 2)
		while mult > 1:
			arch.append((x, y * mult))
			mult = int(round(mult / 2.0))
		arch.append((x, y))
		print(arch)
		print(sum([x * y for x, y in arch]))
		self.predictive_network = Neural_Network(arch, convolutional=mult)

	def train_predictive_network(self, folder, starting_rate=1):
		print "Currently unsupported"

	def train_value_network(self, folder, starting_rate=1):
		print "Currently unsupported"

	def train_system_of_systems(self, starting_rate=1):
		print "Currently unsupported"

	def decide_move(self, board):
		inputs = []
		for pos in [(x, y) for x in range(board.sizex + 1) for y in range(board.sizey + 1)]:
			inputs.append(int(bool(board[pos]) and board[pos].color == self.color))
			inputs.append(int(bool(board[pos]) and board[pos].color != self.color))
			inputs.append(int(not board[pos]))
			inputs.append(1)
			for i in range(1,9):
				inputs.append(int(len(board.move_history) > i and board.move_history[-i][1:3] == pos))
			if board[pos]:
				libs = sum([stone.liberties() for stone in board[pos].connected()]) - 3 * stone.num_eyes()
				for i in range(8):
					inputs.append(libs & 2**i)
			else:
				inputs.extend([0] * 8)
			results = board.test_placement(self.color, pos[0], pos[1])
			if not results:
				inputs.extend([0] * 8)
			else:
				prisoners = results.pop(self.color)
				for i in range(8):
					inputs.append(prisoners & 2**i)
			if board[pos] or not board.test_placement(self.color, pos[0], pos[1]):
				inputs.extend([0] * 8)
			else:
				brd = board.copy()
				brd.place(self.color, pos[0], pos[1], True)
				libs = sum([stone.liberties() for stone in brd[pos].connected()]) - 3 * stone.num_eyes()
				del brd
				for i in range(8):
					inputs.append(libs & 2**i)
			inputs.append(int(board.test_placement(self.color, pos[0], pos[1]) and not board.is_eye(pos[0], pos[1])))
			inputs.append(0)
			inputs.append(int(self.color == "black"))
		likely_moves = self.predictive_network.feed(inputs)
		sorted_moves = [(move, pos) for move, pos in zip(likely_moves, [(x, y) for x in range(self.x) for y in range(self.y)])]
		shellSort(sorted_moves)
		del likely_moves
		legal_moves = []
		for move in sorted_moves:
			if board.test_placement(self.color, move[1][0], move[1][1]):
				legal_moves.append(move)
				if len(legal_moves) > 5:
					break
		del sorted_moves
		import itertools, random
		move = random.choice(list(itertools.chain.from_iterable([[b] * (len(legal_moves) - legal_moves.index(b)) for b in legal_moves])))
		# This makes a random move from a weighted list. If the list has moves of probabilities [0.3, 0.2, 0.15, 0.14, 0.1],
		# The weighted list will look like: [0.3, 0.3, 0.3, 0.3, 0.3, 0.2, 0.2, 0.2, 0.2, 0.15, 0.15, 0.15, 0.14, 0.14, 0.1]
		# This allows for some variability in how the AI plays, while still tending towards the best moves available to it
		return move[1]


def shellSort(array):
    "Shell sort using Shell's (original) gap sequence: n/2, n/4, ..., 1."
    gap = len(array) // 2
    # loop over the gaps
    while gap > 0:
        # do the insertion sort
        for i in range(gap, len(array)):
            val = array[i]
            j = i
            while j >= gap and array[j - gap][0] > val[0]:
            	array[j] = array[j - gap]
            	j -= gap
            array[j] = val
        gap //= 2