import pygame, random, math
from modules.assets import Assets

class BaseEnemy:
    """Base class for all enemies. 
    New enemy types inherit from this."""

    def __init__(self, player, info, level):
        self.image = Assets.enemy_image_basic
        self.lives = 1
        self.speed = 3 + level * 0.1
        self.player = player
        self.info = info
        self.rect = self.image.get_rect(topleft=(0, 0))
        self.independent = False
        self.x_speed = 0
        self.y_speed = 0
        self.just_spawned = True
        self.points = 100
        self.credits = 100
        self.direction = 1
        self.drop_amount = 60
        self.bullets = []
        self.shoot_cooldown = 1500
        self.last_shot_time = 0

    def spawn(self, x, y):
        self.rect.topleft = (x, y)

    def update(self, dt):
        """Default movement: 
        horizontal bouncing and edge drop."""

        if not self.independent:
            self.rect.x += self.speed * dt * 60 * self.direction
            if self.rect.left < 5:
                self.rect.left = 5
                self.direction *= -1
                self.rect.y += self.drop_amount
            elif self.rect.right > self.info.screenX - 5:
                self.rect.right = self.info.screenX - 5
                self.direction *= -1
                self.rect.y += self.drop_amount
                
            # Possibly become independent if reaches player
            if self.rect.top > self.player.playerY:
                self.independent = True
                self.x_speed = random.choice([-2, -1, 1, 2])
                self.y_speed = random.randint(1, 3)
        else:
            self.rect.x += self.x_speed
            self.rect.y += self.y_speed
            if self.rect.left < 0 or self.rect.right > self.info.screenX:
                self.x_speed *= -1
            if self.rect.bottom >= self.info.screenY:
                self.independent = False
                self.x_speed = 0
                self.y_speed = 0
                self.rect.y = 0

        if self.info.level >= 20:
            self.shoot()

        for bullet in self.bullets[:]:
            bullet.y += 5 * self.info.dt * 60  
            if bullet.top > self.info.screenY:
                self.bullets.remove(bullet)

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot_time >= self.shoot_cooldown:
            self.last_shot_time = now
            bullet = pygame.Rect(
                self.rect.centerx - 3,
                self.rect.bottom, 6, 10
                )
            
            self.bullets.append(bullet)

    def draw(self, screen):
        screen.blit(self.image, self.rect)

class TankEnemy(BaseEnemy):
    """Slow but tough enemy."""

    def __init__(self, player, info, level):
        super().__init__(player, info, level)
        self.image = Assets.enemy_image_tank
        self.lives = 4
        self.speed = 2 
        self.points = 300
        self.credits = 250

class ZigzagEnemy(BaseEnemy):
    """Enemy with sine-wave horizontal movement."""

    def __init__(self, player, info, level):
        super().__init__(player, info, level)
        self.image = Assets.enemy_image_zigzag
        self.lives = 2
        self.speed = 4 + level * 0.2
        self.points = 200
        self.credits = 150
        self.start_x = 0
        self.amplitude = 100
        self.frequency = 2
        self.time = 0

    def spawn(self, x, y):
        super().spawn(x, y)
        self.start_x = x

    def update(self, dt):
        self.time += dt
        self.rect.y += self.speed * dt * 60
        self.rect.x = self.start_x + math.sin(self.time * self.frequency) * self.amplitude
        # Respawn at top if offscreen
        if self.rect.top > self.info.screenY:
            self.rect.y = -self.rect.height
            self.start_x = random.randint(50, self.info.screenX - 50)

class EnemyManager:
    """Handles all enemies, spawning by level, modular system."""
    def __init__(self, player, info):
        self.player = player
        self.info = info
        self.enemies = []
        self.level_enemy_map = {
            1: [BaseEnemy],       
            5: [TankEnemy],       
            10: [ZigzagEnemy],  
        }
        self.enemy_speed = 5
        self.direction = 1
        self.drop_amount = 60

    def get_available_enemy_types(self):
        """Return list of enemy classes based on current level."""

        types = []
        for lvl in sorted(self.level_enemy_map.keys()):
            if self.info.level >= lvl:
                types.extend(self.level_enemy_map[lvl])
        return types

    def spawn_enemies(self, rows=3, columns=8):
        """Spawn a grid of enemies with modular types."""

        self.enemies.clear()
        available_types = self.get_available_enemy_types()

        enemy_width = Assets.enemy_image_basic.get_width()
        enemy_height = Assets.enemy_image_basic.get_height()
        total_width = columns * enemy_width + (columns - 1) * 20
        start_x = (self.info.screenX - total_width) // 2
        start_y = 50

        for row in range(rows):
            for col in range(columns):
                EnemyClass = random.choice(available_types)
                enemy = EnemyClass(self.player, self.info, self.info.level)

                if enemy.lives <= 0:
                    continue

                x = start_x + col * (enemy_width + 20)
                y = start_y + row * (enemy_height + 20)
                enemy.spawn(x, y)
                self.enemies.append(enemy)

    def update_and_draw(self, screen, dt):

        for enemy in self.enemies[:]:
            enemy.update(dt)
            enemy.draw(screen)
            for bullet in enemy.bullets[:]:
                pygame.draw.rect(screen, (255, 0, 0), bullet)