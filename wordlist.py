from ui_tools.ui_string import String
import enchant
import pygame
import game_data

class WordList(object):
    lib = enchant.Dict("en_US")
    
    def __init__(self, parent, position, size, color, font=None):
        self.rect = pygame.Rect(position, size)
        self.surface = pygame.Surface(size)
        self.color = color
        
        if font:
            self.font = font
        else:
            self.font = pygame.font.Font(None, 30)

        height = self.font.size('Ay')[1]
        self.spacer = int(height / 2.5) + (height - 8)
        self.max_length = int(size[1] / self.spacer)
        
        self.clear()
        
        if parent:
            parent.bind_event(pygame.MOUSEMOTION, self.on_mousemotion)
            parent.bind_event(pygame.MOUSEBUTTONDOWN, self.on_mousedown)
        
    def blit(self, surface):
        surface.blit(self.surface, self.rect.topleft)
        
    def clear(self):
        self.surface.fill(self.color)
        self.wordlist = []
        self.scroll = 0
        self.mouseover = False
        
    def render(self):
        self.surface.fill(self.color)
        length = len(self.wordlist)
        if length > self.max_length:
            start = length - self.max_length - self.scroll
            end = length - self.scroll
            word_data = self.wordlist[start:end]
        else:
            word_data = self.wordlist
            
        step = 0
        for word in word_data:
            image = self.font.render(word, 1, (0,150,200))
            position = 10, step * self.spacer + 5
            self.surface.blit(image, position)
            step += 1
            
    def on_mousemotion(self, event):
        self.mouseover = self.rect.collidepoint(event.pos)
            
    def on_mousedown(self, event):
        if event.button == 4:
            if self.mouseover:
                if len(self.wordlist) > self.max_length + self.scroll:
                    self.scroll += 1
                    self.render()
        elif event.button == 5:
            if self.mouseover:
                if self.scroll > 0:
                    self.scroll -= 1
                    self.render()
        
