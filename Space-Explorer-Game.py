"""
Space Explorer - A 3-sector space exploration and combat game.

This game features multiple space sectors connected by portals, enemy ships,
combat mechanics, and advanced visual effects including energy shields and droids.
"""

import pygame
import random
import math
import sys

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Game Constants
SCREEN_WIDTH = 1440
SCREEN_HEIGHT = 900
FPS = 60
STAR_COUNT = 300

# Shield Animation Constants
SHIELD_PULSE_INTERVAL = 2.0  # Seconds between pulses
SHIELD_PULSE_DURATION = 0.5  # Duration of pulse animation
SHIELD_BASE_RADIUS = 60
SHIELD_ROTATION_SPEED = 30  # Degrees per second

# Player Constants
PLAYER_SPEED = 850
PLAYER_COLLISION_SIZE = 12
PLAYER_ROTATION_SPEED_TARGETING = 0.15
PLAYER_ROTATION_SPEED_MOVING = 0.1
DROID_FOLLOW_SPEED = 3.0  # Rotation lag speed

# Enemy Constants
ENEMY_SPEED = 100
ENEMY_SIZE = 15
ENEMY_MAX_HEALTH = 4000
ENEMY_MIN_ROTATION_SPEED = 50
ENEMY_MAX_ROTATION_SPEED = 150

# Laser Constants
LASER_SPEED = 800
LASER_LIFETIME = 3.0
LASER_SIZE = 3
LASER_DAMAGE = 25
LASER_FIRE_RATE = 0.15  # Seconds between shots

# Portal Constants
PORTAL_RADIUS = 40
PORTAL_ROTATION_SPEED = 100

# Warp Constants
WARP_SPEED = 1.5


def normalize_angle(angle):
    """
    Normalize angle to -180 to 180 range for shortest rotation path.

    Args:
        angle: Angle in degrees

    Returns:
        Normalized angle between -180 and 180 degrees
    """
    while angle > 180:
        angle -= 360
    while angle < -180:
        angle += 360
    return angle


class Exiting:
    """Handles game exit operations."""

    @staticmethod
    def quit_game():
        """Quit pygame and exit the application cleanly."""
        pygame.quit()
        sys.exit()


class SpaceMap:
    """
    Represents a space sector/map with unique visual properties.

    Each map has its own background color, star field, and enemy types,
    creating distinct exploration zones.
    """

    def __init__(self, name, bg_color, star_color, enemy_types):
        """
        Initialize a space map.

        Args:
            name: Display name of the sector
            bg_color: RGB tuple for background color
            star_color: RGB tuple for star field color
            enemy_types: List of enemy type identifiers (currently unused)
        """
        self.name = name
        self.bg_color = bg_color
        self.star_color = star_color
        self.enemy_types = enemy_types
        self.stars = []
        self.portals = []

    def generate_stars(self, count, screen_width, screen_height):
        """
        Generate procedural star field for parallax scrolling.

        Args:
            count: Number of stars to generate
            screen_width: Width of the play area
            screen_height: Height of the play area
        """
        self.stars = []
        for _ in range(count):
            star = {
                'x': random.randint(0, screen_width),
                'y': random.randint(0, screen_height),
                'speed': random.uniform(0.5, 2),
                'size': random.randint(1, 3),
                'brightness': random.randint(100, 255)
            }
            self.stars.append(star)


class Assets:
    """
    Centralized asset management for images and map definitions.

    Handles loading and scaling of all game sprites and defines
    the available space sectors.
    """

    # Image assets
    ship_5_image = None
    enemy_image = None
    droid_image = None
    player_size = 40
    portal_size = 80
    enemy_collision_radius = 15  # Will be set after loading enemy image

    @staticmethod
    def load_assets():
        """
        Load and scale all game image assets.

        Images are scaled to appropriate sizes for the game's zoom level.
        Gracefully handles missing assets by setting to None.
        """
        try:
            original_ship = pygame.image.load("si_game_assets/images/ship_5.png")
            original_size = original_ship.get_size()
            new_size = (int(original_size[0] * 0.4), int(original_size[1] * 0.4))
            Assets.ship_5_image = pygame.transform.smoothscale(original_ship, new_size)
        except:
            Assets.ship_5_image = None

        try:
            original_enemy = pygame.image.load("si_game_assets/images/555.png")
            enemy_size = original_enemy.get_size()
            new_enemy_size = (int(enemy_size[0] * 0.35), int(enemy_size[1] * 0.35))
            Assets.enemy_image = pygame.transform.smoothscale(original_enemy, new_enemy_size)
            # Calculate collision radius as half of the average dimension
            Assets.enemy_collision_radius = (new_enemy_size[0] + new_enemy_size[1]) // 4
        except:
            Assets.enemy_image = None
            Assets.enemy_collision_radius = ENEMY_SIZE  # Fallback to constant

        try:
            original_droid = pygame.image.load("si_game_assets/images/side_cannon.png")
            droid_size = original_droid.get_size()
            new_droid_size = (int(droid_size[0] * 0.5), int(droid_size[1] * 0.5))
            Assets.droid_image = pygame.transform.smoothscale(original_droid, new_droid_size)
        except:
            Assets.droid_image = None

    # Map/Sector definitions
    maps = {
        'nebula': SpaceMap(
            "Crimson Nebula",
            (20, 5, 30),  # Dark purple background
            (255, 100, 150),  # Pink stars
            ['basic', 'fast']
        ),
        'asteroid': SpaceMap(
            "Asteroid Field",
            (10, 15, 5),  # Dark green background
            (150, 200, 100),  # Green stars
            ['tank', 'basic']
        ),
        'deep_space': SpaceMap(
            "Deep Space",
            (5, 5, 15),  # Deep blue background
            (200, 200, 255),  # Blue stars
            ['zigzag', 'guardian']
        )
    }

    current_map = 'nebula'


