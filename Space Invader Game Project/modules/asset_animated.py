import pygame

class animation_images():
    """Display required to be Initialized
    before these images can be converted"""

    hearts_image = [
        pygame.image.load('si_game_assets/animated_images/heart1.png').convert_alpha(), 
        pygame.image.load('si_game_assets/animated_images/heart2.png').convert_alpha()
        ]
    three_shot_image = [
        pygame.image.load('si_game_assets/animated_images/three_shot_power1.png').convert_alpha(), 
        pygame.image.load('si_game_assets/animated_images/three_shot_power2.png').convert_alpha()
        ]
    shield_coin_image = [
        pygame.image.load('si_game_assets/animated_images/shield_coin1.png').convert_alpha(),
        pygame.image.load('si_game_assets/animated_images/shield_coin2.png').convert_alpha()
        ]
    health_coin_image = [
        pygame.image.load('si_game_assets/animated_images/health_coin1.png').convert_alpha(),
        pygame.image.load('si_game_assets/animated_images/health_coin2.png').convert_alpha()
        ]