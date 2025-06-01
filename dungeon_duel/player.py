from .config import *

class Player:
    def __init__(self, pos, hp=PLAYER_START_HP):
        self.pos = pos
        self.hp = hp
        self.score = 0
        self.alive = True

    def move(self, direction, dungeon):
        if not self.alive:
            return False
        dx, dy = direction
        new_pos = (self.pos[0] + dx, self.pos[1] + dy)
        if dungeon.is_walkable(new_pos):
            dungeon.set_tile(self.pos, TILE_EMPTY)
            self.pos = new_pos
            dungeon.set_tile(self.pos, TILE_PLAYER)
            return True
        return False

    def loot(self, dungeon):
        if dungeon.get_tile(self.pos) == TILE_TREASURE:
            self.score += TREASURE_SCORE
            dungeon.set_tile(self.pos, TILE_EMPTY)
            return True
        return False

    def heal(self, dungeon):
        if dungeon.get_tile(self.pos) == TILE_POTION:
            self.hp = min(self.hp + POTION_HEAL, PLAYER_START_HP)
            dungeon.set_tile(self.pos, TILE_EMPTY)
            return True
        return False

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            self.alive = False
