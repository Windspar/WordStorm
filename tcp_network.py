import time
import socket
import select
import threading
import sys

BUFFER_SIZE = 1012
# ----- ----- ----- ----- ----- --*-- ----- ----- ----- ----- ----- #
#                            Host Server                            #
# ----- ----- ----- ----- ----- --*-- ----- ----- ----- ----- ----- #
class HostServer(threading.Thread):
    def __init__(self, host, port, max_connection):
        threading.Thread.__init__(self)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((host, port))
        self.sock.listen(max_connection)
        self.socket_list = [self.sock]

        self.running = True
        
    def socket_disconnected(self, socket):
        self.disconnect(socket) # internal
        if socket in self.socket_list:
            self.socket_list.remove(socket)

    def run(self):
        self.running = True
        while self.running:
            sread, swrite, serror = select.select(self.socket_list, self.socket_list[], [], 0)

            for read_socket in sread:
                if read_socket == self.sock:
                    sockfd, addr = socket.accept()
                    self.socket_list.append(sockfd)
                    self.accepting(sockfd) # internal
                else:
                    try:
                        data = read_socket.recv(BUFFER_SIZE)
                        if data:
                            self.recieving(read_socket, data) # internal
                        else:
                            self.socket_disconnected(read_socket)
                    except:
                        self.socket_disconnected(read_socket)
                        continue
                        
            for write_socket in swrite:
                self.sending(write_socket) #internal
                
            time.sleep(0.04)

        self.sock.close()        
        
    def accepting(self, socket):
        pass
        
    def recieving(self, socket, data):
        pass
        
    def disconnect(self, socket):
        pass
        
    def sending(self, socket):
        pass

# ----- ----- ----- ----- ----- --*-- ----- ----- ----- ----- ----- #
#                               Client                              #
# ----- ----- ----- ----- ----- --*-- ----- ----- ----- ----- ----- #
class Client(threading.Thread):
    def __init__(self, host, port):
        threading.Thread.__init__(self)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(2)
        self.socket_list = [self.sock]

        try:
            self.sock.connect((host, port))
            self.running = True
        except:
            self.failed_to_connect() # internal
            self.running = False

    def run(self):
        while self.running:
            sread, swrite, serror = select.select(self.socket_list, self.socket_list, [], 0)

            for read_socket in sread:
                if read_socket == self.sock:
                    data = read_socket.recv(BUFFER_SIZE)
                    if data:                        
                        self.recieving(data) # internal
                    else:
                        self.lost_connection() # internal
                        self.running = False

            for write_socket in swrite:
                self.sending(write_socket) # internal

            time.sleep(0.04)

        self.sock.close()
    
    def recieving(self, data):
        pass
        
    def sending(self, socket):
        pass
        
    def lost_connection(self):
        pass
        
    def failed_to_connect(self):
        pass
