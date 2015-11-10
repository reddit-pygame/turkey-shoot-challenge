import sys
import pygame as pg

from state_engine import Game, GameState
import prepare
import hunting

states = {"HUNTING": hunting.Hunting()}

game = Game(prepare.SCREEN, states, "HUNTING")
game.run()
pg.quit()
sys.exit()