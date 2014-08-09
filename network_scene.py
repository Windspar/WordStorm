import pygame
import network
import ui_tools.screen as screen
import ui_tools.button as button
import ui_tools.gradient as gradient
from ui_tools.ui_string import String
import commands
import urllib2

def get_public_ip():
    return urllib2.urlopen('http://ip.42.pl/raw').read()

class Connection(object):
    stream = None
    host = False
    names = None
    scores = None
    word_count = None
    
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
        local_ip = commands.getoutput('hostname -I')
        rect = screen.handler.rect
        leftx = rect.centerx / 2
        rightx = rect.centerx + leftx
        self.local_string = String(self, 'Local: ' + local_ip, (leftx, 20))
        self.public_string = String(self, 'Public: ' + get_public_ip(), (rightx, 20)) 
        self.back_button = button.Button(self, self.back_push, 'Back', (10, 728))
        
        self.bind_event(pygame.QUIT, self.on_quit)
        self.tick = 0
        
    def entrance(self):
        name = screen.handler.scenes['intro'].name.get_text()
        if name == "":
            name == 'Host'
            
        self.players = [PlayerBox(name, (50,80))]
        Connection.names = None
        Connection.scores = None
        Connection.word_count = None
        
    def blit(self, surface):
        surface.blit(self.background, (0,0))        
        for pbox in self.players:
            pbox.blit(surface)
        
    def update(self, tick):
        if tick > self.tick:
            self.tick = tick + 50
            if Connection.stream:
                if Connection.stream.running:
                    data = Connection.stream.get()                    
                    if data:
                        d = data.split()
                        if data.startswith('#Names'):
                            Connection.names = d[1:]
                            self.players = []
                            for enum, name in enumerate(Connection.names):
                                self.players.append(PlayerBox(name, (enum * 200 + 50, 80)))
                        elif data.startswith('#Start'):
                            screen.handler.set_scene = 'game'
     
    # host function only
    def start_push(self, pydata):
        Connection.stream.send('#Start game', True)
        
    def back_push(self, pydata):
        if Connection.stream:
            Connection.stream.stop()
            Connection.stream.join()
            Connection.stream = None
            Connection.host = False
        
        screen.handler.set_scene = 'intro'
        
    def host(self):
        name = screen.handler.scenes['intro'].name.get_text()
        if name == "":
            name = 'Host'
            
        Connection.stream = network.Host(name)
        Connection.stream.start()
        Connection.host = True
        self.start_button = button.Button(self, self.start_push, 'Start Game', (864,728))
        
    def client(self):
        name = screen.handler.scenes['intro'].name.get_text()
        if name == "":
            name = 'Player'
            
        join_ip = screen.handler.scenes['intro'].connect_ip.get_text()  
        Connection.stream = network.Client(join_ip, name)
        Connection.stream.start()
        
    def on_quit(self, event):
        if Connection.stream:
            if Connection.stream.running:
                Connection.stream.stop()
                Connection.stream.join()
        screen.handler.running = 0
        
