import pygame
import random
import math

# Initialize the pygame module
pygame.init()

############################################################
# Creates the display/screen, size position is width (X, Left to Right) then height (Y, Top to Bottom)
screenX = 1820
screenY = 980
screen = pygame.display.set_mode((screenX, screenY))
clock = pygame.time.Clock()

############################################################
# Title and Icon
pygame.display.set_caption("Alien Invaders from the Universe")
icon = pygame.image.load('Game Assets\Ship.png')
pygame.display.set_icon(icon)

############################################################
# Image assets
playerimg = pygame.image.load('Game Assets/Ship.png')
alienimg = pygame.image.load('Game Assets/Alien.png')
powerup_threeshot = [
    pygame.image.load('Game Assets/Threeshot_power1.png').convert_alpha(),
    pygame.image.load('Game Assets/Threeshot_power2.png').convert_alpha()
]

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
# player's speed movement.
player_speed = 7
# player lives
player_lives = 3
font = pygame.font.Font(None, 36)

############################################################
# Alien Configs

alien_speed = 15
# Creation of multiple enemies
aliens = []
for i in range(5): 
    alien_rect = alienimg.get_rect(topleft=(i * 100, 50))
    alien = {
        "rect": alien_rect,
        "just_spawned": True
    }
    aliens.append(alien)

############################################################
# Shooting configs

bullet_rect = None
bullet_active = False
bullet_speed = 600

bullets = []
bullet_cooldown = 200
last_shot_time = 0
multi_shot_enabled = True

############################################################
# Enemy Wave code
game_state = "playing"
level = 1
alien_direction = 1
EDGE_BUFFER = 5 # Amount of Pixels
DROP_AMOUNT = 30

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
    global aliens, alien_speed, bullets
    bullets = []
    aliens = []
    rows = min(5, 2 + level)   # increase rows up to 3 #Change this number to update the minimum rows.
    cols = min(10, 3 + level)  # increase columns up to 5 #Change this number to update the minimum columns.

    vertical_padding = 50
    alien_width = alienimg.get_width()
    alien_height = alienimg.get_width()

    total_width = cols * alien_width + (cols - 1) * 20
    start_x = (screenX - total_width) // 2
    start_y = vertical_padding

    for row in range(rows):
        for col in range(cols):
            x = start_x + col * (alien_width)
            y = start_y + row * (alien_height)
            alien_rect = alienimg.get_rect(topleft=(x, y))
            aliens.append({"rect": alien_rect, "just_spawned": True})

    alien_speed = alien_speed * (1 + level * 0.1)  # increase speed, 10% faster per level.

############################################################
#######----------------Main Loop Code----------------#######
############################################################

# Game Loop to make sure the window is running/working with all game assets
running = True
while running:
    
############################################################ [Put new code underneath these configs to make things work] ############################################################
    # Required Configs

    player_rect = pygame.Rect(playerX, playerY, iconX, iconY) # Creating Collision detection between Alien & Player
    dt = clock.tick(60) / 1000 # Using clock to make sure the game is running properly on a certain amount of FPS
    screen.fill('black') #Creates the background colour
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

############################################################
    # Pause Screen configs

    def show_pause_screen(message="Wave Cleared! Press C to Continue or Q to Quit"):
        global playerX, playerY, running
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
                        playerX = screenX // 2 - iconX // 2
                        playerY = screenY
                        paused = False
                    elif event.key == pygame.K_q:
                        running = False
                        paused = False

############################################################
    # Levels/Waves config

    if game_state == "playing":
        if len(aliens) == 0:
            game_state = "Wave_Cleared"
            show_pause_screen()

    elif game_state == "Wave_Cleared":
        wave_text = font.render(f"Wave {level} CLeared!", True, (255, 255, 255))
        continue_text = font.render("Please C to Continue", True, (255, 255, 255))
        screen.blit(wave_text, (screenX//2 - wave_text.get_width()//2, screenY//2 - 50))
        screen.blit(continue_text, (screenX//2 - continue_text.get_width()//2, screenY//2 + 10))

        keys = pygame.key.get_pressed()
        if keys[pygame.K_c]:
            level += 1
            spawn_aliens(level)
            game_state = "playing"

############################################################
    # Code for threeshot powerup // Might become redunant once the upgrade shop becomes available.

    current_img = powerup_threeshot[flash_frame]
    # Update flash
    flash_timer += dt
    if flash_timer >= flash_speed:
        flash_timer = 0
        flash_frame = (flash_frame + 1) % len(powerup_threeshot)

    rotated_img = pygame.transform.rotate(current_img, rotation_angle)
    rotated_rect = rotated_img.get_rect(center=powerup_rect.center)
    # Floating animation
    float_offset = math.sin(pygame.time.get_ticks() * 0.005) * float_amplitude
    rotated_rect.y += float_offset

    screen.blit(rotated_img, rotated_rect)

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

    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        playerX -= player_speed
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        playerX += player_speed
    if keys[pygame.K_UP] or keys[pygame.K_w]:
        playerY -= player_speed
    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
        playerY += player_speed

############################################################
    # Alien movement code, hits edge, moves down by 10 pixels, moves opposite direction.

    hit_edge = False
    for alien in aliens:
        rect = alien["rect"]
        rect.x += alien_speed * alien_direction * dt * 60

        if rect.left < EDGE_BUFFER:
            rect.left = EDGE_BUFFER
            hit_edge = True
        elif rect.right > screenX - EDGE_BUFFER:
            rect.right = screenX - EDGE_BUFFER
            hit_edge = True

    # Check for edge collisions
    if rect.right >= screenX - EDGE_BUFFER or rect.left <= EDGE_BUFFER:
        hit_edge = True

    # Flip direction once if any alien hit an edge
    if hit_edge:
        alien_direction *= -1
        for alien in aliens:
            alien["rect"].y += DROP_AMOUNT

    # Remove spawn protection after first frame
    for alien in aliens:
        if alien["just_spawned"] and alien["rect"].top > 50:
            alien["just_spawned"] = False

    # Draw aliens
    for alien in aliens:
        screen.blit(alienimg, alien["rect"])

############################################################
    # Player boundary
    playerX = max(0, min(playerX, screenX - iconX))
    playerY = max(450, min(playerY, screenY - iconY))

############################################################
    # Shooting Mechanics/ Fire bullet
    
    current_time = pygame.time.get_ticks()

    if keys[pygame.K_SPACE] and current_time - last_shot_time > bullet_cooldown:
        last_shot_time = current_time

        if multi_shot_enabled:
        # Fire 3 bullets: center, left, right
            bullet1 = pygame.Rect(player_rect.centerx - 2, player_rect.top - 10, 4, 10)
            bullet2 = pygame.Rect(player_rect.centerx - 17, player_rect.top - 10, 4, 10)
            bullet3 = pygame.Rect(player_rect.centerx + 13, player_rect.top - 10, 4, 10)
            bullets.extend([bullet1, bullet2, bullet3])
        else:
        # Single bullet
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
    # Player collision with aliens
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
    screen.blit(lives_text, (40, 17))
    screen.blit(levels_text, (screenX - levels_text.get_width() - 10, 17))
 
############################################################

    player(playerX, playerY)
    pygame.display.flip()

