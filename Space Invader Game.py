import pygame
import random

# Initialize the pygame module
pygame.init()

# Creates the display/screen, size position is width (X) then height (Y)
screenX = 800
screenY = 600
screen = pygame.display.set_mode((screenX, screenY))

# Title and Icon
pygame.display.set_caption("Slime Invaders")
icon = pygame.image.load('Game Assets\Slime.png')
pygame.display.set_icon(icon)

# Player images
playerimg = pygame.image.load('Game Assets\Slime.png')
alienimg = pygame.image.load('Game Assets\Alien.png')
# Scaling image size as it's over 64x64
img_width = 64
img_height = 64
img_size = (img_width, img_height)
img_scaled = pygame.transform.scale(playerimg, img_size)

# Positioning of the player icon at first boot up
playerX = 370
playerY = 480
# Positioning of the Alien icon, will be randomized at death or boot up.
alienX = random.randint(0, 800)
alienY = random.randint(50, 150) 

# Allows for movement code to know how big your image/icon really is.
iconX = 64
iconY = 64
# player's speed movement.
player_speed = 0.1
alien_speed = 0.3

# Collision detection
enemy_rect = pygame.Rect(alienX, alienY, screenX, screenY)
wall_rect = pygame.Rect(screenX, screenY, 64, 64)

# Self-Reminder, X is left & right, Y is up & down.

# Function is created using .blit() to draw player/alien images on top of window.
def player(x, y):
    screen.blit(img_scaled, (x, y))
def alien(x, y):
    screen.blit(alienimg, (x, y))    


# Game Loop to make sure the window is running/working with all game assets
running = True
while running:
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
    alienX.x =+ alien_speed
    if alienX.right >= 600 or alienX.left <= 0:
        alien_speed = -alien_speed #reverses direction
        alien




# Creating Player boundaries so they don't go off screen.
    playerX = max(0, min(playerX, screenX - iconX))
    playerY = max(350, min(playerY, screenY - iconY))
    alienX = max(0, min(alienX, screenX - iconX))
    alienY = max(50, min(alienY, screenY - iconY))



    player(playerX, playerY)
    alien(alienX, alienY)
    pygame.display.flip()