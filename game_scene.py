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
    
class Word(object):
    surface = pygame.Surface((200, 688))
    render = []
    words= []
    rect = []
    word = ""
    image = String(None, "", (512, 30), pygame.font.Font(None, 50), (50,200,0))
    lib = enchant.Dict("en_US")

class Game(screen.Scene):
    def __init__(self, handler):
        screen.Scene.__init__(self)
        self.handler = handler
        for i in xrange(0,600,Board.size):
            for j in xrange(0,600,Board.size):
                pygame.draw.rect(Board.surface, (0,0,100), (i,j,Board.size,Board.size), 2)
                
        center = self.handler.get_rect().center
        Board.position = center[0] - Board.width / 2, center[1] - Board.width / 2 - 80
        for i, j in product(xrange(Board.length),xrange(Board.length)):
            offset = (Board.size - Board.select) / 2
            position = Board.position[0] + i * Board.size + offset, Board.position[1] + j * Board.size + offset
            rect = pygame.Rect(position, (Board.select, Board.select))
            Board.squares[repr(rect)] = rect, j + i * 4
            
        self.left_mouse_button = False
        self.last_key = None
        Word.surface.fill((0,100,200))
        
        style = textbox.default_textbox_image((480, 34))
        self.game_textbox = textbox.Textbox(self, (272, 726), image=style)        
        
        self.bind_event(pygame.QUIT, self.on_quit)
        self.bind_event(pygame.KEYDOWN, self.on_keydown)
        self.bind_event(pygame.MOUSEBUTTONDOWN, self.on_mousedown)
        self.bind_event(pygame.MOUSEBUTTONUP, self.on_mouseup)
        self.bind_event(pygame.MOUSEMOTION, self.on_mousemotion)
        self.shake()
        self.shake_render()
        
    def shake(self):
        track = {}
        roll = [random.choice(ROLL[0]), 0, 
                random.choice(ROLL[2]), 
                random.choice(ROLL[3])]
                
        n = random.choice([None, None, 0, 0, 2, 3])
        if n:
            roll[n] += 1
                
        roll[1] = 16 - sum(roll)  
        # build choice      
        choice = []
        for enum, r in enumerate(roll):
            for x in xrange(r):         
                choice.append(enum)        
        
        # always make one vowel in the center
        center_choice = random.choice([5,6,9,10])
        choice.remove(0)
        
        self.shake_data = []
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
                   
            self.shake_data.append(pick)
            
        while True:
            pick = random.choice(DICE[choice[0]])
            if track.get(pick, 0) < LETTERS[pick][1]:
                track[pick] = track.get(pick, 0) + 1
                break
                
        self.shake_data.append(pick)
        
    def shake_render(self):
        self.shake_image = pygame.Surface((Board.width, Board.width))
        self.shake_image.set_colorkey((0,0,0))
        locations = tuple(product(xrange(Board.length),xrange(Board.length)))
        color = (204, 180, 150)
        font = pygame.font.Font(None, Board.font_size)
        for position, letter in zip(locations, self.shake_data):
            #print position, letter
            string = String(None, letter, self.location(position), font, color)
            string.blit(self.shake_image)
     
    def solver(self):
        pass
    
    def location(self, position):
        half = Board.size / 2
        return Board.size * position[0] + half, Board.size * position[1] + half
        
    def render_word_list(self):
        Word.surface.fill((0,100,200))
        if len(Word.words) > 21:
            word_data = Word.render[-21:]
        else:
            word_data = Word.render
            
        step = 0
        for string in word_data:
            string.position = (10, step * 30 + 15)
            string.blit(Word.surface)
            step += 1
        
    def blit(self, surface):
        surface.fill((0,100,200))
        surface.blit(Board.surface, Board.position)
        for key in Word.rect:
            pygame.draw.rect(surface, (200,50,25), Board.squares[key][0])
            
        surface.blit(self.shake_image, Board.position)
        surface.blit(Word.surface, (782, 40))
        Word.image.blit(surface)
        
    def on_keydown(self, event):
        if not self.game_textbox.selected:
            if event.key == pygame.K_SPACE:
                self.shake()
                self.shake_render()
                Word.surface.fill((0,100,200))
                Word.render = []
                Word.words = []
                Word.word = ""
        
    def on_quit(self, event):
        self.handler.running = 0
        
    def on_mousemotion(self, event):
        if self.left_mouse_button:
            hit = None
            for key in Board.squares.iterkeys():
                if Board.squares[key][0].collidepoint(event.pos):
                    hit = key
                    break
            
            if hit and hit != self.last_key:
                self.last_key = hit
                if len(Word.rect) > 1:
                    if hit == Word.rect[-2]:
                        Word.word = Word.word[:-1]
                        Word.rect = Word.rect[:-1]
                        Word.image.text = Word.word
                    elif hit in Word.rect:
                        pass
                    else:
                        check = Board.squares[Word.rect[-1]][1]
                        number = Board.squares[hit][1]
                        if number in ALLOWED_MOVEMENT[check]:
                            Word.rect.append(hit)
                            Word.word += self.shake_data[number].lower()
                            Word.image.text = Word.word
                else:
                    allow = True
                    if len(Word.rect) == 1:
                        allow = False
                        check = Board.squares[Word.rect[-1]][1]
                        number = Board.squares[hit][1]
                        if number in ALLOWED_MOVEMENT[check]:
                            allow = True
                            
                    if allow:
                        Word.rect.append(hit)
                        Word.word += self.shake_data[Board.squares[hit][1]].lower()
                        Word.image.text = Word.word
        
    def on_mousedown(self, event):
        if event.button == 1:
            self.left_mouse_button = True
                        
    def on_mouseup(self, event):
        if event.button == 1:
            if len(Word.word) >= 3 and Word.word not in Word.words:
                if Word.lib.check(Word.word):
                    Word.words.append(Word.word)
                    Word.render.append(String(None, Word.word, (0, 0), FONT30, (0,50,200), String.LEFT))
                    self.render_word_list()
                
            self.left_mouse_button = False
            Word.rect = []
            Word.word = ""
            Word.image.text = ""
            self.last_key = None            
