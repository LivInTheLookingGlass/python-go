from .board import board
import asynchat
import asyncore
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

    def start(self):
        self.comm = threading.Thread(target=asyncore.loop)
        self.comm.daemon = True
        self.comm.start()

    def process_queue(self):
        while not self.in_queue.empty():
            msg = self.in_queue.get()
            req = msg.split(sep_sequence)
            print("Response to request " + req[0] + ": " + str(req[1:]))

    def send(self, msg):
        self.out_queue.put(str(msg) + end_sequence)

    def get_board(self):
        self.send("history")
        self.process_queue()


class ChatClient(asynchat.async_chat):
    def __init__(self, host, port, in_queue, out_queue):
        asynchat.async_chat.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect((host, port))
        self.set_terminator(end_sequence)                                            # End of text, End of tx, End of tx block, End of tx, End of text
        self.buffer = []
        self.out_queue = out_queue
        self.in_queue = in_queue
 
    def collect_incoming_data(self, data):
        self.buffer.append(data)
 
    def found_terminator(self):
        msg = ''.join(self.buffer)
        print 'Received:', msg
        self.buffer = []
        self.out_queue.put(msg)

    def writable(self):
        count = 0
        while not self.in_queue.empty():
            msg = self.in_queue.get()
            print(count, msg)
            count += 1
            self.push(msg)
        return True