class Info:
    """
    Core game information and state management.

    Manages timing, game state transitions, camera positioning,
    and star field rendering.
    """

    screenX = SCREEN_WIDTH
    screenY = SCREEN_HEIGHT

    def __init__(self):
        """Initialize game information and timing systems."""
        self.clock = pygame.time.Clock()
        self.dt = 0  # Delta time for frame-independent movement
        self.game_state = "Exploring"  # Possible states: Exploring, WarpingOut, WarpingIn

        # Camera system for infinite scrolling
        self.camera_x = 0
        self.camera_y = 0

        # Warp transition effect
        self.warp_progress = 0
        self.warp_target = None

        # Initialize star fields for all maps
        for map_key in Assets.maps:
            Assets.maps[map_key].generate_stars(STAR_COUNT, Info.screenX * 2, Info.screenY * 2)

    def update_time(self):
        """Update delta time, capping at 60 FPS."""
        self.dt = self.clock.tick(FPS) / 1000

    def get_current_map(self):
        """Get the currently active space map."""
        return Assets.maps[Assets.current_map]

    def update_stars(self, player):
        """
        Update star positions with wrapping for infinite scrolling.

        Args:
            player: Player object (used for potential parallax effects)
        """
        current_map = self.get_current_map()

        for star in current_map.stars:
            # Wrap stars around screen edges for infinite scrolling
            if star['x'] < -100:
                star['x'] = Info.screenX + 100
                star['y'] = random.randint(0, Info.screenY)
            if star['x'] > Info.screenX + 100:
                star['x'] = -100
                star['y'] = random.randint(0, Info.screenY)
            if star['y'] < -100:
                star['y'] = Info.screenY + 100
                star['x'] = random.randint(0, Info.screenX)
            if star['y'] > Info.screenY + 100:
                star['y'] = -100
                star['x'] = random.randint(0, Info.screenX)

    def draw_stars(self, screen):
        """
        Render the star field with glow effects.

        Args:
            screen: Pygame display surface to draw on
        """
        current_map = self.get_current_map()

        for star in current_map.stars:
            brightness_factor = star['brightness'] / 255
            color = tuple(int(c * brightness_factor) for c in current_map.star_color)

            # Draw star glow for larger stars
            if star['size'] > 1:
                glow_surf = pygame.Surface((star['size']*4, star['size']*4), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (*color, 50), (star['size']*2, star['size']*2), star['size']*2)
                screen.blit(glow_surf, (int(star['x']) - star['size']*2, int(star['y']) - star['size']*2))

            # Draw star core
            pygame.draw.circle(screen, color, (int(star['x']), int(star['y'])), star['size'])


class Portal:
    """
    Animated portal for sector transitions.

    Portals connect different space sectors and feature rotating particles
    and pulsing glow effects.
    """

    def __init__(self, x, y, target_map, color):
        """
        Initialize a portal.

        Args:
            x: World x-coordinate
            y: World y-coordinate
            target_map: Key of the destination map
            color: RGB tuple for portal color theme
        """
        self.x = x
        self.y = y
        self.target_map = target_map
        self.color = color
        self.radius = PORTAL_RADIUS
        self.rotation = 0
        self.pulse = 0

    def update(self, dt):
        """
        Update portal animation.

        Args:
            dt: Delta time in seconds
        """
        self.rotation += dt * PORTAL_ROTATION_SPEED
        self.pulse = math.sin(pygame.time.get_ticks() * 0.003) * 10

    def draw(self, screen, camera_x, camera_y):
        """
        Render the portal with glow and particle effects.

        Args:
            screen: Pygame display surface
            camera_x: Camera x-offset for world-to-screen conversion
            camera_y: Camera y-offset for world-to-screen conversion
        """
        draw_x = self.x - camera_x
        draw_y = self.y - camera_y

        # Only draw if visible on screen
        if -100 < draw_x < Info.screenX + 100 and -100 < draw_y < Info.screenY + 100:
            # Draw outer glow layers
            for i in range(3, 0, -1):
                glow_size = int(self.radius + self.pulse + i * 15)
                alpha = int(100 / i)
                glow_surf = pygame.Surface((glow_size*2, glow_size*2), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (*self.color, alpha), (glow_size, glow_size), glow_size)
                screen.blit(glow_surf, (int(draw_x) - glow_size, int(draw_y) - glow_size))

            # Draw portal ring
            pygame.draw.circle(screen, self.color, (int(draw_x), int(draw_y)), int(self.radius + self.pulse), 3)

            # Draw rotating particles
            for i in range(8):
                angle = math.radians(self.rotation + i * 45)
                px = draw_x + math.cos(angle) * (self.radius + self.pulse)
                py = draw_y + math.sin(angle) * (self.radius + self.pulse)
                pygame.draw.circle(screen, (255, 255, 255), (int(px), int(py)), 3)

            # Draw center dot
            pygame.draw.circle(screen, self.color, (int(draw_x), int(draw_y)), 5)


