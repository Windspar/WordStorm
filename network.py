import tcp_network
import Queue

class ClientObject(object):
    def __init__(self):
        self.data = Queue.Queue()
        self.name = None
        self.score = 0
        self.word_count = 0
        
    def send(self, data):
        self.data.put(data)
        self.data.task_done()
        
    def get(self):
        if self.data.empty():
            return None
        return self.data.get()
        
class Host(tcp_network.HostServer):
    def __init__(self, name):
        tcp_network.HostServer.__init__(self, '0.0.0.0', 9012, 3)
        self.clients = {}
        self.recieved = Queue.Queue()
        self.name = name
        self.score = 0
        self.word_count = 0
        
    def accepting(self, socket):
        client = ClientObject()
        client.send('@@Accept')
        self.clients[socket] = client
        
    def recieving(self, socket, data):
        if data.startswith('@@'):
            d = data.split()
            if data.startswith('@@Name'):
                self.clients[socket].name = d[1]
                names = [self.clients[p].name for p in self.socket_list if p != self.sock]
                names = [self.name] + names
                self.send('#Names ' + ' '.join(names)
            elif data.startswith('@@Score'):
                self.clients[socket].score = int(d[1])
                score = [self.clients[p].score for p in self.socket_list if p != self.sock]
                score = [self.score] + score
                self.send('#Scores ' +' '.join(map(str, score)))
            elif data.startswith('@@WordCount'):
                self.clients[socket].word_count = int(d[1])
                count = [self.clients[p].word_count for p in self.socket_list if p != self.sock]
                count = [self.word_count] + count
                self.send('#WordCount ' + ' '.join(map(str, count)))
        else:
            for player_socket in self.socket_list:
                if player_socket != self.sock and player_socket != socket:
                    self.clients[player_socket].send(data)
            
            self.recieved.put(data)
            self.recieved.task_done()
            
    def sending(self, socket):
        if socket != self.sock:
            if socket in self.socket_list:                
                data = self.clients[socket].get()
                if data:                                        
                    try:
                        socket.send(data)
                    except:
                        self.socket_disconnected(socket)
                
    def socket_disconnected(self, socket):
        if socket in self.socket_list:
            self.socket_list.remove(socket)
            del self.clients[socket]

    def send(self, data):        
        for player_socket in self.socket_list:
            if player_socket != self.sock:
                self.client[player_socket].send(data)    
        
    def get(self):
        if self.recieved.empty():
            return None
            
        return self.recieved.get()
        
    def stop(self):
        self.running = False
        
# ----- ----- ----- ----- ----- --*-- ----- ----- ----- ----- ----- #
#                               Client                              #
# ----- ----- ----- ----- ----- --*-- ----- ----- ----- ----- ----- #
class Client(tcp_network.Client):
    def __init__(self, host, name):
        tcp_network.Client.__init__(self, host, 9012)
        self.recieved = Queue.Queue()
        self.outgoing = Queue.Queue()
        self.name = name
        
    def sending(self, socket):
        if not self.outgoing.empty():
            data = self.outgoing.get()
            socket.send(data)
            
    def recieving(self, data):
        if data.startswith('@@'):
            #d = data.split()
            if data.startswith('@@Accept'):
                self.send('@@Name ' + self.name)
        else:
            self.recieved.put(data)
            self.recieved.task_done()

    def send(self, data):
        self.outgoing.put(data)
        self.outgoing.task_done()
        
    def get(self):
        if self.recieved.empty():
            return None
            
        return self.recieved.get()
