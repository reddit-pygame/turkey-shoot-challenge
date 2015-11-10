from math import degrees
import pygame as pg
import prepare
from angles import project


class Bullet(pg.sprite.DirtySprite):
    base_image = prepare.GFX["bullet"]
    def __init__(self, pos, angle, *groups):
        super(Bullet, self).__init__(*groups)
        self.pos = pos
        self.angle = angle
        self.speed = 500 / 1000. #30 pixels per second
        self.image = pg.Surface((4, 4)).convert()
        self.image.fill(pg.Color("gray30"))
        self.rect = self.image.get_rect(center=self.pos)

        #self.image = pg.transform.rotate(self.base_image, degrees(self.angle))
        #self.rect = self.image.get_rect(center=self.pos)
        #self.mask = pg.mask.from_surface(self.image)
        self.collider = self.rect.copy()

    def update(self, dt):
    #    self.pos = project(self.pos, self.angle, self.speed * dt)
    #    self.rect.center = self.pos
        self.collider.center = self.rect.center
