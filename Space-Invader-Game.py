
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

    game_state = "Paused"
    level = 1

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



class Upgrades:
    """ Will contain the player
    shop inventory, and be updatable
    as needed. """

    upgrades = {
    "speed": {
        "cost": 100,
        "effect": lambda player: setattr(player, "speed", player.speed * 3),
        "repeatable": False,   
        "purchased": False     
    },
    "health": {
        "cost": 50,
        "effect": lambda player: setattr(player, "health", min(player.max_health, player.health + 20)),
        "repeatable": True
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
        self.points = 0

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

        self.shield_coin_rect = Assets.shield_coin_image[0].get_rect(
            topleft=(random.randint(50, Info.screenX - 50), 
                     random.randint(Info.screenY // 2, Info.screenY - 50))
                     )
        self.coin_collected = False
        self.coin_frame = 0
        self.coin_timer = 0
        self.coin_effect_timer = 0
        self.coin_speed = 250   
        self.coin_duration = 5000
        self.coin_respawn_delay = 5000
        self.coin_respawn_timer = 0
        self.float_amplitude = 5
    
    def player_movement(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.playerX -= self.speed * Info.dt * 60
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.playerX += self.speed * Info.dt * 60
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.playerY -= self.speed * Info.dt * 60
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.playerY += self.speed * Info.dt * 60 

    def update_position(self):
        self.playerX = max(0, min(self.playerX, Info.screenX - Info.iconX))
        self.playerY = max(350, min(self.playerY, Info.screenY - Info.iconY))
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

    def __init__(self):
        self.player = player

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

    def coin_collision(self):
        
        if self.player.player_box.colliderect(self.player.shield_coin_rect) and not self.player.shield_coin_active:
            self.player.shield += 1
            self.player.coin_collected = True
            self.player.shield_coin_active = True
            self.player.coin_effect_timer = 0
            Assets.shield_sound.set_volume(0.3)
            Assets.shield_sound.play()

        if self.player.shield_coin_active:
            self.player.coin_effect_timer += Info.dt * 1000
            effect_duration = 15000
            if self.player.coin_effect_timer >= effect_duration:
                self.player.shield_coin_active = False
                self.player.shield -= 1

        if self.player.coin_collected and not self.player.shield_coin_active:
            self.player.coin_respawn_timer += Info.dt * 1000
            if self.player.coin_respawn_timer >= self.player.coin_respawn_delay:
                self.player.shield_coin_rect.topleft = (
                    random.randint(50, Info.screenX -50), 
                    random.randint(Info.screenY // 2, Info.screenY - 50)
                    )
                self.player.coin_collected = False
                self.player.coin_respawn_timer = 0
  
class Shop:

    def __init__(self, player, info):
        self.player = player
        self.info = info
        self.active = False
        self.key_map = {
            pygame.K_1: "speed",
            pygame.K_2: "health"
        }

    def player_shop(self, screen):
        if not self.active:
            return
        font = pygame.font.Font(None, 50)
        screen.blit(Assets.background_image, (0, 0))
        y_offset = 200

        for key, upgrade in Upgrades.upgrades.items():
            display_name = upgrade.get("name", key)
            text = font.render(
                f"Press '{key}' to buy {display_name}: {upgrade['cost']} Credits",
                True, (255, 255, 255)
            )
            screen.blit(text, (Info.screenX // 2 - text.get_width() // 2, y_offset))
            y_offset += 70

        money_text = font.render(f"CREDITS: {self.player.credits}", True, (255, 255, 255))
        screen.blit(money_text, (15, 127))

    def buy_upgrade(self, key):
        if key in self.key_map:
            upgrade_name = self.key_map[key]
            upgrade = Upgrades.upgrades[upgrade_name]

        # Check if already bought and non-repeatable
        if not upgrade.get("repeatable", False) and upgrade.get("purchased", False):
            self.info.show_message(f"{upgrade_name} already purchased!", duration=1200)
            return

        if self.player.credits >= upgrade["cost"]:
            self.player.credits -= upgrade["cost"]
            upgrade["effect"](self.player)
            if not upgrade.get("repeatable", False):
                upgrade["purchased"] = True
            self.info.show_message(f"{upgrade_name} purchased successfully! Current credits: {self.player.credits}", duration=1200)
        else:
            self.info.show_message("Not enough credits!", duration=1200)
 
class Animations:
    """Will contain basic code for
    flipping 2 images back and forth
    to simulate animation, and also
    static information on screen"""

    heart_animation_timer = 0
    heart_animation_speed = 150
    heart_frame = 0
    def __init__(self):
        self.player = player

    def heart_animation(self, screen):
        self.heart_animation_timer += Info.dt * 1000
        if self.heart_animation_timer >= self.heart_animation_speed:
            self.heart_animation_timer = 0
            self.heart_frame = (self.heart_frame + 1) % len(Assets.hearts_image)
        for i in range(self.player.player_lives):
            screen.blit(Assets.hearts_image[self.heart_frame], (10 + i * 40, 40))

    def draw_shields(self, screen):
        """Draws 1-3 visual blue rings 
        around player depending 
        on shield tokens collect, will last
        15 seconds before expiring."""

        for i in range(self.player.shield):
            radius = max(Info.iconX, Info.iconY) + (i * 10)  # each ring slightly bigger
            shield_surface = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
            pygame.draw.circle(shield_surface, (0, 0, 255, 100), (radius, radius), radius, 4)  # 4px thick ring
            screen.blit(shield_surface, (self.player.playerX - radius + Info.iconX/2, self.player.playerY - radius + Info.iconY/2))

    def floating_coin(self, screen):   

        if not self.player.coin_collected:
            shield_image = Assets.shield_coin_image[self.player.coin_frame]

            # Switches between two images, creating a *Flash* effect.
            self.player.coin_timer += Info.dt * 1000
            if self.player.coin_timer >= self.player.coin_speed:
                self.player.coin_timer = 0
                self.player.coin_frame = (self.player.coin_frame + 1) % len(Assets.shield_coin_image)
            
            # Floating animation
            float_offset = math.sin(pygame.time.get_ticks() * 0.005) * self.player.float_amplitude
            draw_rect = shield_image.get_rect(center=self.player.shield_coin_rect.center) 
            draw_rect.y += float_offset
    
            screen.blit(shield_image, draw_rect)

class Inputs:
    def __init__(self,player, shop, info):
        self.player = player
        self.shop = shop
        self.info = info

    def keyboard_inputs(self, events):
        for event in events:

            if event.type == pygame.QUIT:
                Exiting.quit_game()  

            elif event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:
                    if info.game_state == "Playing":
                        info.game_state = "Paused"
                    elif info.game_state == "Paused":
                        info.game_state == "Playing"
                    shop.active = False

                elif event.key == pygame.K_s and (info.game_state in ["Paused", "WaveCleared"]):
                    self.shop.active = True

                elif event.key == pygame.K_c and self.info.game_state == "WaveCleared":
                    self.info.level += 1
                    enemy.spawn_aliens(self.info.level, self.player)
                    self.info.game_state = "Playing"

                elif event.key == pygame.K_q and self.info.game_state in ["Paused", "WaveCleared"]:
                    Exiting.quit_game()

                elif self.shop.active:
                    self.shop.buy_upgrade(event.key)

screen = pygame.display.set_mode((Info.screenX, Info.screenY))

pygame.display.set_caption("Alien Invaders")
pygame.display.set_icon(Assets.game_icon)
Assets.animation_images()

info = Info()
player = Player()
enemy = Enemy()
enemy.spawn_aliens(Info.level, player)
weapon = Weapons(player, enemy)
animated = Animations()
move = Movement()
shop = Shop(player, info)
inputs = Inputs(player, shop, info)

while True:
    events = pygame.event.get()
    for e in events:
        if e.type == pygame.QUIT:
            Exiting.quit_game()

    inputs.keyboard_inputs(events)

    info.dt = info.clock.tick(60) / 1000
    info.clock_ticks = pygame.time.get_ticks()

    screen.fill("black")

    if info.game_state == "Paused":
        info.pause_screen("Q to Quit, S to Shop or C to Continue (Paused)")
        shop.player_shop(screen)

    elif info.game_state == "WaveCleared":
        info.pause_screen("Q to Quit, S to Shop or C to Continue (Wave Cleared)")
        shop.player_shop(screen)

    elif info.game_state == "Playing":

        player.player_movement()
        player.update_position()
        player.draw_player(screen)

        enemy.alien_movement(player, screen)
        move.collision_check()
        move.coin_collision()

        animated.heart_animation(screen)
        animated.floating_coin(screen)
        animated.draw_shields(screen)

        weapon.shooting_function()
        weapon.update_bullets(screen)

        if len(enemy.aliens) == 0:
            enemy.earn_credits()
            info.game_state = "WaveCleared"

    if shop.active:
        shop.player_shop(screen)

    pygame.display.flip()
