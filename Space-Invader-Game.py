
import pygame
import random
import math
import sys

pygame.init()
pygame.mixer.init()

class Exiting:
    def quit_game():
        pygame.quit()
        sys.exit()

class Assets:
    """The 'Assets' class store and 
    loads the collective ball assets for 
    images, effects and music"""

    game_icon = pygame.image.load('Game Assets/ship.png')
    player_image = pygame.image.load('Game Assets/ship.png')
    enemy_image = pygame.image.load('Game Assets/alien_basic.png')
    background_image = pygame.image.load('Game Assets/shop_background.png')

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

    starter_sound = pygame.mixer.Sound('AudioAssets/starter_weapon.mp3')
    triple_sound = pygame.mixer.Sound('AudioAssets/triple_power_up.wav')
    cannon_sound = pygame.mixer.Sound('AudioAssets/cannon_shot.wav')
    gatling_sound = pygame.mixer.Sound('AudioAssets/gatling_laser.wav')
    shield_sound = pygame.mixer.Sound('AudioAssets/shield_energy.wav')

class Game_info:
    """The 'Game_info' class will store
    information regarding the games
    most basic information, 
    dimensions, variables and reusable
    fonts or functions"""

    hit_edge = False
    game_paused = False
    clock = pygame.time.Clock()
    clock_ticks = pygame.time.get_ticks()
    dt = clock.tick(60) / 1000
    screenX = 1920
    screenY = 1080
    iconX = 64
    iconY = 64
    font = pygame.font.Font(None, 36)

    game_state = "Playing"
    level = 1

    edge_buffer = 5

    last_shot_time = 0
    bullet_speed = 500
    bullet_cooldown = 200
    bullet_rect = None
    bullet_active = False

    heart_animation_timer = 0
    heart_animation_speed = 1000
    heart_frame = 0
    
pygame.display.set_caption("Alien Invaders")
pygame.display.set_icon(Assets.game_icon)
screen = pygame.display.set_mode((Game_info.screenX, Game_info.screenY))
Assets.animation_images() # Images that need to be converted are loaded here.
 
class Upgrades:
    """The 'Power_ups' class contains
    information such as statements,
    a set variable for speed, amount, costs,
    and descriptions."""

    booster = False
    booster_speed = 10
    triple_shot = False
    upgrades = {
    "1": {  # Key to trigger the upgrade
        "name": "Permanent Speed Boost",
        "cost": 100,
        "effect": lambda: setattr(Upgrades, "booster", True)
    },
    "2": {
        "name": "Triple Shot",
        "cost": 500,
        "effect": lambda: setattr(Upgrades, "triple_shot", True)
        }
}

