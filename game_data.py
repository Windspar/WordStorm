import pygame
import random
from ui_tools.ui_string import String
from constant import DICE, ROLL, LETTERS
from itertools import product

pygame.init()

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
            random.choice(ROLL[2]), 0]
    
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
