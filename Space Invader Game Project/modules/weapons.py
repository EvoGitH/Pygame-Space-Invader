import pygame
from modules.assets import Assets

class Weapons:
    """ Mechanics and the
     visuals of game weapons """

    def __init__(self, player, enemy, info):
        self.player = player
        self.enemy = enemy
        self.info = info

        self.last_shot_time = 0
        self.bullet_speed = 500
        self.bullet_cooldown = 200

    def weapon_mechanic(self):

        if self.player.triple_shot_unlocked:
        # Fire 3 bullets: center, left, right
            Assets.triple_sound.set_volume(0.5)
            Assets.triple_sound.play() # Audio file

            bullet1 = pygame.Rect(self.player.player_box.centerx - 2, self.player.player_box.top - 10, 4, 10)
            bullet2 = pygame.Rect(self.player.player_box.centerx - 17, self.player.player_box.top - 10, 4, 10)
            bullet3 = pygame.Rect(self.player.player_box.centerx + 13, self.player.player_box.top - 10, 4, 10)
            self.player.bullets.extend([bullet1, bullet2, bullet3])
        else:
        # Single bullet, basic beginner.
            Assets.starter_sound.set_volume(0.3)
            Assets.starter_sound.play()
            bullet = pygame.Rect(self.player.player_box.centerx - 2, self.player.player_box.top - 10, 4, 10)
            self.player.bullets.append(bullet)        

        if self.player.side_cannon_count >= 1:
            Assets.starter_sound.set_volume(0.2)
            Assets.starter_sound.play()
            left_bullet = pygame.Rect(self.player.player_box.centerx - 77, self.player.player_box.top - 10, 4, 10)
            self.player.bullets.append(left_bullet)

        if self.player.side_cannon_count >= 2:
            Assets.starter_sound.set_volume(0.2)
            Assets.starter_sound.play()
            right_bullet = pygame.Rect(self.player.player_box.centerx + 77, self.player.player_box.top - 10, 4, 10)
            self.player.bullets.append(right_bullet)

    def shooting_function(self):
        keys = pygame.key.get_pressed()
        now = pygame.time.get_ticks()

        if keys[pygame.K_SPACE] and (now - self.last_shot_time) >= self.bullet_cooldown:
            self.last_shot_time = now
            self.weapon_mechanic()

    def update_bullets(self, screen):
        for bullet in self.player.bullets[:]:
            bullet.y -= self.bullet_speed * self.info.dt
            pygame.draw.rect(screen, (255, 255, 0), bullet)

            if bullet.bottom < 0:
                self.player.bullets.remove(bullet)
                continue

            for enemy in self.enemy.enemies[:]: 
                if bullet.colliderect(enemy.rect):
                    enemy.lives -= 1
                    if enemy.lives <= 0:
                        self.enemy.enemies.remove(enemy) 
                        self.player.points += enemy.points 
                        self.player.credits += enemy.credits  

                    if bullet in self.player.bullets:
                        self.player.bullets.remove(bullet)
                    break
