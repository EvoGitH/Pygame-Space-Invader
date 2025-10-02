
import pygame, random, math, sys

# Self reminder that __init__ creates literal instances of what ever you deem necessary
# you don't have to create multiple player or enemy profiles, 
# # just having that one class and calling it with __init__ will allow for
# multiple instances, I FINALLY GET IT!

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
    game_icon = pygame.image.load('Game Assets/ship.png')
    player_image = pygame.image.load('Game Assets/ship.png')
    enemy_image = pygame.image.load('Game Assets/alien_basic.png')
    background_image = pygame.image.load('Game Assets/shop_background.png')
    buy_button_image = pygame.image.load('Game Assets/buy_button.png')
    close_button_image = pygame.image.load('Game Assets/close_button.png')

    # Audio effects
    starter_sound = pygame.mixer.Sound('AudioAssets/starter_weapon.mp3')
    triple_sound = pygame.mixer.Sound('AudioAssets/triple_power_up.wav')
    cannon_sound = pygame.mixer.Sound('AudioAssets/cannon_shot.wav')
    gatling_sound = pygame.mixer.Sound('AudioAssets/gatling_laser.wav')
    shield_sound = pygame.mixer.Sound('AudioAssets/shield_energy.wav')
    shield_failed_sound = pygame.mixer.Sound('AudioAssets/shield_failed.wav')

    # *Animated* images
    def animation_images():
        """Display required to be Initialized
        before these images can be converted"""

        Assets.hearts_image = [
            pygame.image.load('Game Assets/heart1.png').convert_alpha(), 
            pygame.image.load('Game Assets/heart2.png').convert_alpha()
            ]
        Assets.three_shot_image = [
            pygame.image.load('Game Assets/three_shot_power1.png').convert_alpha(), 
            pygame.image.load('Game Assets/three_shot_power2.png').convert_alpha()
            ]
        Assets.shield_coin_image = [
            pygame.image.load('Game Assets/shield_coin1.png').convert_alpha(),
            pygame.image.load('Game Assets/shield_coin2.png').convert_alpha()
        ]
    
