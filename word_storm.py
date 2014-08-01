import pygame
import ui_tools.screen as screen
import intro_scene
import game_scene

pygame.init()

if __name__ == '__main__':
    handler = screen.Handler('Word Storm', (1024, 768))
    screen.handler.scenes['intro'] = intro_scene.Intro()
    screen.handler.scenes['game'] = game_scene.Game()
    handler.loop('intro', 30)
    pygame.quit()
