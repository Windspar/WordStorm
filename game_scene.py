import pygame
import ui_tools.screen as screen
import ui_tools.textbox as textbox
from constant import ALLOWED_MOVEMENT
from ui_tools.ui_string import String
from wordlist import WordList
import game_data
from network_scene import Connection
pygame.init()

class Player(object):
    score = 0
    word_count = 0
    
class Display(object):
    def __init__(self, name, score, word_count, offset):
        self.name = String(None, name, (120, offset * 100 + 100))
        self.data = String(None, 'words : %-7d count : %d' % (word_count, score), (120, offset * 100 + 130))
        
    def single_update(self):
        self.data = String(None, 'words : %-7d count : %d' % (Player.word_count, Player.score), (120, 130))
        
    def blit(self, surface):
        self.name.blit(surface)
        self.data.blit(surface)
            
class Chat(object):
    def __init__(self, parent, screen_width):
        width = screen_width / 2 - Board.width / 2
        style = textbox.default_textbox_image((Board.width, 34))
        self.game_textbox = textbox.Textbox(parent, (width, 726), image=style)
        
class LetterSelect(object):
    def __init__(self, parent):
        self.wordlist = WordList(parent, (762,63), (240, 480), (0,50,200))
        self.clear()
        
        if parent:
            parent.bind_event(pygame.MOUSEMOTION, self.on_mousemotion)
            parent.bind_event(pygame.MOUSEBUTTONDOWN, self.on_mousedown)
            parent.bind_event(pygame.MOUSEBUTTONUP, self.on_mouseup)
            
    def blit(self, surface):
        for key in self.rectlist:
            pygame.draw.rect(surface, (200,50,25), game_data.Board.squares[key][0])          

        self.wordlist.blit(surface)
        if Connection.stream is None:
            if self.display:
                self.display.blit(surface)
            
    def clear(self):
        self.display = Display('', 0, 0, 0)
        self.rectlist = []
        self.wordlist.clear()
        self.last_key = None
        self.leftmouse = False
        
    def update_score(self):
        word_count = len(self.wordlist.wordlist)
        dscore = {4:1, 5:2, 6:3, 7:5, 8:11}
        score = sum([dscore[min(max(4,len(word)),8)] for word in self.wordlist.wordlist])
        if Connection.stream:
            if Connection.stream.running:
                if Connection.host:
                    Connection.stream.host_recieving('@@Score %d' % (score))
                    Connection.stream.host_recieving('@@WordCount %d' % (word_count))
                else:
                    Connection.stream.send('@@Score %d' % (score))
                    Connection.stream.send('@@WordCount %d' % (word_count))
        
        Player.score = score
        Player.word_count = word_count
        self.display.single_update()
        
    def on_mouseup(self, event):
        if event.button == 1:            
            if len(game_data.Word.word) >= 3 and game_data.Word.word not in self.wordlist.wordlist:
                if WordList.lib.check(game_data.Word.word):
                    self.wordlist.wordlist.append(game_data.Word.word)
                    self.wordlist.render()
                    self.update_score()
            
            self.leftmouse = False
            self.last_key = None
            self.rectlist = []
            game_data.Word.word = ""
            game_data.Word.image.text = ""
        
    def on_mousedown(self, event):
        if event.button == 1:
            self.leftmouse = True
            
    def on_mousemotion(self, event):
        if self.leftmouse:
            hit = None
            for key in game_data.Board.squares.iterkeys():
                if game_data.Board.squares[key][0].collidepoint(event.pos):
                    hit = key
                    break
            
            if hit and hit != self.last_key:
                self.last_key = hit
                if len(self.rectlist) > 1:
                    if hit == self.rectlist[-2]:
                        game_data.Word.word = game_data.Word.word[:-1]
                        self.rectlist = self.rectlist[:-1]
                        game_data.Word.image.text = game_data.Word.word
                    elif hit in self.rectlist:
                        pass
                    else:
                        check = game_data.Board.squares[self.rectlist[-1]][1]
                        number = game_data.Board.squares[hit][1]
                        if number in ALLOWED_MOVEMENT[check]:
                            self.rectlist.append(hit)
                            game_data.Word.word += game_data.Shake.data[number].lower()
                            game_data.Word.image.text = game_data.Word.word
                else:
                    allow = True
                    if len(self.rectlist) == 1:
                        allow = False
                        check = game_data.Board.squares[self.rectlist[-1]][1]
                        number = game_data.Board.squares[hit][1]
                        if number in ALLOWED_MOVEMENT[check]:
                            allow = True
                            
                    if allow:
                        self.rectlist.append(hit)
                        game_data.Word.word += game_data.Shake.data[game_data.Board.squares[hit][1]].lower()
                        game_data.Word.image.text = game_data.Word.word
            
# ----- ----- ----- ----- ----- --*-- ----- ----- ----- ----- ----- #
#                               Game                                #
# ----- ----- ----- ----- ----- --*-- ----- ----- ----- ----- ----- #

class Game(screen.Scene):
    def __init__(self):
        screen.Scene.__init__(self)
        
        game_data.set_board(screen.handler.rect.center)
        self.letter_select = LetterSelect(self)
        self.timer = String(self, '3:00', (120,50), pygame.font.Font(None, 60))
        
        self.bind_event(pygame.QUIT, self.on_quit)        
        
    def entrance(self):
        game_data.shake()
        self.letter_select.clear()
        
        style = textbox.default_textbox_image((480, 34))
        self.game_textbox = textbox.Textbox(self, (272, 726), image=style)        
        
        self.display = []
        Player.score = 0
        Player.word_count = 0
        self.tick = 0        
        self.timer.text = '3:00'
        if Connection.stream:
            self.update_display()
     
    def solver(self):
        pass
        
    def blit(self, surface):
        surface.fill((0,100,200))
        surface.blit(game_data.Board.surface, game_data.Board.position)
        self.letter_select.blit(surface)
        surface.blit(game_data.Shake.image, game_data.Board.position)
        game_data.Word.image.blit(surface)
        for item in self.display:
            item.blit(surface)
        
    def on_quit(self, event):
        if Connection.stream:
            if Connection.stream.running:
                Connection.stream.stop()
                Connection.stream.join()
        screen.handler.running = 0
        
    def update(self, tick):
        if self.tick == 0:
            self.tick = tick
        else:
            data = 180000 - (tick - self.tick)
            if  data < 0:
                screen.handler.set_scene = 'gameover'
                pass
            else:
                data = data / 1000
                m = data / 60
                s = data - m * 60
                self.timer.text = '%(a)d:%(b)02d' %{"a":m, "b":s}
                
        if Connection.stream:
            if Connection.stream.running:
                data = Connection.stream.get()
                if data:
                    if data.startswith('#'):
                        d = data.split()
                        if data.startswith('#Scores'):
                            Connection.scores = list(map(int, d[1:]))
                        elif data.startswith('#WordCount'):
                            Connection.word_count = list(map(int, d[1:]))
                        self.update_display()
                    else:
                        # send to chat
                        pass

    def update_display(self):
        length = len(Connection.names)
        self.display = []
        for x in xrange(length):
            try:
                score = Connection.scores[x]
            except:
                score = 0
                
            try:
                word_count = Connection.word_count[x]
            except:
                word_count = 0
            
            self.display.append(Display(Connection.names[x],score,word_count,x))
        
        
