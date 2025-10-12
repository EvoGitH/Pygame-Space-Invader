import pygame

class Button:
    def __init__(self, x, y, width=172, height=71, text="Button", color=(0, 0 ,0), hover_color=(255, 255, 255), action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.action = action

    def draw(self, screen):

        font = pygame.font.Font(None, 30) 

        current_color = self.hover_color if self.rect.collidepoint(pygame.mouse.get_pos()) else self.color
        pygame.draw.rect(screen, current_color, self.rect)

        text_surface = font.render(self.text, True, (255, 255, 255)) 
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: 
            if self.rect.collidepoint(event.pos):
                if self.action:
                    self.action()