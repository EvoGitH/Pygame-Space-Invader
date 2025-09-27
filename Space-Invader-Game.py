import pygame
import random
import math

# Initialize the pygame module
pygame.init()
pygame.mixer.init()

############################################################
# Creates the display/screen, size position is width (X, Left to Right) then height (Y, Top to Bottom)
screenX = 1920
screenY = 1080
screen = pygame.display.set_mode((screenX, screenY))
clock = pygame.time.Clock()

############################################################
# Title and Icon
pygame.display.set_caption("Alien Invaders from the Universe")
icon = pygame.image.load('Game Assets/Ship.png')
pygame.display.set_icon(icon)

############################################################
# Image assets
playerimg = pygame.image.load('Game Assets/Ship.png')
alienimg = pygame.image.load('Game Assets/Alien.png')
shopbackground = pygame.image.load('Game Assets/Shopbackground.png').convert()
powerup_threeshot = [
    pygame.image.load('Game Assets/Threeshot_power1.png').convert_alpha(),
    pygame.image.load('Game Assets/Threeshot_power2.png').convert_alpha()
]


############################################################
# Audio Assets
startgun = pygame.mixer.Sound('AudioAssets/Starter.mp3')
tripleshot = pygame.mixer.Sound('AudioAssets/tripleshot.wav')
gattling = pygame.mixer.Sound('AudioAssets/GatlingLaser.wav')
cannon = pygame.mixer.Sound('AudioAssets/CannonShot.wav')

############################################################
# Setting a set pixel size for assets
iconX = 64
iconY = 64

############################################################
# Powerup Configs

powerup_rect = powerup_threeshot[0].get_rect(
    topleft=(random.randint(50, screenX - 50), random.randint(350, screenY -50))) # forced second randint to spawn orb in the bottom half of map

# --- Variables for effects ---
rotation_angle = 0
flash_frame = 0
flash_timer = 0
flash_speed = 250  # milliseconds between flashes
float_amplitude = 5

############################################################
# Player Configs

# Positioning of the player
playerX = screenX / 2
playerY = screenY 
player_speed = 3

############################################################
# Shooting configs

bullet_rect = None
bullet_active = False
bullet_speed = 500

bullets = []
bullet_cooldown = 200
last_shot_time = 0

############################################################
# Shop Inventory
purchased = False
player_money = 0
booster = False
boosterspeed = 10
gat_gun = (bullet_speed + 100), (bullet_cooldown - 100)

############################################################
# Player Health Config, might change to a higher number instead of single lives. RPG style
player_lives = 3
font = pygame.font.Font(None, 36)

############################################################
# Alien Configs

alien_speed = 10
aliens = [] # Empty list to check how many NPCs left



############################################################
# Powerup configs
multi_shot_enabled = False

powerup_active = False
powerup_collected = False
powerup_timer = 0
powerup_duration = 5000 # 5 seconds / 5000 miliseconds
powerup_respawn_timer = 0
powerup_respawn_delay = 8000

############################################################
# Enemy Wave code
game_state = "playing"
level = 1
alien_direction = 1
EDGE_BUFFER = 5 # Amount of Pixels
DROP_AMOUNT = 60

############################################################
# Heart Health *animation* asset.
heart1 = pygame.image.load("Game Assets/Heart1.png").convert_alpha()
heart2 = pygame.image.load("Game Assets/Heart2.png").convert_alpha()

heart_images = [heart1, heart2]
heart_frame = 0
heart_animation_timer = 0
heart_animation_speed = 250

############################################################

# Functions
def player(x, y): # Function that tells the code where character should spawn/ be drawn
    screen.blit(playerimg, (x, y))

