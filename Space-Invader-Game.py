import pygame
import random
import math

pygame.init()
pygame.mixer.init()

screenX = 1920
screenY = 1080
screen = pygame.display.set_mode((screenX, screenY))
clock = pygame.time.Clock()


pygame.display.set_caption("Alien Invaders from the Universe")
icon = pygame.image.load('Game Assets\Ship.png')
pygame.display.set_icon(icon)

player_img = pygame.image.load('Game Assets/Ship.png')
alien_img = pygame.image.load('Game Assets/Alien.png')
shop_background = pygame.image.load('Game Assets/Shop_background.png').convert()
power_up_three_shot = [
    pygame.image.load('Game Assets/Three_shot_power1.png').convert_alpha(),
    pygame.image.load('Game Assets/Three_shot_power2.png').convert_alpha()]

start_gun = pygame.mixer.Sound('AudioAssets/Starter.mp3')
triple_shot = pygame.mixer.Sound('AudioAssets/triple_shot.wav')
gatling = pygame.mixer.Sound('AudioAssets/GatlingLaser.wav')
cannon = pygame.mixer.Sound('AudioAssets/CannonShot.wav')

iconX = 64
iconY = 64

power_up_rect = power_up_three_shot[0].get_rect(
    topleft=(random.randint(50, screenX - 50), random.randint(350, screenY -50))) # forced second randint to spawn orb in the bottom half of map

rotation_angle = 0
flash_frame = 0
flash_timer = 0
flash_speed = 250  
float_amplitude = 5

playerX = screenX / 2
playerY = screenY 
player_speed = 3

bullet_speed = 500
bullet_cool_down = 200

bullets = []
last_shot_time = 0
bullet_rect = None
bullet_active = False

purchased = False
player_money = 0
booster = False
booster_speed = 10
gat_gun = (bullet_speed + 100), (bullet_cool_down - 100)
upgrades = {
    "H": {  # Key to trigger the upgrade
        "name": "Permanent Speed Boost",
        "cost": 100,
        "effect": lambda: globals().update(booster=True)
    },
}

player_lives = 3
font = pygame.font.Font(None, 36)

alien_speed = 10
aliens = [] 

multi_shot_enabled = False

power_up_active = False
power_up_collected = False
power_up_timer = 0
power_up_duration = 5000 
power_up_respawn_timer = 0
power_up_respawn_delay = 8000

game_state = "playing"
level = 1
alien_direction = 1
EDGE_BUFFER = 5
DROP_AMOUNT = 60

heart1 = pygame.image.load("Game Assets/heart1.png").convert_alpha()
heart2 = pygame.image.load("Game Assets/heart2.png").convert_alpha()

heart_images = [heart1, heart2]
heart_frame = 0
heart_animation_timer = 0
heart_animation_speed = 250

