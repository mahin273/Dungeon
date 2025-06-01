import numpy as np
import random
from .config import *

class Dungeon:
    def __init__(self, width=GRID_WIDTH, height=GRID_HEIGHT):
        self.width = width
        self.height = height
        self.grid = np.zeros((height, width), dtype=int)
        self.player_pos = None
        self.monster_pos = None
        self.generate()

    def generate(self):
        self.grid.fill(TILE_EMPTY)
        # Place walls
        for _ in range(NUM_WALLS):
            x, y = self._random_empty()
            self.grid[y, x] = TILE_WALL
        # Place treasures
        for _ in range(NUM_TREASURES):
            x, y = self._random_empty()
            self.grid[y, x] = TILE_TREASURE
        # Place potions
        for _ in range(NUM_POTIONS):
            x, y = self._random_empty()
            self.grid[y, x] = TILE_POTION
        # Place player
        x, y = self._random_empty()
        self.grid[y, x] = TILE_PLAYER
        self.player_pos = (x, y)
        # Place monster
        x, y = self._random_empty()
        self.grid[y, x] = TILE_MONSTER
        self.monster_pos = (x, y)

    def _random_empty(self):
        while True:
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            if self.grid[y, x] == TILE_EMPTY:
                return x, y

    def get_tile(self, pos):
        x, y = pos
        return self.grid[y, x]

    def set_tile(self, pos, tile):
        x, y = pos
        self.grid[y, x] = tile

    def is_walkable(self, pos):
        x, y = pos
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.grid[y, x] in (TILE_EMPTY, TILE_TREASURE, TILE_POTION)
        return False
