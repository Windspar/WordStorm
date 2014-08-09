from wordlist import WordList
import ui_tools.screen as screen
import ui_tools.button as button
from network_scene import Connection
import pygame

class GameOver(screen.Scene):
    def __init__(self):
        screen.Scene.__init__(self)
        self.wordlist = WordList(self, (20,50), (240, 600), (0, 50, 200))
        self.new_game = button.Button(self, self.push_scene, 'New Game', (10, 10), 'game')
        self.main_menu = button.Button(self, self.push_scene, 'Main Menu', (170, 10), 'intro')
        
        self.bind_event(pygame.QUIT, self.on_quit)
        
    def entrance(self):
        self.wordlist.wordlist = screen.handler.scenes['game'].letter_select.wordlist.wordlist
        self.wordlist.render()
        
    def blit(self, surface):
        surface.fill((0,10,120))
        self.wordlist.blit(surface)
        
    def push_scene(self, data):
        screen.handler.set_scene = data.pydata
        
    def on_quit(self, event):
        if Connection.stream:
            if Connection.stream.running:
                Connection.stream.stop()
                Connection.stream.join()
                
        screen.handler.running = 0
        
