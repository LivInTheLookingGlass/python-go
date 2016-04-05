from .board import board
import asynchat
import asyncore
import json
import socket

chat_room = {}
handlers = []

sep_sequence = "\x1c\x1d\x1e\x1f"
end_sequence = sep_sequence[::-1]


class server():
    def __init__(self, x, y, komi=6.5, port=44444):
        self.chat = ChatServer("0.0.0.0", port, self)
        self.board = board(x, y, komi)
        self.state = "SETUP"
        self.black = None
        self.white = None
        self.spectator = None

    def start(self):
        if self.state == "SETUP":
            self.state = "LIVE"
            asyncore.loop(map=chat_room)
            return True
        return False

    def color(self, player):
        if player == self.white:
            return "white"
        elif player == self.black:
            return "black"
        else:
            return False

    def make_move(self, color, x, y):
        try:
            return str(self.board.place(color, x, y))
        except Exception as e:
            return str(e.args[0])

    def process_player_request(self, player, req):
        if req[0] == 'move':
            grid = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
            x = req[1]
            y = req[2]
            move = self.make_move(self.color(player), grid.index(x), grid.index(y))
            player.snd(req[0] + sep_sequence + str(move))
            if move == 'True':
                board = json.dumps(self.board.move_history)
                for client in handlers:
					client.snd("history" + sep_sequence + board)
        else:
            self.process_spectator_request(player, req)

    def process_spectator_request(self, handler, req):
        if req[0] in ["score", "territorial_score"]:
            handler.snd(req[0] + sep_sequence + str(self.board.score(req[0] == "territorial_score")))
        elif req[0] == "history":
            handler.snd(req[0] + sep_sequence + json.dumps(self.board.move_history, 0))
        elif req[0] == "be_player":
			self.handle_be_player(handler, req)
        elif req[0] == "chat":
        	import operator
        	msg = sep_sequence.join(req)
        	map(operator.methodcaller('snd', msg), handlers)
        else:
            handler.snd(req[0] + sep_sequence + "Unknown request")
    
    def handle_be_player(self, handler, req):
        color = "spectator"
        if not self.black:
            self.black = handler
            color = "black"
            print("Assigned black player")
        elif not self.white and handler != self.black:
            self.white = handler
            color = "white"
            print("Assigned white player")
        else:
            print("Rejected player")
        handler.snd(req[0] + sep_sequence + color)

    def handle_request(self, msg, handler):
        if handler in [self.black, self.white]:
            self.process_player_request(handler, msg.split(sep_sequence))
        else:
            self.process_spectator_request(handler, msg.split(sep_sequence))


class ChatHandler(asynchat.async_chat):
    def __init__(self, sock, server):
        asynchat.async_chat.__init__(self, sock=sock, map=chat_room)
        self.set_terminator(end_sequence)
        self.buffer = []
        self.server = server
 
    def collect_incoming_data(self, data):
        self.buffer.append(data)

    def found_terminator(self):
        msg = ''.join(self.buffer)
        print('Received:', msg)
        self.buffer = []
        self.server.handle_request(msg, self)

    def snd(self, msg):
        print(str(msg) + end_sequence)
        self.push(str(msg) + end_sequence)


class ChatServer(asyncore.dispatcher):
    def __init__(self, host, port, server):
        asyncore.dispatcher.__init__(self, map=chat_room)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.bind((host, port))
        self.listen(5)
        self.server = server

    def handle_accept(self):
        pair = self.accept()
        if pair is not None:
            sock, addr = pair
            print('Incoming connection from ', repr(addr))
            handler = ChatHandler(sock, self.server)
            handlers.append(handler)
