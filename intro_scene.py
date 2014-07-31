import pygame
import ui_tools.screen as screen
import ui_tools.button as button
import ui_tools.menu as menu
import ui_tools.gradient as gradient
from ui_tools.ui_string import String
#pygame.init()

class Intro(screen.Scene):
    def __init__(self, handler):
        screen.Scene.__init__(self)
        self.handler = handler
        self.background = gradient.vertical(((0,150,220), (0,50,150), (0,0,120)))
        self.background = pygame.transform.scale(self.background, handler.get_size())
        
        font = pygame.font.Font(None, 180)
        self.string = String(self, 'Word Storm', (512, 150), font, (204, 180, 150))
        
        font = pygame.font.Font(None, 60)
        hfont = pygame.font.Font(None, 70)
        style = menu.MenuStyle(font, hfont, (0,75,150), (0,100,200))
        q_style = menu.MenuStyle(font, hfont, (100,0,0), (150,0,0))
        self.menulist = [ menu.MenuItem(self, 'Single Player', self.single_push, style),
                menu.MenuItem(self, 'Host Game', self.single_push, style),
                menu.MenuItem(self, 'Join Game', self.single_push, style),
                menu.MenuItem(self, 'Quit', self.on_quit, q_style) ]
        
        menu.set_menu(self.menulist, (512, 500))
        
        self.bind_event(pygame.QUIT, self.on_quit)
        
    def blit(self, surface):
        surface.blit(self.background, (0,0))
        
    def single_push(self, event):
        self.handler.set_scene = 'game'
        
    def on_quit(self, event):
        self.handler.running = 0
        
