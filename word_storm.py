import pygame
import ui_tools.screen as screen
import intro_scene
import game_scene

pygame.init()

if __name__ == '__main__':
    handler = screen.Handler('Word Storm', (1024, 768))
    handler.scenes['intro'] = intro_scene.Intro(handler)
    handler.scenes['game'] = game_scene.Game(handler)
    handler.loop('intro', 30)
    pygame.quit()
