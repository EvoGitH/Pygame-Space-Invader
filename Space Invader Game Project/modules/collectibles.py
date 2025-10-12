import pygame, random, math

class Collectible:
    """Handles individual collectible animation and drawing."""

    def __init__(self, info, name, images, rect, speed=150, amplitude=5):
        self.name = name
        self.images = images
        self.rect = rect
        self.collected = False
        self.frame = 0
        self.timer = 0
        self.speed = speed
        self.amplitude = amplitude
        self.respawn_timer = 0
        self.info = info

    def update(self, dt):
        """Updates animation and respawn timers."""

        if self.collected:
            self.respawn_timer += dt * 1000
            if self.respawn_timer >= 5000:
                self.rect.topleft = (
                    random.randint(50, self.info.screenX - 50),
                    random.randint(self.info.screenY // 2, self.info.screenY - 50)
                )
                self.collected = False
                self.respawn_timer = 0
        else:
            self.timer += dt * 1000
            if self.timer >= self.speed:
                self.timer = 0
                self.frame = (self.frame + 1) % len(self.images)

    def draw(self, screen):
        """Draw the collectible on screen with floating effect."""

        if self.collected:
            return
        float_offset = math.sin(pygame.time.get_ticks() * 0.005) * self.amplitude
        draw_rect = self.images[self.frame].get_rect(center=self.rect.center)
        draw_rect.y += float_offset
        screen.blit(self.images[self.frame], draw_rect)