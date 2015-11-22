#Turkey Shoot Challenge

A seasonally-themed challenge for autumn, this one focuses on implementing a mini-map to help the player navigate the game world. The provided code is a
 topdown shooter where you hunt turkeys.

Github repo: https://github.com/reddit-pygame/turkey-shoot-challenge


##How It Works

*Turkeys*

Turkeys use a simple state engine to determine their behavior. The duration of each state (Walking, Idle, Fleeing) is randomly determined when it is instantiated. When the 
current state finishes a new state is randomly chosen and instantiated (the Fleeing state is never chosen randomly).

Turkeys are a nervous lot and will flee from the player (see Stealth section below).

*Stealth* 

Each footstep adds to the player's noise level (orange meter in topleft corner of screen). The distance at which turkeys flee is determined by the player's noise level. The noise level will 
slowly decrease over time.

*Ammo*

The player can only carry ten shotgun shells at a time. There is an ammo crate located at the center of the map. Stand next to the ammo crate to reload.

*Collisions*

Turkey and Hunter objects use a "look ahead" collision system for collisions with Trees (and any other collidable sprites in the `colliders` group). A sprite is only moved to a new position if the sprite's footprint at that 
postion doesn't result in any collisions. If the new position is blocked, turkeys will reverse direction; the player will simply not move.

Bullet collisions are handled normally and are imperfect - it's possible for a bullet to travel "through" a turkey or tree without triggering a collision.

*Drawing*

The game world is drawn onto a 3200x3200 surface and a screen-sized subsurface centered on the player's position and clamped inside the bounding rectangle of the world surface is drawn to the screen. This keeps the
 player centered on the screen until they reach the edge of the world map. This approach also avoids having to either move all the game objects or calculate their screen positions (this is possible because
the mouse isn't used, otherwise you would need to at least calculate the relative world position of the mouse).

##Controls

UP: Move player forward

SHIFT: Hustle

LEFT / RIGHT: Rotate player

SPACE: Shoot

F: Toggle fullscreen

ESC: Exit

#Challenge

**You are Here** Implement a mini-map that displays the player and ammo crate positions. This will require scaling the sprites' world positions relative to the mini-map, e.g., a position of (100, 100) on a 1000x1000 world map
 should be drawn at (20, 20) on a 200x200 mini-map (relative to the topleft position of the minimap).

###Achievements

**Can't Kill What You Can't See** The current implementation allows offscreen turkeys to be shot. Change this so that only visible turkeys can be killed.

**Off the Map** Stop the player from leaving the boundaries of the world map.

**Ghost Roast** Roasts dropped when turkeys are killed should fade away over time then disappear.

**Projection Perfection** Implement a better system for bullet collisions that doesn't allow bullets to pass "through" trees or turkeys.

#[Happy Thanksgiving - Gobble, Gobble!](https://www.youtube.com/watch?v=MKiwwO9KBpA&feature=youtu.be&t=1640)