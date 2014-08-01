from constant import ALLOWED_MOVEMENT
from ui_tools.ui_string import String
import enchant
import pygame
import game_data

class WordList(object):
    lib = enchant.Dict("en_US")
    
    def __init__(self, parent, position, size, color, callback, font=None):
        self.rect = pygame.Rect(position, size)
        self.surface = pygame.Surface(size)
        self.color = color
        self.callback = callback
        
        if font:
            self.font = font
        else:
            self.font = pygame.font.Font(None, 30)

        height = self.font.size('Ay')[1]
        self.spacer = int(height / 2.5) + height
        self.max_length = int(size[1] / self.spacer)
        
        self.clear()
        
        if parent:
            parent.bind_event(pygame.MOUSEMOTION, self.on_mousemotion)
            parent.bind_event(pygame.MOUSEBUTTONDOWN, self.on_mousedown)
            parent.bind_event(pygame.MOUSEBUTTONUP, self.on_mouseup)
            
    def blit(self, surface):
        for key in self.rectlist:
            pygame.draw.rect(surface, (200,50,25), game_data.Board.squares[key][0])          

        surface.blit(self.surface, self.rect.topleft)
        
    def clear(self):
        self.surface.fill(self.color)
        self.renderlist = []
        self.wordlist = []
        self.rectlist = []
        self.scroll = 0
        self.last_key = None
        self.mouseover = False
        self.left_mouse_button = False
        
    def render(self):
        self.surface.fill(self.color)
        length = len(self.wordlist)
        if length > self.max_length:
            start = length - self.max_length - self.scroll
            end = length - self.scroll
            word_data = self.renderlist[start:end]
        else:
            word_data = self.renderlist
            
        step = 0
        for string in word_data:
            string.position = (10, step * self.spacer + 15)
            string.blit(self.surface)
            step += 1
        
    def on_mousemotion(self, event):
        self.mouseover = self.rect.collidepoint(event.pos)
        if self.left_mouse_button:
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
                        
    def on_mousedown(self, event):
        if event.button == 1:
            self.left_mouse_button = True
        elif event.button == 4:
            if self.mouseover:
                if len(self.wordlist) > self.max_length + self.scroll:
                    self.scroll += 1
                    self.render()
        elif event.button == 5:
            if self.mouseover:
                if self.scroll > 0:
                    self.scroll -= 1
                    self.render()
                        
    def on_mouseup(self, event):
        if event.button == 1:
            if len(game_data.Word.word) >= 3 and game_data.Word.word not in self.wordlist:
                if WordList.lib.check(game_data.Word.word):
                    self.wordlist.append(game_data.Word.word)
                    self.renderlist.append(String(None, game_data.Word.word, (0, 0), self.font, (0,150,200), String.LEFT))
                    self.render()
                    self.callback()
                
            self.left_mouse_button = False
            self.last_key = None
            self.rectlist = []
            game_data.Word.word = ""
            game_data.Word.image.text = ""
