import pygame as pg
import prepare

class World(object):
    def __init__(self, size, tile_size=64):
        grass = prepare.GFX["grass"]
        w, h  = size    
        surf = pg.Surface(size).convert()
        for y in range(0, h + 1, tile_size):
            for x in range(0, w + 1, tile_size):
                surf.blit(grass, (x, y))
                
    def update(self, dt):
        pass