import pygame
import random
import ui_tools.screen as screen
from itertools import product
from ui_tools.ui_string import String
from constant import DICE4, DICE5, ROLL4, ROLL5
from wordlist_display import WordlistDisplay
import Queue
pygame.init()

class Struct(object): pass

# game_engine replaces game_data.py

# Player replaces network.ClientObject
class Display(object):
    def __init__(self, name, score, word_count, offset):
        self.player_name = name
        width = screen.handler.rect.w / 8
        self.name = String(None, name, (width, offset * 100 + 100))
        self.data = String(None, 'words : %-7d count : %d' % (word_count, score), (width, offset * 100 + 130))
    
    def update_player(self):
        score = engine.player.score
        count = engine.player.word_count
        self.data.text = 'words : %-7d count : %d' % (count, score)
            
    def update(self):
        score = engine.players[self.player_name].score
        count = engine.players[self.player_name].word_count
        self.data.text = 'words : %-7d count : %d' % (count, score)

    def blit(self, surface):
        self.name.blit(surface)
        self.data.blit(surface)
        
class Player(object):
    def __init__(self):
        self.base_score = {4:1, 5:2, 6:3, 7:5, 8:11}
        self.data = Queue.Queue()
        self.wordlist = []
        self.clear()

    def clear(self):
        self.display = None
        self.wordlist[:] = []
        self.word_count = 0
        self.score = 0

    def send(self, data):
        self.data.put(data)        

    def get(self, callback):
        if not self.data.empty():
            callback(self.data.get())
            self.data.task_done()
        
    def update(self, word):
        self.wordlist.append(word)
        self.word_count = len(self.wordlist)
        self.score = sum([self.base_score[min(max(4,len(lword)),8)] for lword in self.wordlist])


class Board(object):
    def __init__(self, cells, width, font_size):
        self.surface = pygame.Surface((width, width))
        self.cells = cells
        self.size = width / cells
        self.font_size = font_size
        self.width = width
        self.squares = {}
        self.select = int(self.size * 0.65)
        self.shake_data = []
        self.shake_image = pygame.Surface((width,width))
        self.shake_image.set_colorkey((0,0,0))

        center = screen.handler.rect.center
        self.position = center[0] - width // 2, 60

        for x in xrange(0, self.width, self.size):
            for y in xrange(0, self.width, self.size):
                pygame.draw.rect(self.surface, (0,0,100), (x,y,self.size,self.size), 2)

        for j, i in product(xrange(self.cells), xrange(self.cells)):
            offset = (self.size - self.select) / 2
            position = self.position[0] + i * self.size + offset, self.position[1] + j * self.size + offset
            rect = pygame.Rect(position, (self.select, self.select))
            self.squares[repr(rect)] = rect, j + i * self.cells

        self.allowed_movements()
        self.min_letters = cells - 1

    def shake(self):
        if self.cells == 5:
            R = ROLL5
            dice = list(map(list, DICE5))
            dcount = 24
        else:
            R = ROLL4
            dice = list(map(list, DICE4))
            dcount = 15

        roll = [random.choice(R[0]), 0, random.choice(R[2]), R[3]]
        roll[1] = dcount - sum(roll)
        n = random.choice([1, 1, 1, 0, 0, 2, 3])
        roll[n] += 1

        # build choice
        choice = []
        for enum, r in enumerate(roll):
            for x in xrange(r):
                choice.append(enum)

        # always make one vowel in the center
        if self.cells == 4:
            center_choice = random.choice([5,6,9,10])
            center_choice2 = None
            choice.remove(0)
        else:
            center_choice = random.choice([6,7,8,11])
            choice.remove(0)
            center_choice2 = random.choice([13,16,17,18])
            choice.remove(0)

        self.shake_data = []
        for x in xrange(dcount):
            if x == center_choice or x == center_choice2:
                value = 0
            else:
                value = random.choice(choice)
                choice.remove(value)

            pick = random.choice(dice[value])
            dice[value].remove(pick)
            self.shake_data.append(pick)

        pick = random.choice(dice[value])
        self.shake_data.append(pick)
        
        self.shake_render()

    def shake_render(self):
        def location(position):
            half = self.size / 2
            return self.size * position[0] + half, self.size * position[1] + half
            
        self.shake_image.fill((0,0,0))
        locations = tuple(product(xrange(self.cells),xrange(self.cells)))
        color = (204, 180, 150)
        font = pygame.font.Font(None, self.font_size)
        for position, letter in zip(locations, self.shake_data):
            string = String(None, letter, location(position), font, color)
            string.blit(self.shake_image)

    # replaces constant.ALLOWED_MOVEMENT
    def allowed_movements(self):
        self.movement = []
        m = self.cells * self.cells
        data = [[j + i for i in xrange(self.cells)] for j in xrange(0,m,self.cells)]
        high = self.cells - 1
        
        for i in range(self.cells):
            for j in range(self.cells):
                jlist = []
                if i > 0:
                    jlist.append(data[i - 1][j])
                    if j > 0:
                        jlist.append(data[i - 1][j - 1])
                    if j < high:
                        jlist.append(data[i - 1][j + 1])
                if i < high:
                    jlist.append(data[i + 1][j])
                    if j > 0:
                        jlist.append(data[i + 1][j - 1])
                    if j < high:
                        jlist.append(data[i + 1][j + 1])
                if j > 0:
                    jlist.append(data[i][j - 1])
                if j < high:
                    jlist.append(data[i][j + 1])

                self.movement.append(jlist)

