from random import randint, choice
import itertools as it
import pygame as pg

import tools, prepare
from animation import Animation, Task


strip = tools.strip_from_sheet


class TurkeyState(object):
    """Base class for turkey states to inherit from."""
    directions = ["left", "right", "up", "down"]
    opposites = {"left": "right",
                         "right": "left",
                         "up": "down",
                         "down": "up"}
    def __init__(self, turkey):
        self.done = False
        self.turkey = turkey
        self.timer = 0

    def update(self, dt, trees):
        pass

    def move_turkey(self, dt, trees):
        """
        Check for collisions with trees and move turkey if new position
        is unblocked, otherwise reverse direction.
        """
        t = self.turkey
        x, y  = t.pos
        x += self.speed * dt * t.velocities[t.direction][0]
        y += self.speed * dt * t.velocities[t.direction][1]
        look_ahead = t.collider.copy()
        look_ahead.center = (x, y)
        world = pg.Rect((0, 0), prepare.WORLD_SIZE)
        clamped = look_ahead.clamp(world)
        if (not any((tree.collider.colliderect(look_ahead) for tree in trees))
            and clamped == look_ahead):
            t.pos = (x, y)
            t.rect.center = (x, y)
            t.collider.topleft = (t.rect.centerx + t.collider_offsets[t.direction][0],
                                         t.rect.centery + t.collider_offsets[t.direction][1])
        else:
            direction = self.opposites[t.direction]
            self.turkey.change_direction(self.name, direction)
            x, y  = t.pos
            t.pos = (x + (t.velocities[t.direction][0] * 2),
                         y + (t.velocities[t.direction][1] * 2))
            t.rect.center = t.pos
            t.collider.topleft = (t.rect.centerx + t.collider_offsets[t.direction][0],
                                         t.rect.centery + t.collider_offsets[t.direction][1])


class Walking(TurkeyState):
    """Turkey is walking around the map."""
    def __init__(self, turkey):
        super(Walking, self).__init__(turkey)
        self.name = "walk"
        self.duration = randint(1000, 5000)
        direction = choice(self.directions)
        self.turkey.change_direction(self.name, direction)
        self.speed = 100 / 1000. #random.randint(100, 200) / 1000.
        self.animations = pg.sprite.Group()
        task = Task(self.turkey.flip_image, 30, -1)
        self.animations.add(task)

    def update(self, dt, trees):
        self.animations.update(dt)
        self.timer += dt
        if self.timer >= self.duration:
            self.done = True
        self.move_turkey(dt, trees)


class Idle(TurkeyState):
    """Turkey is standing still."""
    def __init__(self, turkey):
        super(Idle, self).__init__(turkey)
        self.name = "idle"
        self.duration = randint(700, 3000)
        direction = choice(self.directions)
        self.turkey.change_direction(self.name, direction)
        self.animations = pg.sprite.Group()
        task = Task(self.turkey.flip_image, 30, -1)
        self.animations.add(task)

    def update(self, dt, trees):
        self.timer += dt
        if self.timer >= self.duration:
            self.done = True


class Fleeing(TurkeyState):
    """Turkey is running away from the player."""
    def __init__(self, turkey):
        super(Fleeing, self).__init__(turkey)
        self.name = "flee"
        self.duration = randint(500, 1500)
        direction = self.turkey.direction
        self.turkey.change_direction(self.name, direction)
        self.speed = 200 / 1000.
        self.animations = pg.sprite.Group()
        task = Task(self.turkey.flip_image, 15, -1)
        self.animations.add(task)
        self.turkey.gobble()

    def update(self, dt, trees):
        self.animations.update(dt)
        self.timer += dt
        if self.timer >= self.duration:
            self.done = True
        self.move_turkey(dt, trees)


class Turkey(pg.sprite.DirtySprite):
    """
    Create a turkey at a certain map position."""
    sheet = prepare.GFX["turkey-sheet"]
    base_images = {}
    for state_name in ("walk", "idle"):
        base_images[state_name] = {}
        for direct, start in zip(("up", "left", "down", "right"), range(0, 1025, 128)):
            base_images[state_name][direct] = [pg.transform.smoothscale(img, (96, 96))
                                                                     for img in strip(sheet, (0, start) , (128, 128), 4)]
    base_images["flee"] = base_images["walk"]
    directions = ["left", "right", "up", "down"]
    velocities = {"left": (-1, 0), "right": (1, 0), "up": (0, -1), "down": (0, 1)}
    states = {"walk": Walking, "idle": Idle, "flee": Fleeing}
    state_choices = ["walk", "walk", "idle"]
    collider_offsets = {"left": (-8, 2),
                                 "right": (-8, 2),
                                 "up": (-8, -1),
                                 "down": (-8, -1)}
    sounds = [prepare.SFX["gobble{}".format(x)] for x in range(1, 6)]

    def __init__(self, pos, *groups):
        super(Turkey, self).__init__(*groups)
        self.pos = pos
        self.collider = pg.Rect(0, 0, 16, 16)
        state = choice(self.state_choices)
        self.state = self.states[state](self)
        self.speed = 100 / 1000.
        self.gobble_timer = 0
        self.gobble_time_range = (1000, 20000)
        self.gobble_time = randint(*self.gobble_time_range)

    def change_direction(self, state_name, direction):
        """Change direction and switch to the appropriate animation cycle."""
        self.direction = direction
        self.images = it.cycle(self.base_images[state_name][self.direction])
        self.image= next(self.images)
        self.rect = self.image.get_rect(center=self.pos)
        self.collider.topleft = (self.rect.centerx + self.collider_offsets[self.direction][0],
                                         self.rect.centery + self.collider_offsets[self.direction][1])

    def gobble(self):
        """Play a goblle sound."""
        choice(self.sounds).play()

    def flee(self, hunter):
        """Change direction to flee from the player."""
        h = hunter.collider
        t = self.collider
        xdiff = t.centerx - h.centerx
        ydiff = t.centery - h.centery
        if abs(xdiff) < abs(ydiff):
            direct = "left" if xdiff <= 0 else "right"
        else:
            direct = "up" if ydiff <= 0 else "down"
        self.direction = direct
        self.state = self.states["flee"](self)

    def flip_image(self):
        self.image = next(self.images)

    def update(self, dt, trees):
        if self.state.done:
            state = choice(self.state_choices)
            self.state = self.states[state](self)
        self.state.update(dt, trees)


class Roast(pg.sprite.DirtySprite):
    """Created when a Turkey is killed by the player."""
    def __init__(self, pos, *groups):
        super(Roast, self).__init__(*groups)
        self.image = prepare.GFX["roast"]
        self.rect = self.image.get_rect(center=pos)
        self.collider = self.rect.copy()


