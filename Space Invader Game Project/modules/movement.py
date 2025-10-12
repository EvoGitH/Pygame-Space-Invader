import pygame, sys
from modules.assets import Assets

class Exiting:
    def quit_game():
        pygame.quit()
        sys.exit()


class Movement:
    """ Contains collision checks between
    enemies and player, but also updates to
    player character, dash/short-teleports, etc."""

    def __init__(self, enemy, player, info):
        self.player = player
        self.enemy = enemy
        self.info = info

    def collision_check(self):
        for alien in self.enemy.enemies[:]:
            if self.player.player_box.colliderect(alien.rect):
                if self.player.shield > 0:
                    self.player.shield -= 1
                    self.info.show_message("Shield absorbed the hit!", duration=100)
                    if self.player.shield == 0:
                        Assets.shield_failed_sound.set_volume(0.1)
                        Assets.shield_failed_sound.play()
                else:
                    self.player.player_lives -= 1
                    self.info.show_message("Ouch! Lost a Life", duration=100)

                if alien in self.enemy.enemies:
                    self.enemy.enemies.remove(alien)
                    
                if self.player.player_lives == 0:
                    Exiting.quit_game()
        
        for enemy in self.enemy.enemies:
            for bullet in enemy.bullets[:]:
                if self.player.player_box.colliderect(bullet):
                    if self.player.shield > 0:
                        self.player.shield -= 1
                        self.info.show_message("Shield absorbed the hit!", duration=100)
                        Assets.shield_failed_sound.set_volume(0.1)
                        Assets.shield_failed_sound.play()
                    else:
                        self.player.player_lives -= 1
                        self.info.show_message("Ouch! Lost a Life", duration=100)
                    enemy.bullets.remove(bullet)

                    if self.player.player_lives == 0:
                        Exiting.quit_game()


    def coin_collision(self):
        for collectible in self.player.collectibles:
            if collectible.collected:
                continue

            if self.player.player_box.colliderect(collectible.rect):
                collectible.collected = True

                if collectible.name == "shield_coin":
                    self.player.shield = min(self.player.shield + 1, self.player.shield_max)
                    Assets.shield_sound.set_volume(0.3)
                    Assets.shield_sound.play()

                elif collectible.name == "health_coin":
                    self.player.player_lives = min(self.player.player_lives + 1, 4)

                pygame.time.set_timer(pygame.USEREVENT + 1, 5000, loops=1)