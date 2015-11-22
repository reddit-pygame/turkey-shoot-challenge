from random import randint, sample, choice
import pygame as pg
import prepare
from state_engine import GameState
from animation import Animation, Task
from hunter import Hunter
from turkey import Turkey, Roast
from tree import Tree, Leaf
from leaf_spots import leaf_spots
from helpers import AmmoCrate, NoiseDetector, MiniMap, Icon, Duck, Flock
from labels import Label


def footprint_collide(left, right):
    return left.collider.colliderect(right.collider)


def make_background(size, tile_size=64):
    grass = prepare.GFX["grass"]
    w, h  = size
    surf = pg.Surface(size).convert()
    for y in range(0, h + 1, tile_size):
        for x in range(0, w + 1, tile_size):
            surf.blit(grass, (x, y))
    return surf


class Hunting(GameState):
    """The main game state."""
    def __init__(self):
        super(Hunting, self).__init__()
        self.world_surf = pg.Surface(prepare.WORLD_SIZE).convert()
        self.world_rect = self.world_surf.get_rect()
        self.background  = make_background(prepare.WORLD_SIZE)
        self.all_sprites = pg.sprite.LayeredDirty()
        self.colliders = pg.sprite.Group()
        self.ui = pg.sprite.Group()
        self.noise_detector = NoiseDetector((10, 80), self.ui)
        self.hunter = Hunter(self.world_rect.center, 0,
                                       self.noise_detector, self.all_sprites)
        self.turkeys = self.add_turkeys()
        self.bullets = pg.sprite.Group()
        self.make_trees()
        hx, hy = self.hunter.rect.center
        self.ammo_crate = AmmoCrate((hx - 50, hy - 50), self.colliders,
                                                          self.all_sprites)
        self.all_sprites.clear(self.world_surf, self.background)
        self.leaves = pg.sprite.Group()
        self.roasts = pg.sprite.Group()
        self.flocks = pg.sprite.Group()
        self.animations = pg.sprite.Group()
        self.rustle_sounds = [prepare.SFX["rustle{}".format(x)]
                                        for x in range(1, 21)]
        self.wind_gust()
        style = {"font_path": prepare.FONTS["pretzel"],
                     "font_size": 24, "text_color": (58, 41, 18)}
        self.shell_label = Label("{}".format(self.hunter.shells),
                                          {"topleft": (50, 10)}, **style)
        self.roasts_label = Label("{}".format(self.hunter.roasts),
                                             {"topleft": (50, 50)}, **style)
        Icon((20, 3), "shell", self.ui)
        Icon((10, 45), "roast", self.ui)
        self.add_flock()        
        
    def wind_gust(self):
        """Play wind sound and set up next gust."""
        prepare.SFX["wind"].play()
        task = Task(self.wind_gust, randint(15000, 45000))
        self.animations.add(task)

    def add_turkeys(self):
        """Spawn turkeys."""
        turkeys = pg.sprite.Group()
        w, h = prepare.WORLD_SIZE
        for _ in range(35):
            pos = randint(20, w - 20), randint(20, h - 20)
            Turkey(pos, turkeys, self.all_sprites)
        return turkeys
          
    def make_trees(self):
        """Spawn trees."""
        self.trees = pg.sprite.Group()
        w, h  = prepare.WORLD_SIZE
        for _ in range(120):
            while True:
                pos = (randint(50, w - 20), randint(20, h - 20))
                tree = Tree(pos)
                collisions = (tree.collider.colliderect(other.collider)
                                   for other in self.colliders) 
                if not any(collisions) and not tree.collider.colliderect(self.hunter.collider):
                    break
            self.trees.add(tree)
            self.colliders.add(tree)
            self.all_sprites.add(tree)

    def add_flock(self):
        """Add a Flock of birds."""
        flock = Flock((self.hunter.collider.centerx, -1500), self.animations,
                             self.all_sprites, self.flocks)
        next_flock = randint(45000, 150000) #next flock in 45-150 seconds
        task = Task(self.add_flock, next_flock)
        self.animations.add(task)

    def update(self, dt):
        self.animations.update(dt)
        keys = pg.key.get_pressed()
        self.hunter.update(dt, keys, self.bullets, self.turkeys,
                                    self.colliders, self.all_sprites, self.animations)
        self.turkeys.update(dt, self.trees)
        self.bullets.update(dt)
        for sprite in self.all_sprites:
            self.all_sprites.change_layer(sprite, sprite.collider.bottom)
        
        tree_hits = pg.sprite.groupcollide(self.bullets, self.trees, True,
                                                          False, footprint_collide)
        for bullet in tree_hits:
            for tree in tree_hits[bullet]:
                choice(self.rustle_sounds).play()
                num = randint(3, 9)
                for spot_info in sample(leaf_spots[tree.trunk], num):
                    self.add_leaf(tree, spot_info)
        
        turkey_hits = pg.sprite.groupcollide(self.bullets, self.turkeys,
                                                              True, True, footprint_collide)
        for t_bullet in turkey_hits:
            for turkey in turkey_hits[t_bullet]:
                Roast(turkey.pos, self.roasts, self.all_sprites)
        
        if self.hunter.shells < self.hunter.max_shells:
            if self.hunter.collider.colliderect(self.ammo_crate.rect.inflate(16, 16)):
                prepare.SFX["gunload"].play()
                self.hunter.shells = self.hunter.max_shells

        if self.hunter.state == "move":
            self.scare_turkeys()
        self.noise_detector.update(dt)
        self.shell_label.set_text("{}".format(self.hunter.shells))
        self.roasts_label.set_text("{}".format(self.hunter.roasts))
        roast_collisions = pg.sprite.spritecollide(self.hunter, self.roasts,
                                                                   True, footprint_collide)
        if roast_collisions:
            prepare.SFX["knifesharpener"].play()
            self.hunter.roasts += len(roast_collisions)            
        self.mini_map.update(self.world_surf, self.hunter, self.turkeys)
        self.flocks.update(self.hunter)
        
    def scare_turkeys(self):
        """Make turkeys flee depending on distance and the player's noise level."""
        size = self.noise_detector.noise_level
        scare_rect = self.hunter.collider.inflate(size, size)
        scared_turkeys = (t for t in self.turkeys
                                    if t.collider.colliderect(scare_rect) and t.state.name != "flee")
        for scared in scared_turkeys:
            scared.flee(self.hunter)

    def add_leaf(self, tree, spot_info):
        """Add a falling leaf."""
        fall_time = randint(2000, 2500)
        leaf = Leaf(tree, spot_info, self.leaves, self.all_sprites)
        y = leaf.rect.centery + leaf.fall_distance
        ani = Animation(centery=y, duration=fall_time, round_values=True)
        ani.callback = leaf.land
        ani.start(leaf.rect)
        ani2 = Animation(centery=leaf.collider.centery + leaf.fall_distance,
                                   duration=fall_time, round_values=True)
        ani2.start(leaf.collider)
        fade = Animation(img_alpha=0, duration=3000, delay=fall_time,
                                  round_values=True)
        fade.callback = leaf.kill
        fade.update_callback = leaf.set_alpha
        fade.start(leaf)
        self.animations.add(ani, ani2, fade)

    def get_view_rect(self):
        """
        Return the currently visible portion of the world map
        centered on the player.
        """
        view_rect = pg.Rect((0, 0), prepare.SCREEN_SIZE)
        view_rect.center = self.hunter.pos
        view_rect.clamp_ip(self.world_rect)
        return view_rect

    def draw(self, surface):
        self.all_sprites.draw(self.world_surf)
        rect = self.get_view_rect()
        surf = self.world_surf.subsurface(rect)        
        surface.blit(surf, (0, 0))
        self.shell_label.draw(surface)
        self.roasts_label.draw(surface)
        self.ui.draw(surface)

        