class Laser:
    """
    Projectile fired by the player ship.

    Features directional movement, lifetime management, and collision detection.
    """

    def __init__(self, x, y, angle):
        """
        Initialize a laser projectile.

        Args:
            x: World x-coordinate
            y: World y-coordinate
            angle: Direction in degrees
        """
        self.world_x = x
        self.world_y = y
        self.angle = angle
        self.speed = LASER_SPEED
        self.lifetime = LASER_LIFETIME
        self.size = LASER_SIZE
        self.damage = LASER_DAMAGE

    def update(self, dt):
        """
        Update laser position and lifetime.

        Args:
            dt: Delta time in seconds
        """
        rad = math.radians(self.angle)
        self.world_x += math.cos(rad) * self.speed * dt
        self.world_y += math.sin(rad) * self.speed * dt
        self.lifetime -= dt

    def draw(self, screen, camera_x, camera_y):
        """
        Render the laser with glow effect.

        Args:
            screen: Pygame display surface
            camera_x: Camera x-offset
            camera_y: Camera y-offset
        """
        draw_x = self.world_x - camera_x
        draw_y = self.world_y - camera_y

        # Only draw if on screen
        if -50 < draw_x < Info.screenX + 50 and -50 < draw_y < Info.screenY + 50:
            rad = math.radians(self.angle)
            end_x = draw_x + math.cos(rad) * 15
            end_y = draw_y + math.sin(rad) * 15

            # Draw glow effect
            glow_surf = pygame.Surface((30, 30), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (0, 200, 255, 100), (15, 15), 8)
            screen.blit(glow_surf, (int(draw_x) - 15, int(draw_y) - 15))

            # Draw laser core
            pygame.draw.line(screen, (100, 220, 255), (draw_x, draw_y), (end_x, end_y), 3)
            pygame.draw.circle(screen, (200, 240, 255), (int(draw_x), int(draw_y)), self.size)

    def check_collision(self, enemy):
        """
        Check collision with an enemy using circular collision detection.

        Args:
            enemy: Enemy object to check collision with

        Returns:
            True if collision detected, False otherwise
        """
        dx = self.world_x - enemy.world_x
        dy = self.world_y - enemy.world_y
        distance = math.sqrt(dx*dx + dy*dy)
        return distance < enemy.size + self.size


class Enemy:
    """
    Enemy ship that patrols a designated area.

    Features autonomous movement, health system, and continuous rotation.
    """

    def __init__(self, x, y, patrol_range=500):
        """
        Initialize an enemy ship.

        Args:
            x: Initial world x-coordinate
            y: Initial world y-coordinate
            patrol_range: Radius of patrol area from spawn point
        """
        self.world_x = x
        self.world_y = y
        self.spawn_x = x
        self.spawn_y = y
        self.patrol_range = patrol_range

        # Movement properties
        self.speed = ENEMY_SPEED
        self.target_x = x
        self.target_y = y
        self.set_random_target()

        # Rotation (continuous spin for visual interest)
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = random.uniform(ENEMY_MIN_ROTATION_SPEED, ENEMY_MAX_ROTATION_SPEED)

        # Use dynamically calculated collision radius based on actual image size
        self.size = Assets.enemy_collision_radius

        # Health system
        self.max_health = ENEMY_MAX_HEALTH
        self.health = self.max_health

    def set_random_target(self):
        """Select a random patrol destination within patrol range."""
        angle = random.uniform(0, math.pi * 2)
        distance = random.uniform(100, self.patrol_range)
        self.target_x = self.spawn_x + math.cos(angle) * distance
        self.target_y = self.spawn_y + math.sin(angle) * distance

    def update(self, dt):
        """
        Update enemy movement and rotation.

        Args:
            dt: Delta time in seconds
        """
        # Move towards current target
        dx = self.target_x - self.world_x
        dy = self.target_y - self.world_y
        distance = math.sqrt(dx*dx + dy*dy)

        if distance < 50:
            # Reached target, pick new one
            self.set_random_target()
        else:
            # Continue moving toward target
            self.world_x += (dx / distance) * self.speed * dt
            self.world_y += (dy / distance) * self.speed * dt

        # Update rotation
        self.rotation += self.rotation_speed * dt
        if self.rotation >= 360:
            self.rotation -= 360

    def take_damage(self, damage):
        """
        Apply damage to the enemy.

        Args:
            damage: Amount of damage to apply

        Returns:
            True if enemy is destroyed, False otherwise
        """
        self.health -= damage
        return self.health <= 0

    def draw(self, screen, camera_x, camera_y):
        """
        Render the enemy ship with optional health bar.

        Args:
            screen: Pygame display surface
            camera_x: Camera x-offset
            camera_y: Camera y-offset
        """
        draw_x = self.world_x - camera_x
        draw_y = self.world_y - camera_y

        # Only draw if on screen
        if -100 < draw_x < Info.screenX + 100 and -100 < draw_y < Info.screenY + 100:
            if Assets.enemy_image:
                rotated_enemy = pygame.transform.rotate(Assets.enemy_image, -self.rotation)
                enemy_rect = rotated_enemy.get_rect(center=(int(draw_x), int(draw_y)))
                screen.blit(rotated_enemy, enemy_rect)
            else:
                # Fallback rendering
                pygame.draw.circle(screen, (255, 100, 100), (int(draw_x), int(draw_y)), self.size)

            # Draw health bar when damaged
            if self.health < self.max_health:
                bar_width = 50
                bar_height = 5
                bar_x = draw_x - bar_width // 2
                bar_y = draw_y - 35

                # Background
                pygame.draw.rect(screen, (100, 0, 0), (bar_x, bar_y, bar_width, bar_height))

                # Health indicator
                health_width = int(bar_width * (self.health / self.max_health))
                if health_width > 0:
                    pygame.draw.rect(screen, (0, 255, 0), (bar_x, bar_y, health_width, bar_height))

                # Border
                pygame.draw.rect(screen, (200, 200, 200), (bar_x, bar_y, bar_width, bar_height), 1)


