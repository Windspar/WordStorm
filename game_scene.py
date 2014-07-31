import pygame
import random
import enchant
import ui_tools.screen as screen
import ui_tools.textbox as textbox
from ui_tools.ui_string import String
from constant import DICE, ROLL, LETTERS, ALLOWED_MOVEMENT
from itertools import product

pygame.init()

FONT30 = pygame.font.Font(None, 30)

# boggle like game
# points (3,4) = 1 , (5) = 2, (6) = 3, (7) = 5, (8+) = 11
# 

class Board(object):
    length = 4
    size = 120
    font_size = 60
    select = int(size * 0.65)
    width = length * size
    surface = pygame.Surface((width, width))
    position = None
    squares = {}
    
def set_board(center):
    for i in xrange(0,600,Board.size):
        for j in xrange(0,600,Board.size):
            pygame.draw.rect(Board.surface, (0,0,100), (i,j,Board.size,Board.size), 2)
            
    Board.position = center[0] - Board.width / 2, center[1] - Board.width / 2 - 80
    for i, j in product(xrange(Board.length),xrange(Board.length)):
        offset = (Board.size - Board.select) / 2
        position = Board.position[0] + i * Board.size + offset, Board.position[1] + j * Board.size + offset
        rect = pygame.Rect(position, (Board.select, Board.select))
        Board.squares[repr(rect)] = rect, j + i * 4
        
class Shake(object):
    data = []
    image = pygame.Surface((Board.width, Board.width))
    image.set_colorkey((0,0,0))
    
def shake():
    track = {}
    roll = [random.choice(ROLL[0]), 0, 
            random.choice(ROLL[2]), 
            random.choice(ROLL[3])]
    
    roll[1] = 15 - sum(roll)         
    n = random.choice([1, 1, 0, 0, 2, 3])
    roll[n] += 1
            
    # build choice      
    choice = []
    for enum, r in enumerate(roll):
        for x in xrange(r):         
            choice.append(enum)        
    
    # always make one vowel in the center
    center_choice = random.choice([5,6,9,10])
    choice.remove(0)
    
    Shake.data = []
    for x in xrange(15):
        if x == center_choice:
            value = 0
        else:
            value = random.choice(choice)
            choice.remove(value)
            
        while True:
            pick = random.choice(DICE[value])
            if track.get(pick, 0) < LETTERS[pick][1]:
                track[pick] = track.get(pick, 0) + 1
                break
               
        Shake.data.append(pick)
        
    while True:
        pick = random.choice(DICE[choice[0]])
        if track.get(pick, 0) < LETTERS[pick][1]:
            track[pick] = track.get(pick, 0) + 1
            break
            
    Shake.data.append(pick)
    
    def location(position):
        half = Board.size / 2
        return Board.size * position[0] + half, Board.size * position[1] + half
    
    # render
    Shake.image.fill((0,0,0))
    locations = tuple(product(xrange(Board.length),xrange(Board.length)))
    color = (204, 180, 150)
    font = pygame.font.Font(None, Board.font_size)
    for position, letter in zip(locations, Shake.data):
        string = String(None, letter, location(position), font, color)
        string.blit(Shake.image)    
    
class Word(object):
    word = ""
    image = String(None, "", (512, 30), pygame.font.Font(None, 50), (50,200,0))

class WordList(object):
    lib = enchant.Dict("en_US")
    
    def __init__(self, parent, position, size, color, font=None):
        self.rect = pygame.Rect(position, size)
        self.surface = pygame.Surface(size)
        self.color = color
        
        self.mouseover = False
        self.left_mouse_button = False
        self.last_key = None
        
        if font:
            self.font = font
        else:
            self.font = pygame.font.Font(None, 30)

        height = self.font.size('Ay')[1]
        self.spacer = int(height / 2.5) + height
        self.max_length = int(size[1] / self.spacer)
        self.scroll = 0
        
        self.clear()
        
        if parent:
            parent.bind_event(pygame.MOUSEMOTION, self.on_mousemotion)
            parent.bind_event(pygame.MOUSEBUTTONDOWN, self.on_mousedown)
            parent.bind_event(pygame.MOUSEBUTTONUP, self.on_mouseup)
            
    def blit(self, surface):
        for key in self.rectlist:
            pygame.draw.rect(surface, (200,50,25), Board.squares[key][0])          

        surface.blit(self.surface, self.rect.topleft)
        
    def clear(self):
        self.surface.fill(self.color)
        self.renderlist = []
        self.wordlist = []
        self.rectlist = []
        
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
            for key in Board.squares.iterkeys():
                if Board.squares[key][0].collidepoint(event.pos):
                    hit = key
                    break
            
            if hit and hit != self.last_key:
                self.last_key = hit
                if len(self.rectlist) > 1:
                    if hit == self.rectlist[-2]:
                        Word.word = Word.word[:-1]
                        self.rectlist = self.rectlist[:-1]
                        Word.image.text = Word.word
                    elif hit in self.rectlist:
                        pass
                    else:
                        check = Board.squares[self.rectlist[-1]][1]
                        number = Board.squares[hit][1]
                        if number in ALLOWED_MOVEMENT[check]:
                            self.rectlist.append(hit)
                            Word.word += Shake.data[number].lower()
                            Word.image.text = Word.word
                else:
                    allow = True
                    if len(self.rectlist) == 1:
                        allow = False
                        check = Board.squares[self.rectlist[-1]][1]
                        number = Board.squares[hit][1]
                        if number in ALLOWED_MOVEMENT[check]:
                            allow = True
                            
                    if allow:
                        self.rectlist.append(hit)
                        Word.word += Shake.data[Board.squares[hit][1]].lower()
                        Word.image.text = Word.word
                        
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
            if len(Word.word) >= 3 and Word.word not in self.wordlist:
                if WordList.lib.check(Word.word):
                    self.wordlist.append(Word.word)
                    self.renderlist.append(String(None, Word.word, (0, 0), self.font, (0,150,200), String.LEFT))
                    self.render()
                
            self.left_mouse_button = False
            self.last_key = None       
            self.rectlist = []
            Word.word = ""
            Word.image.text = ""
            
class Chat(object):
    def __init__(self, parent, screen_width):
        width = screen_width / 2 - Board.width / 2
        style = textbox.default_textbox_image((Board.width, 34))
        self.game_textbox = textbox.Textbox(parent, (width, 726), image=style)
        
# ----- ----- ----- ----- ----- --*-- ----- ----- ----- ----- ----- #
#                               Game                                #
# ----- ----- ----- ----- ----- --*-- ----- ----- ----- ----- ----- #

class Game(screen.Scene):
    def __init__(self, handler):
        screen.Scene.__init__(self)
        self.handler = handler

        shake()
        set_board(self.handler.get_rect().center)
        self.wordlist = WordList(self, (762,63), (240, 480), (0,50,200))
        
        style = textbox.default_textbox_image((480, 34))
        self.game_textbox = textbox.Textbox(self, (272, 726), image=style)        
        
        self.bind_event(pygame.QUIT, self.on_quit)
     
    def solver(self):
        pass
        
    def blit(self, surface):
        surface.fill((0,100,200))
        surface.blit(Board.surface, Board.position)
        self.wordlist.blit(surface)            
        surface.blit(Shake.image, Board.position)
        Word.image.blit(surface)
        
    def on_quit(self, event):
        self.handler.running = 0
        
        
