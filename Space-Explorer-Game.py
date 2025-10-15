import pygame, random, math, sys

pygame.init()
pygame.mixer.init()

class Exiting:
    def quit_game():
        pygame.quit()
        sys.exit()

class SpaceMap:
    """Represents different space sectors/maps"""
    def __init__(self, name, bg_color, star_color, enemy_types):
        self.name = name
        self.bg_color = bg_color
        self.star_color = star_color
        self.enemy_types = enemy_types
        self.stars = []
        self.portals = []

    def generate_stars(self, count, screenX, screenY):
        """Generate stars for this map"""
        self.stars = []
        for _ in range(count):
            star = {
                'x': random.randint(0, screenX),
                'y': random.randint(0, screenY),
                'speed': random.uniform(0.5, 2),
                'size': random.randint(1, 3),
                'brightness': random.randint(100, 255)
            }
            self.stars.append(star)

class Assets:
    """Game assets"""
    # Images
    game_icon = None
    ship_5_image = None
    enemy_image = None
    droid_image = None
    player_size = 40
    portal_size = 80

    @staticmethod
    def load_assets():
        """Load game assets"""
        try:
            # Load ship and scale down for better zoom level
            original_ship = pygame.image.load("si_game_assets/images/ship_5.png")
            original_size = original_ship.get_size()
            # Scale to 40% for zoomed out view
            new_size = (int(original_size[0] * 0.4), int(original_size[1] * 0.4))
            Assets.ship_5_image = pygame.transform.smoothscale(original_ship, new_size)
        except:
            Assets.ship_5_image = None

        try:
            # Load enemy ship - symmetric, will rotate 360
            original_enemy = pygame.image.load("si_game_assets/images/555.png")
            enemy_size = original_enemy.get_size()
            # Scale to 35% for enemy size
            new_enemy_size = (int(enemy_size[0] * 0.35), int(enemy_size[1] * 0.35))
            Assets.enemy_image = pygame.transform.smoothscale(original_enemy, new_enemy_size)
        except:
            Assets.enemy_image = None

        try:
            # Load droid/side cannon
            original_droid = pygame.image.load("si_game_assets/images/side_cannon.png")
            droid_size = original_droid.get_size()
            # Scale to 50% for bigger droid size
            new_droid_size = (int(droid_size[0] * 0.5), int(droid_size[1] * 0.5))
            Assets.droid_image = pygame.transform.smoothscale(original_droid, new_droid_size)
        except:
            Assets.droid_image = None

    # Maps/Sectors
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
    """Game information"""
    screenX = 1440
    screenY = 900

    def __init__(self):
        self.clock = pygame.time.Clock()
        self.dt = 0
        self.game_state = "Exploring"  # Exploring, Fighting, WarpingOut, WarpingIn

        # Camera position for infinite scrolling
        self.camera_x = 0
        self.camera_y = 0

        # Warp effect
        self.warp_progress = 0
        self.warp_target = None

        # Initialize map stars
        for map_key in Assets.maps:
            Assets.maps[map_key].generate_stars(300, Info.screenX * 2, Info.screenY * 2)

    def update_time(self):
        self.dt = self.clock.tick(60) / 1000

    def get_current_map(self):
        return Assets.maps[Assets.current_map]

    def update_stars(self, player):
        """Update stars with parallax based on player movement"""
        current_map = self.get_current_map()

        for star in current_map.stars:
            # Wrap stars around screen
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
        """Draw stars"""
        current_map = self.get_current_map()

        for star in current_map.stars:
            brightness_factor = star['brightness'] / 255
            color = tuple(int(c * brightness_factor) for c in current_map.star_color)

            # Draw star glow
            if star['size'] > 1:
                glow_surf = pygame.Surface((star['size']*4, star['size']*4), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (*color, 50), (star['size']*2, star['size']*2), star['size']*2)
                screen.blit(glow_surf, (int(star['x']) - star['size']*2, int(star['y']) - star['size']*2))

            # Draw star core
            pygame.draw.circle(screen, color, (int(star['x']), int(star['y'])), star['size'])

