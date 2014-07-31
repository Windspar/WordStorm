import time
import socket
import select
import threading
import Queue
import sys

# ----- ----- ----- ----- ----- --*-- ----- ----- ----- ----- ----- #
#                            Host Server                            #
# ----- ----- ----- ----- ----- --*-- ----- ----- ----- ----- ----- #
class HostServer(threading.Thread):
    def __init__(self, host, port):
        threading.Thread.__init__(self)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((host, port))
        self.sock.listen(3)
        self.sock_list = [self.sock]

        self.running = True
        
        self.recieved = Queue.Queue()
        self.outgoing = Queue.Queue()
        self.broadcast = Queue.Queue()
        self.sendto = Queue.Queue()
        
        self.ID_counter = 0
        self.ID = {}

    def run(self):
        self.running = True
        while self.running:
            sread, swrite, serror = select.select(self.sock_list, self.sock_list[], [], 0)

            for socket in sread:

                if socket == self.sock:
                    sockfd, addr = socket.accept()
                    self.sock_list.append(sockfd)
                    ID = self.ID_counter
                    self.ID[ID] = sockfd
                    self.ID_counter += 1
                    self.sendto.put([ID, '@@AcceptRequest %d' %(ID)])
                    self.sendto.task_done()
                else:
                    try:
                        data = socket.recv(4096)
                        if data:
                            if data.startswith('@@'):
                                self.recieved.put(data)
                                self.recieved.task_done()
                            else:
                                self.broadcast.put([socket, data])
                                self.broadcast.task_done()
                                self.recieved.put(data)
                                self.recieved.task_done()
                        else:
                            if socket in self.sock:
                                self.sock.remove(socket)
                    except:
                        continue
                        
            for socket in swrite:
                if not self.outgoing.empty():
                    data = self.outgoing.get()
                    for socket in self.sock_list:
                        if socket != self.sock:
                            self.send_data(socket, data)
                            
                if not self.broadcast.empty():
                    sock, data = self.broadcast.get()
                    for socket in self.socket:
                        if socket != self.sock and socket != sock:
                            self.send_data(socket, data)
                
                if not self.sendto.empty:
                    ID, data = self.sendto.get()
                    sock = self.ID[ID]
                    self.send_data(sock, data)

            time.sleep(0.04)

        self.sock.close()
        
    def send_data(self, socket, data):
        try:
            socket.send(data)
        except:
            socket.close()
            if socket in self.sock_list:
                self.sock_list.remove(socket)

    def stop(self):
        self.recieved.join()
        self.outgoing.join()
        self.sendto.join()
        self.running = False

    def get(self):
        if self.recieved.empty():
            return None

        return self.recieved.get()

    def send(self, data, too=0):
        if too == 0:
            self.outgoing.put(data)
            self.outgoing.task_done()
        else:
            self.sendto[too].put(data)
            self.sendto[too].task_done()

# ----- ----- ----- ----- ----- --*-- ----- ----- ----- ----- ----- #
#                               Client                              #
# ----- ----- ----- ----- ----- --*-- ----- ----- ----- ----- ----- #
class Client(threading.Thread):
    def __init__(self, host, port):
        threading.Thread.__init__(self)

        self.recv_queue = Queue.Queue()
        self.send_queue = Queue.Queue()

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(2)
        self.sock_list = [self.sock]

        try:
            self.sock.connect((host, port))
            self.running = True
        except:
            self.running = False

    def run(self):
        while self.running:
            sread, swrite, serror = select.select(self.sock_list, self.sock_list, [], 0)

            for socket in sread:

                if socket == self.sock:
                    data = socket.recv(4096)
                    if data:                        
                        self.recv_queue.put(data)
                        self.recv_queue.task_done()
                    else:
                        self.running = False

            for socket in swrite:
                if not self.send_queue.empty():

                    data = self.send_queue.get()
                    socket.send(data)

            time.sleep(0.04)

        self.sock.close()

    def stop(self):
        self.recv_queue.join()
        self.send_queue.join()
        self.running = False

    def get(self):
        if self.recv_queue.empty():
            return None

        return self.recv_queue.get()

    def send(self, data):
        self.send_queue.put(data)
        self.send_queue.task_done()
