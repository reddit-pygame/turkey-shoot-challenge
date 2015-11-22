from random import randint, choice
import itertools
import pygame as pg

import prepare, tools
from leaf_spots import leaf_spots


class Tree(pg.sprite.DirtySprite):
    """Trees block movement of turkeys and the player."""
    def __init__(self, midbottom, *groups):
        super(Tree, self).__init__(*groups)
        self.num = choice((1, 1, 2, 3, 4, 5, 5, 6, 6))
        self.trunk = choice(("curvy", "straight"))
        self.image = prepare.GFX["{}-tree{}".format(self.trunk, self.num)]
        self.rect = self.image.get_rect(midbottom=midbottom)
        x, y = self.rect.topleft
        if self.trunk == "curvy":
            self.collider = pg.Rect(x + 65, y + 102, 16, 11)
            self.leaf_fall_distance = 60
        else:
            self.collider = pg.Rect(x + 39, y + 102, 14, 10)
            self.leaf_fall_distance = 64


class Leaf(pg.sprite.DirtySprite):
    """Some eye candy for when the player shoots a tree."""
    offsets  = {"curvy": ((18, 109), (31, 63)),
                     "straight": ((17, 85), (26, 74))}
    images = {}
    for i in range(1, 7):
        sheet = prepare.GFX["leaf-strip{}".format(i)]
        leaves = tools.strip_from_sheet(sheet, (0, 0), (16, 16), 24)
        images[i] = leaves

    def __init__(self, tree, spot_info, *groups):
        super(Leaf, self).__init__(*groups)
        treex, treey = tree.rect.topleft
        x = treex + spot_info[0][0]
        y = treey + spot_info[0][1]
        self.image = choice(self.images[tree.num]).copy()
        self.rect = self.image.get_rect(center=(x, y))
        self.collider = self.rect.copy()
        self.collider.bottom = tree.collider.bottom - ((spot_info[1] + tree.rect.top) - self.rect.centery)
        self.fall_distance = tree.leaf_fall_distance
        self.img_alpha = 220
        self.image.set_alpha(self.img_alpha)

    def land(self):
        self.collider.center = self.rect.center

    def set_alpha(self):
        self.image.set_alpha(self.img_alpha)


