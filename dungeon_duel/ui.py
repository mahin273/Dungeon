import pygame
from .config import *

class GameUI:
    def __init__(self, engine):
        pygame.init()
        self.engine = engine
        self.screen = pygame.display.set_mode((GRID_WIDTH * TILE_SIZE, GRID_HEIGHT * TILE_SIZE + 60))
        pygame.display.set_caption('Dungeon Duel: Rogue AI')
        self.font = pygame.font.SysFont('consolas', 24)

    def draw(self):
        self.screen.fill(COLOR_BG)
        grid = self.engine.dungeon.grid
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                tile = grid[y, x]
                color = COLOR_BG
                if tile == TILE_WALL:
                    color = COLOR_WALL
                elif tile == TILE_TREASURE:
                    color = COLOR_TREASURE
                elif tile == TILE_POTION:
                    color = COLOR_POTION
                elif tile == TILE_PLAYER:
                    color = COLOR_PLAYER
                elif tile == TILE_MONSTER:
                    color = COLOR_MONSTER
                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, (40, 40, 40), rect, 1)
        # Draw UI text
        self.draw_ui()
        pygame.display.flip()

    def draw_ui(self):
        player = self.engine.player
        monster = self.engine.monster
        text = f"Player HP: {player.hp}  Score: {player.score}   Monster HP: {monster.hp}   Turn: {self.engine.turn.capitalize()}"
        surf = self.font.render(text, True, COLOR_TEXT)
        self.screen.blit(surf, (10, GRID_HEIGHT * TILE_SIZE + 10))
        if self.engine.state != 'ongoing':
            end_text = f"Game Over: {self.engine.state.replace('_', ' ').title()}"
            surf2 = self.font.render(end_text, True, COLOR_TEXT)
            self.screen.blit(surf2, (10, GRID_HEIGHT * TILE_SIZE + 35))

    def handle_events(self):
        # Returns (action, direction) or None
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'quit', None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return 'quit', None
                if event.key == pygame.K_UP:
                    return 'move', (0, -1)
                if event.key == pygame.K_DOWN:
                    return 'move', (0, 1)
                if event.key == pygame.K_LEFT:
                    return 'move', (-1, 0)
                if event.key == pygame.K_RIGHT:
                    return 'move', (1, 0)
                if event.key == pygame.K_SPACE:
                    return 'fight', None
                if event.key == pygame.K_l:
                    return 'loot', None
                if event.key == pygame.K_h:
                    return 'heal', None
        return None, None
