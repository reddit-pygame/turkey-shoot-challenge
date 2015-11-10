import os
import pygame as pg
import tools


SCREEN_SIZE = (1280, 720)
WORLD_SIZE = (3200, 3200)
ORIGINAL_CAPTION = "Turkey Shoot"


pg.mixer.pre_init(44100, -16, 1, 512)
pg.init()
os.environ['SDL_VIDEO_CENTERED'] = "TRUE"
pg.display.set_caption(ORIGINAL_CAPTION)
SCREEN = pg.display.set_mode(SCREEN_SIZE) #, pg.FULLSCREEN)
SCREEN_RECT = SCREEN.get_rect()


GFX   = tools.load_all_gfx(os.path.join("resources", "graphics"))
SFX = tools.load_all_sfx(os.path.join("resources", "sounds"))
FONTS = tools.load_all_fonts(os.path.join("resources", "fonts"))
MUSIC = tools.load_all_music(os.path.join("resources", "music"))

for num in range(1, 7):
    img = GFX["tree{}".format(num)]
    curvy = pg.Rect(0, 0, 128, 128)
    straight = pg.Rect(128, 0, 96, 128)
    GFX["curvy-tree{}".format(num)] = img.subsurface(curvy)
    GFX["straight-tree{}".format(num)] = img.subsurface(straight)


for x in range(1, 7):
    SFX["gobble{}".format(x)].set_volume(.2)
for x in range(1, 3):
    SFX["step{}".format(x)].set_volume(.5)
SFX["knifesharpener"].set_volume(.4)

pg.mixer.music.load(MUSIC["woodland"])
pg.mixer.music.play(-1)