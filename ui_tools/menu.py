import pygame
from ui_string import String

class MenuStyle(object):
    def __init__(self, font, hfont, color, hcolor, surface=None, hsurface=None):
        self.font = font
        self.hfont = hfont
        self.color = color
        self.hcolor = hcolor
        self.surface = surface
        self.hsurface = hsurface

class MenuItem(object):
    def __init__(self, parent, string, callback, style, pydata=None):
            
        self.callback = callback
        self.pydata = pydata
        self.mouseover = False            
        self.string = String(None, string, (0,0), style.font, style.color)
        self.hstring = String(None, string, (0,0), style.hfont, style.hcolor)
        self.height = self.string.font.size('Ay')[1]
        
        if style.surface:
            self.string.apply_surface(style.surface)
            
        if style.hsurface:
            self.hstring.apply_surface(style.hsurface)
        
        if parent:
            parent.bind_event(pygame.MOUSEMOTION, self.on_mousemotion)
            parent.bind_event(pygame.MOUSEBUTTONDOWN, self.on_mousedown)
            parent.bind_blit(self.blit)
            
    def blit(self, surface):
        if self.mouseover:
            self.hstring.blit(surface)
        else:
            self.string.blit(surface)
            
    def on_mousemotion(self, event):
        if self.mouseover:
            self.mouseover = self.hstring.collidepoint(event.pos)
        else:
            self.mouseover = self.string.collidepoint(event.pos)
        
    def on_mousedown(self, event):
        if self.mouseover:
            if event.button == 1:
                if self.callback:
                    self.callback(self.pydata)
                    
def set_menu(menulist, position, spacer=10, topleft=False):    
    if topleft:
        y = position[1] + spacer
    else:
        height = sum([item.height + spacer for item in menulist])
        y = position[1] - height / 2
        
    x = position[0]
    down = 0
    for item in menulist:
        item.string.position = x, y + down
        item.hstring.position = x, y + down
        down += item.height + spacer
