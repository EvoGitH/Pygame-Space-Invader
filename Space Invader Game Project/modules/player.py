import pygame
import random
from modules.assets import Assets
from modules.asset_animated import animation_images as Assnimated
from modules.collectibles import Collectible

class Player:
    """ Will hold instanced 
    information for the Player"""

    def __init__(self, info):
        self.speed = 4
        self.player_lives = 3
        self.credits = 0
        self.inventory = []
        self.bullets = []
        self.points = 0
        self.info = info

        self.playerX = self.info.screenX / 2
        self.playerY = self.info.screenY - self.info.iconY - 10
        self.player_box = pygame.Rect(self.playerX, self.playerY, self.info.iconX, self.info.iconY)
        
        self.triple_shot_unlocked = False
        self.side_cannon_count = 0 
        self.side_cannon_max = 2
        self.shield = 0
        self.shield_max = 3

        self.shield_coin_rect = Assnimated.shield_coin_image[0].get_rect(
            topleft=(random.randint(50, info.screenX - 50), 
                     random.randint(info.screenY // 2, self.info.screenY - 50))
                     )
        
        self.health_coin_rect = Assnimated.health_coin_image[0].get_rect(
            topleft=(random.randint(50, self.info.screenX - 50), 
                     random.randint(info.screenY // 2, self.info.screenY - 50))
                     )
        
        # Dict for coin collect, modular
        self.collectibles = [
            Collectible(
                self.info,
                "shield_coin",
                Assnimated.shield_coin_image,
                Assnimated.shield_coin_image[0].get_rect(
                    topleft=(
                        random.randint(50, self.info.screenX - 50),
                        random.randint(self.info.screenY // 2, self.info.screenY - 50)
                    )
                ),
                speed=250,
                amplitude=5
            ),
            Collectible(
                self.info,
                "health_coin",
                Assnimated.health_coin_image,
                Assnimated.health_coin_image[0].get_rect(
                    topleft=(
                        random.randint(50, self.info.screenX - 50),
                        random.randint(self.info.screenY // 2, self.info.screenY - 50)
                    )
                ),
                speed=250,
                amplitude=5
            )
        ]

    def player_movement(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.playerX -= self.speed * self.info.dt * 60
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.playerX += self.speed * self.info.dt * 60
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.playerY -= self.speed * self.info.dt * 60
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.playerY += self.speed * self.info.dt * 60 
        if keys[pygame.K_l]:
            self.credits += 5000

    def update_position(self):
        self.playerX = max(0, min(self.playerX, self.info.screenX - self.info.iconX))
        self.playerY = max(350, min(self.playerY, self.info.screenY - self.info.iconY))
        self.player_box.topleft = (self.playerX, self.playerY)

    def draw_player(self, screen):
        screen.blit(Assets.player_image, self.player_box)     