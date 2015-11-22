import itertools
from math import degrees, pi
import pygame as pg

import prepare
from prepare import GFX
from angles import project
from bullet import Bullet
from animation import Animation, Task

SIZE = (96, 96)

class Hunter(pg.sprite.DirtySprite):
    """The player's character."""
    moves = [pg.transform.smoothscale(GFX["move_{}".format(x)], SIZE) for x in range(20)]
    shoots = [pg.transform.smoothscale(GFX["shoot_{}".format(x)], SIZE) for x in range(3)]
    idles = [pg.transform.smoothscale(GFX["idle_{}".format(x)], SIZE) for x in range(19)]
    base_images = {
            "move": itertools.cycle(moves),
            "shoot": itertools.cycle(shoots),
            "idle": itertools.cycle(idles)}
    walk_sounds = itertools.cycle([prepare.SFX["step{}".format(x)] for x in range(1, 3)])

    def __init__(self, pos, angle, noise_detector, *groups):
        super(Hunter, self).__init__(*groups)
        self.pos = pos
        self.angle = angle
        self.speed = 80 / 1000.
        self.controls = {
                "turn left": [pg.K_LEFT, pg.K_a],
                "turn right": [pg.K_RIGHT, pg.K_d],
                "move": [pg.K_UP, pg.K_w],
                "hustle": [pg.K_LSHIFT, pg.K_RSHIFT]}
        self.actions = {
                "turn left": self.turn_left,
                "turn right": self.turn_right,
                "move": self.move}
        self.state = "idle"
        self.images = self.base_images[self.state]
        self.current_image = next(self.images)
        self.image = pg.transform.rotate(self.current_image, degrees(self.angle))
        self.rect = self.image.get_rect(center=self.pos)
        self.collider = pg.Rect(0, 0, 20, 20)
        self.collider.center = self.pos
        self.ani_timer = 0
        self.ani_time = 40
        self.cooldown_timer = 0
        self.cooldown_time = 1000
        self.rot_speed = (.5 * pi) / 1000.
        self.animations = pg.sprite.Group()
        self.footstep_animations = pg.sprite.Group()
        self.roasts = 0
        self.max_shells = 10
        self.shells = self.max_shells
        self.noise_detector = noise_detector

    def play_walk_sound(self):
        """
        Play a footstep sound, increase the player's noise level and
        set up the next footstep.
        """
        next(self.walk_sounds).play()
        self.noise_detector.add_noise(80 * self.hustle)
        self.start_walking()

    def start_walking(self):
        """Add a footstep sound with delay depending on player's movement."""
        task = Task(self.play_walk_sound, 400 // self.hustle)
        self.footstep_animations.add(task)

    def stop_walking(self):
        """Stop playing footstep sounds."""
        self.footstep_animations.empty()

    def flip_state(self, new_state):
        """
        Set self.state to new_state and switch to the appropriate
        animation cycle.
        """
        self.state = new_state
        self.images = self.base_images[self.state]
        self.current_image = next(self.images)
        self.image = pg.transform.rotate(self.current_image, degrees(self.angle))
        self.rect = self.image.get_rect(center=self.pos)

    def update(self, dt, keys, bullets, turkeys, colliders, all_sprites, animations):
        self.hustle = 1
        if any((keys[k] for k in self.controls["hustle"])):
            self.hustle = 1.5
        self.animations.update(dt)
        self.footstep_animations.update(dt)
        self.cooldown_timer += dt
        self.ani_timer += dt
        if self.ani_timer >= self.ani_time:
            self.ani_timer -= self.ani_time
            self.current_image = next(self.images)
            angle = degrees(self.angle)
            self.image = pg.transform.rotate(self.current_image, angle)
            self.rect = self.image.get_rect(center=self.pos)

        for action in self.actions:

            if any((keys[key] for key in self.controls[action])):
                self.actions[action](dt, colliders)
                if action == "move":
                    self.actions[action](dt, colliders)

                else:
                    self.actions[action](dt)
        if keys[pg.K_SPACE]:
            self.shoot(bullets, turkeys, all_sprites, animations)
        if not any((keys[x] for x in self.controls["move"])):
            if self.state == "move":
                self.flip_state("idle")
                self.stop_walking()

    def turn(self, dt, direction):
        self.angle += self.rot_speed * dt * direction
        angle = degrees(self.angle)
        self.image = pg.transform.rotate(self.current_image, angle)
        self.rect = self.image.get_rect(center=self.pos)

    def turn_left(self, dt, *args):
        self.turn(dt, 1)

    def turn_right(self, dt, *args):
        self.turn(dt, -1)

    def move(self, dt, colliders):
        if self.state == "shoot":
            return
        elif self.state != "move":
            self.flip_state("move")
            self.start_walking()
        dist = self.speed * dt * self.hustle
        pos = project(self.pos, self.angle, dist)
        collider = self.collider.copy()
        collider.center = pos
        if not any((collider.colliderect(obj.collider) for obj in colliders)):
            self.pos = pos
            self.rect.center = self.pos
            self.collider.center = self.pos

    def shoot(self, bullets, turkeys, all_sprites, animations):
        """
        Fire a bullet if the player has enough ammo and enough time has passed
        since the last shot.
        """
        if self.cooldown_timer >= self.cooldown_time:
            self.stop_walking()
            if self.shells <= 0:
                prepare.SFX["gunclick"].play()
            else:
                self.shells -= 1
                prepare.SFX["gunshot"].play()
                pos = project(self.pos, (self.angle - .1745) % (2 * pi), 42) #end of rifle at 96x96
                bullet  = Bullet(pos, self.angle, bullets, all_sprites)
                distance = 2000.
                x, y  = project(pos, self.angle, distance)
                ani = Animation(centerx=x, centery=y, duration=distance/bullet.speed, round_values=True)
                ani.callback = bullet.kill
                ani.start(bullet.rect)
                animations.add(ani)
                scare_rect = self.collider.inflate(1200, 1200)
                scared_turkeys = [t for t in turkeys if scare_rect.colliderect(t.collider)]
                for scared in scared_turkeys:
                    task = Task(scared.flee, 750, args=(self,))
                    self.animations.add(task)
            task = Task(self.flip_state, 120, args=("idle",))
            animations.add(task)
            self.cooldown_timer = 0
            self.flip_state("shoot")

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        pg.draw.rect(surface, pg.Color("red"), self.rect, 2)