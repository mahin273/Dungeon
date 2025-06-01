from .config import *
from .dungeon import Dungeon
from .player import Player
from .ai_monster import AIMonster
from .combat import resolve_combat

class GameEngine:
    def __init__(self):
        self.dungeon = Dungeon()
        self.player = Player(self.dungeon.player_pos)
        self.monster = AIMonster(self.dungeon.monster_pos)
        self.turn = 'player'  # or 'monster'
        self.state = 'ongoing'  # or 'player_win', 'monster_win', 'draw'
        self.turn_count = 0
        self.max_turns = MAX_TURNS
        self.history = []  # For AI learning

    def next_turn(self):
        if self.state != 'ongoing':
            return
        self.turn_count += 1
        if self.turn == 'player':
            self.turn = 'monster'
        else:
            self.turn = 'player'
        self.check_end()

    def check_end(self):
        if not self.player.alive:
            self.state = 'monster_win'
        elif not self.monster.alive:
            self.state = 'player_win'
        elif self.turn_count >= self.max_turns:
            self.state = 'draw'

    def player_action(self, action, direction=None):
        if self.turn != 'player' or self.state != 'ongoing':
            return
        if action == 'move' and direction:
            self.player.move(direction, self.dungeon)
        elif action == 'loot':
            self.player.loot(self.dungeon)
        elif action == 'heal':
            self.player.heal(self.dungeon)
        elif action == 'fight':
            if self.player.pos == self.monster.pos:
                self.state = resolve_combat(self.player, self.monster)
        self.next_turn()

    def monster_action(self):
        if self.turn != 'monster' or self.state != 'ongoing':
            return
        # AI decides action
        self.monster.move(self.dungeon, self.player.pos)
        if self.monster.pos == self.player.pos:
            self.state = resolve_combat(self.player, self.monster)
        self.next_turn()
