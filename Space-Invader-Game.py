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
icon = pygame.image.load('Game Assets/Slime.png')
pygame.display.set_icon(icon)

# Player images
playerimg = pygame.image.load('Game Assets/Slime.png')
alienimg = pygame.image.load('Game Assets/Alien.png')

# Scaling image size as it's over 64x64
img_width = 64
img_height = 64
img_size = (img_width, img_height)
img_scaled = pygame.transform.scale(playerimg, img_size)

# Positioning of the player icon at first boot up
playerX = 370
playerY = 480

# Positioning of the Alien icon at boot up.
aliens_rect = alienimg.get_rect(topleft= (100, 50))
 
# Allows for movement code to know how big your image/icon really is.
iconX = 64
iconY = 64

# player's speed movement.
player_speed = 2.5
alien_speed = 3

# Function is created using .blit() to draw player/alien images on top of window.
def player(x, y):
    screen.blit(img_scaled, (x, y))

# Game Loop to make sure the window is running/working with all game assets
running = True
while running:
    dt = clock.tick(60) / 1000
    # RGB - Red, Green, Blue
    screen.fill((0, 150, 255)) #Creates the background colour
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Movement for player based on Keys pressed W,A,S,D/Up,Left,Down,Right
    keys = pygame.key.get_pressed()

    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        playerX -= player_speed
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        playerX += player_speed
    if keys[pygame.K_UP] or keys[pygame.K_w]:
        playerY -= player_speed
    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
        playerY += player_speed
    
    # Automated script for Alien movement
    aliens_rect.x += alien_speed * dt * 100
    if aliens_rect.right >= screenX or aliens_rect.left <= 0:
        alien_speed = -alien_speed
        aliens_rect.y += 5

    playerX = max(0, min(playerX, screenX - iconX))
    playerY = max(350, min(playerY, screenY - iconY))
    screen.blit(alienimg, aliens_rect) 
    player(playerX, playerY)
    pygame.display.flip()
