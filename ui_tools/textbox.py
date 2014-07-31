import pygame
import gradient

class TextboxImage(object):
    def __init__(self):
        self.selected = None
        self.hover = None
        self.normal = None
        self.size = None
        
def default_textbox_image(size):
    pyobject = TextboxImage()
    offset = 6, 6
    half = 3, 3
    nsize = size[0] + offset[0], size[1] + offset[1]
    pyobject.size = nsize
    
    def build(attr, outside, inside):
        image = gradient.vertical(outside)
        image = pygame.transform.scale(image, nsize)
        nimage = gradient.vertical(inside)
        nimage = pygame.transform.scale(nimage, size)
        image.blit(nimage, half)
        setattr(pyobject, attr, image)
        
    build('normal', ((0,100,200), (0,50,100)), ((0,50,100), (0,100,200)))
    build('hover', ((0,125,250), (0,50,100)), ((0,50,100), (0,100,200)))
    build('selected', ((0,175,175), (0,75,75)), ((0,75,75), (0,150,150)))
    
    return pyobject
    
DEFAULT_IMAGE = default_textbox_image((150, 34))

class HiddenTextboxValue(object):
    def __init__(self, rect, font, color):
        if font:
            self.font = font
        else:
            self.font = pygame.font.Font(None, 30)
            
        self.rect = rect.inflate(-14,0)
        h = self.font.size("Ay")[1]
        self.rect.h =  h
        self.rect.center = rect.center
        self.text = ""
        self.image = None
        
        if color:
            self.color = color
        else:
            self.color = (204, 180, 150)
        
        self.carret = pygame.Surface((2, h))
        self.carret.fill(self.color)
        self.carret_x = self.rect.x + 1
        
    def draw_carret(self, surface):
        surface.blit(self.carret, (self.carret_x, self.rect.top))
        
    def render(self):
        length = len(self.text)
        if length == 0:
            self.image = None
            self.carret_x = self.rect.x + 1
        else:
            for x in xrange(length):
                if self.font.size(self.text[x:])[0] < self.rect.w - 4:
                    self.image = self.font.render(self.text[x:], 1, self.color)
                    self.carret_x = self.image.get_width() + self.rect.x + 1
                    break        

class Textbox(object):
    def __init__(self, parent, position, font=None, color=None, image=DEFAULT_IMAGE):
        self.rect = pygame.Rect(position, image.size)
        self.hidden = HiddenTextboxValue(self.rect, font, color)
                
        self.selected = False
        self.mouseover = False
        self.image = image
        
        if parent:
            parent.bind_blit(self.blit)
            parent.bind_event(pygame.KEYDOWN, self.on_keydown)
            parent.bind_event(pygame.MOUSEMOTION, self.on_motion)
            parent.bind_event(pygame.MOUSEBUTTONDOWN, self.on_mousedown)
            
    def blit(self, surface):
        if self.selected:
            surface.blit(self.image.selected, self.rect.topleft)
            self.hidden.draw_carret(surface)
        elif self.mouseover:
            surface.blit(self.image.hover, self.rect.topleft)
        else:
            surface.blit(self.image.normal, self.rect.topleft)
            
        if self.hidden.image:
            surface.blit(self.hidden.image, self.hidden.rect.topleft)
        
    def get_text(self):
        return self.hidden.text    
        
    def on_motion(self, event):
        self.mouseover = self.rect.collidepoint(event.pos)
        
    def on_mousedown(self, event):
        if event.button == 1:
            if self.mouseover:
                self.selected = True
            else:
                self.selected = False

    def on_keydown(self, event):
        if self.selected:
            if 32 <= event.key < 123:
                self.hidden.text += str(event.unicode)
            elif event.key == pygame.K_BACKSPACE:
                if len(self.hidden.text) > 1:
                    self.hidden.text = self.hidden.text[:-1]
                else:
                    self.hidden.text = ""
            elif event.key == pygame.K_DELETE:
                self.hidden.text = ""
                
            self.hidden.render()
