from ui_string import String
import gradient 
import pygame

class ButtonImage(object):
    def __init__(self):
        self.up = None
        self.down = None
        self.toggle = None
        self.hover = None
        self.size = None

def default_button_image(size):
    pyobject = ButtonImage()
    pyobject.size = size
    
    def build(attr, color_tuple, color):
        image = gradient.vertical(color_tuple)
        image = pygame.transform.scale(image, size)
        rect = pygame.Rect(size[0] - 8, 5, 3, size[1] - 10)
        pygame.draw.rect(image, color, rect)
        setattr(pyobject, attr, image)
        
    build('up', ((0,100,200),(0,50,100)), (250,250,250))
    build('down', ((0,50,100),(0,100,200)), (0,0,200))
    build('toggle', ((0,50,100),(0,100,200)), (200,0,0))
    build('hover', ((0,100,200),(0,50,100)), (0,200,0))
    
    return pyobject
            
DEFAULT_IMAGE = default_button_image((150,30))

class ButtonCallback(object):
    def __init__(self, pydata, toggle, text):
        self.pydata = pydata
        self.toggle = toggle
        self.text = text

class Button(object):
    def __init__(self, parent, callback, string, position, pydata=None, image=DEFAULT_IMAGE, group=None):
        self.image = image
        self.rect = pygame.Rect(position, image.size)
        self.string = String(None, string, self.rect.center)        
        self.data = ButtonCallback(pydata, False, self.text)
        self.callback = callback
        
        self.mouseover = False
        self.group = group
        
        if parent:
            parent.bind_event(pygame.MOUSEMOTION, self.on_mousemotion)
            parent.bind_event(pygame.MOUSEBUTTONDOWN, self.on_mousedown)
            parent.bind_event(pygame.MOUSEBUTTONUP, self.on_mouseup)
            parent.bind_blit(self.blit)
            
    def blit(self, surface):
        if self.mouseover and self.data.toggle:
            surface.blit(self.image.toggle, self.rect.topleft)
        elif self.mouseover:
            surface.blit(self.image.hover, self.rect.topleft)
        elif self.data.toggle:
            surface.blit(self.image.down, self.rect.topleft)
        else:
            surface.blit(self.image.up, self.rect.topleft)

        self.string.blit(surface)
            
    def on_mousemotion(self, event):
        self.mouseover = self.rect.collidepoint(event.pos)
        if not self.mouseover and self.data.toggle:
            self.data.toggle = False
        
    def on_mousedown(self, event):
        if event.button == 1 and self.mouseover:
            self.data.toggle = True
        
    def on_mouseup(self, event):
        if event.button == 1 and self.mouseover and self.data.toggle:
            self.data.toggle = False
            if self.callback:
                self.callback(self.data)
        
    @property    
    def pydata(self):
        return self.data.pydata
        
    @pydata.setter
    def pydata(self, pydata):
        self.data.pydata = pydata
        
    @property
    def toggle(self):
        self.data.toggle
        
    @toggle.setter    
    def toggle(self, pybool):
        self.data.toggle = pybool
        
    def text(self, pystring):
        self.string.text = pystring
        