class LetterSelect(object):
    def __init__(self, parent):
        self.clear()

        if parent:
            parent.bind_event(pygame.MOUSEMOTION, self.on_mousemotion)
            parent.bind_event(pygame.MOUSEBUTTONDOWN, self.on_mousedown)
            parent.bind_event(pygame.MOUSEBUTTONUP, self.on_mouseup)

    def blit(self, surface):
        for key in self.rectlist:
            pygame.draw.rect(surface, (200,50,25), engine.board.squares[key][0])

        engine.wordlist_display.blit(surface)

    def clear(self):        
        self.rectlist = []
        self.last_key = None
        self.leftmouse = False

    def send_word(self):
        if engine.connection.stream:
            if engine.connection.stream.running:
                if engine.connection.host:
                    engine.connection.stream.host_send_data('@@Data %s' % (engine.word))
                else:
                    engine.connection.stream.send('@@Data %s' % (engine.word))        

    def on_mouseup(self, event):
        if event.button == 1:
            if len(engine.word) >= engine.board.min_letters and engine.word not in engine.player.wordlist:
                if engine.wordlist_display.lib.check(engine.word):
                    engine.player.update(engine.word)
                    engine.wordlist_display.render()
                    engine.player.display.update_player()
                    self.send_word()

            self.leftmouse = False
            self.last_key = None
            self.rectlist = []
            engine.word = ""
            engine.word_image.text = ""

    def on_mousedown(self, event):
        if event.button == 1:
            self.leftmouse = True

    def on_mousemotion(self, event):
        if self.leftmouse:
            hit = None
            for key in engine.board.squares.iterkeys():
                if engine.board.squares[key][0].collidepoint(event.pos):
                    hit = key
                    break

            if hit and hit != self.last_key:
                self.last_key = hit
                if len(self.rectlist) > 1:
                    if hit == self.rectlist[-2]:
                        engine.word = engine.word[:-1]
                        self.rectlist = self.rectlist[:-1]
                        engine.word_image.text = engine.word
                    elif hit in self.rectlist:
                        pass
                    else:
                        check = engine.board.squares[self.rectlist[-1]][1]
                        number = engine.board.squares[hit][1]
                        if number in engine.board.movement[check]:
                            self.rectlist.append(hit)
                            engine.word += engine.board.shake_data[number].lower()
                            engine.word_image.text = engine.word
                else:
                    allow = True
                    if len(self.rectlist) == 1:
                        allow = False
                        check = engine.board.squares[self.rectlist[-1]][1]
                        number = engine.board.squares[hit][1]
                        if number in engine.board.movement[check]:
                            allow = True

                    if allow:
                        self.rectlist.append(hit)
                        engine.word += engine.board.shake_data[engine.board.squares[hit][1]].lower()
                        engine.word_image.text = engine.word

class engine(object):
    word_image = None
    wordlist_display = None
    word = ""
    socket_names = {}
    player_name = ""
    player = Player()
    players = {}
    board = None
    letter_select = None
    connection = Struct()
    connection.stream = None
    connection.host = False

    @classmethod
    def setup_board(cls, cells):
        width = screen.handler.rect.w / 2
        fsize = width / 10
        cls.word_image = String(None, "", (width, 30), pygame.font.Font(None, fsize), (50,200,0))
        width = int(width / cells) * cells
        fsize = width / 10
        if cells == 5:
            cls.board = Board(cells, width, fsize)
        else:
            cls.board = Board(4, width, fsize + 4)
            
        parent = screen.handler.scenes['game']
        position = width + width / 2 + 10
        xlength = screen.handler.rect.width - position - 10
        cls.wordlist_display = WordlistDisplay(parent, (position,60), (xlength, width), (0,50,200))
        cls.wordlist_display.wordlist = cls.player.wordlist
        cls.letter_select = LetterSelect(parent)
                
