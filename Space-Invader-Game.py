import pygame

# Initialize the pygame module
pygame.init()

# Creates the display/screen, size position is width (X) then height (Y)
screenX = 800
screenY = 600
screen = pygame.display.set_mode((screenX, screenY))
clock = pygame.time.Clock()

# Title and Icon
pygame.display.set_caption("Slime Invaders")
icon = pygame.image.load('Game Assets\Slime.png')
pygame.display.set_icon(icon)

# Image assets
playerimg = pygame.image.load('Game Assets\Slime.png')
# Scaling image size as it's over 64x64
img_width = 64
img_height = 64
img_size = (img_width, img_height)
img_scaled = pygame.transform.scale(playerimg, img_size)
alienimg = pygame.image.load('Game Assets\Alien.png')

# Setting a set pixel size for assets
iconX = 64
iconY = 64

############################################################
# Player Configs

# Positioning of the player
playerX = 370
playerY = 480
# player's speed movement.
player_speed = 2.5
# player lives
player_lives = 3
font = pygame.font.Font(None, 36)

############################################################
# Alien Configs

# Alien's speed
alien_speed = 10
# Creation of multiple enemies
aliens = []
for i in range(5): # 5 will spawn in random areas. 
    alien_rect = alienimg.get_rect(topleft=(i * 100, 50))  # space them out
    aliens.append(alien_rect)

############################################################

# Shooting configs
bullet_rect = None
bullet_active = False
bullet_speed = 400

############################################################
# Enemy Wave code

game_state = "playing"
level = 1
alien_direction = 1

############################################################

# Function is created using .blit() to draw player images on top of window.
def player(x, y):
    screen.blit(img_scaled, (x, y))

############################################################
#######----------------Main Loop Code----------------#######
############################################################

# Game Loop to make sure the window is running/working with all game assets
running = True
while running:

############################################################
    # Levels/Waves code

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
    # Required Configs

    player_rect = pygame.Rect(playerX, playerY, iconX, iconY) # Creating Collision detection between Alien & Player
    dt = clock.tick(60) / 1000 # Using clock to make sure the game is running properly on a certain amount of FPS
    screen.fill('black') #Creates the background colour

############################################################

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

############################################################    

    # Movement for player based on Keys pressed W,A,S,D/Up,Left,Down,Right or arrow keys.
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

    # Alien movement code, hits edge, moves down by 10 pixels and moves in the opposite direction.

    for alien in aliens:
        alien.x += alien_speed * alien_direction * dt * 60  # move horizontally

    hit_edge = False
    for alien in aliens:
        if alien.right >= screenX:
            hit_edge = True
            alien_direction = -1
            break
        elif alien.left <= 0:
            hit_edge = True
            alien_direction = 1
            break
    if hit_edge:
        for alien in aliens:
            alien.y += 20  # drop


    for alien in aliens:
        screen.blit(alienimg, alien)

############################################################
# Alien spawning mechanic after pressing "c" to continue.

    def spawn_aliens(level): 
        global aliens, alien_speed
        aliens = []
        rows = min(3, 2 + level)   # increase rows up to 3
        cols = min(5, 3 + level)  # increase columns up to 5
        for row in range(rows):
            for col in range(cols):
                alien_rect = alienimg.get_rect(topleft=(col*70, 50 + row*50))
                aliens.append(alien_rect)
        alien_speed = 5 * (1 + level * 0.1)  # increase speed, 10% faster per level.

############################################################
    # Pause Screen function

    def show_pause_screen(message="Wave Cleared! Press C to Continue"):
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
                        paused = False

############################################################

    # player boundary
    playerX = max(0, min(playerX, screenX - iconX))
    playerY = max(350, min(playerY, screenY - iconY))

############################################################

    # Shooting Mechanics/ Fire bullet
    if keys[pygame.K_SPACE] and not bullet_active:
        bullet_rect = pygame.Rect(playerX + iconX//2 - 2, playerY, 4, 10)
        bullet_active = True

    # Move bullet if active
    if bullet_active and bullet_rect is not None:
        bullet_rect.y -= bullet_speed * dt
        pygame.draw.rect(screen, (255, 255, 0), bullet_rect)
        # Remove bullet if it goes off-screen
        if bullet_rect.bottom < 0: # Check the bullet where the player is has reached the end.
            bullet_active = False # disables the bullet to make it available to shoot again.
            bullet_rect = None
    # Bullet collision with aliens
    if bullet_active and bullet_rect is not None:
        for alien in aliens[:]:
            if bullet_rect.colliderect(alien):
                bullet_active = False
                bullet_rect = None
                aliens.remove(alien)  # remove alien when hit
                break

############################################################

    # Player collision with aliens
    for alien in aliens[:]:
        if player_rect.colliderect(alien):
            player_lives -= 1
            aliens.remove(alien)  # remove alien that hit player
            if player_lives <= 0:
                running = False

############################################################                

    # Render lives
    lives_text = font.render(f"Lives: {player_lives}", True, (255, 255, 255))
    screen.blit(lives_text, (10, 10))
 
############################################################

    player(playerX, playerY)
    pygame.display.flip()
