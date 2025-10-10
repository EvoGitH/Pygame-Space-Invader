import pygame, sys, random
from settings import Info

screen = pygame.display.set_mode((1920, 1080))
info = Info(screen)

from movement import Movement
from assets import Assets 
from enemy import EnemyManager
from player import Player
from shop import Shop
from inputs import Inputs
from weapons import Weapons
from animation import Animations
from asset_animated import animation_images as Assnimated # lol

pygame.display.set_caption("Alien Invaders")
pygame.display.set_icon(Assets.game_icon)
Assnimated()
pygame.init()
pygame.mixer.init()

class Exiting:
    def quit_game():
        pygame.quit()
        sys.exit()

player = Player(info)
enemy = EnemyManager(player, info)
enemy.spawn_enemies(rows=3, columns=8)
weapon = Weapons(player, enemy, info)
animated = Animations(player, info)
move = Movement(enemy, player, info)
shop = Shop(player, info)
inputs = Inputs(player, shop, enemy, info)

while True:
    info.update_time()
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            Exiting.quit_game()
        if shop.active:
            shop.handle_event(event)
        inputs.keyboard_inputs([event])


    screen.fill((0, 0, 0))

    if info.game_state == "Paused":
        info.pause_screen("Q to Quit, S to Shop or C to Continue (Paused)")
        shop.draw(screen)

    elif info.game_state == "WaveCleared":
        info.pause_screen("Q to Quit, S to Shop or C to Continue (Wave Cleared)")
        shop.draw(screen)

    elif info.game_state == "Playing":
        player.player_movement()
        player.update_position()
        player.draw_player(screen)
        animated.side_cannon(screen)

        enemy.update_and_draw(screen, info.dt)
        move.collision_check()
        move.coin_collision()

        weapon.shooting_function()
        weapon.update_bullets(screen)

        if len(enemy.enemies) == 0:
            info.game_state = "WaveCleared"

    for event in events:
        if event.type == pygame.USEREVENT + 1:
            if info.game_state == "Playing":
                for collectible in player.collectibles:
                    if collectible.collected:
                        collectible.rect.topleft = (
                            random.randint(50, Info.screenX - 50),
                            random.randint(Info.screenY // 2, Info.screenY - 50)
                        )
                        collectible.collected = False

    animated.heart_animation(screen)
    animated.floating_collectibles(screen)

    if info.game_state == "Playing":
        animated.draw_shields(screen)

    animated.screen_text(screen)

    if shop.active:
        shop.draw(screen)

    pygame.display.flip()