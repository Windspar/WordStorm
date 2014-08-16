import pygame
import ui_tools.screen as screen
import ui_tools.textbox as textbox
from ui_tools.ui_string import String
from game_engine import engine, Display
pygame.init()

class Game(screen.Scene):
    def __init__(self):
        screen.Scene.__init__(self)

        self.timer = String(self, '3:00', (120,50), pygame.font.Font(None, 60))
        engine.setup(self)

        self.bind_event(pygame.QUIT, self.on_quit)

    def entrance(self):
        if engine.connection.stream:
            if engine.connection.host:
                engine.board.shake()
                engine.connection.stream.send('#Shake ' + ' '.join(engine.board.shake_data))
        else:
            engine.board.shake()

        engine.player.clear()
        engine.player.display = Display(engine.player_name, 0, 0, 0)
        engine.letter_select.clear()
        engine.wordlist_display.wordlist = engine.player.wordlist
        engine.wordlist_display.render()
        
        x = 1
        for name in engine.players.iterkeys():
            engine.players[name].clear()
            engine.players[name].display = Display(name, 0, 0, x)
            x += 1

        style = textbox.default_textbox_image((480, 34))
        self.game_textbox = textbox.Textbox(self, (272, 726), image=style)

        self.tick = 0
        self.timer.text = '3:00'

    def solver(self):
        pass

    def blit(self, surface):
        surface.fill((0,100,200))
        surface.blit(engine.board.surface, engine.board.position)
        engine.letter_select.blit(surface)
        surface.blit(engine.board.shake_image, engine.board.position)
        engine.word_image.blit(surface)
        
        # You are always on top
        engine.player.display.blit(surface)
        for name in engine.players.iterkeys():
            engine.players[name].display.blit(surface)

    def on_quit(self, event):
        if engine.connection.stream:
            if engine.connection.stream.running:
                engine.connection.stream.stop()
                engine.connection.stream.join()
        screen.handler.running = 0

    def update(self, tick):
        if self.tick == 0:
            self.tick = tick
        else:
            data = 180000 - (tick - self.tick)
            if  data < 0:
                screen.handler.set_scene = 'gameover'
                pass
            else:
                data = data / 1000
                m = data / 60
                s = data - m * 60
                self.timer.text = '%(a)d:%(b)02d' %{"a":m, "b":s}

        if engine.connection.stream:
            if engine.connection.stream.running:
                data = engine.connection.stream.get()
                if data:
                    if data.startswith('#'):
                        d = data.split()
                        if data.startswith('#Data'):
                            name = d[1]
                            if name != engine.player_name:
                                engine.players[name].update(d[2])                                
                                engine.players[name].display.update()
                        elif data.startswith('#Shake'):
                            if not engine.connection.host:
                                engine.board.shake_data = d[1:]
                                engine.board.shake_render()
                    else:
                        # send to chat
                        pass
