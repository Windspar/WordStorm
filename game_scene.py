import pygame
import ui_tools.screen as screen
import ui_tools.textbox as textbox
from ui_tools.ui_string import String
from wordlist import WordList
import game_data

pygame.init()

# boggle like game
# points (3,4) = 1 , (5) = 2, (6) = 3, (7) = 5, (8+) = 11
# 
            
class Chat(object):
    def __init__(self, parent, screen_width):
        width = screen_width / 2 - Board.width / 2
        style = textbox.default_textbox_image((Board.width, 34))
        self.game_textbox = textbox.Textbox(parent, (width, 726), image=style)
        
# ----- ----- ----- ----- ----- --*-- ----- ----- ----- ----- ----- #
#                               Game                                #
# ----- ----- ----- ----- ----- --*-- ----- ----- ----- ----- ----- #

class Game(screen.Scene):
    def __init__(self):
        screen.Scene.__init__(self)
        
        game_data.set_board(screen.handler.rect.center)
        self.wordlist = WordList(self, (762,63), (240, 480), (0,50,200), self.update_score)
        self.timer = String(self, '3:00', (120,50), pygame.font.Font(None, 60))
        self.player_data = String(self, 'words : 0      score : 0', (882, 560), pygame.font.Font(None, 30))
        
        self.bind_event(pygame.QUIT, self.on_quit)
        
    def entrance(self):
        game_data.shake()
        self.wordlist.clear()
        
        style = textbox.default_textbox_image((480, 34))
        self.game_textbox = textbox.Textbox(self, (272, 726), image=style)        
        
        self.tick = 0        
        self.timer.text = '3:00'
        self.player_data.text = 'words : 0      score : 0'
     
    def solver(self):
        pass
        
    def blit(self, surface):
        surface.fill((0,100,200))
        surface.blit(game_data.Board.surface, game_data.Board.position)
        self.wordlist.blit(surface)            
        surface.blit(game_data.Shake.image, game_data.Board.position)
        game_data.Word.image.blit(surface)
        
    def on_quit(self, event):
        screen.handler.running = 0
        
    def update(self, tick):
        if self.tick == 0:
            self.tick = tick
        else:
            data = 180000 - (tick - self.tick)
            if  data < 0:
                # need gameover_scene
                pass
            else:
                data = data / 1000
                m = data / 60
                s = data - m * 60
                self.timer.text = '%(a)d:%(b)02d' %{"a":m, "b":s}
                
    def update_score(self):
        word_count = len(self.wordlist.wordlist)
        dscore = {4:1, 5:2, 6:3, 7:5, 8:11}
        score = sum([dscore[min(max(4,len(word)),8)] for word in self.wordlist.wordlist])
                
        self.player_data.text = 'words : %-6d score : %d' %(word_count, score)