class Portal:
    """Portal to another map"""
    def __init__(self, x, y, target_map, color):
        self.x = x
        self.y = y
        self.target_map = target_map
        self.color = color
        self.radius = 40
        self.rotation = 0
        self.pulse = 0

    def update(self, dt):
        self.rotation += dt * 100
        self.pulse = math.sin(pygame.time.get_ticks() * 0.003) * 10

    def draw(self, screen, camera_x, camera_y):
        draw_x = self.x - camera_x
        draw_y = self.y - camera_y

        # Only draw if on screen
        if -100 < draw_x < Info.screenX + 100 and -100 < draw_y < Info.screenY + 100:
            # Outer glow
            for i in range(3, 0, -1):
                glow_size = int(self.radius + self.pulse + i * 15)
                alpha = int(100 / i)
                glow_surf = pygame.Surface((glow_size*2, glow_size*2), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (*self.color, alpha), (glow_size, glow_size), glow_size)
                screen.blit(glow_surf, (int(draw_x) - glow_size, int(draw_y) - glow_size))

            # Portal ring
            pygame.draw.circle(screen, self.color, (int(draw_x), int(draw_y)), int(self.radius + self.pulse), 3)

            # Rotating particles
            for i in range(8):
                angle = math.radians(self.rotation + i * 45)
                px = draw_x + math.cos(angle) * (self.radius + self.pulse)
                py = draw_y + math.sin(angle) * (self.radius + self.pulse)
                pygame.draw.circle(screen, (255, 255, 255), (int(px), int(py)), 3)

            # Center
            pygame.draw.circle(screen, self.color, (int(draw_x), int(draw_y)), 5)

class Laser:
    """Laser projectile"""
    def __init__(self, x, y, angle):
        self.world_x = x
        self.world_y = y
        self.angle = angle  # Direction in degrees
        self.speed = 800
        self.lifetime = 3.0  # 3 seconds
        self.size = 3
        self.damage = 25  # Damage per hit

    def update(self, dt):
        # Move in the direction of angle
        rad = math.radians(self.angle)
        self.world_x += math.cos(rad) * self.speed * dt
        self.world_y += math.sin(rad) * self.speed * dt

        # Decrease lifetime
        self.lifetime -= dt

    def draw(self, screen, camera_x, camera_y):
        draw_x = self.world_x - camera_x
        draw_y = self.world_y - camera_y

        # Only draw if on screen
        if -50 < draw_x < Info.screenX + 50 and -50 < draw_y < Info.screenY + 50:
            # Draw laser as bright line
            rad = math.radians(self.angle)
            end_x = draw_x + math.cos(rad) * 15
            end_y = draw_y + math.sin(rad) * 15

            # Glow effect
            glow_surf = pygame.Surface((30, 30), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (0, 200, 255, 100), (15, 15), 8)
            screen.blit(glow_surf, (int(draw_x) - 15, int(draw_y) - 15))

            # Laser core
            pygame.draw.line(screen, (100, 220, 255), (draw_x, draw_y), (end_x, end_y), 3)
            pygame.draw.circle(screen, (200, 240, 255), (int(draw_x), int(draw_y)), self.size)

    def check_collision(self, enemy):
        """Check if laser hits enemy"""
        dx = self.world_x - enemy.world_x
        dy = self.world_y - enemy.world_y
        distance = math.sqrt(dx*dx + dy*dy)
        return distance < enemy.size + self.size