class Info:
    """ Will hold only basic
    information that is reuseable 
    but mutable for the game here"""
    clock = pygame.time.Clock()
    ticks = pygame.time.get_ticks()
    dt = clock.tick(60) / 1000
    screenX = 1080
    screenY = 720
    iconX = 64
    iconY = 64
    game_state = "Playing"
    game_paused = False
    wave_cleared = False
    level = 1

    def show_message(self, text, duration=1000):
        font = pygame.font.Font(None, 50)
        msg_surface = font.render(text, True, (255, 255, 255))
        msg_rect = msg_surface.get_rect(center=(Info.screenX//2, Info.screenY//2))
        screen.blit(msg_surface, msg_rect)
        pygame.display.flip()
        pygame.time.delay(duration)

class Upgrades:
    """ Will contain the player
    shop inventory, and be updatable
    as needed. """

    upgrades = {
    "1": {  # Key to trigger the upgrade
        "name": "Permanent Speed Boost",
        "cost": 800,
        "flag": "booster",
        "effect": lambda: setattr(Upgrades, "booster", True)
    },
    "2": {
        "name": "Triple Shot",
        "cost": 500,
        "flag": "triple_shot",
        "effect": lambda: setattr(Upgrades, "triple_shot", True)
        }
}

class Player:
    """ Will hold instanced 
    information for the Player"""
    def __init__(self):
        self.speed = 3
        self.player_lives = 3
        self.credits = 0
        self.inventory = []
        self.bullets = []

        self.playerX = Info.screenX / 2
        self.playerY = Info.screenY
        self.player_box = pygame.Rect(self.playerX, self.playerY, Info.iconX, Info.iconY)
        
        self.fly_boost_unlock = False
        self.fly_boost_speed = 10
        self.triple_shot_unlock = False

        self.shield = 0
        self.shield_max = 3
        self.shield_duration = 0
        self.shield_coin_active = False

    def draw_shields(self, screen):
        """Draws 1-3 visual blue rings 
        around player depending 
        on shield count"""

        for i in range(self.shield):
            radius = max(Info.iconX, Info.iconY) + (i * 10)  # each ring slightly bigger
            shield_surface = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
            pygame.draw.circle(shield_surface, (0, 0, 255, 100), (radius, radius), radius, 4)  # 4px thick ring
            screen.blit(shield_surface, (self.playerX - radius + Info.iconX/2, self.playerY - radius + Info.iconY/2))
    
    def player_movement(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            player.playerX -= player.speed * Info.dt * 60
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            player.playerX += player.speed * Info.dt * 60
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            player.playerY -= player.speed * Info.dt * 60
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            player.playerY += player.speed * Info.dt * 60    

    def update_position(self):
        self.playerX = max(0, min(self.playerX, Info.screenX - Info.iconX))
        self.playerY = max(450, min(self.playerY, Info.screenY - Info.iconY))
        self.player_box.topleft = (self.playerX, self.playerY)

    def draw_player(self, screen):
        screen.blit(Assets.player_image, self.player_box)

class Enemy:
    """ Will contain everything
    about the Alien enemy and its
    basic movement script """

    def __init__(self):
        self.aliens = []
        self.alien_direction = 1
        self.alien_speed = 5
        self.alien_drop_amount = 60
        self.vertical_padding = 50
        self.rows = min(5, 0 + Info.level)
        self.columns = min(10,10 + Info.level)
        self.alien_width = Assets.enemy_image.get_width()
        self.alien_height = Assets.enemy_image.get_height()
        self.total_width = self.columns * self.alien_width + (self.columns - 1) * 20
        self.start_x = (Info.screenX - self.total_width) // 2
        self.start_y = self.vertical_padding

    
    def spawn_aliens(self, level, player):
        player.bullets = []
        self.aliens = []
        Info.game_state = "Playing"
        for row in range(self.rows):
            for col in range(self.columns):
                x = self.start_x + col * (self.alien_width + 20)
                y = self.start_y + row * (self.alien_height + 20)
                alien_rect = Assets.enemy_image.get_rect(topleft=(x, y))
                self.aliens.append({
                    "rect": alien_rect,
                    "just_spawned": True,
                    "independent": False,
                    "x_speed": 0,
                    "y_speed": 0
                })
        self.alien_speed = 5 + (level * 0.3)
        self.last_wave_count = len(self.aliens)

    def earn_credits(self):
        player.credits +=self.last_wave_count * 100 
    
    def alien_movement(self, player, screen):
        hit_edge = False
        edge_buffer = 5

        for alien in self.aliens:
            rect = alien["rect"]

            if not alien["independent"]:  
                rect.x += self.alien_speed * self.alien_direction * Info.dt * 60

                if rect.left < edge_buffer:
                    rect.left = edge_buffer
                    hit_edge = True
                elif rect.right > Info.screenX - edge_buffer:
                    rect.right = Info.screenX - edge_buffer
                    hit_edge = True

                if rect.top > player.playerY:
                    alien["independent"] = True
                    alien["x_speed"] = random.choice([-2, -1, 1, 2])
                    alien["y_speed"] = random.randint(1, 3)

            else:
                rect.x += alien["x_speed"]
                rect.y += alien["y_speed"]

                if rect.left < 0 or rect.right > Info.screenX:
                    alien["x_speed"] *= -1

                if rect.bottom >= Info.screenY:
                    alien["independent"] = False
                    alien["x_speed"] = 0
                    alien["y_speed"] = 0
                    rect.y = 0

        if hit_edge:
            self.alien_direction *= -1
            for alien in self.aliens:
                if not alien["independent"]:
                    alien["rect"].y += self.alien_drop_amount

        for alien in self.aliens:
            if alien["just_spawned"] and alien["rect"].top > 50:
                alien["just_spawned"] = False

        for alien in self.aliens:
            screen.blit(Assets.enemy_image, alien["rect"])

class Weapons:
    """ Mechanics and the
     visuals of game weapons """
    last_shot_time = 0
    bullet_speed = 500
    bullet_cooldown = 200
    bullet_rect = None
    bullet_active = False

    def weapon_mechanic(self):
            if player.triple_shot_unlock:
            # Fire 3 bullets: center, left, right
                Assets.triple_sound.set_volume(0.5)
                Assets.triple_sound.play() # Audio file

                bullet1 = pygame.Rect(player.player_box.centerx - 2, player.player_box.top - 10, 4, 10)
                bullet2 = pygame.Rect(player.player_box.centerx - 17, player.player_box.top - 10, 4, 10)
                bullet3 = pygame.Rect(player.player_box.centerx + 13, player.player_box.top - 10, 4, 10)
                player.bullets.extend([bullet1, bullet2, bullet3])
            else:
            # Single bullet, basic beginner.
                Assets.starter_sound.set_volume(0.5)
                Assets.starter_sound.play()
                bullet = pygame.Rect(player.player_box.centerx - 2, player.player_box.top - 10, 4, 10)
                player.bullets.append(bullet)

    def __init__(self, player, enemy):
        self.player = player
        self.enemy = enemy

    def shooting_function(self):
        keys = pygame.key.get_pressed()
        now = pygame.time.get_ticks()
        if keys[pygame.K_SPACE] and (now - self.last_shot_time) >= self.bullet_cooldown:
            self.last_shot_time = now
            self.weapon_mechanic()

    def update_bullets(self, screen):
        for bullet in self.player.bullets[:]:
            bullet.y -= Weapons.bullet_speed * Info.dt
            pygame.draw.rect(screen, (255, 255, 0), bullet)

            if bullet.bottom < 0:
                self.player.bullets.remove(bullet)
                continue
        
            for alien in self.enemy.aliens[:]:
                if bullet.colliderect(alien["rect"]):
                    self.enemy.aliens.remove(alien)
                    if bullet in self.player.bullets:
                        self.player.bullets.remove(bullet)
                    break
    
class Movement:
    """ Contains collision checks between
    enemies and player, but also updates to
    player character, dash/short-teleports, etc."""

    def collision_check(self):
        info = Info()
        for alien in enemy.aliens[:]:
            if player.player_box.colliderect(alien["rect"]):
                if player.shield > 0:
                    player.shield -= 1
                    info.show_message("Shield absorbed the hit!", duration=150)
                    if player.shield == 0:
                        Assets.shield_failed_sound.set_volume(0.1)
                        Assets.shield_failed_sound.play()

                else:
                    player.player_lives -= 1
                    info.show_message("Ouch! Lost a Life", duration=150)
                if alien in enemy.aliens:
                    enemy.aliens.remove(alien)
                    
                if player.player_lives == 0:
                    Exiting.quit_game()


class Shop:
    """ Will contain the basic
    structure of code that'll allow player 
    to buy upgrades from Upgrade class"""

    def __init__(self, player):
        self.player = player
    
    def buy_upgrade(self, key):
        if key in Upgrades.upgrades:
            upgrade = Upgrades.upgrades[key]

            if getattr(self.player, f"{upgrade['flag']}_unlock", False):
                print(f"{upgrade['name']} already unlocked!")
                return False
            if self.player.credits >= upgrade["cost"]:
                self.player.credits -= upgrade["cost"]
                setattr(self.player, f"{upgrade['flag']}_unlock", True)
                print(f"Purchased {upgrade['name']}!")
                return True
            else:
                print("Not enough credits!")
                return False

class Animations:
    """Will contain basic code for
    flipping 2 images back and forth
    to simulate animation"""

    heart_animation_timer = 0
    heart_animation_speed = 150
    heart_frame = 0

    def heart_animation(self):
        Animations.heart_animation_timer += Info.dt * 1000
        if Animations.heart_animation_timer >= Animations.heart_animation_speed:
            Animations.heart_animation_timer = 0
            Animations.heart_frame = (Animations.heart_frame + 1) % len(Assets.hearts_image)
        for i in range(player.player_lives):
            screen.blit(Assets.hearts_image[Animations.heart_frame], (10 + i * 40, 40))

screen = pygame.display.set_mode((Info.screenX, Info.screenY))

pygame.display.set_caption("Alien Invaders")
pygame.display.set_icon(Assets.game_icon)
Assets.animation_images()

player = Player()
enemy = Enemy()
enemy.spawn_aliens(Info.level, player)
weapon = Weapons(player, enemy)
animated = Animations()
mover = Movement()

while True:

    Info.clock_ticks = pygame.time.get_ticks()
    Info.dt = Info.clock.tick(60) / 1000
    screen.fill('black')

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()

    player.player_movement()
    player.update_position()
    enemy.alien_movement(player, screen)
    player.draw_player(screen)
    mover.collision_check()
    animated.heart_animation()
    weapon.shooting_function()
    weapon.update_bullets(screen)

    if Info.game_state == "Playing" and len(enemy.aliens) == 0:
        enemy.earn_credits()
        Info.game_state = "Wave_cleared"
        Info.wave_cleared = True
        continue

    pygame.display.flip()
