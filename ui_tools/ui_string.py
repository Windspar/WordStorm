import pygame

# String(parent, string, position, font, color, anchor)

# function to set class *args and **kargs
def attr_list(class_object, arglist, args, kargs):
    length = len(args)
    for key, value in zip(arglist[:length], args):
        setattr(class_object, key, value)
        
    for key, value in kargs.iteritems():
        if key in arglist:
            setattr(class_object, key, value)
        else:
            raise KeyError()

class StringHiddenValues(object):
    def __init__(self):
        self.string = " "
        self.position = 0, 0
        self.font = pygame.font.Font(None, 24)
        self.color = (255,255,255)
        self.anchor = 0
        # non args
        self.image = None
        self.rect = None
        self.gradient = None
        
    def render(self):
        self.image = self.font.render(self.string, 1, self.color)
        self.rect = self.image.get_rect()
        if self.gradient:
            # make alpha match
            gtemp = pygame.transform.scale(self.gradient, self.rect.size)
            tarray = pygame.surfarray.pixels_alpha(self.image)
            garray = pygame.surfarray.pixels_alpha(gtemp)
            ysize, xsize = tarray.shape
            for i in xrange(ysize):
                for j in xrange(xsize):
                    garray[i][j] = tarray[i][j]
                    
            self.image = gtemp
        
        if self.anchor == 0:
            self.rect.center = self.position
        else:
            self.rect.left = self.position[0]
            self.rect.centery = self.position[1]
                

# self centering string
class String(object):
    arglist = ('string','position', 'font', 'color', 'anchor')
    # anchors
    CENTER = 0
    LEFT = 1
                    
    def __init__(self, parent, *args, **kargs):
        self.hidden = StringHiddenValues()
        attr_list(self.hidden, String.arglist, args, kargs)
        self.hidden.render()
        if parent:
            parent.bind_blit(self.blit)
        
    def blit(self, surface):
        surface.blit(self.hidden.image, self.hidden.rect.topleft)
        
    @property
    def color(self):
        self.hidden.color
        
    @color.setter
    def color(self, color):
        self.hidden.color = color
        self.hidden.render()

    @property
    def font(self):
        return self.hidden.font
        
    @font.setter
    def font(self, font):
        self.hidden.font = font
        self.hidden.render()
    
    @property    
    def text(self):
        return self.hidden.string
        
    @text.setter
    def text(self, pystring):
        self.hidden.string = pystring
        self.hidden.render()
        
    @property
    def position(self):
        return self.hidden.position
        
    @position.setter
    def position(self, pytuple):
        self.hidden.position = pytuple
        if self.hidden.anchor == 0:
            self.hidden.rect.center = pytuple
        else:
            self.hidden.rect.left = pytuple[0]
            self.hidden.rect.centery = pytuple[1]
            
    def anchor_center(self):
        self.hidden.anchor = 0
        self.hidden.rect.center = self.hidden.position
        
    def anchor_left(self):
        self.hidden.anchor = 1
        self.hidden.rect.left = self.hidden.position[0]
        self.hidden.rect.centery = self.hidden.position[1]
        
    def apply_surface(self, surface):
        self.hidden.gradient = surface.convert_alpha()
        self.hidden.render()
        
    def get_rect(self):
        return self.hidden.rect
        
    def collidepoint(self, position):
        return self.hidden.rect.collidepoint(position)
        
    def __repr__(self):
        return '<String(%s)>' %(self.hidden.string)
        

