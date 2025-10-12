import pygame, sys

class Exiting:
    def quit_game():
        pygame.quit()
        sys.exit()

class Inputs:
    """Keyboard inputs will effect
    the event keys within this class"""

    def __init__(self, player, shop, enemy, info):
        self.player = player
        self.shop = shop
        self.enemy = enemy
        self.info = info

    def keyboard_inputs(self, events):
        for event in events:

            if event.type == pygame.QUIT:
                Exiting.quit_game()  

            elif event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:
                    if self.info.game_state == "Playing":
                        self.info.game_state = "Paused"
                    elif self.info.game_state == "Paused":
                        self.info.game_state = "Playing"
                    self.shop.active = False

                elif event.key == pygame.K_s and (self.info.game_state in ["Paused", "WaveCleared"]):
                    self.shop.active = True

                elif event.key == pygame.K_c and self.info.game_state in ["WaveCleared", "Paused"]:
                    if self.info.game_state == "WaveCleared":
                        self.info.level += 1
                        if self.info.level > 25:
                            self.enemy.spawn_enemies(rows=6, columns=10)
                        elif self.info.level > 20:
                            self.enemy.spawn_enemies(rows=5, columns=10)
                        elif self.info.level > 15:
                            self.enemy.spawn_enemies(rows=4, columns=9)
                        elif self.info.level > 10:
                            self.enemy.spawn_enemies(rows=3, columns=9)
                        elif self.info.level > 5:
                            self.enemy.spawn_enemies(rows=3, columns=8)
                        else:
                            self.enemy.spawn_enemies(rows=2, columns=6)
                    self.player.bullets.clear()

                    self.player.playerX = self.info.screenX / 2
                    self.player.playerY = self.info.screenY
                    self.player.update_position()
                    self.info.game_state = "Playing"

                elif event.key == pygame.K_q and self.info.game_state in ["Paused", "WaveCleared"]:
                    Exiting.quit_game()
                
                elif self.shop.active:
                    self.shop.buy_upgrade_by_key(event.key)