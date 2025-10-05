
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
    background_image = pygame.image.load('si_game_assets/images/shop_background.png')

    buy_button_image = pygame.image.load('si_game_assets/images/buy_button.png')
    close_button_image = pygame.image.load('si_game_assets/images/close_button.png')

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

    screenX = 1080
    screenY = 720
    iconX = 64
    iconY = 64

    def __init__(self):
        self.clock = pygame.time.Clock()
        self.ticks = 0
        self.dt = 0
        self.game_state = "Paused"
        self.level = 1
    
    def update_time(self):
        self.dt = self.clock.tick(60) / 1000
        self.ticks = pygame.time.get_ticks()

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
        self.speed = 4
        self.player_lives = 3
        self.credits = 0
        self.inventory = []
        self.bullets = []
        self.points = 0

        self.playerX = Info.screenX / 2
        self.playerY = Info.screenY - Info.iconY - 10
        self.player_box = pygame.Rect(self.playerX, self.playerY, Info.iconX, Info.iconY)
        
        self.triple_shot_unlocked = False
        self.shield = 0
        self.shield_max = 3

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
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.playerX -= self.speed * info.dt * 60
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.playerX += self.speed * info.dt * 60
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.playerY -= self.speed * info.dt * 60
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.playerY += self.speed * info.dt * 60 

    def update_position(self):
        self.playerX = max(0, min(self.playerX, Info.screenX - Info.iconX))
        self.playerY = max(350, min(self.playerY, Info.screenY - Info.iconY))
        self.player_box.topleft = (self.playerX, self.playerY)

    def draw_player(self, screen):
        screen.blit(Assets.player_image, self.player_box)        

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
    "speed": {
        "cost": 500,
        "effect": lambda player: setattr(player, "speed", player.speed * 2),
        "repeatable": False,   
        "purchased": False     
    },
    "triple shot": {
        "cost": 800,
        "effect": lambda player: setattr(player, "triple_shot_unlocked", True),
        "repeatable": False,
        "purchased": False
    }
}

class Enemy:
    """ Will contain everything
    about the Alien enemy and its
    basic movement script """

    def __init__(self, player, info):
        self.player = player
        self.info = info

        self.aliens = []
        self.alien_direction = 1
        self.alien_speed = 5
        self.alien_drop_amount = 60
        self.vertical_padding = 50

    def spawn_aliens(self, level):
        self.player.bullets = []
        self.aliens = []
        self.info.game_state = "Playing"

        self.rows = min(5, 0 + self.info.level)
        self.columns = min(10,10 + self.info.level)
        self.alien_width = Assets.enemy_image_basic.get_width()
        self.alien_height = Assets.enemy_image_basic.get_height()
        self.total_width = self.columns * self.alien_width + (self.columns - 1) * 20
        self.start_x = (self.info.screenX - self.total_width) // 2
        self.start_y = self.vertical_padding

        for row in range(self.rows):
            for col in range(self.columns):
                x = self.start_x + col * (self.alien_width + 20)
                y = self.start_y + row * (self.alien_height + 20)
                alien_rect = Assets.enemy_image_basic.get_rect(topleft=(x, y))
                self.aliens.append({
                    "rect": alien_rect,
                    "just_spawned": True,
                    "independent": False,
                    "x_speed": 0,
                    "y_speed": 0
                })
        self.alien_speed = 5 + (level * 0.3)

    def alien_movement(self, screen):
        hit_edge = False
        edge_buffer = 5

        for alien in self.aliens:
            rect = alien["rect"]

            if not alien["independent"]:  
                rect.x += self.alien_speed * self.alien_direction * self.info.dt * 60

                if rect.left < edge_buffer:
                    rect.left = edge_buffer
                    hit_edge = True
                elif rect.right > self.info.screenX - edge_buffer:
                    rect.right = self.info.screenX - edge_buffer
                    hit_edge = True

                if rect.top > self.player.playerY:
                    alien["independent"] = True
                    alien["x_speed"] = random.choice([-2, -1, 1, 2])
                    alien["y_speed"] = random.randint(1, 3)

            else:
                rect.x += alien["x_speed"]
                rect.y += alien["y_speed"]

                if rect.left < 0 or rect.right > self.info.screenX:
                    alien["x_speed"] *= -1

                if rect.bottom >= self.info.screenY:
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
            screen.blit(Assets.enemy_image_basic, alien["rect"])

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
            Assets.starter_sound.set_volume(0.5)
            Assets.starter_sound.play()
            bullet = pygame.Rect(self.player.player_box.centerx - 2, self.player.player_box.top - 10, 4, 10)
            self.player.bullets.append(bullet)

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
        
            for alien in self.enemy.aliens[:]:
                if bullet.colliderect(alien["rect"]):
                    self.enemy.aliens.remove(alien)
                    if bullet in self.player.bullets:
                        self.player.bullets.remove(bullet)
                        self.player.points += 100
                        self.player.credits += 100
                    break

class Movement:
    """ Contains collision checks between
    enemies and player, but also updates to
    player character, dash/short-teleports, etc."""

    def __init__(self, enemy, player, info):
        self.player = player
        self.enemy = enemy
        self.info = info

    def collision_check(self):
        for alien in self.enemy.aliens[:]:
            if self.player.player_box.colliderect(alien["rect"]):
                if self.player.shield > 0:
                    self.player.shield -= 1
                    self.info.show_message("Shield absorbed the hit!", duration=150)
                    if self.player.shield == 0:
                        Assets.shield_failed_sound.set_volume(0.1)
                        Assets.shield_failed_sound.play()

                else:
                    self.player.player_lives -= 1
                    self.info.show_message("Ouch! Lost a Life", duration=150)
                if alien in self.enemy.aliens:
                    self.enemy.aliens.remove(alien)
                    
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
            pygame.K_1: "speed",
            pygame.K_2: "triple shot"
        }
        
        self.buttons = []
        y_offset = 200
        for key, upgrade_name in self.key_map.items():
                upgrade_info = Upgrades.upgrades[upgrade_name]
                button_text = f"[{pygame.key.name(key).upper()}] {upgrade_name} ({upgrade_info['cost']} Credits)"
                self.buttons.append(
                    Button(
                        x=Info.screenX // 2 - 150,
                        y=y_offset,
                        width=300,
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
        # Check if already bought and non-repeatable
        if not upgrade.get("repeatable", False) and upgrade.get("purchased", False):
            self.info.show_message(f"{upgrade_name} already purchased!", duration=1000)
            return
        if self.player.credits >= upgrade["cost"]:
            self.player.credits -= upgrade["cost"]
            upgrade["effect"](self.player)
            if not upgrade.get("repeatable", False):
                upgrade["purchased"] = True
            self.info.show_message(f"{upgrade_name} purchased successfully! Current credits: {self.player.credits}", duration=1000)
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

        points_text = font.render(f"Score: {self.player.points}", True, (255, 255, 255))
        screen.blit(points_text, (15, 10))

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

                elif event.key == pygame.K_c and self.info.game_state == "WaveCleared":
                    self.info.level += 1
                    self.enemy.spawn_aliens(self.info.level)

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
enemy = Enemy(player, info)
enemy.spawn_aliens(info.level)
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

        enemy.alien_movement(screen)
        move.collision_check()
        move.coin_collision()

        weapon.shooting_function()
        weapon.update_bullets(screen)

        if len(enemy.aliens) == 0:
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
