from .config import *

def attack(attacker, defender):
    defender.take_damage(HIT_DAMAGE)
    return HIT_DAMAGE

def resolve_combat(player, monster):
    # Simple turn-based: player attacks first
    if player.alive and monster.alive:
        attack(player, monster)
    if monster.alive:
        attack(monster, player)

    if not player.alive:
        return 'monster_win'
    elif not monster.alive:
        return 'player_win'
    return 'ongoing'
