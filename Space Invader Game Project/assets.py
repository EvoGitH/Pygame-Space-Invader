import pygame
pygame.mixer.init()

class Assets:
    """The 'Assets' class store and 
    loads the collective images, effects 
    and music for the game"""

    # Images
    game_icon = pygame.image.load('si_game_assets/images/ship.png')
    player_image = pygame.image.load('si_game_assets/images/ship.png')
    enemy_image_basic = pygame.image.load('si_game_assets/images/alien_basic.png')
    enemy_image_zigzag = pygame.image.load('si_game_assets/images/alien_zigzag.png')
    enemy_image_tank = pygame.image.load('si_game_assets/images/alien_tank.png')

    background_image = pygame.image.load('si_game_assets/images/shop_background.png')

    side_cannon_image = pygame.image.load('si_game_assets/images/side_cannon.png')

    # Audio effects
    starter_sound = pygame.mixer.Sound('si_game_assets/audio/starter_weapon.mp3')
    triple_sound = pygame.mixer.Sound('si_game_assets/audio/triple_power_up.wav')
    cannon_sound = pygame.mixer.Sound('si_game_assets/audio/cannon_shot.wav')
    gatling_sound = pygame.mixer.Sound('si_game_assets/audio/gatling_laser.wav')
    shield_sound = pygame.mixer.Sound('si_game_assets/audio/shield_energy.wav')
    shield_failed_sound = pygame.mixer.Sound('si_game_assets/audio/shield_failed.wav')