class Enemy:
    """Enemy ship that patrols an area"""
    def __init__(self, x, y, patrol_range=500):
        self.world_x = x
        self.world_y = y
        self.spawn_x = x
        self.spawn_y = y
        self.patrol_range = patrol_range

        # Movement
        self.speed = 100
        self.target_x = x
        self.target_y = y
        self.set_random_target()

        # Rotation (continuous spin)
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = random.uniform(50, 150)  # degrees per second

        self.size = 15

        # Health system
        self.max_health = 100
        self.health = self.max_health

    def set_random_target(self):
        """Set a random target within patrol range"""
        angle = random.uniform(0, math.pi * 2)
        distance = random.uniform(100, self.patrol_range)
        self.target_x = self.spawn_x + math.cos(angle) * distance
        self.target_y = self.spawn_y + math.sin(angle) * distance

    def update(self, dt):
        # Move towards target
        dx = self.target_x - self.world_x
        dy = self.target_y - self.world_y
        distance = math.sqrt(dx*dx + dy*dy)

        if distance < 50:
            # Reached target, pick new one
            self.set_random_target()
        else:
            # Move towards target
            self.world_x += (dx / distance) * self.speed * dt
            self.world_y += (dy / distance) * self.speed * dt

        # Rotate continuously
        self.rotation += self.rotation_speed * dt
        if self.rotation >= 360:
            self.rotation -= 360

    def take_damage(self, damage):
        """Take damage and return True if enemy is destroyed"""
        self.health -= damage
        return self.health <= 0

    def draw(self, screen, camera_x, camera_y):
        # Calculate screen position
        draw_x = self.world_x - camera_x
        draw_y = self.world_y - camera_y

        # Only draw if on screen
        if -100 < draw_x < Info.screenX + 100 and -100 < draw_y < Info.screenY + 100:
            if Assets.enemy_image:
                # Rotate enemy image
                rotated_enemy = pygame.transform.rotate(Assets.enemy_image, -self.rotation)
                enemy_rect = rotated_enemy.get_rect(center=(int(draw_x), int(draw_y)))
                screen.blit(rotated_enemy, enemy_rect)
            else:
                # Fallback circle
                pygame.draw.circle(screen, (255, 100, 100), (int(draw_x), int(draw_y)), self.size)

            # Draw health bar
            if self.health < self.max_health:
                bar_width = 50
                bar_height = 5
                bar_x = draw_x - bar_width // 2
                bar_y = draw_y - 35

                # Background (red)
                pygame.draw.rect(screen, (100, 0, 0), (bar_x, bar_y, bar_width, bar_height))

                # Health (green)
                health_width = int(bar_width * (self.health / self.max_health))
                if health_width > 0:
                    pygame.draw.rect(screen, (0, 255, 0), (bar_x, bar_y, health_width, bar_height))

                # Border
                pygame.draw.rect(screen, (200, 200, 200), (bar_x, bar_y, bar_width, bar_height), 1)

