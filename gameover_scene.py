from wordlist_display import WordlistDisplay
import ui_tools.screen as screen
import ui_tools.button as button
from ui_tools.ui_string import String
from game_engine import engine
import pygame

class Display(object):
    def __init__(self, name, score, word_count, offset):
        self.name = String(None, name, (270 * offset + 140, 670))
        self.data = String(None, 'words : %-7d count : %d' % (word_count, score), (240 * offset + 140, 700))
        
    def blit(self, surface):
        self.name.blit(surface)
        self.data.blit(surface)

class GameOver(screen.Scene):
    def __init__(self):
        screen.Scene.__init__(self)
        self.wordlist = WordlistDisplay(self, (20,50), (240, 600), (0, 50, 200))
        self.new_game = button.Button(self, self.push_scene, 'New Game', (10, 10), 'game')
        self.main_menu = button.Button(self, self.push_scene, 'Main Menu', (170, 10), 'intro')
                
        self.bind_event(pygame.QUIT, self.on_quit)

    def entrance(self):
        self.wordlist.wordlist = engine.player.wordlist
        self.wordlist.render()
        self.display = Display(engine.player_name, engine.player.score, engine.player.word_count, 0)
        
        self.all_wordlist = []
        self.displays = []
        x = 1
        for name in engine.players.iterkeys():
            wd = WordlistDisplay(self, (270 * x + 20,50), (240, 600), (0,50,200))
            wd.wordlist = engine.players[name].wordlist
            self.all_wordlist.append(wd)
            self.displays.append(Display(name, engine.players[name].score, engine.players[name].word_count, x))
            x += 1

    def blit(self, surface):
        surface.fill((0,10,120))
        self.wordlist.blit(surface)
        self.display.blit(surface)
        
        for player in self.all_wordlist:
            player.blit(surface)
            
        for player in self.displays:
            player.blit(surface)

    def push_scene(self, data):
        screen.handler.set_scene = data.pydata

    def on_quit(self, event):
        if engine.connection.stream:
            if engine.connection.stream.running:
                engine.connection.stream.stop()
                engine.connection.stream.join()

        screen.handler.running = 0

