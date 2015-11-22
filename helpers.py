from __future__ import division
from random import shuffle, randint
from itertools import cycle
import pygame as pg

import prepare
from animation import Animation, Task
from angles import get_distance


def parse_color(color):
    try:
        return pg.Color(color)
    except ValueError:
        return pg.Color(*color)

class AmmoCrate(pg.sprite.DirtySprite):
    def __init__(self, pos, *groups):
        super(AmmoCrate, self).__init__(*groups)
        self.image = prepare.GFX["crate"]
        self.rect = self.image.get_rect(center=pos)
        self.collider = self.rect.copy()


class Icon(pg.sprite.DirtySprite):
    def __init__(self, topleft, img_name, *groups):
        super(Icon, self).__init__(*groups)
        self.image = prepare.GFX[img_name]
        self.rect = self.image.get_rect(topleft=topleft)


class StatusMeter(pg.sprite.Sprite):
    def __init__(self, topleft, size, frame_color, fill_color, bar_color,
                         frame_width, *groups):
        super(StatusMeter, self).__init__(*groups)
        self.frame_rect = pg.Rect((0, 0), size)
        shrink = -frame_width * 2
        self.inner_rect = self.frame_rect.inflate(shrink, shrink)
        self.surf = pg.Surface(self.frame_rect.size)
        self.rect = self.surf.get_rect(topleft=topleft)

        self.frame_color = parse_color(frame_color)
        self.fill_color = parse_color(fill_color)
        self.bar_color = parse_color(bar_color)
        self.frame_width = frame_width
        self.update(0)

    def update(self, level):
        width = int(self.inner_rect.width * level)
        bar_rect = pg.Rect(self.inner_rect.topleft, (width, self.inner_rect.height))
        self.surf.fill(self.frame_color)
        pg.draw.rect(self.surf, self.fill_color, self.inner_rect)
        pg.draw.rect(self.surf, self.bar_color, bar_rect)
        self.image = self.surf


class NoiseDetector(object):
    """Handles the stealth aspect of the game."""
    def __init__(self, meter_topleft, *groups):
        self.noise_level = 0
        self.max_noise_level = 1000
        self.recovery_rate = 150 / 1000.
        self.meter = StatusMeter(meter_topleft, (100, 20), (58, 41, 18),
                                               (43, 35, 15), (255, 121, 57), 4, *groups)


    def update(self, dt):
        self.recover(dt)
        self.meter.update(self.noise_level / self.max_noise_level)

    def add_noise(self, num=1):
        self.noise_level = min(self.noise_level + num, self.max_noise_level)

    def recover(self, dt):
        amount = self.recovery_rate * dt
        self.noise_level = max(0, self.noise_level - amount)


class Duck(pg.sprite.DirtySprite):
    image_nums = [1, 2]
    def __init__(self, centerpoint, *groups):
        super(Duck, self).__init__(*groups)
        shuffle(self.image_nums)
        self.images = cycle([prepare.GFX["duck{}".format(x)] for x in self.image_nums])
        self.image = next(self.images)
        self.rect = self.image.get_rect(center=centerpoint)
        self.collider = self.rect.copy()
        self.collider.bottom = prepare.WORLD_SIZE[1] + 1000

    def flap(self):
        self.image = next(self.images)


class Flock(pg.sprite.Sprite):
    offsets = [(0, 0), (-40, -40), (40, -40), (-80, -80),
                        (80, -80), (-120, -120), (120, -120)]
    fly_time = 32000
    def __init__(self, leader_centerpoint, animations, all_sprites, *groups):
        super(Flock, self).__init__(*groups)
        x, y  = leader_centerpoint
        for offset in self.offsets:
            center = x + offset[0], y + offset[1]
            duck = Duck(center, all_sprites)
            if offset == (0, 0):
                self.leader = duck
            dest = duck.rect.y + (prepare.WORLD_SIZE[1] * 2)
            ani = Animation(y=dest, duration=self.fly_time, round_values=True)
            ani.callback = duck.kill
            ani.start(duck.rect)
            flap_time = randint(100, 150)
            task = Task(duck.flap, flap_time, self.fly_time // flap_time)
            animations.add(ani, task)
        finish = Task(self.kill, self.fly_time + 100)
        animations.add(finish)
        self.honked = False

    def update(self, hunter):
        #dist = get_distance(self.leader.rect.center, hunter.rect.center)

        dist = hunter.rect.centery - self.leader.rect.centery
        if not self.honked and dist < 2000:
            prepare.SFX["ducks"].play()
            self.honked = True

