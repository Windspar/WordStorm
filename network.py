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
                engine.socket_names[socket] = d[1]
                engine.players[d[1]] = self.waiting_playername[socket]
                del self.waiting_playername[socket]
                names = [engine.socket_names[p] for p in self.socket_list if p != self.sock]
                names = [engine.player_name] + names
                self.send('#Names ' + ' '.join(names), True)
            # sends( name, word )
            elif data.startswith('@@Data'):
                name = engine.socket_names[socket]
                self.send('#Data %s %s' % (name,d[1]), True)

        else:
            for player_socket in self.socket_list:
                if player_socket != self.sock and player_socket != socket:
                    name = engine.socket_names[player_socket]
                    engine.players[name].send(data)

            self.recieved.put(data)
            self.recieved.task_done()

    def host_recieving(self, data):
        if data.startswith('@@'):
            d = data.split()
            if data.startswith('@@Data'):
                name = engine.player_name
                self.send('#Data %s %s' % (name,d[1]))

    def sending(self, socket):
        if socket != self.sock:
            if socket in self.socket_list:
                if socket in self.waiting_playername.keys():
                    data = self.waiting_playername[socket].get()
                elif socket in engine.socket_names.keys():
                    name = engine.socket_names[socket]
                    data = engine.players[name].get()
                else:
                    data = None

                if data:
                    try:
                        socket.send(data)
                    except:
                        self.socket_disconnected(socket)

    def socket_disconnected(self, socket):
        if socket in self.socket_list:
            self.socket_list.remove(socket)
            if socket in engine.socket_names.keys():
                del engine.socket_names[socket]

    def send(self, data, to_self=False):
        for player_socket in self.socket_list:
            if player_socket in engine.socket_names.keys():
                name = engine.socket_names[player_socket]
                engine.players[name].send(data)

        if to_self:
            self.recieved.put(data)
            self.recieved.task_done()

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
    def __init__(self, host):
        tcp_network.Client.__init__(self, host, 9012)
        self.recieved = Queue.Queue()
        self.outgoing = Queue.Queue()

    def sending(self, socket):
        if not self.outgoing.empty():
            data = self.outgoing.get()
            socket.send(data)

    def recieving(self, data):
        if data.startswith('@@'):
            d = data.split()
            if data.startswith('@@Accept'):
                engine.setup_board(int(d[1]))
                self.send('@@Name ' + engine.player_name)
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

    def stop(self):
        self.running = False