class Player:
    def __init__(self):
        self.player_lives = 3
        self.credits = 0
        self.speed = 3
        self.inventory = []
        
        self.playerX = Game_info.screenX / 2
        self.playerY = Game_info.screenY 
        
        self.player_box = pygame.Rect(self.playerX, self.playerY, Game_info.iconX, Game_info.iconY) #Player collision box
        
        self.bullets = []

        self.shield_coin_rect = Assets.shield_coin_image[0].get_rect(
            topleft=(random.randint(50, Game_info.screenX - 50), 
                     random.randint(Game_info.screenY // 2, Game_info.screenY - 50))
                     )

        self.shield_coin_active = False
        self.coin_collected = False
        self.coin_frame = 0
        self.coin_timer = 0
        self.coin_effect_timer = 0
        self.coin_speed = 250   
        self.coin_duration = 5000
        self.coin_respawn_delay = 8000
        self.coin_respawn_timer = 0
        self.float_amplitude = 5
    
    def player(x, y):
        screen.blit(Assets.player_image, (x, y))
    
    def show_message(self, text, duration=1000):
        font = pygame.font.Font(None, 50)
        msg_surface = font.render(text, True, (255, 255, 255))
        msg_rect = msg_surface.get_rect(center=(Game_info.screenX//2, Game_info.screenY//2))
        screen.blit(msg_surface, msg_rect)
        pygame.display.flip()
        pygame.time.delay(duration)

    def player_position(self):
        self.playerX = max(0, min(self.playerX, Game_info.screenX - Game_info.iconX))
        self.playerY = max(450, min(self.playerY, Game_info.screenY - Game_info.iconY))
        self.player_box.topleft = (self.playerX, self.playerY)

    def drawing(self, screen):
        screen.blit(Assets.player_image, self.player_box)

    def player_shop(self):
        font = pygame.font.Font(None, 50)

        while Game_info.game_paused:
            screen.blit(Assets.background_image, (0, 0))
            y_offset = 200

            for key, upgrade in Upgrades.upgrades.items():
                text = font.render(f"Press '{key}' to buy {upgrade['name']}: {upgrade['cost']} Credits", True, (255, 255, 255))
                screen.blit(text, (Game_info.screenX // 2 - text.get_width() // 2, y_offset))
                y_offset += 70

            money_text = font.render(f"CREDITS: {player.credits}", True, (255, 255, 255))
            screen.blit(money_text, (15, 127))

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.KEYDOWN:
                    key_pressed = pygame.key.name(event.key).upper()

                    if key_pressed in Upgrades.upgrades:
                        upgrade = Upgrades.upgrades[key_pressed]
                        if player.credits >= upgrade["cost"]:
                            player.credits -= upgrade["cost"]
                            upgrade["effect"]()
                            player.show_message(f"Purchased {upgrade['name']}!") 
                            pygame.time.delay(1000)                            
                        else:
                            player.show_message("Not enough credits")

                    elif event.key == pygame.K_ESCAPE:
                        Game_info.game_paused = False

    def shooting_mechanic(self):
            if Upgrades.triple_shot:
            # Fire 3 bullets: center, left, right
                Assets.triple_sound.play() # Audio file
                bullet1 = pygame.Rect(player.player_box.centerx - 2, player.player_box.top - 10, 4, 10)
                bullet2 = pygame.Rect(player.player_box.centerx - 17, player.player_box.top - 10, 4, 10)
                bullet3 = pygame.Rect(player.player_box.centerx + 13, player.player_box.top - 10, 4, 10)
                player.bullets.extend([bullet1, bullet2, bullet3])
            else:
            # Single bullet, basic beginner.
                Assets.starter_sound.play()
                bullet = pygame.Rect(player.player_box.centerx - 2, player.player_box.top - 10, 4, 10)
                player.bullets.append(bullet)

    def update_bullets(self, screen):
        for bullet in player.bullets[:]:
            bullet.y -= Game_info.bullet_speed * Game_info.dt
            pygame.draw.rect(screen, (255, 255, 0), bullet)

            if bullet.bottom < 0:
                player.bullets.remove(bullet)
                continue
        
            for alien in Alien_info.aliens[:]:
                if bullet.colliderect(alien["rect"]):
                    Alien_info.aliens.remove(alien)
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                    break

    def coin_collision(self, dt):

        if self.player_box.colliderect(self.shield_coin_rect) and not self.shield_coin_active:
            self.shield_coin_active = True
            self.coin_collected = True
            self.coin_effect_timer = 0
            Assets.shield_sound.play()

        if self.shield_coin_active:
            self.coin_effect_timer += dt * 1000
            effect_duration = 10000
            if self.coin_effect_timer >= effect_duration:
                self.shield_coin_active = False

        if self.coin_collected and not self.shield_coin_active:
            self.coin_respawn_timer += dt * 1000
            if self.coin_respawn_timer >= self.coin_respawn_delay:
                self.shield_coin_rect.topleft = (
                    random.randint(50, Game_info.screenX -50), 
                    random.randint(Game_info.screenY // 2, Game_info.screenY - 50)
                    )
                self.coin_collected = False
                self.coin_respawn_timer = 0
    
        if not self.coin_collected:
            current_img = Assets.shield_coin_image[self.coin_frame]
        # Update flash
            self.coin_timer += dt * 1000
            if self.coin_timer >= self.coin_speed:
                self.coin_timer = 0
                self.coin_frame = (self.coin_frame + 1) % len(Assets.shield_coin_image)

            # Floating animation
            float_offset = math.sin(pygame.time.get_ticks() * 0.005) * self.float_amplitude
            draw_rect = current_img.get_rect(center=self.shield_coin_rect.center) 
            draw_rect.y += float_offset
    
            screen.blit(current_img, draw_rect) 

class Alien_info:
    """The 'Alien_info' class holds
    configurable information"""     

    aliens = []
    alien_direction = 1
    alien_speed = 5
    alien_drop_amount = 60 #In pixels
    vertical_padding = 50
    rows = min(5, 0 + Game_info.level)
    cols = min(10, 10 + Game_info.level)

class Spawning:
    def spawn_aliens(self, level):
        player.bullets = []
        Alien_info.aliens = []

        alien_width = Assets.enemy_image.get_width()
        alien_height = Assets.enemy_image.get_height()

        total_width = Alien_info.cols * alien_width + (Alien_info.cols - 1) * 20
        start_x = (Game_info.screenX - total_width) // 2
        start_y = Alien_info.vertical_padding

        for row in range(Alien_info.rows):
            for col in range(Alien_info.cols):
                x = start_x + col * (alien_width + 20)
                y = start_y + row * (alien_height + 20)
                alien_rect = Assets.enemy_image.get_rect(topleft=(x, y))
                Alien_info.aliens.append({
                    "rect": alien_rect, 
                    "just_spawned": True,
                    "independent": False,
                    "x_speed": 0,
                    "y_speed": 0,
                    })    
        Alien_info.alien_speed = 5 + (level * 0.3)
        Spawning.last_wave_count = len(Alien_info.aliens)

    def earn_credits(self):
        player.credits += Spawning.last_wave_count * 100 

class Movement:
    def alien_movement(self):
        Game_info.hit_edge = False

        for alien in Alien_info.aliens:
            rect = alien["rect"]

            if not alien["independent"]:  
                rect.x += Alien_info.alien_speed * Alien_info.alien_direction * Game_info.dt * 60

                if rect.left < Game_info.edge_buffer:
                    rect.left = Game_info.edge_buffer
                    Game_info.hit_edge = True
                elif rect.right > Game_info.screenX - Game_info.edge_buffer:
                    rect.right = Game_info.screenX - Game_info.edge_buffer
                    Game_info.hit_edge = True

                if rect.top > player.playerY:
                    alien["independent"] = True
                    alien["x_speed"] = random.choice([-2, -1, 1, 2])
                    alien["y_speed"] = random.randint(1, 3)

            else:
                rect.x += alien["x_speed"]
                rect.y += alien["y_speed"]

                if rect.left < 0 or rect.right > Game_info.screenX:
                    alien["x_speed"] *= -1

                if rect.bottom >= Game_info.screenY:
                    alien["independent"] = False
                    alien["x_speed"] = 0
                    alien["y_speed"] = 0
                    rect.y = 0

        if Game_info.hit_edge:
            Alien_info.alien_direction *= -1
            for alien in Alien_info.aliens:
                if not alien["independent"]:
                    alien["rect"].y += Alien_info.alien_drop_amount

        for alien in Alien_info.aliens:
            if alien["just_spawned"] and alien["rect"].top > 50:
                alien["just_spawned"] = False

        for alien in Alien_info.aliens:
            screen.blit(Assets.enemy_image, alien["rect"])

    def collision_check(self):
        for alien in Alien_info.aliens[:]:
            if player.player_box.colliderect(alien["rect"]):
                player.player_lives -= 1
                Alien_info.aliens.remove(alien)
                player.show_message("Ouch! Lost a Life", duration=500)
                break

class Pause_manager:
    def show_pause_screen(message):
        Game_info.game_paused = True
        font = pygame.font.Font(None, 50)  
        screen.fill((0, 0, 0))  
        text = font.render(message, True, (255, 255, 255)) 
        text_rect = text.get_rect(center=(Game_info.screenX//2, Game_info.screenY//2))
        screen.blit(text, text_rect)
        pygame.display.flip()

class Input_manager:
    """The 'Input_manager' class will
    house all related keyboard inputs
    and related functions to said inputs"""
    
    def process_events():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                Exiting.quit_game()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    Game_info.game_paused = not Game_info.game_paused
                elif event.key == pygame.K_s and Game_info.game_paused:
                    player.player_shop()
                elif event.key == pygame.K_q and Game_info.game_paused:
                    Exiting.quit_game()
                elif event.key == pygame.K_c and Game_info.game_paused:
                    Game_info.level += 1
                    spawner.spawn_aliens(Game_info.level)
                    player.playerX = Game_info.screenX // 2 - Game_info.iconX // 2
                    player.playerY = Game_info.screenY
                    Game_info.game_state = "playing"
                    Game_info.game_paused = False   

    def keyboard_input():
        keys = pygame.key.get_pressed()
        if Upgrades.booster == True:
            player.speed = Upgrades.booster_speed

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            player.playerX -= player.speed * Game_info.dt * 60
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            player.playerX += player.speed * Game_info.dt * 60
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            player.playerY -= player.speed * Game_info.dt * 60
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            player.playerY += player.speed * Game_info.dt * 60

        now = pygame.time.get_ticks()    
        if keys[pygame.K_SPACE] and (now - Game_info.last_shot_time) >= Game_info.bullet_cooldown:
            Game_info.last_shot_time = now
            player.shooting_mechanic()

class Animations:
    def heart_animation(self):
        Game_info.heart_animation_timer += Game_info.dt * 1000
        if Game_info.heart_animation_timer >= Game_info.heart_animation_speed:
            Game_info.heart_animation_timer = 0
            Game_info.heart_frame = (Game_info.heart_frame + 1) % len(Assets.hearts_image)
        for i in range(player.player_lives):
            screen.blit(Assets.hearts_image[Game_info.heart_frame], (10 + i * 40, 40))

player = Player()
spawner = Spawning()
mover = Movement()
animated = Animations()

spawner.spawn_aliens(Game_info.level)
Game_info.game_state = "Playing"

while True:

    Game_info.clock_ticks = pygame.time.get_ticks()
    Game_info.dt = Game_info.clock.tick(60) / 1000

    Input_manager.process_events()

    if Game_info.game_paused:
        Pause_manager.show_pause_screen("'S' to open Upgrade Shops, 'Q' to Quit, or 'ESC/C' to Resume")
        continue

    screen.fill('black')

    Input_manager.keyboard_input() 
    player.player_position()
    player.coin_collision(Game_info.dt)
    player.update_bullets(screen)

    if Game_info.game_state == "Playing" and len(Alien_info.aliens) == 0:
        spawner.earn_credits()
        Game_info.game_state = "Wave_cleared"
        Pause_manager.show_pause_screen("Wave_cleared Press ESC to continue")
        spawner.spawn_aliens(Game_info.level)
        Game_info.game_state = "Playing"

    mover.alien_movement()
    mover.alien_movement()
    mover.collision_check()
    animated.heart_animation()
    player.drawing(screen)

    pygame.display.flip()
