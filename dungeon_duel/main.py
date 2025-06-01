from .engine import GameEngine
from .ui import GameUI
import pygame
import sys

def main():
    engine = GameEngine()
    ui = GameUI(engine)
    clock = pygame.time.Clock()
    running = True
    while running:
        ui.draw()
        if engine.state != 'ongoing':
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    running = False
            continue
        if engine.turn == 'player':
            action, direction = ui.handle_events()
            if action == 'quit':
                running = False
            elif action:
                engine.player_action(action, direction)
        else:
            pygame.time.wait(400)
            engine.monster_action()
        clock.tick(30)
    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