class Player:
    """Player ship"""
    def __init__(self):
        self.x = Info.screenX // 2
        self.y = Info.screenY // 2
        self.world_x = 0  # Position in the world
        self.world_y = 0
        self.speed = 850  # Speed adjusted for 40% zoom
        self.size = 12  # Collision size adjusted
        self.rotation = 0
        self.velocity_x = 0
        self.velocity_y = 0
        self.trail = []
        self.target_enemy = None  # Currently targeted enemy

        # Laser spawn positions (relative to ship center, scaled to 40%)
        # Based on ship_4 coordinates: (6,34), (138,34), (73,82), (110,132), (37,132)
        # Assuming ship center at (72, 72), scaled to 40%
        self.laser_offsets = [
            (-26, -15),  # Left top gun
            (26, -15),   # Right top gun
            (0, 4),      # Center gun
            (15, 24),    # Right bottom gun
            (-14, 24)    # Left bottom gun
        ]

        self.lasers = []
        self.fire_cooldown = 0
        self.fire_rate = 0.15  # Seconds between shots

        # Droid positions (relative to ship center)
        # Ship image is 90 degrees up, so coordinates are rotated
        # Each droid is independent with unique position
        self.droid_positions = [
            # Right side (2 droids)
            (5, -55),    # Right droid 1
            (5, 55),   # Right droid 2
            (-15, 65),   # Right droid 2

            # Left side (2 droids)
            (5, -75),   # Left droid 1
            (5, 75),  # Left droid 2
            (-15, -65),   # Right droid 2

            (-80, 0),   # Right droid 2
            (-100, 20),   # Right droid 2
            (-120, 0),   # Right droid 2
            (-100, -20),   # Right droid 2

        ]

        # Droid group rotation - all droids rotate together with delay
        self.droid_group_rotation = 0.0
        self.droid_follow_speed = 3.0  # Lower = more lag, Higher = faster follow (per second)

        # Energy shield animation
        self.shield_timer = 0.0  # Timer for pulse trigger
        self.shield_pulse_progress = 0.0  # 0 to 1, pulse animation progress
        self.shield_rotation = 0.0  # Rotating hexagon pattern
        self.shield_scanline_offset = 0.0  # Moving scanlines

    def find_nearest_enemy(self, enemies):
        """Find the nearest enemy to target"""
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
        """Fire lasers from all gun positions"""
        if self.fire_cooldown > 0:
            return

        # Fire from each gun position
        for offset_x, offset_y in self.laser_offsets:
            # Rotate offset based on ship rotation
            rad = math.radians(self.rotation)
            rotated_x = offset_x * math.cos(rad) - offset_y * math.sin(rad)
            rotated_y = offset_x * math.sin(rad) + offset_y * math.cos(rad)

            # Calculate world position
            laser_x = self.world_x + rotated_x
            laser_y = self.world_y + rotated_y

            # Calculate laser angle
            if self.target_enemy:
                # If targeting, aim towards enemy center (converge to target)
                dx = self.target_enemy.world_x - laser_x
                dy = self.target_enemy.world_y - laser_y
                laser_angle = math.degrees(math.atan2(dy, dx))
            else:
                # If not targeting, use ship's rotation
                laser_angle = self.rotation

            # Create laser with calculated angle
            laser = Laser(laser_x, laser_y, laser_angle)
            self.lasers.append(laser)

        self.fire_cooldown = self.fire_rate

    def update(self, dt, info, enemies):
        keys = pygame.key.get_pressed()

        # Fire cooldown
        if self.fire_cooldown > 0:
            self.fire_cooldown -= dt

        # Fire lasers
        if keys[pygame.K_SPACE]:
            self.fire_laser()

        # Update lasers
        for laser in self.lasers[:]:
            laser.update(dt)
            if laser.lifetime <= 0:
                self.lasers.remove(laser)

        # Movement
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

        # Calculate rotation
        if self.target_enemy:
            # If targeting, rotate towards enemy
            dx = self.target_enemy.world_x - self.world_x
            dy = self.target_enemy.world_y - self.world_y
            target_rotation = math.degrees(math.atan2(dy, dx))

            # Calculate shortest angle difference
            angle_diff = target_rotation - self.rotation
            # Normalize to -180 to 180 range
            while angle_diff > 180:
                angle_diff -= 360
            while angle_diff < -180:
                angle_diff += 360

            self.rotation += angle_diff * 0.15  # Faster rotation when targeting
        elif move_x != 0 or move_y != 0:
            # If moving without target, rotate based on movement
            target_rotation = math.degrees(math.atan2(move_y, move_x))

            # Calculate shortest angle difference
            angle_diff = target_rotation - self.rotation
            # Normalize to -180 to 180 range
            while angle_diff > 180:
                angle_diff -= 360
            while angle_diff < -180:
                angle_diff += 360

            self.rotation += angle_diff * 0.1

        # Update stars based on movement
        current_map = info.get_current_map()
        for star in current_map.stars:
            star['x'] -= move_x * self.speed * dt * 0.3 * star['speed']
            star['y'] -= move_y * self.speed * dt * 0.3 * star['speed']

        # Update droid group rotation with smooth follow (lag effect)
        # Calculate shortest angle difference
        angle_diff = self.rotation - self.droid_group_rotation

        # Normalize to -180 to 180 range
        while angle_diff > 180:
            angle_diff -= 360
        while angle_diff < -180:
            angle_diff += 360

        # Smoothly interpolate toward target rotation
        self.droid_group_rotation += angle_diff * self.droid_follow_speed * dt

        # Update shield animation
        self.shield_timer += dt
        self.shield_rotation += dt * 30  # Rotate hexagon pattern slowly
        self.shield_scanline_offset += dt * 100  # Move scanlines

        # Trigger pulse every 2 seconds
        if self.shield_timer >= 2.0:
            self.shield_timer = 0.0
            self.shield_pulse_progress = 0.0

        # Update pulse animation (0 to 1, then stays at 1)
        if self.shield_pulse_progress < 1.0:
            self.shield_pulse_progress += dt * 2.0  # 0.5 second pulse duration
            if self.shield_pulse_progress > 1.0:
                self.shield_pulse_progress = 1.0

    def draw_shield(self, screen):
        """Draw hexagonal energy shield with pulse animation"""
        shield_radius = 60  # Base shield radius

        # Calculate pulse wave effect (0 = start of pulse, 1 = end)
        pulse_intensity = 1.0 - self.shield_pulse_progress  # Inverted for fade out
        pulse_expansion = self.shield_pulse_progress * 20  # Expands outward

        # Create shield surface with alpha
        shield_size = int((shield_radius + pulse_expansion) * 2 + 50)
        shield_surf = pygame.Surface((shield_size, shield_size), pygame.SRCALPHA)
        center = shield_size // 2

        # Draw hexagonal segments
        num_segments = 6
        for i in range(num_segments):
            angle = math.radians(self.shield_rotation + i * 60)

            # Hexagon vertices
            hex_points = []
            for j in range(6):
                hex_angle = angle + math.radians(j * 60)
                x = center + math.cos(hex_angle) * (shield_radius + pulse_expansion * 0.5)
                y = center + math.sin(hex_angle) * (shield_radius + pulse_expansion * 0.5)
                hex_points.append((x, y))

            # Draw hexagon outline with pulse effect
            hex_alpha = int(100 * pulse_intensity + 30)  # 30-130 alpha range
            hex_color = (0, 200, 255, hex_alpha)
            pygame.draw.polygon(shield_surf, hex_color, hex_points, 2)

            # Draw energy glow at vertices
            for point in hex_points:
                glow_alpha = int(150 * pulse_intensity + 50)
                pygame.draw.circle(shield_surf, (100, 220, 255, glow_alpha),
                                 (int(point[0]), int(point[1])), 3)

        # Draw main shield circle with glow
        for glow_layer in range(3, 0, -1):
            glow_radius = shield_radius + pulse_expansion + glow_layer * 8
            glow_alpha = int((80 / glow_layer) * pulse_intensity + 20)
            pygame.draw.circle(shield_surf, (50, 180, 255, glow_alpha),
                             (center, center), int(glow_radius), 2)

        # Draw energy core circle
        core_alpha = int(120 * pulse_intensity + 40)
        pygame.draw.circle(shield_surf, (150, 230, 255, core_alpha),
                         (center, center), int(shield_radius + pulse_expansion), 1)

        # Pulse wave ring (expands outward)
        if pulse_intensity > 0.3:
            wave_radius = shield_radius + pulse_expansion
            wave_alpha = int(200 * pulse_intensity)
            pygame.draw.circle(shield_surf, (150, 240, 255, wave_alpha),
                             (center, center), int(wave_radius), 3)

        # Blit shield to screen
        shield_x = self.x - center
        shield_y = self.y - center
        screen.blit(shield_surf, (int(shield_x), int(shield_y)))

    def draw(self, screen):
        # Draw shield first (behind everything)
        self.draw_shield(screen)

        # Draw droids
        for idx, (droid_offset_x, droid_offset_y) in enumerate(self.droid_positions):
            # Rotate offset based on droid group rotation (position follows with delay)
            rad = math.radians(self.droid_group_rotation)
            rotated_x = droid_offset_x * math.cos(rad) - droid_offset_y * math.sin(rad)
            rotated_y = droid_offset_x * math.sin(rad) + droid_offset_y * math.cos(rad)

            # Calculate screen position
            droid_x = self.x + rotated_x
            droid_y = self.y + rotated_y

            if Assets.droid_image:
                # Rotate droid image - use group's delayed rotation
                rotated_droid = pygame.transform.rotate(Assets.droid_image, -self.droid_group_rotation - 90)
                droid_rect = rotated_droid.get_rect(center=(int(droid_x), int(droid_y)))

                # Draw droid
                screen.blit(rotated_droid, droid_rect)
            else:
                # Fallback - draw circle if image not loaded
                pygame.draw.circle(screen, (255, 255, 0), (int(droid_x), int(droid_y)), 5)
                pygame.draw.circle(screen, (255, 100, 0), (int(droid_x), int(droid_y)), 3)

        # Draw ship
        if Assets.ship_5_image:
            # Use ship_5 image - rotate it
            # Ship image default is pointing up (90 degrees), pygame rotates counter-clockwise
            rotated_ship = pygame.transform.rotate(Assets.ship_5_image, -self.rotation - 90)
            ship_rect = rotated_ship.get_rect(center=(int(self.x), int(self.y)))

            # Draw ship image
            screen.blit(rotated_ship, ship_rect)
        else:
            # Fallback to triangle if image not loaded
            points = []
            for angle in [0, 140, 220]:
                rad = math.radians(angle + self.rotation)
                px = self.x + math.cos(rad) * self.size
                py = self.y + math.sin(rad) * self.size
                points.append((px, py))

            # Ship body
            pygame.draw.polygon(screen, (200, 220, 255), points)
            pygame.draw.polygon(screen, (255, 255, 255), points, 2)

    def check_portal_collision(self, portals):
        """Check if player is touching any portal"""
        for portal in portals:
            dx = self.world_x - portal.x
            dy = self.world_y - portal.y
            distance = math.sqrt(dx*dx + dy*dy)

            if distance < portal.radius + self.size:
                return portal
        return None

