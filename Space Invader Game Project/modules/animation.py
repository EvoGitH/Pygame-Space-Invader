import pygame
from modules.assets import Assets
from modules.asset_animated import animation_images as Assnimated

class Animations:
    """Will contain basic code for
    flipping 2 images back and forth
    to simulate animation, and also
    static information on screen"""

    def __init__(self, player, info):
        self.player = player
        self.info = info
        self.heart_animation_timer = 0
        self.heart_animation_speed = 150
        self.heart_frame = 0

    def heart_animation(self, screen):
        self.heart_animation_timer += self.info.dt * 1000
        if self.heart_animation_timer >= self.heart_animation_speed:
            self.heart_animation_timer = 0
            self.heart_frame = (self.heart_frame + 1) % len(Assnimated.hearts_image)
        for i in range(self.player.player_lives):
            screen.blit(Assnimated.hearts_image[self.heart_frame], (10 + i * 40, 40))

    def side_cannon(self, screen):
        if self.player.side_cannon_count >= 1:
            screen.blit(
                Assets.side_cannon_image,
                (self.player.player_box.centerx - 93, self.player.player_box.top - 10)
            )
        if self.player.side_cannon_count >= 2:
            screen.blit(
                Assets.side_cannon_image,
                (self.player.player_box.centerx + 70, self.player.player_box.top - 10)
            )

    def draw_shields(self, screen):
        """Draws 1-3 visual blue rings 
        around player depending 
        on shield tokens collect, will last
        15 seconds before expiring."""

        for i in range(self.player.shield):
            radius = max(self.info.iconX, self.info.iconY) + (i * 10)  # each ring slightly bigger
            shield_surface = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
            pygame.draw.circle(shield_surface, (0, 0, 255, 100), (radius, radius), radius, 4)  # 4px thick ring
            screen.blit(shield_surface, (self.player.playerX - radius + self.info.iconX/2, self.player.playerY - radius + self.info.iconY/2))

    def floating_collectibles(self, screen):
        for collectible in self.player.collectibles:
            collectible.update(self.info.dt)
            collectible.draw(screen)

    def screen_text(self, screen):
        font = pygame.font.Font(None, 35)

        points_text = font.render(f"Score: {self.player.points}", True, (255, 255, 255))
        points_rect = points_text.get_rect()
        points_rect.topleft = (35, 10)
        screen.blit(points_text, points_rect)

        level_text = font.render(f"Level: {self.info.level}", True, (255, 255, 255))
        level_rect = level_text.get_rect()
        level_rect.topright = (self.info.screenX - 35, 10)
        screen.blit(level_text, level_rect)