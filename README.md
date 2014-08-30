WordStorm
=========
Boggle like game

__markdowns__ .... https://github.com/tchapi/markdown-cheatsheet/blob/master/README.md
### Requirement ###
* GNU/Linux Distro
* python 2.7
* pygame
* numpy
* PyEnchant ... http://pythonhosted.org/pyenchant/

This is my first time playing with network code.

#### TODO ####
* setup start.ini file
* __networking__ __framework__
 * tell when some disconnect
 * have network_scene go back when failed to connect
* __game_scene__
 * solver
 * chat
 * have game wait until all players are done.
* __gameover_scene__
 * have list cross out words

This game is still in alpha mode.
* added 5x5 board

#### FIX ####
* fix my queue.task_done() mistake
* fix gameover_scene show word list
* allow for different screen sizes (800,600), (1024,768). now need setting_scene