class Player:
    """
    Player-controlled spaceship with weapons, shields, and support droids.

    Features smooth rotation, multi-gun laser firing, energy shield animation,
    and a formation of droids that follow with lag effect.
    """

    def __init__(self):
        """Initialize the player ship and all systems."""
        # Screen position (fixed at center)
        self.x = Info.screenX // 2
        self.y = Info.screenY // 2

        # World position (actual position in game world)
        self.world_x = 0
        self.world_y = 0

        # Movement properties
        self.speed = PLAYER_SPEED
        self.size = PLAYER_COLLISION_SIZE
        self.rotation = 0

        # Combat system
        self.target_enemy = None
        self.lasers = []
        self.fire_cooldown = 0
        self.fire_rate = LASER_FIRE_RATE

        # Multi-gun laser spawn positions (relative to ship center)
        self.laser_offsets = [
            (-26, -15),  # Left forward gun
            (26, -15),   # Right forward gun
            (0, 4),      # Center gun
            (15, 24),    # Right aft gun
            (-14, 24)    # Left aft gun
        ]

        # Support droid formation (relative to ship center)
        self.droid_positions = [
            (5, -55), (5, 55), (-15, 65),
            (5, -75), (5, 75), (-15, -65),
            (-80, 0), (-100, 20), (-120, 0), (-100, -20)
        ]

        # Droid rotation lag system (all droids rotate as a group)
        self.droid_group_rotation = 0.0
        self.droid_follow_speed = DROID_FOLLOW_SPEED

        # Energy shield animation system
        self.shield_timer = 0.0
        self.shield_pulse_progress = 0.0
        self.shield_rotation = 0.0

    def find_nearest_enemy(self, enemies):
        """
        Locate the closest enemy for targeting.

        Args:
            enemies: List of Enemy objects

        Returns:
            Nearest Enemy object or None if no enemies exist
        """
        if not enemies:
            return None

        nearest = None
        min_distance = float('inf')

        for enemy in enemies:
            dx = enemy.world_x - self.world_x
            dy = enemy.world_y - self.world_y
            distance = math.sqrt(dx*dx + dy*dy)

            if distance < min_distance:
                min_distance = distance
                nearest = enemy

        return nearest

    def fire_laser(self):
        """
        Fire lasers from all gun positions.

        If targeting an enemy, lasers converge on target.
        Otherwise, fires in the direction ship is facing.
        """
        if self.fire_cooldown > 0:
            return

        for offset_x, offset_y in self.laser_offsets:
            # Rotate gun offset based on ship rotation
            rad = math.radians(self.rotation)
            rotated_x = offset_x * math.cos(rad) - offset_y * math.sin(rad)
            rotated_y = offset_x * math.sin(rad) + offset_y * math.cos(rad)

            # Calculate laser spawn position in world space
            laser_x = self.world_x + rotated_x
            laser_y = self.world_y + rotated_y

            # Calculate laser firing angle
            if self.target_enemy:
                # Converge all lasers on target
                dx = self.target_enemy.world_x - laser_x
                dy = self.target_enemy.world_y - laser_y
                laser_angle = math.degrees(math.atan2(dy, dx))
            else:
                # Fire forward
                laser_angle = self.rotation

            self.lasers.append(Laser(laser_x, laser_y, laser_angle))

        self.fire_cooldown = self.fire_rate

    def update(self, dt, info, enemies):
        """
        Update all player systems: input, movement, rotation, weapons, and animations.

        Args:
            dt: Delta time in seconds
            info: Info object for camera and map access
            enemies: List of enemies (unused but kept for consistency)
        """
        keys = pygame.key.get_pressed()

        # Update weapon cooldown
        if self.fire_cooldown > 0:
            self.fire_cooldown -= dt

        # Handle firing
        if keys[pygame.K_SPACE]:
            self.fire_laser()

        # Update existing lasers
        for laser in self.lasers[:]:
            laser.update(dt)
            if laser.lifetime <= 0:
                self.lasers.remove(laser)

        # Get movement input
        move_x = 0
        move_y = 0

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            move_x = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            move_x = 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            move_y = -1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            move_y = 1

        # Normalize diagonal movement
        if move_x != 0 and move_y != 0:
            move_x *= 0.707
            move_y *= 0.707

        # Update world position
        self.world_x += move_x * self.speed * dt
        self.world_y += move_y * self.speed * dt

        # Update camera to follow player
        info.camera_x = self.world_x - Info.screenX // 2
        info.camera_y = self.world_y - Info.screenY // 2

        # Update rotation
        if self.target_enemy:
            # Rotate toward targeted enemy
            dx = self.target_enemy.world_x - self.world_x
            dy = self.target_enemy.world_y - self.world_y
            target_rotation = math.degrees(math.atan2(dy, dx))
            angle_diff = normalize_angle(target_rotation - self.rotation)
            self.rotation += angle_diff * PLAYER_ROTATION_SPEED_TARGETING
        elif move_x != 0 or move_y != 0:
            # Rotate in movement direction
            target_rotation = math.degrees(math.atan2(move_y, move_x))
            angle_diff = normalize_angle(target_rotation - self.rotation)
            self.rotation += angle_diff * PLAYER_ROTATION_SPEED_MOVING

        # Update parallax star field
        current_map = info.get_current_map()
        for star in current_map.stars:
            star['x'] -= move_x * self.speed * dt * 0.3 * star['speed']
            star['y'] -= move_y * self.speed * dt * 0.3 * star['speed']

        # Update droid group rotation with lag effect
        angle_diff = normalize_angle(self.rotation - self.droid_group_rotation)
        self.droid_group_rotation += angle_diff * self.droid_follow_speed * dt

        # Update shield animation
        self.shield_timer += dt
        self.shield_rotation += dt * SHIELD_ROTATION_SPEED

        # Trigger pulse every 2 seconds
        if self.shield_timer >= SHIELD_PULSE_INTERVAL:
            self.shield_timer = 0.0
            self.shield_pulse_progress = 0.0

        # Update pulse animation
        if self.shield_pulse_progress < 1.0:
            self.shield_pulse_progress += dt / SHIELD_PULSE_DURATION
            if self.shield_pulse_progress > 1.0:
                self.shield_pulse_progress = 1.0

    def draw_shield(self, screen):
        """
        Render hexagonal energy shield with animated pulse effect.

        Features hexagonal segments, rotating pattern, and expanding pulse wave.

        Args:
            screen: Pygame display surface
        """
        # Calculate pulse animation values
        pulse_intensity = 1.0 - self.shield_pulse_progress
        pulse_expansion = self.shield_pulse_progress * 20

        # Create shield surface
        shield_size = int((SHIELD_BASE_RADIUS + pulse_expansion) * 2 + 50)
        shield_surf = pygame.Surface((shield_size, shield_size), pygame.SRCALPHA)
        center = shield_size // 2

        # Draw hexagonal pattern segments
        num_segments = 6
        for i in range(num_segments):
            angle = math.radians(self.shield_rotation + i * 60)

            # Generate hexagon vertices
            hex_points = []
            for j in range(6):
                hex_angle = angle + math.radians(j * 60)
                x = center + math.cos(hex_angle) * (SHIELD_BASE_RADIUS + pulse_expansion * 0.5)
                y = center + math.sin(hex_angle) * (SHIELD_BASE_RADIUS + pulse_expansion * 0.5)
                hex_points.append((x, y))

            # Draw hexagon outline
            hex_alpha = int(100 * pulse_intensity + 30)
            pygame.draw.polygon(shield_surf, (0, 200, 255, hex_alpha), hex_points, 2)

            # Draw energy nodes at vertices
            for point in hex_points:
                glow_alpha = int(150 * pulse_intensity + 50)
                pygame.draw.circle(shield_surf, (100, 220, 255, glow_alpha),
                                 (int(point[0]), int(point[1])), 3)

        # Draw glow layers
        for glow_layer in range(3, 0, -1):
            glow_radius = SHIELD_BASE_RADIUS + pulse_expansion + glow_layer * 8
            glow_alpha = int((80 / glow_layer) * pulse_intensity + 20)
            pygame.draw.circle(shield_surf, (50, 180, 255, glow_alpha),
                             (center, center), int(glow_radius), 2)

        # Draw core circle
        core_alpha = int(120 * pulse_intensity + 40)
        pygame.draw.circle(shield_surf, (150, 230, 255, core_alpha),
                         (center, center), int(SHIELD_BASE_RADIUS + pulse_expansion), 1)

        # Draw pulse wave ring
        if pulse_intensity > 0.3:
            wave_radius = SHIELD_BASE_RADIUS + pulse_expansion
            wave_alpha = int(200 * pulse_intensity)
            pygame.draw.circle(shield_surf, (150, 240, 255, wave_alpha),
                             (center, center), int(wave_radius), 3)

        # Blit to screen
        shield_x = self.x - center
        shield_y = self.y - center
        screen.blit(shield_surf, (int(shield_x), int(shield_y)))

    def draw(self, screen):
        """
        Render all player components: shield, droids, and ship.

        Args:
            screen: Pygame display surface
        """
        # Draw shield (rendered first so it appears behind ship)
        self.draw_shield(screen)

        # Draw support droids
        for idx, (droid_offset_x, droid_offset_y) in enumerate(self.droid_positions):
            # Rotate droid offset based on lagged group rotation
            rad = math.radians(self.droid_group_rotation)
            rotated_x = droid_offset_x * math.cos(rad) - droid_offset_y * math.sin(rad)
            rotated_y = droid_offset_x * math.sin(rad) + droid_offset_y * math.cos(rad)

            # Calculate screen position
            droid_x = self.x + rotated_x
            droid_y = self.y + rotated_y

            if Assets.droid_image:
                rotated_droid = pygame.transform.rotate(Assets.droid_image, -self.droid_group_rotation - 90)
                droid_rect = rotated_droid.get_rect(center=(int(droid_x), int(droid_y)))
                screen.blit(rotated_droid, droid_rect)
            else:
                # Fallback rendering
                pygame.draw.circle(screen, (255, 255, 0), (int(droid_x), int(droid_y)), 5)
                pygame.draw.circle(screen, (255, 100, 0), (int(droid_x), int(droid_y)), 3)

        # Draw player ship
        if Assets.ship_5_image:
            rotated_ship = pygame.transform.rotate(Assets.ship_5_image, -self.rotation - 90)
            ship_rect = rotated_ship.get_rect(center=(int(self.x), int(self.y)))
            screen.blit(rotated_ship, ship_rect)
        else:
            # Fallback triangle rendering
            points = []
            for angle in [0, 140, 220]:
                rad = math.radians(angle + self.rotation)
                px = self.x + math.cos(rad) * self.size
                py = self.y + math.sin(rad) * self.size
                points.append((px, py))

            pygame.draw.polygon(screen, (200, 220, 255), points)
            pygame.draw.polygon(screen, (255, 255, 255), points, 2)

    def check_portal_collision(self, portals):
        """
        Check if player is in contact with any portal.

        Args:
            portals: List of Portal objects

        Returns:
            Collided Portal object or None
        """
        for portal in portals:
            dx = self.world_x - portal.x
            dy = self.world_y - portal.y
            distance = math.sqrt(dx*dx + dy*dy)

            if distance < portal.radius + self.size:
                return portal
        return None


