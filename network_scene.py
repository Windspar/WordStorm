import pygame
import network
import ui_tools.screen as screen
import ui_tools.button as button
import ui_tools.gradient as gradient
from ui_tools.ui_string import String
from game_engine import engine, Player
import commands
import urllib2

def get_public_ip():
    return urllib2.urlopen('http://ip.42.pl/raw').read()

def get_local_ip():
    data = commands.getoutput('hostname -I')
    if data.startswith('hostname'):
        # Arch Linux
        data = commands.getoutput('hostname -i')
    return data

class PlayerBox(object):
    def __init__(self, name, position):
        self.rect = pygame.Rect(position, (100,100))
        self.name = String(None, name, self.rect.center)

    def blit(self, surface):
        pygame.draw.rect(surface, (50, 0, 150), self.rect)
        self.name.blit(surface)

class Connect(screen.Scene):
    def __init__(self):
        screen.Scene.__init__(self)
        image = gradient.vertical(((0,0,200),(0,0,150),(0,0,75)))
        self.background = pygame.transform.scale(image, screen.handler.rect.size)
        self.start_button = None
        local_ip = get_local_ip()
        rect = screen.handler.rect
        leftx = rect.centerx / 2
        rightx = rect.centerx + leftx
        self.local_string = String(self, 'Local: ' + local_ip, (leftx, 20))
        self.public_string = String(self, 'Public: ' + get_public_ip(), (rightx, 20))
        self.back_button = button.Button(self, self.back_push, 'Back', (10, 728))

        self.bind_event(pygame.QUIT, self.on_quit)
        self.tick = 0

    def entrance(self):
        self.players = [PlayerBox(engine.player_name, (50,80))]

    def blit(self, surface):
        surface.blit(self.background, (0,0))
        for pbox in self.players:
            pbox.blit(surface)

    def update(self, tick):
        if tick > self.tick:
            self.tick = tick + 50
            if engine.connection.stream:
                if engine.connection.stream.running:
                    data = engine.connection.stream.get()
                    if data:
                        d = data.split()
                        if data.startswith('#Names'):
                            names = d[1:]
                            self.players = []
                            try:
                            	names.remove(engine.player_name)
                            except:
								pass
								
                            for enum, name in enumerate(names):
                                self.players.append(PlayerBox(name, (enum * 200 + 50, 80)))
                                if name not in engine.players.keys():
                                    engine.players[name] = Player()
                                    
                        elif data.startswith('#Start'):
                            screen.handler.set_scene = 'game'

    # host function only
    def start_push(self, pydata):
        engine.connection.stream.send('#Start game', True)

    def back_push(self, pydata):
        if engine.connection.stream:
            engine.connection.stream.stop()
            engine.connection.stream.join()
            engine.connection.stream = None
            engine.connection.host = False

        screen.handler.set_scene = 'intro'

    def host(self):
        if engine.player_name == "":
            engine.player_name = 'Host'

        engine.connection.stream = network.Host()
        engine.connection.stream.start()
        engine.connection.host = True
        self.start_button = button.Button(self, self.start_push, 'Start Game', (864,728))

    def client(self):
        if engine.player_name == "":
            engine.player_name = 'Player'

        join_ip = screen.handler.scenes['intro'].connect_ip.get_text()
        engine.connection.stream = network.Client(join_ip)
        engine.connection.stream.start()

    def on_quit(self, event):
        if engine.connection.stream:
            if engine.connection.stream.running:
                engine.connection.stream.stop()
                engine.connection.stream.join()
        screen.handler.running = 0

