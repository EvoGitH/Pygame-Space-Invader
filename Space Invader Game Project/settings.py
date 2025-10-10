import pygame

class Info:
    """ Will hold only basic
    information that is reuseable 
    but mutable for the game here"""

    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.ticks = 0
        self.dt = 0
        self.game_state = "Playing"
        self.level = 1
        self.screenX = 1920
        self.screenY = 1080
        self.iconX = 64
        self.iconY = 64
    
    def update_time(self):
        self.dt = self.clock.tick(60) / 1000
        self.ticks = pygame.time.get_ticks()

    def show_message(self, text, duration=1000):
        font = pygame.font.Font(None, 50)
        msg_surface = font.render(text, True, (255, 255, 255))
        msg_rect = msg_surface.get_rect(center=(self.screenX//2, self.screenY//2))
        self.screen.blit(msg_surface, msg_rect)
        pygame.display.flip()
        pygame.time.delay(duration)

    def pause_screen(self, message):
            font = pygame.font.Font(None, 50)  
            overlay = pygame.Surface((self.screenX, self.screenY), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            text = font.render(message, True, (255, 255, 255)) 
            text_rect = text.get_rect(center=(self.screenX//2, self.screenY//2))
            self.screen.blit(text, text_rect)