class UI:
    """
    User interface rendering including minimap, HUD, and warp effects.
    """

    @staticmethod
    def draw_minimap(screen, player, portals, enemies, info):
        """
        Render tactical minimap showing player, portals, and enemies.

        Args:
            screen: Pygame display surface
            player: Player object
            portals: List of Portal objects
            enemies: List of Enemy objects
            info: Info object for current map data
        """
        minimap_size = 200
        minimap_x = Info.screenX - minimap_size - 20
        minimap_y = 20

        # Create minimap surface
        minimap_surf = pygame.Surface((minimap_size, minimap_size), pygame.SRCALPHA)
        pygame.draw.rect(minimap_surf, (20, 20, 40, 180), (0, 0, minimap_size, minimap_size))
        pygame.draw.rect(minimap_surf, (100, 100, 150, 200), (0, 0, minimap_size, minimap_size), 2)

        # Calculate scaling
        world_range = 3000
        scale = minimap_size / (world_range * 2)
        center_x = minimap_size // 2
        center_y = minimap_size // 2

        # Draw portals
        for portal in portals:
            rel_x = portal.x - player.world_x
            rel_y = portal.y - player.world_y
            map_x = center_x + rel_x * scale
            map_y = center_y + rel_y * scale

            if 0 <= map_x <= minimap_size and 0 <= map_y <= minimap_size:
                pygame.draw.circle(minimap_surf, portal.color, (int(map_x), int(map_y)), 5)
                pygame.draw.circle(minimap_surf, portal.color, (int(map_x), int(map_y)), 8, 1)

        # Draw enemies
        for enemy in enemies:
            rel_x = enemy.world_x - player.world_x
            rel_y = enemy.world_y - player.world_y
            map_x = center_x + rel_x * scale
            map_y = center_y + rel_y * scale

            if 0 <= map_x <= minimap_size and 0 <= map_y <= minimap_size:
                pygame.draw.circle(minimap_surf, (255, 100, 100), (int(map_x), int(map_y)), 3)

        # Draw player at center
        pygame.draw.circle(minimap_surf, (0, 255, 0), (center_x, center_y), 4)
        pygame.draw.circle(minimap_surf, (255, 255, 255), (center_x, center_y), 6, 1)

        # Draw title
        font = pygame.font.Font(None, 24)
        title = font.render("MAP", True, (200, 200, 200))
        minimap_surf.blit(title, (minimap_size // 2 - 20, 5))

        screen.blit(minimap_surf, (minimap_x, minimap_y))

    @staticmethod
    def draw_hud(screen, info, player):
        """
        Render heads-up display with sector name, position, and controls.

        Args:
            screen: Pygame display surface
            info: Info object for current map data
            player: Player object for position and target data
        """
        font = pygame.font.Font(None, 40)
        small_font = pygame.font.Font(None, 30)

        # Current sector name
        current_map = info.get_current_map()
        map_text = font.render(f"Sector: {current_map.name}", True, (255, 255, 255))
        screen.blit(map_text, (20, 20))

        # Player coordinates
        coord_text = small_font.render(f"Position: ({int(player.world_x)}, {int(player.world_y)})", True, (200, 200, 200))
        screen.blit(coord_text, (20, 60))

        # Target status
        if player.target_enemy:
            dx = player.target_enemy.world_x - player.world_x
            dy = player.target_enemy.world_y - player.world_y
            distance = math.sqrt(dx*dx + dy*dy)
            target_text = small_font.render(f"TARGET LOCKED - Distance: {int(distance)}", True, (255, 50, 50))
            screen.blit(target_text, (20, 100))
        else:
            target_text = small_font.render("Q - Lock Target", True, (150, 150, 150))
            screen.blit(target_text, (20, 100))

        # Control instructions
        controls = [
            "WASD/Arrows - Move  |  Q - Target  |  SPACE - Fire",
            "Find portals to travel between sectors!"
        ]

        y_offset = Info.screenY - 100
        for control in controls:
            text = small_font.render(control, True, (150, 150, 150))
            screen.blit(text, (20, y_offset))
            y_offset += 30

    @staticmethod
    def draw_warp_effect(screen, progress):
        """
        Render warp tunnel transition effect.

        Args:
            screen: Pygame display surface
            progress: Warp progress from 0 to 1
        """
        overlay = pygame.Surface((Info.screenX, Info.screenY), pygame.SRCALPHA)

        # Draw radial warp lines
        center_x = Info.screenX // 2
        center_y = Info.screenY // 2

        for i in range(20):
            angle = (i / 20) * math.pi * 2 + progress * 5

            # Calculate line endpoints
            start_dist = Info.screenX * (1 - progress)
            end_dist = Info.screenX * 0.3

            start_x = center_x + math.cos(angle) * start_dist
            start_y = center_y + math.sin(angle) * start_dist
            end_x = center_x + math.cos(angle) * end_dist
            end_y = center_y + math.sin(angle) * end_dist

            alpha = int(255 * progress)
            pygame.draw.line(overlay, (100, 150, 255, alpha), (start_x, start_y), (end_x, end_y), 3)

        # Draw vignette
        vignette_alpha = int(200 * progress)
        pygame.draw.rect(overlay, (0, 0, 50, vignette_alpha), (0, 0, Info.screenX, Info.screenY))

        screen.blit(overlay, (0, 0))

        # Draw warp text
        if progress > 0.3:
            font = pygame.font.Font(None, 80)
            text = font.render("WARPING...", True, (150, 200, 255, int(255 * progress)))
            text_rect = text.get_rect(center=(Info.screenX // 2, Info.screenY // 2))
            screen.blit(text, text_rect)


def create_portals_for_map(map_key):
    """
    Create portal connections for a specific map.

    Args:
        map_key: Map identifier string

    Returns:
        List of Portal objects
    """
    portals = []

    if map_key == 'nebula':
        portals.append(Portal(1500, 0, 'asteroid', (100, 255, 100)))
        portals.append(Portal(0, -1500, 'deep_space', (150, 150, 255)))

    elif map_key == 'asteroid':
        portals.append(Portal(-1500, 0, 'nebula', (255, 100, 150)))
        portals.append(Portal(1000, -1000, 'deep_space', (150, 150, 255)))

    elif map_key == 'deep_space':
        portals.append(Portal(0, 1500, 'nebula', (255, 100, 150)))
        portals.append(Portal(-1000, 1000, 'asteroid', (100, 255, 100)))

    return portals


def create_enemies_for_map(map_key):
    """
    Spawn enemies for a specific map.

    Args:
        map_key: Map identifier string

    Returns:
        List of Enemy objects
    """
    enemies = []

    if map_key == 'nebula':
        enemies.append(Enemy(800, 500, 400))
        enemies.append(Enemy(-600, -400, 350))
        enemies.append(Enemy(300, -700, 450))
        enemies.append(Enemy(-900, 600, 400))

    elif map_key == 'asteroid':
        enemies.append(Enemy(500, 600, 500))
        enemies.append(Enemy(-800, 300, 400))
        enemies.append(Enemy(600, -500, 450))
        enemies.append(Enemy(-400, -700, 350))
        enemies.append(Enemy(0, 800, 400))

    elif map_key == 'deep_space':
        enemies.append(Enemy(700, -600, 500))
        enemies.append(Enemy(-500, 700, 400))
        enemies.append(Enemy(900, 400, 450))
        enemies.append(Enemy(-700, -500, 400))
        enemies.append(Enemy(200, 900, 350))
        enemies.append(Enemy(-900, -200, 400))

    return enemies


def draw_target_brackets(screen, enemy, camera_x, camera_y):
    """
    Draw targeting brackets around a locked enemy.

    Args:
        screen: Pygame display surface
        enemy: Enemy object being targeted
        camera_x: Camera x-offset
        camera_y: Camera y-offset
    """
    draw_x = enemy.world_x - camera_x
    draw_y = enemy.world_y - camera_y

    if -100 < draw_x < Info.screenX + 100 and -100 < draw_y < Info.screenY + 100:
        bracket_size = 40
        bracket_length = 15
        color = (255, 50, 50)
        thickness = 3

        # Top-left bracket
        pygame.draw.line(screen, color,
                       (draw_x - bracket_size, draw_y - bracket_size),
                       (draw_x - bracket_size + bracket_length, draw_y - bracket_size), thickness)
        pygame.draw.line(screen, color,
                       (draw_x - bracket_size, draw_y - bracket_size),
                       (draw_x - bracket_size, draw_y - bracket_size + bracket_length), thickness)

        # Top-right bracket
        pygame.draw.line(screen, color,
                       (draw_x + bracket_size, draw_y - bracket_size),
                       (draw_x + bracket_size - bracket_length, draw_y - bracket_size), thickness)
        pygame.draw.line(screen, color,
                       (draw_x + bracket_size, draw_y - bracket_size),
                       (draw_x + bracket_size, draw_y - bracket_size + bracket_length), thickness)

        # Bottom-left bracket
        pygame.draw.line(screen, color,
                       (draw_x - bracket_size, draw_y + bracket_size),
                       (draw_x - bracket_size + bracket_length, draw_y + bracket_size), thickness)
        pygame.draw.line(screen, color,
                       (draw_x - bracket_size, draw_y + bracket_size),
                       (draw_x - bracket_size, draw_y + bracket_size - bracket_length), thickness)

        # Bottom-right bracket
        pygame.draw.line(screen, color,
                       (draw_x + bracket_size, draw_y + bracket_size),
                       (draw_x + bracket_size - bracket_length, draw_y + bracket_size), thickness)
        pygame.draw.line(screen, color,
                       (draw_x + bracket_size, draw_y + bracket_size),
                       (draw_x + bracket_size, draw_y + bracket_size - bracket_length), thickness)


def main():
    """
    Main game loop entry point.

    Initializes game systems, handles events, updates game state,
    and renders all visual elements.
    """
    # Initialize display
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Space Explorer - 3 Sector Universe")

    # Load assets
    Assets.load_assets()

    # Initialize game objects
    info = Info()
    player = Player()
    portals = create_portals_for_map(Assets.current_map)
    enemies = create_enemies_for_map(Assets.current_map)

    # Main game loop
    while True:
        info.update_time()

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                Exiting.quit_game()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    Exiting.quit_game()
                elif event.key == pygame.K_q:
                    # Toggle target lock
                    if player.target_enemy:
                        player.target_enemy = None
                    else:
                        player.target_enemy = player.find_nearest_enemy(enemies)

        # Update game state
        if info.game_state == "Exploring":
            player.update(info.dt, info, enemies)
            info.update_stars(player)

            # Update portals
            for portal in portals:
                portal.update(info.dt)

            # Update enemies
            for enemy in enemies:
                enemy.update(info.dt)

            # Check laser-enemy collisions
            for laser in player.lasers[:]:
                for enemy in enemies[:]:
                    if laser.check_collision(enemy):
                        is_destroyed = enemy.take_damage(laser.damage)

                        if laser in player.lasers:
                            player.lasers.remove(laser)

                        if is_destroyed and enemy in enemies:
                            if player.target_enemy == enemy:
                                player.target_enemy = None
                            enemies.remove(enemy)
                        break

            # Check portal collision
            collided_portal = player.check_portal_collision(portals)
            if collided_portal:
                info.game_state = "WarpingOut"
                info.warp_progress = 0
                info.warp_target = collided_portal.target_map

        elif info.game_state == "WarpingOut":
            info.warp_progress += info.dt * WARP_SPEED

            if info.warp_progress >= 1.0:
                # Transition to new map
                Assets.current_map = info.warp_target
                portals = create_portals_for_map(Assets.current_map)
                enemies = create_enemies_for_map(Assets.current_map)

                # Reset player state
                player.world_x = 0
                player.world_y = 0
                player.target_enemy = None
                player.droid_group_rotation = player.rotation

                info.game_state = "WarpingIn"
                info.warp_progress = 1.0

        elif info.game_state == "WarpingIn":
            info.warp_progress -= info.dt * WARP_SPEED

            if info.warp_progress <= 0:
                info.game_state = "Exploring"
                info.warp_progress = 0

        # Render frame
        current_map = info.get_current_map()
        screen.fill(current_map.bg_color)

        # Draw background elements
        info.draw_stars(screen)

        # Draw portals
        for portal in portals:
            portal.draw(screen, info.camera_x, info.camera_y)

        # Draw enemies and target indicators
        for enemy in enemies:
            enemy.draw(screen, info.camera_x, info.camera_y)
            if player.target_enemy == enemy:
                draw_target_brackets(screen, enemy, info.camera_x, info.camera_y)

        # Draw player
        player.draw(screen)

        # Draw lasers
        for laser in player.lasers:
            laser.draw(screen, info.camera_x, info.camera_y)

        # Draw UI elements
        UI.draw_hud(screen, info, player)
        UI.draw_minimap(screen, player, portals, enemies, info)

        # Draw warp effect overlay
        if info.game_state in ["WarpingOut", "WarpingIn"]:
            UI.draw_warp_effect(screen, info.warp_progress)

        pygame.display.flip()


if __name__ == "__main__":
    main()
