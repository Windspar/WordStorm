import pygame
import ui_tools.screen as screen
import intro_scene
import game_scene
import gameover_scene
import network_scene

pygame.init()

if __name__ == '__main__':
    handler = screen.Handler('Word Storm', (1024, 768))
    screen.handler.scenes['intro'] = intro_scene.Intro()
    screen.handler.scenes['game'] = game_scene.Game()
    screen.handler.scenes['gameover'] = gameover_scene.GameOver()
    screen.handler.scenes['network'] = network_scene.Connect()
    handler.loop('intro', 30)
    pygame.quit()
