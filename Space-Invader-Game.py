
import pygame, random, math, sys

pygame.init()
pygame.mixer.init()

class Exiting:
    def quit_game():
        pygame.quit()
        sys.exit()

class Assets:
    """The 'Assets' class store and 
    loads the collective images, effects 
    and music for the game"""

    # Images
    game_icon = pygame.image.load('si_game_assets/images/ship.png')
    player_image = pygame.image.load('si_game_assets/images/ship.png')
    enemy_image_basic = pygame.image.load('si_game_assets/images/alien_basic.png')
    enemy_image_guardian = pygame.image.load('si_game_assets/images/alien_guardian.png')
    enemy_image_zigzag = pygame.image.load('si_game_assets/images/alien_zigzag.png')
    enemy_image_tank = pygame.image.load('si_game_assets/images/alien_tank.png')

    background_image = pygame.image.load('si_game_assets/images/shop_background.png')

    buy_button_image = pygame.image.load('si_game_assets/images/buy_button.png')
    close_button_image = pygame.image.load('si_game_assets/images/close_button.png')

    side_cannon_image = pygame.image.load('si_game_assets/images/side_cannon.png')

    # Audio effects
    starter_sound = pygame.mixer.Sound('si_game_assets/audio/starter_weapon.mp3')
    triple_sound = pygame.mixer.Sound('si_game_assets/audio/triple_power_up.wav')
    cannon_sound = pygame.mixer.Sound('si_game_assets/audio/cannon_shot.wav')
    gatling_sound = pygame.mixer.Sound('si_game_assets/audio/gatling_laser.wav')
    shield_sound = pygame.mixer.Sound('si_game_assets/audio/shield_energy.wav')
    shield_failed_sound = pygame.mixer.Sound('si_game_assets/audio/shield_failed.wav')

    # *Animated* images
    def animation_images():
        """Display required to be Initialized
        before these images can be converted"""

        Assets.hearts_image = [
            pygame.image.load('si_game_assets/animated_images/heart1.png').convert_alpha(), 
            pygame.image.load('si_game_assets/animated_images/heart2.png').convert_alpha()
            ]
        Assets.three_shot_image = [
            pygame.image.load('si_game_assets/animated_images/three_shot_power1.png').convert_alpha(), 
            pygame.image.load('si_game_assets/animated_images/three_shot_power2.png').convert_alpha()
            ]
        Assets.shield_coin_image = [
            pygame.image.load('si_game_assets/animated_images/shield_coin1.png').convert_alpha(),
            pygame.image.load('si_game_assets/animated_images/shield_coin2.png').convert_alpha()
            ]
        Assets.health_coin_image = [
            pygame.image.load('si_game_assets/animated_images/health_coin1.png').convert_alpha(),
            pygame.image.load('si_game_assets/animated_images/health_coin2.png').convert_alpha()
            ]
        