class UI:
    """UI elements"""
    @staticmethod
    def draw_minimap(screen, player, portals, enemies, info):
        """Draw minimap in top right corner"""
        minimap_size = 200
        minimap_x = Info.screenX - minimap_size - 20
        minimap_y = 20

        # Minimap background
        minimap_surf = pygame.Surface((minimap_size, minimap_size), pygame.SRCALPHA)
        pygame.draw.rect(minimap_surf, (20, 20, 40, 180), (0, 0, minimap_size, minimap_size))
        pygame.draw.rect(minimap_surf, (100, 100, 150, 200), (0, 0, minimap_size, minimap_size), 2)

        # Define minimap world bounds (how much world space to show)
        world_range = 3000  # Show 3000 units in each direction
        scale = minimap_size / (world_range * 2)

        # Center of minimap
        center_x = minimap_size // 2
        center_y = minimap_size // 2

        # Draw portals on minimap
        for portal in portals:
            # Calculate portal position relative to player
            rel_x = portal.x - player.world_x
            rel_y = portal.y - player.world_y

            # Scale to minimap
            map_x = center_x + rel_x * scale
            map_y = center_y + rel_y * scale

            # Only draw if in minimap bounds
            if 0 <= map_x <= minimap_size and 0 <= map_y <= minimap_size:
                pygame.draw.circle(minimap_surf, portal.color, (int(map_x), int(map_y)), 5)
                # Portal ring
                pygame.draw.circle(minimap_surf, portal.color, (int(map_x), int(map_y)), 8, 1)

        # Draw enemies on minimap
        for enemy in enemies:
            # Calculate enemy position relative to player
            rel_x = enemy.world_x - player.world_x
            rel_y = enemy.world_y - player.world_y

            # Scale to minimap
            map_x = center_x + rel_x * scale
            map_y = center_y + rel_y * scale

            # Only draw if in minimap bounds
            if 0 <= map_x <= minimap_size and 0 <= map_y <= minimap_size:
                pygame.draw.circle(minimap_surf, (255, 100, 100), (int(map_x), int(map_y)), 3)

        # Draw player at center (always visible)
        pygame.draw.circle(minimap_surf, (0, 255, 0), (center_x, center_y), 4)
        pygame.draw.circle(minimap_surf, (255, 255, 255), (center_x, center_y), 6, 1)

        # Draw minimap title
        current_map = info.get_current_map()
        font = pygame.font.Font(None, 24)
        title = font.render("MAP", True, (200, 200, 200))
        minimap_surf.blit(title, (minimap_size // 2 - 20, 5))

        screen.blit(minimap_surf, (minimap_x, minimap_y))

    @staticmethod
    def draw_hud(screen, info, player):
        font = pygame.font.Font(None, 40)
        small_font = pygame.font.Font(None, 30)

        # Current map name
        current_map = info.get_current_map()
        map_text = font.render(f"Sector: {current_map.name}", True, (255, 255, 255))
        screen.blit(map_text, (20, 20))

        # Coordinates
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

        # Controls
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
        """Draw warp tunnel effect"""
        overlay = pygame.Surface((Info.screenX, Info.screenY), pygame.SRCALPHA)

        # Radial lines
        center_x = Info.screenX // 2
        center_y = Info.screenY // 2

        for i in range(20):
            angle = (i / 20) * math.pi * 2 + progress * 5

            # Start from edge
            start_dist = Info.screenX * (1 - progress)
            end_dist = Info.screenX * 0.3

            start_x = center_x + math.cos(angle) * start_dist
            start_y = center_y + math.sin(angle) * start_dist
            end_x = center_x + math.cos(angle) * end_dist
            end_y = center_y + math.sin(angle) * end_dist

            alpha = int(255 * progress)
            pygame.draw.line(overlay, (100, 150, 255, alpha), (start_x, start_y), (end_x, end_y), 3)

        # Vignette
        vignette_alpha = int(200 * progress)
        pygame.draw.rect(overlay, (0, 0, 50, vignette_alpha), (0, 0, Info.screenX, Info.screenY))

        screen.blit(overlay, (0, 0))

        # Warp text
        if progress > 0.3:
            font = pygame.font.Font(None, 80)
            text = font.render("WARPING...", True, (150, 200, 255, int(255 * progress)))
            text_rect = text.get_rect(center=(Info.screenX // 2, Info.screenY // 2))
            screen.blit(text, text_rect)

def create_portals_for_map(map_key):
    """Create portals for a specific map"""
    portals = []

    if map_key == 'nebula':
        # Portal to asteroid field (right)
        portals.append(Portal(1500, 0, 'asteroid', (100, 255, 100)))
        # Portal to deep space (top)
        portals.append(Portal(0, -1500, 'deep_space', (150, 150, 255)))

    elif map_key == 'asteroid':
        # Portal to nebula (left)
        portals.append(Portal(-1500, 0, 'nebula', (255, 100, 150)))
        # Portal to deep space (top-right)
        portals.append(Portal(1000, -1000, 'deep_space', (150, 150, 255)))

    elif map_key == 'deep_space':
        # Portal to nebula (bottom)
        portals.append(Portal(0, 1500, 'nebula', (255, 100, 150)))
        # Portal to asteroid (bottom-left)
        portals.append(Portal(-1000, 1000, 'asteroid', (100, 255, 100)))

    return portals

def create_enemies_for_map(map_key):
    """Create enemies for a specific map"""
    enemies = []

    if map_key == 'nebula':
        # Spawn enemies around the nebula
        enemies.append(Enemy(800, 500, 400))
        enemies.append(Enemy(-600, -400, 350))
        enemies.append(Enemy(300, -700, 450))
        enemies.append(Enemy(-900, 600, 400))

    elif map_key == 'asteroid':
        # Spawn enemies in asteroid field
        enemies.append(Enemy(500, 600, 500))
        enemies.append(Enemy(-800, 300, 400))
        enemies.append(Enemy(600, -500, 450))
        enemies.append(Enemy(-400, -700, 350))
        enemies.append(Enemy(0, 800, 400))

    elif map_key == 'deep_space':
        # Spawn enemies in deep space
        enemies.append(Enemy(700, -600, 500))
        enemies.append(Enemy(-500, 700, 400))
        enemies.append(Enemy(900, 400, 450))
        enemies.append(Enemy(-700, -500, 400))
        enemies.append(Enemy(200, 900, 350))
        enemies.append(Enemy(-900, -200, 400))

    return enemies

# Initialize Pygame
screen = pygame.display.set_mode((Info.screenX, Info.screenY))
pygame.display.set_caption("Space Explorer - 3 Sector Universe")

# Load assets
Assets.load_assets()

# Initialize game objects
info = Info()
player = Player()
portals = create_portals_for_map(Assets.current_map)
enemies = create_enemies_for_map(Assets.current_map)

# Game loop
while True:
    info.update_time()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            Exiting.quit_game()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                Exiting.quit_game()
            elif event.key == pygame.K_q:
                # Toggle target lock
                if player.target_enemy:
                    # If already targeting, clear target
                    player.target_enemy = None
                else:
                    # Find and lock nearest enemy
                    player.target_enemy = player.find_nearest_enemy(enemies)

    # Update
    if info.game_state == "Exploring":
        player.update(info.dt, info, enemies)
        info.update_stars(player)

        # Update portals
        for portal in portals:
            portal.update(info.dt)

        # Update enemies
        for enemy in enemies:
            enemy.update(info.dt)

        # Check laser collisions with enemies
        for laser in player.lasers[:]:
            for enemy in enemies[:]:
                if laser.check_collision(enemy):
                    # Apply damage to enemy
                    is_destroyed = enemy.take_damage(laser.damage)

                    # Remove laser on hit
                    if laser in player.lasers:
                        player.lasers.remove(laser)

                    # Remove enemy if destroyed
                    if is_destroyed and enemy in enemies:
                        # Clear target if this enemy was targeted
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
        info.warp_progress += info.dt * 1.5

        if info.warp_progress >= 1.0:
            # Switch map
            Assets.current_map = info.warp_target
            portals = create_portals_for_map(Assets.current_map)
            enemies = create_enemies_for_map(Assets.current_map)

            # Reset player position near center
            player.world_x = 0
            player.world_y = 0
            player.target_enemy = None  # Clear target when changing maps

            # Reset droid group rotation to match ship
            player.droid_group_rotation = player.rotation

            info.game_state = "WarpingIn"
            info.warp_progress = 1.0

    elif info.game_state == "WarpingIn":
        info.warp_progress -= info.dt * 1.5

        if info.warp_progress <= 0:
            info.game_state = "Exploring"
            info.warp_progress = 0

    # Draw
    current_map = info.get_current_map()
    screen.fill(current_map.bg_color)

    # Draw stars
    info.draw_stars(screen)

    # Draw portals
    for portal in portals:
        portal.draw(screen, info.camera_x, info.camera_y)

    # Draw enemies
    for enemy in enemies:
        enemy.draw(screen, info.camera_x, info.camera_y)

        # Draw target indicator if this enemy is targeted
        if player.target_enemy == enemy:
            draw_x = enemy.world_x - info.camera_x
            draw_y = enemy.world_y - info.camera_y

            if -100 < draw_x < Info.screenX + 100 and -100 < draw_y < Info.screenY + 100:
                # Draw red brackets around target
                bracket_size = 40
                pygame.draw.line(screen, (255, 50, 50),
                               (draw_x - bracket_size, draw_y - bracket_size),
                               (draw_x - bracket_size + 15, draw_y - bracket_size), 3)
                pygame.draw.line(screen, (255, 50, 50),
                               (draw_x - bracket_size, draw_y - bracket_size),
                               (draw_x - bracket_size, draw_y - bracket_size + 15), 3)

                pygame.draw.line(screen, (255, 50, 50),
                               (draw_x + bracket_size, draw_y - bracket_size),
                               (draw_x + bracket_size - 15, draw_y - bracket_size), 3)
                pygame.draw.line(screen, (255, 50, 50),
                               (draw_x + bracket_size, draw_y - bracket_size),
                               (draw_x + bracket_size, draw_y - bracket_size + 15), 3)

                pygame.draw.line(screen, (255, 50, 50),
                               (draw_x - bracket_size, draw_y + bracket_size),
                               (draw_x - bracket_size + 15, draw_y + bracket_size), 3)
                pygame.draw.line(screen, (255, 50, 50),
                               (draw_x - bracket_size, draw_y + bracket_size),
                               (draw_x - bracket_size, draw_y + bracket_size - 15), 3)

                pygame.draw.line(screen, (255, 50, 50),
                               (draw_x + bracket_size, draw_y + bracket_size),
                               (draw_x + bracket_size - 15, draw_y + bracket_size), 3)
                pygame.draw.line(screen, (255, 50, 50),
                               (draw_x + bracket_size, draw_y + bracket_size),
                               (draw_x + bracket_size, draw_y + bracket_size - 15), 3)

    # Draw player
    player.draw(screen)

    # Draw lasers (on top of player)
    for laser in player.lasers:
        laser.draw(screen, info.camera_x, info.camera_y)

    # Draw UI
    UI.draw_hud(screen, info, player)

    # Draw minimap
    UI.draw_minimap(screen, player, portals, enemies, info)

    # Draw warp effect
    if info.game_state in ["WarpingOut", "WarpingIn"]:
        UI.draw_warp_effect(screen, info.warp_progress)

    pygame.display.flip()
