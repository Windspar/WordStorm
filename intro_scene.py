import pygame
import ui_tools.screen as screen
import ui_tools.button as button
import ui_tools.textbox as textbox
import ui_tools.menu as menu
import ui_tools.gradient as gradient
from ui_tools.ui_string import String
from game_engine import engine
#pygame.init()

class Intro(screen.Scene):
    def __init__(self):
        screen.Scene.__init__(self)
        self.background = gradient.vertical(((0,150,220), (0,50,150), (0,0,120)))
        self.background = pygame.transform.scale(self.background, screen.handler.rect.size)

        font = pygame.font.Font(None, 180)
        self.string = String(self, 'Word Storm', (512, 150), font, (204, 180, 150))

        font = pygame.font.Font(None, 60)
        hfont = pygame.font.Font(None, 70)
        style = menu.MenuStyle(font, hfont, (0,75,150), (0,100,200))
        q_style = menu.MenuStyle(font, hfont, (100,0,0), (150,0,0))
        self.menulist = [ menu.MenuItem(self, 'Small Game', self.game_push, style, 4),
                menu.MenuItem(self, 'Big Game', self.game_push, style, 5),
                menu.MenuItem(self, 'Host Small Game', self.host_push, style, 4),
                menu.MenuItem(self, 'Host Big Game', self.host_push, style, 5),
                menu.MenuItem(self, 'Join Game', self.join_push, style),
                menu.MenuItem(self, 'Quit', self.on_quit, q_style) ]

        menu.set_menu(self.menulist, (512, 500))
        self.name_string = String(self, 'Name', (95, 690))
        self.name = textbox.Textbox(self, (20, 708))
        self.connect_ip_string = String(self, 'Join IP', (929, 690))
        self.connect_ip = textbox.Textbox(self, (854, 708))

        self.bind_event(pygame.QUIT, self.on_quit)

    def blit(self, surface):
        surface.blit(self.background, (0,0))

    def game_push(self, pydata):
        engine.player_name = self.name.get_text()
        engine.setup_board(pydata)
        screen.handler.set_scene = 'game'

    def host_push(self, pydata):
        engine.player_name = self.name.get_text()
        engine.setup_board(pydata)
        screen.handler.scenes['network'].host()
        screen.handler.set_scene = 'network'
        
    def join_push(self, pydata):
        engine.player_name = self.name.get_text()
        screen.handler.scenes['network'].client()
        screen.handler.set_scene = 'network'

    def on_quit(self, event):
        if engine.connection.stream:
            if engine.connection.stream.running:
                engine.connection.stream.stop()
                engine.connection.stream.join()

        screen.handler.running = 0