class Info:
    """ Will hold only basic
    information that is reuseable
    but mutable for the game here"""

    # Optimized for M4 MacBook Pro (14" or 16")
    screenX = 1440
    screenY = 900
    iconX = 64
    iconY = 64

    def __init__(self):
        self.clock = pygame.time.Clock()
        self.ticks = 0
        self.dt = 0
        self.game_state = "Playing"
        self.level = 19  # START AT LEVEL 19

        # Screen shake effect
        self.screen_shake_intensity = 0
        self.screen_shake_duration = 0
        self.screen_offset_x = 0
        self.screen_offset_y = 0

        # Background stars for parallax
        self.stars = []
        self.init_stars()
    
    def update_time(self):
        self.dt = self.clock.tick(60) / 1000
        self.ticks = pygame.time.get_ticks()

        # Update screen shake
        if self.screen_shake_duration > 0:
            self.screen_shake_duration -= self.dt
            self.screen_offset_x = random.randint(-int(self.screen_shake_intensity), int(self.screen_shake_intensity))
            self.screen_offset_y = random.randint(-int(self.screen_shake_intensity), int(self.screen_shake_intensity))
        else:
            self.screen_offset_x = 0
            self.screen_offset_y = 0
            self.screen_shake_intensity = 0

    def init_stars(self):
        """Initialize background stars for parallax effect"""
        for _ in range(200):
            star = {
                'x': random.randint(0, self.screenX),
                'y': random.randint(0, self.screenY),
                'speed': random.uniform(0.5, 3),
                'size': random.randint(1, 3),
                'brightness': random.randint(100, 255)
            }
            self.stars.append(star)

    def update_stars(self):
        """Update star positions for parallax scrolling"""
        for star in self.stars:
            star['y'] += star['speed']
            if star['y'] > self.screenY:
                star['y'] = 0
                star['x'] = random.randint(0, self.screenX)

    def draw_stars(self, screen):
        """Draw stars on background"""
        for star in self.stars:
            color = (star['brightness'], star['brightness'], star['brightness'])
            pygame.draw.circle(screen, color, (int(star['x']), int(star['y'])), star['size'])

    def trigger_screen_shake(self, intensity=10, duration=0.2):
        """Trigger screen shake effect"""
        self.screen_shake_intensity = intensity
        self.screen_shake_duration = duration

    def show_message(self, text, duration=1000):
        font = pygame.font.Font(None, 50)
        msg_surface = font.render(text, True, (255, 255, 255))
        msg_rect = msg_surface.get_rect(center=(Info.screenX//2, Info.screenY//2))
        screen.blit(msg_surface, msg_rect)
        pygame.display.flip()
        pygame.time.delay(duration)

    def pause_screen(self, message):
            font = pygame.font.Font(None, 50)
            overlay = pygame.Surface((Info.screenX, Info.screenY), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            text = font.render(message, True, (255, 255, 255))
            text_rect = text.get_rect(center=(self.screenX//2, self.screenY//2))
            screen.blit(text, text_rect)

class Player:
    """ Will hold instanced
    information for the Player"""

    def __init__(self):
        self.speed = 8  # MAX SPEED
        self.player_lives = 5  # Extra lives
        self.credits = 50000  # Lots of credits to start
        self.inventory = []
        self.bullets = []
        self.points = 0

        self.playerX = Info.screenX / 2
        self.playerY = Info.screenY - Info.iconY - 10
        self.player_box = pygame.Rect(self.playerX, self.playerY, Info.iconX, Info.iconY)

        self.triple_shot_unlocked = True  # START WITH TRIPLE SHOT
        self.side_cannon_count = 2  # START WITH BOTH SIDE CANNONS
        self.side_cannon_max = 2
        self.shield = 3  # START WITH FULL SHIELDS
        self.shield_max = 3

        # Enhanced ship features
        self.dash_cooldown = 0
        self.dash_duration = 0
        self.dash_speed = 15
        self.is_dashing = False
        self.dash_direction = [0, 0]

        # Visual effects
        self.engine_particles = []
        self.ship_rotation = 0
        self.target_rotation = 0

        # Advanced weapon systems
        self.weapon_level = 1
        self.weapon_heat = 0
        self.max_heat = 100
        self.overheated = False

        # Power-up timers
        self.rapid_fire_timer = 0
        self.damage_boost_timer = 0

        self.shield_coin_rect = Assets.shield_coin_image[0].get_rect(
            topleft=(random.randint(50, Info.screenX - 50), 
                     random.randint(Info.screenY // 2, Info.screenY - 50))
                     )
        
        self.health_coin_rect = Assets.health_coin_image[0].get_rect(
            topleft=(random.randint(50, Info.screenX - 50), 
                     random.randint(Info.screenY // 2, Info.screenY - 50))
                     )
        
        # Dict for coin collect, modular
        self.collectibles = [
            Collectible(
                "shield_coin",
                Assets.shield_coin_image,
                Assets.shield_coin_image[0].get_rect(
                    topleft=(
                        random.randint(50, Info.screenX - 50),
                        random.randint(Info.screenY // 2, Info.screenY - 50)
                    )
                ),
                speed=250,
                amplitude=5
            ),
            Collectible(
                "health_coin",
                Assets.health_coin_image,
                Assets.health_coin_image[0].get_rect(
                    topleft=(
                        random.randint(50, Info.screenX - 50),
                        random.randint(Info.screenY // 2, Info.screenY - 50)
                    )
                ),
                speed=250,
                amplitude=5
            )
        ]

    def player_movement(self):
        keys = pygame.key.get_pressed()

        # Dash cooldown management
        if self.dash_cooldown > 0:
            self.dash_cooldown -= info.dt

        # Execute dash
        if self.is_dashing:
            self.dash_duration -= info.dt
            if self.dash_duration <= 0:
                self.is_dashing = False
            else:
                self.playerX += self.dash_direction[0] * self.dash_speed * info.dt * 60
                self.playerY += self.dash_direction[1] * self.dash_speed * info.dt * 60
                # Create dash trail particles
                self.create_dash_particle()
                return

        # Initiate dash with SHIFT
        if keys[pygame.K_LSHIFT] and self.dash_cooldown <= 0:
            move_x = 0
            move_y = 0
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                move_x = -1
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                move_x = 1
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                move_y = -1
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                move_y = 1

            if move_x != 0 or move_y != 0:
                # Normalize diagonal movement
                length = math.sqrt(move_x**2 + move_y**2)
                self.dash_direction = [move_x/length, move_y/length]
                self.is_dashing = True
                self.dash_duration = 0.2  # 200ms dash
                self.dash_cooldown = 1.5  # 1.5s cooldown
                return

        # Normal movement with smooth acceleration
        move_speed = self.speed * info.dt * 60
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.playerX -= move_speed
            self.target_rotation = 15  # Tilt left
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.playerX += move_speed
            self.target_rotation = -15  # Tilt right
        else:
            self.target_rotation = 0  # Return to center

        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.playerY -= move_speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.playerY += move_speed

        # Smooth rotation
        self.ship_rotation += (self.target_rotation - self.ship_rotation) * 0.1

        # Create engine particles during movement
        if keys[pygame.K_UP] or keys[pygame.K_DOWN] or keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]:
            self.create_engine_particle()

        if keys[pygame.K_l]:
            self.credits += 5000

    def create_engine_particle(self):
        """Create particle effects from ship engines"""
        particle = {
            'x': self.playerX + Info.iconX / 2 + random.randint(-5, 5),
            'y': self.playerY + Info.iconY,
            'vel_y': random.uniform(2, 4),
            'vel_x': random.uniform(-0.5, 0.5),
            'lifetime': random.uniform(0.3, 0.6),
            'size': random.randint(2, 4),
            'color': random.choice([(255, 100, 0), (255, 150, 0), (255, 200, 0)])
        }
        self.engine_particles.append(particle)

    def create_dash_particle(self):
        """Create particle trail during dash"""
        for _ in range(3):
            particle = {
                'x': self.playerX + Info.iconX / 2 + random.randint(-10, 10),
                'y': self.playerY + Info.iconY / 2 + random.randint(-10, 10),
                'vel_y': random.uniform(-1, 1),
                'vel_x': random.uniform(-1, 1),
                'lifetime': random.uniform(0.2, 0.4),
                'size': random.randint(3, 6),
                'color': (0, 150, 255)
            }
            self.engine_particles.append(particle)

    def update_particles(self, dt):
        """Update and remove expired particles"""
        for particle in self.engine_particles[:]:
            particle['lifetime'] -= dt
            particle['y'] += particle['vel_y']
            particle['x'] += particle['vel_x']
            if particle['lifetime'] <= 0:
                self.engine_particles.remove(particle)

    def update_position(self):
        self.playerX = max(0, min(self.playerX, Info.screenX - Info.iconX))
        self.playerY = max(350, min(self.playerY, Info.screenY - Info.iconY))
        self.player_box.topleft = (self.playerX, self.playerY)

    def draw_player(self, screen):
        # Draw particles first (behind ship)
        for particle in self.engine_particles:
            alpha = int(255 * (particle['lifetime'] / 0.6))
            color = (*particle['color'], min(alpha, 255))
            s = pygame.Surface((particle['size']*2, particle['size']*2), pygame.SRCALPHA)
            pygame.draw.circle(s, color, (particle['size'], particle['size']), particle['size'])
            screen.blit(s, (particle['x'] - particle['size'], particle['y'] - particle['size']))

        # Draw ship with rotation
        if abs(self.ship_rotation) > 0.5:
            rotated_image = pygame.transform.rotate(Assets.player_image, self.ship_rotation)
            rotated_rect = rotated_image.get_rect(center=self.player_box.center)
            screen.blit(rotated_image, rotated_rect)
        else:
            screen.blit(Assets.player_image, self.player_box)

        # Draw dash cooldown indicator
        if self.dash_cooldown > 0:
            cooldown_percent = self.dash_cooldown / 1.5
            bar_width = Info.iconX
            bar_height = 4
            bar_x = self.playerX
            bar_y = self.playerY - 10
            pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
            pygame.draw.rect(screen, (0, 150, 255), (bar_x, bar_y, bar_width * (1 - cooldown_percent), bar_height))        

class Button:
    def __init__(self, x, y, width=172, height=71, text="Button", color=(0, 0 ,0), hover_color=(255, 255, 255), action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.action = action
        self.font = pygame.font.Font(None, 30) 

    def draw(self, screen):

        current_color = self.hover_color if self.rect.collidepoint(pygame.mouse.get_pos()) else self.color
        pygame.draw.rect(screen, current_color, self.rect)

        text_surface = self.font.render(self.text, True, (255, 255, 255)) 
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: 
            if self.rect.collidepoint(event.pos):
                if self.action:
                    self.action()

class Upgrades:
    """ Will contain the player
    shop inventory, and be updatable
    as needed. 

    Visit "class Shop" to update key_map, buttons, etc.

    Example: *setattr(class/"object", variable/"attribute name", effect/"value")*
    """

    upgrades = {
    "Speed": {
        "cost": 500,
        "effect": lambda player: setattr(player, "speed", player.speed + 1),
        "times_purchased": 0,
        "max_purchases": 5    
    },
    "Triple Shot": {
        "cost": 800,
        "effect": lambda player: setattr(player, "triple_shot_unlocked", True),
        "times_purchased": 0,
        "max_purchases": 1
    },
    "Side Cannon": {
        "cost": 1000,
        "effect": lambda player: setattr(player, "side_cannon_count", min(player.side_cannon_count + 1, player.side_cannon_max)),
        "times_purchased": 0,
        "max_purchases": 2
    },
}

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

        if self.info.level >= 30:
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
                self.rect.bottom,
                6,
                10
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
        self.speed = 4 + level * 0.1
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
            1: [BaseEnemy],        # Level 1-9
            10: [TankEnemy],       # Level 10-14
            15: [ZigzagEnemy],     # Level 15+
            # Future levels can add more types
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

class Bullet:
    """Custom bullet class to hold type and rect"""
    def __init__(self, x, y, width, height, bullet_type='normal'):
        self.rect = pygame.Rect(x, y, width, height)
        self.bullet_type = bullet_type
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.bottom = y + height
        self.top = y

        # Trail system for laser effects
        self.trail = []
        self.max_trail_length = 8

    def colliderect(self, other):
        return self.rect.colliderect(other)

    def update_position(self):
        self.rect.y = self.y
        self.top = self.y
        self.bottom = self.y + self.height

        # Add current position to trail
        self.trail.append({'x': self.x + self.width/2, 'y': self.y, 'age': 0})

        # Update trail age and remove old ones
        for t in self.trail[:]:
            t['age'] += 1
            if t['age'] > self.max_trail_length:
                self.trail.remove(t)

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

        # Bullet types and properties
        self.bullet_types = {
            'normal': {'damage': 1, 'color': (255, 255, 0), 'size': (4, 10)},
            'power': {'damage': 2, 'color': (255, 100, 0), 'size': (6, 12)},
            'laser': {'damage': 1, 'color': (0, 255, 255), 'size': (3, 15)},
            'plasma': {'damage': 3, 'color': (255, 0, 255), 'size': (8, 8)}
        }

        # Muzzle flash effects
        self.muzzle_flashes = []

    def weapon_mechanic(self):
        # Add weapon heat
        if not self.player.overheated:
            self.player.weapon_heat = min(self.player.max_heat, self.player.weapon_heat + 5)
            if self.player.weapon_heat >= self.player.max_heat:
                self.player.overheated = True

        bullet_type = 'power' if self.player.damage_boost_timer > 0 else 'normal'

        if self.player.triple_shot_unlocked:
        # Fire 3 bullets: center, left, right
            Assets.triple_sound.set_volume(0.5)
            Assets.triple_sound.play() # Audio file

            bullet1 = Bullet(self.player.player_box.centerx - 2, self.player.player_box.top - 10, 4, 10, bullet_type)
            bullet2 = Bullet(self.player.player_box.centerx - 17, self.player.player_box.top - 10, 4, 10, bullet_type)
            bullet3 = Bullet(self.player.player_box.centerx + 13, self.player.player_box.top - 10, 4, 10, bullet_type)
            self.player.bullets.extend([bullet1, bullet2, bullet3])
            self.create_muzzle_flash(self.player.player_box.centerx, self.player.player_box.top)
        else:
        # Single bullet, basic beginner.
            Assets.starter_sound.set_volume(0.3)
            Assets.starter_sound.play()
            bullet = Bullet(self.player.player_box.centerx - 2, self.player.player_box.top - 10, 4, 10, bullet_type)
            self.player.bullets.append(bullet)
            self.create_muzzle_flash(self.player.player_box.centerx, self.player.player_box.top)

        if self.player.side_cannon_count >= 1:
            Assets.starter_sound.set_volume(0.2)
            Assets.starter_sound.play()
            left_bullet = Bullet(self.player.player_box.centerx - 77, self.player.player_box.top - 10, 4, 10, 'laser')
            self.player.bullets.append(left_bullet)
            self.create_muzzle_flash(self.player.player_box.centerx - 77, self.player.player_box.top)

        if self.player.side_cannon_count >= 2:
            Assets.starter_sound.set_volume(0.2)
            Assets.starter_sound.play()
            right_bullet = Bullet(self.player.player_box.centerx + 77, self.player.player_box.top - 10, 4, 10, 'laser')
            self.player.bullets.append(right_bullet)
            self.create_muzzle_flash(self.player.player_box.centerx + 77, self.player.player_box.top)

    def create_muzzle_flash(self, x, y):
        """Create visual muzzle flash effect"""
        flash = {
            'x': x,
            'y': y,
            'lifetime': 0.05,
            'size': random.randint(10, 15)
        }
        self.muzzle_flashes.append(flash)

    def shooting_function(self):
        keys = pygame.key.get_pressed()
        now = pygame.time.get_ticks()

        # Weapon heat cooldown
        if self.player.weapon_heat > 0:
            self.player.weapon_heat = max(0, self.player.weapon_heat - 0.5)
        if self.player.overheated and self.player.weapon_heat <= 0:
            self.player.overheated = False

        # Rapid fire mode reduces cooldown
        active_cooldown = self.bullet_cooldown
        if self.player.rapid_fire_timer > 0:
            active_cooldown = self.bullet_cooldown // 2

        if keys[pygame.K_SPACE] and (now - self.last_shot_time) >= active_cooldown and not self.player.overheated:
            self.last_shot_time = now
            self.weapon_mechanic()

    def update_bullets(self, screen):
        # Update and draw muzzle flashes
        for flash in self.muzzle_flashes[:]:
            flash['lifetime'] -= self.info.dt
            if flash['lifetime'] <= 0:
                self.muzzle_flashes.remove(flash)
            else:
                alpha = int(255 * (flash['lifetime'] / 0.05))
                s = pygame.Surface((flash['size']*2, flash['size']*2), pygame.SRCALPHA)
                pygame.draw.circle(s, (255, 255, 150, alpha), (flash['size'], flash['size']), flash['size'])
                screen.blit(s, (flash['x'] - flash['size'], flash['y'] - flash['size']))

        for bullet in self.player.bullets[:]:
            bullet.y -= self.bullet_speed * self.info.dt
            bullet.update_position()

            # Get bullet properties
            bullet_type = getattr(bullet, 'bullet_type', 'normal')
            bullet_props = self.bullet_types.get(bullet_type, self.bullet_types['normal'])
            color = bullet_props['color']

            # Draw laser trail with fading effect
            for i, trail_pos in enumerate(bullet.trail):
                trail_alpha = int(255 * (1 - trail_pos['age'] / bullet.max_trail_length))
                trail_size = max(1, int(bullet.width * (1 - trail_pos['age'] / bullet.max_trail_length)))

                # Draw trail glow
                glow_size = trail_size + 4
                glow_surf = pygame.Surface((glow_size*2, glow_size*2), pygame.SRCALPHA)
                glow_alpha = int(trail_alpha * 0.5)
                pygame.draw.circle(glow_surf, (*color, glow_alpha), (glow_size, glow_size), glow_size)
                screen.blit(glow_surf, (trail_pos['x'] - glow_size, trail_pos['y'] - glow_size))

                # Draw trail core
                trail_surf = pygame.Surface((trail_size*2, trail_size*2), pygame.SRCALPHA)
                pygame.draw.circle(trail_surf, (*color, trail_alpha), (trail_size, trail_size), trail_size)
                screen.blit(trail_surf, (trail_pos['x'] - trail_size, trail_pos['y'] - trail_size))

            # Draw main bullet with multiple glow layers for bloom effect
            # Outer glow (largest, most transparent)
            for glow_layer in range(3, 0, -1):
                glow_size = glow_layer * 8
                glow_alpha = int(80 / glow_layer)
                glow_surface = pygame.Surface((bullet.width + glow_size*2, bullet.height + glow_size*2), pygame.SRCALPHA)
                glow_rect = pygame.Rect(glow_size, glow_size, bullet.width, bullet.height)
                pygame.draw.rect(glow_surface, (*color, glow_alpha), glow_rect, border_radius=2)
                screen.blit(glow_surface, (bullet.x - glow_size, bullet.y - glow_size))

            # Draw bullet core (brightest)
            pygame.draw.rect(screen, (255, 255, 255), bullet.rect)
            # Draw colored overlay
            color_surf = pygame.Surface((bullet.width, bullet.height), pygame.SRCALPHA)
            pygame.draw.rect(color_surf, (*color, 200), (0, 0, bullet.width, bullet.height))
            screen.blit(color_surf, (bullet.x, bullet.y))

            if bullet.bottom < 0:
                self.player.bullets.remove(bullet)
                continue

            for enemy in self.enemy.enemies[:]:
                if bullet.colliderect(enemy.rect):
                    damage = bullet_props['damage']
                    enemy.lives -= damage

                    # Trigger screen shake on hit
                    self.info.trigger_screen_shake(3, 0.1)

                    # Create hit effect
                    self.create_hit_effect(enemy.rect.centerx, enemy.rect.centery)

                    if enemy.lives <= 0:
                        # Bigger screen shake on enemy death
                        self.info.trigger_screen_shake(8, 0.3)
                        self.create_explosion_effect(enemy.rect.centerx, enemy.rect.centery)
                        self.enemy.enemies.remove(enemy)
                        self.player.points += enemy.points
                        self.player.credits += enemy.credits

                    if bullet in self.player.bullets:
                        self.player.bullets.remove(bullet)
                    break

    def create_hit_effect(self, x, y):
        """Create small hit spark effect with electric sparks"""
        for _ in range(12):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 6)
            particle = {
                'x': x,
                'y': y,
                'vel_x': math.cos(angle) * speed,
                'vel_y': math.sin(angle) * speed,
                'lifetime': random.uniform(0.15, 0.35),
                'size': random.randint(2, 5),
                'color': random.choice([(255, 255, 100), (255, 220, 0), (255, 255, 255)])
            }
            self.player.engine_particles.append(particle)

    def create_explosion_effect(self, x, y):
        """Create spectacular explosion effect when enemy dies"""
        # Main explosion particles
        for _ in range(30):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(3, 10)
            particle = {
                'x': x,
                'y': y,
                'vel_x': math.cos(angle) * speed,
                'vel_y': math.sin(angle) * speed,
                'lifetime': random.uniform(0.4, 1.0),
                'size': random.randint(4, 8),
                'color': random.choice([(255, 100, 0), (255, 150, 0), (255, 200, 0), (255, 50, 0)])
            }
            self.player.engine_particles.append(particle)

        # Secondary sparks
        for _ in range(20):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(5, 12)
            particle = {
                'x': x,
                'y': y,
                'vel_x': math.cos(angle) * speed,
                'vel_y': math.sin(angle) * speed,
                'lifetime': random.uniform(0.2, 0.5),
                'size': random.randint(2, 4),
                'color': random.choice([(255, 255, 100), (255, 255, 200), (255, 200, 100)])
            }
            self.player.engine_particles.append(particle)

        # Smoke particles
        for _ in range(15):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 4)
            particle = {
                'x': x,
                'y': y,
                'vel_x': math.cos(angle) * speed,
                'vel_y': math.sin(angle) * speed - 2,  # Rise upward
                'lifetime': random.uniform(0.6, 1.2),
                'size': random.randint(6, 12),
                'color': random.choice([(100, 100, 100), (80, 80, 80), (120, 120, 120)])
            }
            self.player.engine_particles.append(particle)

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
  
class Shop:
    """Player Shop
    functions defined are
    Shop background, and
    Shop's buying function
    
    Update the key_map to add
    new upgrades to shop."""

    def __init__(self, player, info):
        self.player = player
        self.info = info
        self.active = False
        self.key_map = {
            pygame.K_1: "Speed",
            pygame.K_2: "Triple Shot",
            pygame.K_3: "Side Cannon"
        }
        
        self.buttons = []
        y_offset = 200
        for key, upgrade_name in self.key_map.items():
                upgrade_info = Upgrades.upgrades[upgrade_name]
                button_text = f"[{pygame.key.name(key).upper()}] {upgrade_name} ({upgrade_info['cost']}, Max: {upgrade_info['max_purchases']})"
                self.buttons.append(
                    Button(
                        x=Info.screenX // 2 - 150,
                        y=y_offset,
                        width=400,
                        height=71,
                        text=button_text,
                        color=(0,128,255),
                        hover_color=(0,200,255),
                        action=lambda n=upgrade_name: self.buy_upgrade_by_name(n)
                    )
                )
                y_offset += 90

        self.back_button = Button(
            x=20,
            y=40,
            width=100,
            height=50,
            text="BACK",
            color=(255,0,0),
            hover_color=(255,100,100),
            action=self.close_shop 
        )

    def buy_upgrade_by_name(self, upgrade_name):
        upgrade = Upgrades.upgrades[upgrade_name]

        if upgrade["times_purchased"] >= upgrade["max_purchases"]:
            self.info.show_message(f"{upgrade_name} already maxed out!", duration=1000)
            return

        if self.player.credits >= upgrade["cost"]:
            self.player.credits -= upgrade["cost"]

            upgrade["effect"](self.player)
            upgrade["times_purchased"] += 1

            remaining = upgrade["max_purchases"] - upgrade["times_purchased"]
            if remaining > 0:
                self.info.show_message(
                    f"{upgrade_name} purchased! ({remaining} remaining). Credits: {self.player.credits}",
                    duration=1000
                )
            else:
                self.info.show_message(f"{upgrade_name} fully upgraded!", duration=1000)
        else:
            self.info.show_message("Not enough credits!", duration=1000)
        
    def buy_upgrade_by_key(self, key):
        if key in self.key_map:
            upgrade_name = self.key_map[key]
            self.buy_upgrade_by_name(upgrade_name)
    
    def draw(self, screen):
        if not self.active:
            return
        screen.blit(Assets.background_image, (0, 0))

        for button in self.buttons:
            button.draw(screen)

        self.back_button.draw(screen)
        font = pygame.font.Font(None, 40)
        money_text = font.render(f"CREDITS: {self.player.credits}", True, (255, 255, 255))
        screen.blit(money_text, (15, 120))
        info_text = font.render("ESC to Resume", True, (255, 255, 255))
        screen.blit(info_text, (15, 500))

    def handle_event(self, event):
        if not self.active:
            return
        for button in self.buttons:
            button.handle_event(event)
            
        self.back_button.handle_event(event)

        if event.type == pygame.KEYDOWN:
            if event.key not in self.key_map:
                self.buy_upgrade_by_key(event.key)
            if event.key == pygame.K_ESCAPE:
                self.active = False

    def close_shop(self):
        self.active = False

class Collectible:
    """Handles individual collectible animation and drawing."""

    def __init__(self, name, images, rect, speed=150, amplitude=5):
        self.name = name
        self.images = images
        self.rect = rect
        self.collected = False
        self.frame = 0
        self.timer = 0
        self.speed = speed
        self.amplitude = amplitude
        self.respawn_timer = 0

    def update(self, dt):
        """Updates animation and respawn timers."""

        if self.collected:
            self.respawn_timer += dt * 1000
            if self.respawn_timer >= 5000:
                self.rect.topleft = (
                    random.randint(50, Info.screenX - 50),
                    random.randint(Info.screenY // 2, Info.screenY - 50)
                )
                self.collected = False
                self.respawn_timer = 0
        else:
            self.timer += dt * 1000
            if self.timer >= self.speed:
                self.timer = 0
                self.frame = (self.frame + 1) % len(self.images)

    def draw(self, screen):
        """Draw the collectible on screen with floating effect."""

        if self.collected:
            return
        float_offset = math.sin(pygame.time.get_ticks() * 0.005) * self.amplitude
        draw_rect = self.images[self.frame].get_rect(center=self.rect.center)
        draw_rect.y += float_offset
        screen.blit(self.images[self.frame], draw_rect)

class Animations:
    """Will contain basic code for
    flipping 2 images back and forth
    to simulate animation, and also
    static information on screen"""

    def __init__(self, player, info):
        self.player = player
        self.info = info
        self.heart_animation_timer = 0
        self.heart_animation_speed = 150
        self.heart_frame = 0

    def heart_animation(self, screen):
        self.heart_animation_timer += self.info.dt * 1000
        if self.heart_animation_timer >= self.heart_animation_speed:
            self.heart_animation_timer = 0
            self.heart_frame = (self.heart_frame + 1) % len(Assets.hearts_image)
        for i in range(self.player.player_lives):
            screen.blit(Assets.hearts_image[self.heart_frame], (10 + i * 40, 40))

    def side_cannon(self, screen):
        if self.player.side_cannon_count >= 1:
            screen.blit(
                Assets.side_cannon_image,
                (self.player.player_box.centerx - 93, self.player.player_box.top - 10)
            )
        if self.player.side_cannon_count >= 2:
            screen.blit(
                Assets.side_cannon_image,
                (self.player.player_box.centerx + 70, self.player.player_box.top - 10)
            )

    def draw_shields(self, screen):
        """Draws 1-3 visual blue rings 
        around player depending 
        on shield tokens collect, will last
        15 seconds before expiring."""

        for i in range(self.player.shield):
            radius = max(self.info.iconX, self.info.iconY) + (i * 10)  # each ring slightly bigger
            shield_surface = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
            pygame.draw.circle(shield_surface, (0, 0, 255, 100), (radius, radius), radius, 4)  # 4px thick ring
            screen.blit(shield_surface, (self.player.playerX - radius + self.info.iconX/2, self.player.playerY - radius + self.info.iconY/2))

    def floating_collectibles(self, screen):
        for collectible in self.player.collectibles:
            collectible.update(self.info.dt)
            collectible.draw(screen)

    def screen_text(self, screen):
        font = pygame.font.Font(None, 35)
        small_font = pygame.font.Font(None, 25)

        points_text = font.render(f"Score: {self.player.points}", True, (255, 255, 255))
        points_rect = points_text.get_rect()
        points_rect.topleft = (35, 10)
        screen.blit(points_text, points_rect)

        level_text = font.render(f"Level: {self.info.level}", True, (255, 255, 255))
        level_rect = level_text.get_rect()
        level_rect.topright = (self.info.screenX - 35, 10)
        screen.blit(level_text, level_rect)

        # Weapon heat indicator
        heat_bar_width = 200
        heat_bar_height = 20
        heat_bar_x = self.info.screenX / 2 - heat_bar_width / 2
        heat_bar_y = 10

        # Background
        pygame.draw.rect(screen, (50, 50, 50), (heat_bar_x, heat_bar_y, heat_bar_width, heat_bar_height))

        # Heat bar
        heat_percent = self.player.weapon_heat / self.player.max_heat
        heat_width = heat_bar_width * heat_percent

        if self.player.overheated:
            heat_color = (255, 0, 0)
            overheat_text = small_font.render("OVERHEATED!", True, (255, 0, 0))
            screen.blit(overheat_text, (heat_bar_x + heat_bar_width / 2 - 60, heat_bar_y - 25))
        elif heat_percent > 0.7:
            heat_color = (255, 165, 0)
        else:
            heat_color = (0, 255, 0)

        pygame.draw.rect(screen, heat_color, (heat_bar_x, heat_bar_y, heat_width, heat_bar_height))
        pygame.draw.rect(screen, (255, 255, 255), (heat_bar_x, heat_bar_y, heat_bar_width, heat_bar_height), 2)

        heat_text = small_font.render("WEAPON HEAT", True, (255, 255, 255))
        screen.blit(heat_text, (heat_bar_x, heat_bar_y + heat_bar_height + 5))

        # Dash cooldown indicator (bottom right)
        if self.player.dash_cooldown > 0:
            dash_text = small_font.render(f"Dash: {self.player.dash_cooldown:.1f}s", True, (100, 150, 255))
            screen.blit(dash_text, (self.info.screenX - 150, self.info.screenY - 50))
        else:
            dash_text = small_font.render("Dash: READY [SHIFT]", True, (0, 255, 100))
            screen.blit(dash_text, (self.info.screenX - 200, self.info.screenY - 50))

class Inputs:
    """Keyboard inputs will effect
    the event keys within this class"""

    def __init__(self, player, shop, info, enemy):
        self.player = player
        self.shop = shop
        self.info = info
        self.enemy = enemy

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

                elif event.key == pygame.K_s and (info.game_state in ["Paused", "WaveCleared"]):
                    self.shop.active = True

                elif event.key == pygame.K_c and self.info.game_state in ["WaveCleared", "Paused"]:
                    if self.info.game_state == "WaveCleared":
                        self.info.level += 1
                        if self.info.level > 25:
                            self.enemy.spawn_enemies(rows=5, columns=10)
                        elif self.info.level > 20:
                            self.enemy.spawn_enemies(rows=4, columns=9)
                        else:
                            self.enemy.spawn_enemies(rows=3, columns=8)
                    self.player.bullets.clear()

                    self.player.playerX = Info.screenX / 2
                    self.player.playerY = Info.screenY
                    self.player.update_position()
                    self.info.game_state = "Playing"

                elif event.key == pygame.K_q and self.info.game_state in ["Paused", "WaveCleared"]:
                    Exiting.quit_game()
                
                elif self.shop.active:
                    self.shop.buy_upgrade_by_key(event.key)

screen = pygame.display.set_mode((Info.screenX, Info.screenY))

pygame.display.set_caption("Alien Invaders")
pygame.display.set_icon(Assets.game_icon)
Assets.animation_images()

info = Info()
player = Player()
enemy = EnemyManager(player, info)
enemy.spawn_enemies(rows=3, columns=8)
weapon = Weapons(player, enemy, info)
animated = Animations(player, info)
move = Movement(enemy, player, info)
shop = Shop(player, info)
inputs = Inputs(player, shop, info, enemy)

while True:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            Exiting.quit_game()
        if shop.active:
            shop.handle_event(event)
        inputs.keyboard_inputs([event])

    info.update_time()

    # Fill background with deep space black
    screen.fill((5, 5, 15))

    # Draw animated stars background
    info.update_stars()
    info.draw_stars(screen)

    if info.game_state == "Paused":
        info.pause_screen("Q to Quit, S to Shop or C to Continue (Paused)")
        shop.draw(screen)

    elif info.game_state == "WaveCleared":
        info.pause_screen("Q to Quit, S to Shop or C to Continue (Wave Cleared)")
        shop.draw(screen)

    elif info.game_state == "Playing":
        player.player_movement()
        player.update_position()
        player.update_particles(info.dt)  # Update particle effects
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