def spawn_aliens(level): 
    global aliens, alien_speed, bullets, aliens_this_wave
    bullets = []
    aliens = []
    rows = min(5, 0 + level)  
    cols = min(10, 10 + level)

    vertical_padding = 50
    alien_width = alienimg.get_width()
    alien_height = alienimg.get_height()

    total_width = cols * alien_width + (cols - 1) * 20
    start_x = (screenX - total_width) // 2
    start_y = vertical_padding

    for row in range(rows):
        for col in range(cols):
            x = start_x + col * (alien_width + 20)
            y = start_y + row * (alien_height + 20)
            alien_rect = alienimg.get_rect(topleft=(x, y))
            aliens.append({
                "rect": alien_rect, 
                "just_spawned": True,
                "independent": False,
                "x_speed": 0,
                "y_speed": 0,
                "swarm_id": None
                })
            
    alien_speed = 5 + (level * 0.3)

    aliens_this_wave = len(aliens)  # Holds quantity of aliens in variable to cash out      

spawn_aliens(level)

############################################################
#######----------------Main Loop Code----------------#######
############################################################

# Game Loop to make sure the window is running/working with all game assets
running = True
while running:
    
############################################################ [Put new code underneath these configs to make things work] ############################################################
    # Required Configs

    player_rect = pygame.Rect(playerX, playerY, iconX, iconY) # Creating Collision box for Player
    dt = clock.tick(60) / 1000 # Using clock to make sure the game is running properly on a certain amount of FPS
    screen.fill('black') #Creates the background colour
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

############################################################
    # Player boundary
    playerX = max(0, min(playerX, screenX - iconX))
    playerY = max(450, min(playerY, screenY - iconY))

