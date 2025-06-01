import arcade
import random
import numpy as np
import heapq
from .config import *
from sklearn.naive_bayes import GaussianNB

SCREEN_WIDTH = GRID_WIDTH * TILE_SIZE
SCREEN_HEIGHT = GRID_HEIGHT * TILE_SIZE + 80
SCREEN_TITLE = "Dungeon Duel: Rogue AI (Arcade Edition)"

class DungeonArcade(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)
        self.reset_game() # Call reset_game in __init__

    def reset_game(self):
        self.grid = np.zeros((GRID_HEIGHT, GRID_WIDTH), dtype=int)
        self.player_pos = (0, 0)
        self.monster_pos = (0, 0)
        self.player_hp = PLAYER_START_HP
        self.monster_hp = MONSTER_START_HP
        self.player_lives = 3 # Add player lives
        self.score = 0
        self.turn = 'player'
        self.state = 'ongoing'
        self.message = ''
        self.generate_dungeon()
        # For Naive Bayes
        self.player_history = []  # (prev_pos, move_dir)
        self.nb_model = GaussianNB()
        self.nb_trained = False
        self.setup() # Call setup at the end of reset_game

    def generate_dungeon(self):
        self.grid.fill(TILE_EMPTY)
        for _ in range(NUM_WALLS):
            self._place_random(TILE_WALL)
        for _ in range(NUM_TREASURES):
            self._place_random(TILE_TREASURE)
        for _ in range(NUM_POTIONS):
            self._place_random(TILE_POTION)
        self.player_pos = self._place_random(TILE_PLAYER)
        self.monster_pos = self._place_random(TILE_MONSTER)
        self.monster_hp = MONSTER_START_HP

    def _place_random(self, tile):
        while True:
            x = random.randint(0, GRID_WIDTH - 1)
            y = random.randint(0, GRID_HEIGHT - 1)
            if self.grid[y, x] == TILE_EMPTY:
                self.grid[y, x] = tile
                return (x, y)

    def setup(self):
        self.monster_move_timer = 0
        self.monster_move_interval = 0.25  # seconds between monster moves

    def on_update(self, delta_time):
        if self.state == 'ongoing':
            if not hasattr(self, 'monster_move_timer'):
                self.setup()
            self.monster_move_timer += delta_time
            if self.monster_move_timer >= self.monster_move_interval:
                self.monster_turn()
                self.monster_move_timer = 0

    def on_draw(self):
        self.clear()
        # Use a single dark color for all floor tiles
        floor_color = arcade.color.DARK_SLATE_GRAY
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                px = x * TILE_SIZE
                py = y * TILE_SIZE
                arcade.draw_lrbt_rectangle_filled(px, px+TILE_SIZE, py, py+TILE_SIZE, floor_color)
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                tile = self.grid[y, x]
                px = x * TILE_SIZE
                py = y * TILE_SIZE
                if tile == TILE_WALL:
                    arcade.draw_lrbt_rectangle_filled(px, px+TILE_SIZE, py, py+TILE_SIZE, arcade.color.GRAY)
                    arcade.draw_lrbt_rectangle_outline(px+2, px+TILE_SIZE-2, py+2, py+TILE_SIZE-2, arcade.color.DARK_BROWN, 3)
                elif tile == TILE_TREASURE:
                    arcade.draw_lrbt_rectangle_filled(px+6, px+TILE_SIZE-6, py+6, py+TILE_SIZE-6, arcade.color.DARK_GOLDENROD)
                    arcade.draw_lrbt_rectangle_outline(px+6, px+TILE_SIZE-6, py+6, py+TILE_SIZE-6, arcade.color.GOLD, 2)
                elif tile == TILE_POTION:
                    arcade.draw_ellipse_filled(px+TILE_SIZE//2, py+TILE_SIZE//2, TILE_SIZE//2, TILE_SIZE//3, arcade.color.DARK_MAGENTA)
                elif tile == TILE_PLAYER:
                    arcade.draw_circle_filled(px+TILE_SIZE//2, py+TILE_SIZE//2, TILE_SIZE//2-4, arcade.color.DARK_CYAN)
                    arcade.draw_text("P", px+TILE_SIZE//2-8, py+TILE_SIZE//2-12, arcade.color.WHITE, 24, bold=True)
        # Draw the monster
        if self.monster_hp > 0:
            mx, my = self.monster_pos
            px = mx * TILE_SIZE
            py = my * TILE_SIZE
            arcade.draw_circle_filled(px+TILE_SIZE//2, py+TILE_SIZE//2, TILE_SIZE//2-4, arcade.color.DARK_SPRING_GREEN)
            arcade.draw_text("M", px+TILE_SIZE//2-8, py+TILE_SIZE//2-12, arcade.color.RED, 24, bold=True)
        self.draw_ui()

    def draw_ui(self):
        # Center the game name at the very top, with good vertical spacing
        title_y = SCREEN_HEIGHT - 10
        stats_y = SCREEN_HEIGHT - 50
        turn_y = SCREEN_HEIGHT - 90
        log_y = SCREEN_HEIGHT - 120
        gameover_y = SCREEN_HEIGHT - 150
        arcade.draw_text("DUNGEON DUEL: ROGUE AI", SCREEN_WIDTH//2, title_y, arcade.color.WHITE, 32, anchor_x="center", anchor_y="top", align="center")
        arcade.draw_text(f"Player HP: {self.player_hp}    Lives: {self.player_lives}    Score: {self.score}    Monster HP: {self.monster_hp}", SCREEN_WIDTH//2, stats_y, arcade.color.WHITE, 20, anchor_x="center", anchor_y="top")
        arcade.draw_text(f"Turn: {self.turn.capitalize()}", SCREEN_WIDTH//2, turn_y, arcade.color.LIGHT_GRAY, 16, anchor_x="center", anchor_y="top")
        if self.message:
            arcade.draw_text(self.message, SCREEN_WIDTH//2, log_y, arcade.color.LIGHT_YELLOW, 18, anchor_x="center", anchor_y="top")
        if self.state != 'ongoing':
            arcade.draw_text(f"Game Over: {self.state.replace('_', ' ').title()} (Press R to restart)", SCREEN_WIDTH//2, gameover_y, arcade.color.YELLOW, 22, anchor_x="center", anchor_y="top")

    def on_key_press(self, key, modifiers):
        if key == arcade.key.R: # Handle R key press for restart regardless of game state
            self.reset_game()
            return

        if self.state != 'ongoing':
            return
        
        dx, dy = 0, 0
        action = None
        if key == arcade.key.UP:
            dx, dy = 0, 1
            action = 'move'
        elif key == arcade.key.DOWN:
            dx, dy = 0, -1
            action = 'move'
        elif key == arcade.key.LEFT:
            dx, dy = -1, 0
            action = 'move'
        elif key == arcade.key.RIGHT:
            dx, dy = 1, 0
            action = 'move'
        elif key == arcade.key.L:
            action = 'loot'
        elif key == arcade.key.H:
            action = 'heal'
        elif key == arcade.key.SPACE:
            action = 'fight'
        # elif key == arcade.key.R: # Removed from here
        #     # Regenerate dungeon for a new random arena
        #     self.__init__()
        #     return
        if action == 'move':
            self.try_move(dx, dy)
        elif action == 'loot':
            self.try_loot()
        elif action == 'heal':
            self.try_heal()
        elif action == 'fight':
            self.try_fight()

    def a_star(self, start, goal):
        # A* pathfinding on the dungeon grid
        open_set = []
        heapq.heappush(open_set, (0, start))
        came_from = {}
        g_score = {start: 0}
        f_score = {start: abs(goal[0]-start[0]) + abs(goal[1]-start[1])}
        while open_set:
            _, current = heapq.heappop(open_set)
            if current == goal:
                # Reconstruct path
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.reverse()
                return path
            for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                neighbor = (current[0]+dx, current[1]+dy)
                if not (0 <= neighbor[0] < GRID_WIDTH and 0 <= neighbor[1] < GRID_HEIGHT):
                    continue
                if self.grid[neighbor[1], neighbor[0]] == TILE_WALL:
                    continue
                tentative_g = g_score[current] + 1
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + abs(goal[0]-neighbor[0]) + abs(goal[1]-neighbor[1])
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))
        return []  # No path found

    def monster_turn(self):
        # Monster uses simulated annealing to pick target: player, treasure, or potion
        mx, my = self.monster_pos
        # Build list of all possible targets
        all_targets = [('player', self.player_pos)]
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.grid[y, x] == TILE_POTION:
                    all_targets.append(('potion', (x, y)))
                elif self.grid[y, x] == TILE_TREASURE:
                    all_targets.append(('treasure', (x, y)))
        # Filter only reachable targets
        reachable_targets = []
        for ttype, pos in all_targets:
            if self.a_star((mx, my), pos):
                reachable_targets.append((ttype, pos))
        # Always fallback to chasing player if nothing else is reachable
        if not reachable_targets:
            reachable_targets = [('player', self.player_pos)]
        # Use simulated annealing to pick target
        target_type, target_pos = self.simulated_annealing(reachable_targets)
        path = self.a_star((mx, my), target_pos)
        if not path:
            return  # No path to target
        # Move along the path
        next_pos = path[0]
        tile_at_next = self.grid[next_pos[1], next_pos[0]]
        if tile_at_next in (TILE_EMPTY, TILE_TREASURE, TILE_POTION, TILE_PLAYER):
            self.grid[my, mx] = TILE_EMPTY
            self.monster_pos = next_pos
            # Collect treasure or potion if on it
            if tile_at_next == TILE_TREASURE:
                self.message = 'Monster collects treasure!'
            elif tile_at_next == TILE_POTION:
                self.monster_hp = min(self.monster_hp + POTION_HEAL, MONSTER_START_HP)
                self.message = 'Monster heals!'
            self.grid[next_pos[1], next_pos[0]] = TILE_MONSTER
            if next_pos == self.player_pos:
                self.monster_combat_minmax()
        if self.monster_pos == self.player_pos:
            self.monster_combat_minmax()

    def get_targets(self):
        # List of (type, pos) for player, potions, treasures
        targets = [('player', self.player_pos)]
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.grid[y, x] == TILE_POTION:
                    targets.append(('potion', (x, y)))
                elif self.grid[y, x] == TILE_TREASURE:
                    targets.append(('treasure', (x, y)))
        return targets

    def simulated_annealing(self, targets):
        # Cost: distance + (bonus if low HP and potion, or if treasure)
        mx, my = self.monster_pos
        temp = 10.0
        cooling = 0.95
        current = random.choice(targets)
        def cost(target):
            ttype, pos = target
            dist = abs(mx - pos[0]) + abs(my - pos[1])
            if ttype == 'player':
                return dist - 100  # extremely prefer chasing player
            if ttype == 'potion' and self.monster_hp < MONSTER_START_HP//2:
                return dist - 10  # prefer potion if low HP
            if ttype == 'treasure':
                return dist - 2  # prefer treasure a bit
            return dist
        best = current
        best_cost = cost(current)
        for _ in range(20):
            candidate = random.choice(targets)
            delta = cost(candidate) - cost(current)
            if delta < 0 or random.random() < np.exp(-delta/temp):
                current = candidate
                if cost(current) < best_cost:
                    best = current
                    best_cost = cost(current)
            temp *= cooling
        return best

    def predict_player_next_pos(self):
        # Use Naive Bayes to predict next move direction
        if not self.nb_trained or len(self.player_history) < 5:
            return None
        last_pos, _ = self.player_history[-1]
        X = np.array([[last_pos[0], last_pos[1]]])
        pred = self.nb_model.predict(X)[0]
        dx, dy = pred
        return (last_pos[0] + dx, last_pos[1] + dy)

    def update_naive_bayes(self, prev_pos, move_dir):
        self.player_history.append((prev_pos, move_dir))
        if len(self.player_history) >= 5:
            X = np.array([[pos[0], pos[1]] for pos, _ in self.player_history])
            y = np.array([move for _, move in self.player_history])
            self.nb_model.fit(X, y)
            self.nb_trained = True

    def monster_combat_minmax(self):
        # Min-Max: choose best action (attack, defend, heal)
        actions = ['attack']
        x, y = self.monster_pos
        mhp = self.monster_hp # Current monster HP before this turn's action
        php = self.player_hp # Current player HP

        if self.grid[y, x] == TILE_POTION and mhp < MONSTER_START_HP:
            # This logic seems to be for monster standing on a potion tile.
            # The minmax should decide if healing is better than attacking.
            # Let's ensure 'heal' is a valid action for minmax if on potion.
            pass # Minmax will consider healing if it's a good move.

        # Determine best action using Min-Max
        # The minmax function simulates outcomes. Here we apply the chosen action.
        best_action = None
        best_score = -float('inf')

        # Possible actions for the monster. Minmax will choose one.
        possible_actions_for_minmax = ['attack']
        # If monster is on a potion and not full HP, it can consider healing.
        if self.grid[y,x] == TILE_POTION and self.monster_hp < MONSTER_START_HP:
            possible_actions_for_minmax.append('heal')

        for action_option in possible_actions_for_minmax:
            # Score is from monster's perspective (higher is better for monster)
            score = self.minmax(php, mhp, action_option, depth=2) 
            if score > best_score:
                best_score = score
                best_action = action_option

        if best_action == 'heal':
            self.monster_hp = min(mhp + POTION_HEAL, MONSTER_START_HP)
            # Monster consumes the potion, so grid should be updated if it was TILE_POTION
            # Assuming monster is on its own tile after moving, or on player tile for combat.
            # If monster_pos was a potion tile, it should become TILE_MONSTER or TILE_EMPTY if monster moves off.
            # This part needs careful handling of grid state if monster heals on a potion tile.
            # For now, assume monster is on its designated tile or player's tile.
            # If monster is on a potion tile it picked up: self.grid[y,x] = TILE_MONSTER (or TILE_EMPTY if it moves)
            self.message = 'Monster heals itself!'
        elif best_action == 'attack': # Default or chosen action
            self.player_hp -= HIT_DAMAGE
            self.message = 'Monster attacks you!'
            # Check player death after monster's attack
            if self.player_hp <= 0:
                self.player_lives -= 1
                if self.player_lives > 0:
                    self.message = f"Monster defeated you! {self.player_lives} lives remaining."
                    self.player_hp = PLAYER_START_HP
                    # self.player_pos = self._place_random(TILE_PLAYER) # Optional: move player
                    self.turn = 'player' # Give turn back to player to continue
                else:
                    self.state = 'player_dead'
                    self.message = "Game Over! Monster defeated you and you ran out of lives."
            # Monster doesn't take damage from its own attack action here.
            # Monster HP only changes if it heals or if player attacks it (in try_fight).
        
        # Check if monster was defeated (e.g. by a trap or player's previous action if not handled yet)
        # This specific block might be redundant if try_fight handles monster death thoroughly.
        # However, if monster could die from other means on its turn, it's a safeguard.
        if self.monster_hp <= 0 and self.state == 'ongoing': # Ensure game is still ongoing
            self.grid[self.monster_pos[1], self.monster_pos[0]] = TILE_EMPTY
            self.monster_hp = 0
            self.message = "Monster has been defeated!"
            self.score += 50
            # Potentially change game state if monster was a boss, e.g., self.state = 'player_win'

    def minmax(self, player_hp, monster_hp, action, depth):
        # Simple min-max: maximize monster's survival
        if action == 'attack':
            player_hp -= HIT_DAMAGE
            monster_hp -= HIT_DAMAGE
        elif action == 'heal':
            monster_hp = min(monster_hp + POTION_HEAL, MONSTER_START_HP)
        if player_hp <= 0:
            return 100
        if monster_hp <= 0:
            return -100
        if depth == 0:
            return monster_hp - player_hp
        # Assume player always attacks
        return -self.minmax(monster_hp - HIT_DAMAGE, player_hp - HIT_DAMAGE, 'attack', depth-1)

    def try_move(self, dx, dy):
        x, y = self.player_pos
        nx, ny = x+dx, y+dy
        # Allow player to move into monster tile and trigger combat
        if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT and self.grid[ny, nx] in (TILE_EMPTY, TILE_TREASURE, TILE_POTION, TILE_MONSTER):
            self.grid[y, x] = TILE_EMPTY
            self.player_pos = (nx, ny)
            self.grid[ny, nx] = TILE_PLAYER
            self.message = ''
            self.update_naive_bayes((x, y), (dx, dy))
            if (nx, ny) == self.monster_pos and self.monster_hp > 0:
                self.monster_combat_minmax()
        else:
            self.message = 'Blocked!'
        if self.state == 'ongoing':
            self.monster_turn()

    def try_loot(self):
        x, y = self.player_pos
        if self.grid[y, x] == TILE_TREASURE:
            self.score += TREASURE_SCORE
            self.grid[y, x] = TILE_PLAYER
            self.message = 'Looted treasure!'
        else:
            self.message = 'No treasure here.'
        if self.state == 'ongoing':
            self.monster_turn()

    def try_heal(self):
        x, y = self.player_pos
        if self.grid[y, x] == TILE_POTION:
            self.player_hp = min(self.player_hp + POTION_HEAL, PLAYER_START_HP)
            self.grid[y, x] = TILE_PLAYER
            self.message = 'Healed!'
        else:
            self.message = 'No potion here.'
        if self.state == 'ongoing':
            self.monster_turn()

    def try_fight(self):
        if self.player_pos == self.monster_pos:
            self.player_hp -= HIT_DAMAGE
            self.monster_hp -= HIT_DAMAGE
            self.message = f'You and the monster exchange blows!'
            if self.player_hp <= 0:
                self.player_lives -= 1
                if self.player_lives > 0:
                    self.message = f"You died! {self.player_lives} lives remaining."
                    self.player_hp = PLAYER_START_HP # Reset player HP
                    # Optional: Consider resetting player position or the level
                    # self.player_pos = self._place_random(TILE_PLAYER)
                    self.turn = 'player'
                else:
                    self.state = 'player_dead' # Changed from 'monster_win'
                    self.message = "Game Over! You ran out of lives."
            elif self.monster_hp <= 0:
                # Monster defeated logic (e.g., score, remove monster)
                self.grid[self.monster_pos[1], self.monster_pos[0]] = TILE_EMPTY # Remove monster from grid
                self.monster_hp = 0 # Ensure monster HP is 0
                self.message = "Monster defeated!"
                self.score += 50 # Example: add score for defeating monster
                # Potentially spawn a new monster or end the level/game if it's a boss
        else:
            self.message = 'No monster here.'
        if self.state == 'ongoing':
            self.monster_turn()


def main():
    window = DungeonArcade()
    arcade.run()

if __name__ == '__main__':
    main()