def player_shop():
    global player_money
    paused = True
    font = pygame.font.Font(None, 50)

    while paused:
        screen.blit(shop_background, (0, 0))

        y_offset = 200
        for key, upgrade in upgrades.items():
            text = font.render(f"Press '{key}' to buy {upgrade['name']}: {upgrade['cost']} Credits", True, (255, 255, 255))
            screen.blit(text, (screenX // 2 - text.get_width() // 2, y_offset))
            y_offset += 70

        money_text = font.render(f"CREDITS: {player_money}", True, (255, 255, 255))
        screen.blit(money_text, (15, 127))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                key_pressed = pygame.key.name(event.key).upper()

                if key_pressed in upgrades:
                    upgrade = upgrades[key_pressed]
                    if player_money >= upgrade["cost"]:
                        player_money -= upgrade["cost"]
                        upgrade["effect"]()
                        show_message(f"Purchased {upgrade['name']}!") 
                        pygame.time.delay(1000) 
                        paused = False
                    else:
                        show_message("Not enough credits")

                elif event.key == pygame.K_ESCAPE:
                    paused = False 

def show_message(text, duration=1000):
    font = pygame.font.Font(None, 50)
    msg_surface = font.render(text, True, (255, 255, 255))
    msg_rect = msg_surface.get_rect(center=(screenX//2, screenY//2))
    screen.blit(msg_surface, msg_rect)
    pygame.display.flip()
    pygame.time.delay(duration)

def player(x, y): 
    screen.blit(player_img, (x, y))

def spawn_aliens(level): 
    global aliens, alien_speed, bullets, aliens_this_wave
    bullets = []
    aliens = []
    rows = min(5, 0 + level)  
    cols = min(10, 10 + level)

    vertical_padding = 50
    alien_width = alien_img.get_width()
    alien_height = alien_img.get_height()

    total_width = cols * alien_width + (cols - 1) * 20
    start_x = (screenX - total_width) // 2
    start_y = vertical_padding

    for row in range(rows):
        for col in range(cols):
            x = start_x + col * (alien_width + 20)
            y = start_y + row * (alien_height + 20)
            alien_rect = alien_img.get_rect(topleft=(x, y))
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

running = True
while running:
    player_rect = pygame.Rect(playerX, playerY, iconX, iconY) # Creating Collision box for Player
    dt = clock.tick(60) / 1000 # Using clock to make sure the game is running properly on a certain amount of FPS
    screen.fill('black') #Creates the background colour
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    playerX = max(0, min(playerX, screenX - iconX))
    playerY = max(450, min(playerY, screenY - iconY))

    def show_pause_screen(message="Wave Cleared! Press 'C' to Continue, 'S' to Shop or 'Q' to Quit game"):
        global playerX, playerY, running, game_state, level
        paused = True
        font = pygame.font.Font(None, 50)  

        while paused:
            screen.fill((0, 0, 0))  
            text = font.render(message, True, (255, 255, 255)) 
            text_rect = text.get_rect(center=(screenX//2, screenY//2))
            screen.blit(text, text_rect)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_c: 
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

    if game_state == "playing" and len(aliens) == 0:
        player_money += aliens_this_wave * 10 
        game_state = "Wave_cleared"
        show_pause_screen()

    heart_animation_timer += dt * 1000
    if heart_animation_timer >= heart_animation_speed:
        heart_animation_timer = 0
        heart_frame = (heart_frame + 1) % len(heart_images)
    for i in range(player_lives):
        screen.blit(heart_images[heart_frame], (10 + i * 40, 40))

    keys = pygame.key.get_pressed()
    if booster == True:
        player_speed = booster_speed

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

    hit_edge = False
    for alien in aliens:
        rect = alien["rect"]

        if not alien["independent"]:  
            rect.x += alien_speed * alien_direction * dt * 60

            if rect.left < EDGE_BUFFER:
                rect.left = EDGE_BUFFER
                hit_edge = True
            elif rect.right > screenX - EDGE_BUFFER:
                rect.right = screenX - EDGE_BUFFER
                hit_edge = True

            if rect.top > playerY:
                alien["independent"] = True
                alien["x_speed"] = random.choice([-2, -1, 1, 2])
                alien["y_speed"] = random.randint(1, 3)
                alien["swarm_id"] = id(alien)

        else:
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
                rect.y = 0

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
        screen.blit(alien_img, alien["rect"])

    if player_rect.colliderect(power_up_rect) and not power_up_active:
        multi_shot_enabled = True
        power_up_active = True
        power_up_timer = 0
        power_up_collected = True

    if power_up_active:
        power_up_timer += dt * 1000
        current_duration = power_up_duration

        if level >= 7:
            current_duration = 10000

        if power_up_timer >= power_up_duration:
            multi_shot_enabled = False
            power_up_active = False

    if power_up_collected and not power_up_active:
        power_up_respawn_timer += dt * 1000
        if power_up_respawn_timer >= power_up_respawn_delay:
            power_up_rect.topleft = (random.randint(50, screenX -50), 
                                    random.randint(screenY // 2, screenY - 50)
                                    )
            power_up_collected = False
            power_up_respawn_timer = 0
    
    if not power_up_collected:
        current_img = power_up_three_shot[flash_frame]
    # Update flash
        flash_timer += dt * 1000
        if flash_timer >= flash_speed:
            flash_timer = 0
            flash_frame = (flash_frame + 1) % len(power_up_three_shot)

        # Floating animation
        float_offset = math.sin(pygame.time.get_ticks() * 0.005) * float_amplitude
        powerup_draw_rect = current_img.get_rect(center=power_up_rect.center) 
        powerup_draw_rect.y += float_offset
    
        screen.blit(current_img, powerup_draw_rect)   

############################################################
    # Shooting Mechanics/ Fire bullet
    
    current_time = pygame.time.get_ticks()

    if keys[pygame.K_SPACE] and current_time - last_shot_time > bullet_cool_down:
        last_shot_time = current_time
        
        if multi_shot_enabled:
        # Fire 3 bullets: center, left, right
            triple_shot.play() # Audio file
            bullet1 = pygame.Rect(player_rect.centerx - 2, player_rect.top - 10, 4, 10)
            bullet2 = pygame.Rect(player_rect.centerx - 17, player_rect.top - 10, 4, 10)
            bullet3 = pygame.Rect(player_rect.centerx + 13, player_rect.top - 10, 4, 10)
            bullets.extend([bullet1, bullet2, bullet3])
        else:
        # Single bullet, basic beginner.
            start_gun.play()
            bullet = pygame.Rect(player_rect.centerx - 2, player_rect.top - 10, 4, 10)
            bullets.append(bullet)

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

    for alien in aliens[:]:
        if player_rect.colliderect(alien["rect"]):
            player_lives -= 1
            aliens.remove(alien) 
            if player_lives <= 0:
                running = False

    lives_text = font.render(f"LIVES:", True, (255, 255, 255))
    levels_text = font.render(f"LEVEL: {level} ", True, (255, 255, 255))
    money_text = font.render(f"CREDITS: {player_money} ", True, (255, 255, 255))
    screen.blit(lives_text, (40, 57))
    screen.blit(levels_text, (screenX - levels_text.get_width() - 10, 17))
    screen.blit(money_text, (15, 127))

    if level >= 11:
        running = False

    player(playerX, playerY)
    pygame.display.flip()      
