from .board import board
import asynchat
import asyncore
import json
import socket
import threading
import sys
if sys.version_info[0] >= 3:
    from queue import Queue
else:
    from Queue import Queue

sep_sequence = "\x1c\x1d\x1e\x1f"
end_sequence = sep_sequence[::-1]

class player():
    def __init__(self, host, port):
        self.in_queue = Queue()
        self.out_queue = Queue()
        self.server = ChatClient(host, port, self.out_queue, self.in_queue)
        self.comm = None
        self.board = None
        self.color = "spectator"

    def start(self):
        self.comm = threading.Thread(target=asyncore.loop)
        self.comm.daemon = True
        self.comm.start()

    def process_queue(self):
        import time
        time.sleep(0.1)
        while not self.in_queue.empty():
            msg = self.in_queue.get()
            req = msg.split(sep_sequence)
            print(req[0] + ": " + str(req[1:]))
            if req[0] == "history":
                self.board = board.from_history(json.loads(req[1]))
            elif req[0] == "be_player":
                self.color = req[1]

    def chat(self, msg):
    	self.out_queue.put("chat" + sep_sequence + str(msg) + end_sequence)
    	self.process_queue()

    def send(self, msg):
        self.out_queue.put(str(msg) + end_sequence)
        self.process_queue()

    def get_board(self):
        self.send("history")

    def join_game(self):
        self.send("be_player")
        if self.color in ["black", "white"]:
        	self.get_board()

    def make_move(self, x, y):
    	if self.color not in ["black", "white"]:
    		raise Exception("You are not a participant in this game")
    	if self.board.test_placement(self.color, x, y):
    		grid = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    		sx, sy = grid[x], grid[y]
    		self.send("move" + sep_sequence + sx + sep_sequence + sy)


class ChatClient(asynchat.async_chat):
    def __init__(self, host, port, in_queue, out_queue):
        asynchat.async_chat.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect((host, port))
        self.set_terminator(end_sequence)
        self.buffer = []
        self.out_queue = out_queue
        self.in_queue = in_queue
 
    def collect_incoming_data(self, data):
        self.buffer.append(data)
 
    def found_terminator(self):
        msg = ''.join(self.buffer)
        # print('Received:', msg)
        self.buffer = []
        self.out_queue.put(msg)

    def writable(self):
        while not self.in_queue.empty():
            msg = self.in_queue.get()
            self.push(msg)
        return True
