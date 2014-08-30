import tcp_network
import Queue
from game_engine import engine, Player

class Host(tcp_network.HostServer):
    def __init__(self):
        tcp_network.HostServer.__init__(self, '0.0.0.0', 9012, 3)
        self.recieved = Queue.Queue()
        self.waiting_playername = {}

    def accepting(self, socket):
        player = Player()
        player.send('@@Accept %d' % (engine.board.cells))
        self.waiting_playername[socket] = player

    def recieving(self, socket, data):
        if data.startswith('@@'):
            d = data.split()
            if data.startswith('@@Name'):
                name = d[1]
                engine.socket_names[socket] = name
                engine.players[name] = self.waiting_playername[socket]
                del self.waiting_playername[socket]
                names = [engine.socket_names[p] for p in self.socket_list if p != self.sock and p != socket]
                names = [engine.player_name] + names
                engine.players[name].send('#Names ' + ' '.join(names))
                self.broadcast(socket, '#User ' + name)
            # sends( name, word )
            elif data.startswith('@@Data'):
                name = engine.socket_names[socket]
                self.broadcast(socket, '#Data %s %s' % (name,d[1]))
        else:
            self.broadcast(socket, data)
            
    def broadcast(self, socket, data):
        for player_socket in self.socket_list:
            if player_socket != self.sock and player_socket != socket:
                name = engine.socket_names[socket]
                engine.players[name].send(data)
        self.recieved.put(data)

    def host_send_data(self, data):
        if data.startswith('@@'):
            d = data.split()
            if data.startswith('@@Data'):
                name = engine.player_name
                self.send('#Data %s %s' % (name,d[1]))

    def sending(self, socket):
        def sending_data(data):
            try:
                socket.send(data)
            except:
                self.socket_disconnected(socket)
                
        if socket != self.sock:
            if socket in self.socket_list:
                if socket in self.waiting_playername.keys():
                    self.waiting_playername[socket].get(sending_data)
                elif socket in engine.socket_names.keys():
                    name = engine.socket_names[socket]
                    engine.players[name].get(sending_data)

    def socket_disconnected(self, socket):
        if socket in self.socket_list:
            self.socket_list.remove(socket)
            if socket in engine.socket_names.keys():
                del engine.socket_names[socket]

    def send(self, data):
        for player_socket in self.socket_list:
            if player_socket in engine.socket_names.keys():
                name = engine.socket_names[player_socket]
                engine.players[name].send(data)

    def get(self, callback):
        if not self.recieved.empty():
            callback(self.recieved.get())
            self.recieved.task_done()

    def stop(self):
        self.running = False

# ----- ----- ----- ----- ----- --*-- ----- ----- ----- ----- ----- #
#                               Client                              #
# ----- ----- ----- ----- ----- --*-- ----- ----- ----- ----- ----- #
class Client(tcp_network.Client):
    def __init__(self, host):
        tcp_network.Client.__init__(self, host, 9012)
        self.recieved = Queue.Queue()
        self.outgoing = Queue.Queue()

    def sending(self, socket):
        if not self.outgoing.empty():
            socket.send(self.outgoing.get())
            self.outgoing.task_done()

    def recieving(self, data):
        if data.startswith('@@'):
            d = data.split()
            if data.startswith('@@Accept'):
                engine.setup_board(int(d[1]))
                self.send('@@Name ' + engine.player_name)
        else:
            self.recieved.put(data)

    def send(self, data):
        self.outgoing.put(data)

    def get(self, callback):
        if not self.recieved.empty():
            callback(self.recieved.get())
            self.recieved.task_done()

    def stop(self):
        self.running = False