############################################################
    # Player Shop THIS IS WAY TOO FUCKING CHUNKY for 1 speed upgrade, need to compress it somehow.
    def player_shop(message="Press 'H' for a permanent speed boost: $100"):
        global booster, player_money, purchased
        font = pygame.font.Font(None, 50)

        # Texts
        shop_text = font.render(message, True, (255, 255, 255))
        shop_rect = shop_text.get_rect(center=(screenX//2, screenY//2))
        enough_credit = font.render("Thanks for purchasing!", True, (255, 255, 255))
        not_enough_credit = font.render("Not enough credits!", True, (255, 255, 255))
        already_bought = font.render("Upgrade already purchased!", True, (255, 255, 255))
        confirm_text = font.render("Are you sure? Y/N", True, (255, 255, 255))
        confirm_rect = confirm_text.get_rect(center=(screenX//2, screenY//2 + 50))

        paused = True
        while paused:
            # Draw background
            screen.blit(shopbackground, (0, 0))
            screen.blit(shop_text, shop_rect)
            money_text = font.render(f"CREDITS: {player_money}", True, (255, 255, 255))
            screen.blit(money_text, (15, 127))
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_h:
                        if purchased:
                            screen.blit(already_bought, (screenX//2 - already_bought.get_width()//2, screenY//2 + 100))
                            pygame.display.flip()
                            pygame.time.delay(1000)
                            paused = False
                        elif player_money < 100:
                            screen.blit(not_enough_credit, (screenX//2 - not_enough_credit.get_width()//2, screenY//2 + 100))
                            pygame.display.flip()
                            pygame.time.delay(1000)
                            paused = False
                        else:
                            # Show confirmation
                            screen.blit(confirm_text, confirm_rect)
                            pygame.display.flip()

                            confirming = True
                            while confirming:
                                for evt in pygame.event.get():
                                    if evt.type == pygame.QUIT:
                                        pygame.quit()
                                        exit()
                                    elif evt.type == pygame.KEYDOWN:
                                        if evt.key == pygame.K_y:
                                            # Player confirmed purchase
                                            booster = True
                                            player_money -= 100
                                            purchased = True
                                            screen.blit(enough_credit, (screenX//2 - enough_credit.get_width()//2, screenY//2 + 100))
                                            pygame.display.flip()
                                            pygame.time.delay(1000)
                                            confirming = False
                                            paused = False
                                        elif evt.key == pygame.K_n:
                                            # Player canceled purchase
                                            confirming = False
                                            paused = False 

############################################################
    # Pause Screen configs

    def show_pause_screen(message="Wave Cleared! Press 'C' to Continue, 'S' to Shop or 'Q' to Quit game"):
        global playerX, playerY, running, game_state, level
        paused = True
        font = pygame.font.Font(None, 50)  # Bigger font for visibility

        while paused:
            screen.fill((0, 0, 0))  # Black background
            text = font.render(message, True, (255, 255, 255))  # White text
            text_rect = text.get_rect(center=(screenX//2, screenY//2))
            screen.blit(text, text_rect)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_c:  # Continue
                        level += 1
                        spawn_aliens(level)
                        playerX = screenX // 2 - iconX // 2
                        playerY = screenY
                        game_state = "playing"
                        paused = False
                    elif event.key == pygame.K_s:
                        player_shop()
                    elif event.key == pygame.K_q:
                        running = False
                        paused = False

############################################################
    # Levels/Waves/Currency config
    if game_state == "playing" and len(aliens) == 0:
        player_money += aliens_this_wave * 10 # Currency System, x1 alien = 10 Gold
        game_state = "Wave_cleared"
        show_pause_screen()

############################################################
    # Heart Animation:
    heart_animation_timer += dt * 1000
    if heart_animation_timer >= heart_animation_speed:
        heart_animation_timer = 0
        heart_frame = (heart_frame + 1) % len(heart_images)
    for i in range(player_lives):
        screen.blit(heart_images[heart_frame], (10 + i * 40, 40))

############################################################ 
    # Movement for player based on Keys pressed W,A,S,D/Up,Left,Down,Right or arrow keys, might change to mouse position in future.
    keys = pygame.key.get_pressed()
    if booster == True:
        player_speed = boosterspeed

    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        playerX -= player_speed
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        playerX += player_speed
    if keys[pygame.K_UP] or keys[pygame.K_w]:
        playerY -= player_speed
    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
        playerY += player_speed
    if keys[pygame.K_ESCAPE]:
        show_pause_screen()

############################################################
    # Alien movement code, hits edge, moves down by 10 pixels, moves opposite direction.

############################################################
# Alien movement code, hits edge, moves down by 10 pixels, moves opposite direction.

    hit_edge = False
    for alien in aliens:
        rect = alien["rect"]

        if not alien["independent"]:  
            # Formation movement
            rect.x += alien_speed * alien_direction * dt * 60

            if rect.left < EDGE_BUFFER:
                rect.left = EDGE_BUFFER
                hit_edge = True
            elif rect.right > screenX - EDGE_BUFFER:
                rect.right = screenX - EDGE_BUFFER
                hit_edge = True

            # If alien passes player → break off and move independently
            if rect.top > playerY:
                alien["independent"] = True
                alien["x_speed"] = random.choice([-2, -1, 1, 2])
                alien["y_speed"] = random.randint(1, 3)
                alien["swarm_id"] = id(alien)

        else:
            # If in a swarm, follow swarm leader
            if alien["swarm_id"] is not None:
                leader = next(a for a in aliens if a["swarm_id"] == alien["swarm_id"])
                rect.x += leader["x_speed"]
                rect.y += leader["y_speed"]
            else:
                rect.x += alien["x_speed"]
                rect.y += alien["y_speed"]

            # Bounce edges for independent aliens
            if rect.left < 0 or rect.right > screenX:
                alien["x_speed"] *= -1

            # Reset if they hit bottom
            if rect.bottom >= screenY:
                alien["independent"] = False
                alien["swarm_id"] = None
                alien["x_speed"] = 0
                alien["y_speed"] = 0
                rect.y = 0  # Respawn at top

    # Check for edge collisions (for swarm movement in formation)
    if rect.right >= screenX - EDGE_BUFFER or rect.left <= EDGE_BUFFER:
        hit_edge = True

    if hit_edge:
        alien_direction *= -1
        for alien in aliens:
            if not alien["independent"]:
                alien["rect"].y += DROP_AMOUNT

    # Remove spawn protection after first frame
    for alien in aliens:
        if alien["just_spawned"] and alien["rect"].top > 50:
            alien["just_spawned"] = False

    def swarm():# --- Swarm merge check --- I've turned this into a stand alone function so I don't have to comment out a huge chunk of code
        for i, alien1 in enumerate(aliens):
            if alien1["independent"]:
                for alien2 in aliens[i+1:]:
                    if alien2["independent"] and alien1["rect"].colliderect(alien2["rect"]):
                        swarm_id = alien1["swarm_id"] or alien2["swarm_id"] or id(alien1)
                        alien1["swarm_id"] = swarm_id
                        alien2["swarm_id"] = swarm_id
                        alien2["x_speed"] = alien1["x_speed"]
                        alien2["y_speed"] = alien1["y_speed"]

    # Draw aliens
    for alien in aliens:
        screen.blit(alienimg, alien["rect"])

############################################################
    # Code for threeshot powerup animation, collection and respawn // --> Might become redunant once the upgrade shop becomes available.

    if player_rect.colliderect(powerup_rect) and not powerup_active:
        multi_shot_enabled = True
        powerup_active = True
        powerup_timer = 0
        powerup_collected = True

    if powerup_active:
        powerup_timer += dt * 1000
        current_duration = powerup_duration

        if level >= 7:
            current_duration = 10000

        if powerup_timer >= powerup_duration:
            multi_shot_enabled = False
            powerup_active = False

    if powerup_collected and not powerup_active:
        powerup_respawn_timer += dt * 1000
        if powerup_respawn_timer >= powerup_respawn_delay:
            powerup_rect.topleft = (random.randint(50, screenX -50), 
                                    random.randint(screenY // 2, screenY - 50)
                                    )
            powerup_collected = False
            powerup_respawn_timer = 0
    
    if not powerup_collected:
        current_img = powerup_threeshot[flash_frame]
    # Update flash
        flash_timer += dt * 1000
        if flash_timer >= flash_speed:
            flash_timer = 0
            flash_frame = (flash_frame + 1) % len(powerup_threeshot)

        # Floating animation
        float_offset = math.sin(pygame.time.get_ticks() * 0.005) * float_amplitude
        powerup_draw_rect = current_img.get_rect(center=powerup_rect.center) 
        powerup_draw_rect.y += float_offset
    
        screen.blit(current_img, powerup_draw_rect)   

############################################################
    # Shooting Mechanics/ Fire bullet
    
    current_time = pygame.time.get_ticks()

    if keys[pygame.K_SPACE] and current_time - last_shot_time > bullet_cooldown:
        last_shot_time = current_time
        
        if multi_shot_enabled:
        # Fire 3 bullets: center, left, right
            tripleshot.play()
            bullet1 = pygame.Rect(player_rect.centerx - 2, player_rect.top - 10, 4, 10)
            bullet2 = pygame.Rect(player_rect.centerx - 17, player_rect.top - 10, 4, 10)
            bullet3 = pygame.Rect(player_rect.centerx + 13, player_rect.top - 10, 4, 10)
            bullets.extend([bullet1, bullet2, bullet3])
        else:
        # Single bullet
            startgun.play()
            bullet = pygame.Rect(player_rect.centerx - 2, player_rect.top - 10, 4, 10)
            bullets.append(bullet)

    # Move bullet if active
    for bullet in bullets[:]:
        bullet.y -= bullet_speed * dt
        pygame.draw.rect(screen, (255, 255, 0), bullet)

        if bullet.bottom < 0:
            bullets.remove(bullet)
        else:
            for alien in aliens[:]:
                if bullet.colliderect(alien["rect"]):
                    aliens.remove(alien)
                    bullets.remove(bullet)
                    break

############################################################
    # Player collision with aliens/entities
    for alien in aliens[:]:
        if player_rect.colliderect(alien["rect"]):
            player_lives -= 1
            aliens.remove(alien)  # remove alien that hit player
            if player_lives <= 0:
                running = False

############################################################                
    # Render lives
    lives_text = font.render(f"LIVES:", True, (255, 255, 255))
    levels_text = font.render(f"LEVEL: {level} ", True, (255, 255, 255))
    money_text = font.render(f"CREDITS: {player_money} ", True, (255, 255, 255))
    screen.blit(lives_text, (40, 57))
    screen.blit(levels_text, (screenX - levels_text.get_width() - 10, 17))
    screen.blit(money_text, (15, 127))

    if level >= 11:
        running = False

############################################################

    player(playerX, playerY)
    pygame.display.flip()       
