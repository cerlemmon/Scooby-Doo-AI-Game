# Neighborhood class (for suburban area)
class Neighborhood:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.road_map = []  # 2D grid to track roads
        self.house_positions = []  # List of house coordinates
        self.street_lights = []  # List of street light coordinates
        self.exit_position = (0, 0)  # Position of exit to highway
        
        # Generate neighborhood layout
        self.generate_layout()
        
    def generate_layout(self):
        # Initialize grid with no roads
        self.road_map = [[False for _ in range(self.height // TILE_SIZE)] for _ in range(self.width // TILE_SIZE)]
        
        # Start with main roads (grid pattern)
        # Create horizontal roads
        for y in range(3, self.height // TILE_SIZE - 3, 6):
            for x in range(self.width // TILE_SIZE):
                self.road_map[x][y] = True
                
        # Create vertical roads
        for x in range(3, self.width // TILE_SIZE - 3, 6):
            for y in range(self.height // TILE_SIZE):
                self.road_map[x][y] = True
        
        # Create some curved/diagonal roads to make it more interesting
        for _ in range(3):
            start_x = random.randint(6, self.width // TILE_SIZE - 12)
            start_y = random.randint(6, self.height // TILE_SIZE - 12)
            length = random.randint(5, 10)
            
            # Direction of road (curved)
            for i in range(length):
                # Create a simple curved path
                x = min(self.width // TILE_SIZE - 1, start_x + i)
                y = min(self.height // TILE_SIZE - 1, start_y + int(i * 0.5))
                self.road_map[x][y] = True
        
        # Connect some dead-ends
        for x in range(1, self.width // TILE_SIZE - 1):
            for y in range(1, self.height // TILE_SIZE - 1):
                # Look for "T" junctions and connect them
                if (self.road_map[x][y] and 
                    self.road_map[x+1][y] and 
                    self.road_map[x-1][y] and
                    not self.road_map[x][y+1] and
                    not self.road_map[x][y-1]):
                    if random.random() < 0.3:  # 30% chance to extend
                        self.road_map[x][y+1] = True
        
        # Place houses around the roads
        self.place_houses()
        
        # Place street lights along the roads
        self.place_street_lights()
        
        # Create exit to highway (on the right edge)
        exit_y = None
        for y in range(self.height // TILE_SIZE):
            if self.road_map[self.width // TILE_SIZE - 1][y]:
                exit_y = y
                break
                
        if exit_y is not None:
            self.exit_position = (self.width - TILE_SIZE, exit_y * TILE_SIZE)
        else:
            # Fallback if no road leads to right edge
            self.exit_position = (self.width - TILE_SIZE, self.height // 2)
            # Create a path to the exit
            for x in range(self.width // TILE_SIZE - 5, self.width // TILE_SIZE):
                self.road_map[x][self.height // (2 * TILE_SIZE)] = True
    
    def place_houses(self):
        # Place houses adjacent to roads but not on them
        for x in range(1, self.width // TILE_SIZE - 3):
            for y in range(1, self.height // TILE_SIZE - 3):
                # Make sure this position is not a road
                if not self.road_map[x][y] and not self.road_map[x+1][y]:
                    # Check if there's a road nearby
                    has_road_nearby = False
                    for dx in range(-1, 3):
                        for dy in range(-1, 3):
                            nx, ny = x + dx, y + dy
                            if (0 <= nx < self.width // TILE_SIZE and 
                                0 <= ny < self.height // TILE_SIZE and
                                self.road_map[nx][ny]):
                                has_road_nearby = True
                                break
                                
                    if has_road_nearby and random.random() < 0.15:  # Control house density
                        # Make sure houses aren't too close to each other
                        too_close = False
                        for hx, hy in self.house_positions:
                            if abs(hx - x*TILE_SIZE) < TILE_SIZE*3 and abs(hy - y*TILE_SIZE) < TILE_SIZE*3:
                                too_close = True
                                break
                                
                        if not too_close:
                            self.house_positions.append((x*TILE_SIZE, y*TILE_SIZE))
                            
    def place_street_lights(self):
        # Place street lights along roads
        for x in range(self.width // TILE_SIZE):
            for y in range(self.height // TILE_SIZE):
                if self.road_map[x][y] and random.random() < 0.1:  # 10% chance for each road tile
                    self.street_lights.append((x*TILE_SIZE, y*TILE_SIZE))
                    
    def is_road(self, x, y):
        # Convert pixel coordinates to grid coordinates
        grid_x = int(x // TILE_SIZE)
        grid_y = int(y // TILE_SIZE)
    
        # Check bounds
        if (0 <= grid_x < self.width // TILE_SIZE and 
            0 <= grid_y < self.height // TILE_SIZE):
            return self.road_map[grid_x][grid_y]
        return False
        
    def draw(self, screen, camera_x, camera_y):
        # Draw sky background
        screen.blit(SKY_IMG, (0, 0))
        
        # Draw ground/grass everywhere first
        ground_width, ground_height = GROUND_IMG.get_width(), GROUND_IMG.get_height()
        for x in range(0, SCREEN_WIDTH, ground_width):
            for y in range(0, SCREEN_HEIGHT, ground_height):
                offset_x = (camera_x // 3) % ground_width
                offset_y = (camera_y // 3) % ground_height
                screen.blit(GROUND_IMG, (x - offset_x, y - offset_y))
        
        # Draw roads
        for x in range(self.width // TILE_SIZE):
            for y in range(self.height // TILE_SIZE):
                if self.road_map[x][y]:
                    # Calculate screen position
                    screen_x = x * TILE_SIZE - camera_x
                    screen_y = y * TILE_SIZE - camera_y
                    
                    # Only draw if visible on screen
                    if (-TILE_SIZE < screen_x < SCREEN_WIDTH and 
                        -TILE_SIZE < screen_y < SCREEN_HEIGHT):
                        screen.blit(ROAD_IMG, (screen_x, screen_y))
        
        # Draw highway exit
        exit_x, exit_y = self.exit_position
        screen_exit_x = exit_x - camera_x
        screen_exit_y = exit_y - camera_y
        if (-TILE_SIZE < screen_exit_x < SCREEN_WIDTH and 
            -TILE_SIZE < screen_exit_y < SCREEN_HEIGHT):
            screen.blit(HIGHWAY_IMG, (screen_exit_x, screen_exit_y))
            
            # Draw "EXIT" sign
            exit_sign = pygame.font.SysFont(None, 20).render("EXIT", True, (0, 200, 0))
            screen.blit(exit_sign, (screen_exit_x + 10, screen_exit_y + 5))
        
        # Draw houses
        for house_x, house_y in self.house_positions:
            screen_house_x = house_x - camera_x
            screen_house_y = house_y - camera_y
            
            if (-TILE_SIZE*2 < screen_house_x < SCREEN_WIDTH and 
                -TILE_SIZE*2 < screen_house_y < SCREEN_HEIGHT):
                # Use a random house design from our house images
                house_idx = (house_x // TILE_SIZE + house_y // TILE_SIZE) % len(HOUSE_IMGS)
                screen.blit(HOUSE_IMGS[house_idx], (screen_house_x, screen_house_y))
        
        # Draw street lights
        for light_x, light_y in self.street_lights:
            screen_light_x = light_x - camera_x
            screen_light_y = light_y - camera_y
            
            if (-TILE_SIZE < screen_light_x < SCREEN_WIDTH and 
                -TILE_SIZE < screen_light_y < SCREEN_HEIGHT):
                screen.blit(STREET_LIGHT_IMG, (screen_light_x, screen_light_y))

# Highway class (for escape sequence)
class Highway:
    def __init__(self, length):
        self.length = length
        self.width = TILE_SIZE * 5  # 5 lanes
        self.obstacles = []  # List of [position, lane_y]
        
        # Generate some obstacles
        self.generate_obstacles()
        
    def generate_obstacles(self):
        # Add cars and other obstacles along the highway
        for i in range(0, self.length, TILE_SIZE*3):
            if random.random() < 0.3:  # 30% chance for an obstacle
                lane = random.randint(0, 4)  # 5 lanes
                self.obstacles.append([i, lane * TILE_SIZE])  # Use list instead of tuple
                
    def handle_collisions(self, vehicle_x, vehicle_y, vehicle_width, vehicle_height, position):
        for obs in self.obstacles:
            obs_pos, obs_lane = obs
            rel_pos = obs_pos - position
            if 0 <= rel_pos < SCREEN_WIDTH:
                obs_rect = pygame.Rect(rel_pos, SCREEN_HEIGHT // 3 + obs_lane, TILE_SIZE*2, TILE_SIZE)
                vehicle_rect = pygame.Rect(vehicle_x, vehicle_y, vehicle_width, vehicle_height)
                if obs_rect.colliderect(vehicle_rect):
                    # Move obstacle to an adjacent lane
                    current_lane = obs_lane // TILE_SIZE  # Lane index (0-4)
                    possible_lanes = []
                    if current_lane > 0:
                        possible_lanes.append(current_lane - 1)  # Up
                    if current_lane < 4:
                        possible_lanes.append(current_lane + 1)  # Down
                    if possible_lanes:
                        new_lane = random.choice(possible_lanes)
                        obs[1] = new_lane * TILE_SIZE  # Update lane position
                
    def draw(self, screen, position):
        # Draw the highway (position is how far along the highway we've traveled)
        visible_length = SCREEN_WIDTH
        
        # Draw sky
        screen.blit(SKY_IMG, (0, 0))
        
        # Draw grass on sides
        pygame.draw.rect(screen, (50, 100, 60), (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT // 3))
        pygame.draw.rect(screen, (50, 100, 60), (0, SCREEN_HEIGHT * 2 // 3, SCREEN_WIDTH, SCREEN_HEIGHT // 3))
        
        # Draw highway surface
        pygame.draw.rect(screen, (40, 40, 45), (0, SCREEN_HEIGHT // 3, SCREEN_WIDTH, SCREEN_HEIGHT // 3))
        
        # Draw lane markings
        for i in range(0, visible_length + TILE_SIZE, TILE_SIZE):
            # Adjust for position to create scrolling effect
            x_pos = i - (position % TILE_SIZE)
            
            # Center line (solid yellow)
            pygame.draw.rect(screen, (255, 255, 0), (x_pos, SCREEN_HEIGHT // 2, TILE_SIZE // 2, 4))
            
            # Other lines (dashed white)
            for lane in range(1, 3):
                lane_y = SCREEN_HEIGHT // 3 + lane * (SCREEN_HEIGHT // 9)
                # Create dashed effect
                if (i // TILE_SIZE) % 2 == 0:
                    pygame.draw.rect(screen, (255, 255, 255), (x_pos, lane_y, TILE_SIZE // 2, 2))
                    
        # Draw obstacles
        for obs_pos, obs_lane in self.obstacles:
            # Calculate screen position of obstacle
            screen_x = obs_pos - position
            screen_y = SCREEN_HEIGHT // 3 + obs_lane
            
            if 0 <= screen_x < SCREEN_WIDTH:
                # Draw car or other obstacle
                pygame.draw.rect(screen, (0, 0, 0), (screen_x, screen_y, TILE_SIZE*2, TILE_SIZE))
                pygame.draw.rect(screen, (200, 0, 0), (screen_x+2, screen_y+2, TILE_SIZE*2-4, TILE_SIZE-4))
                # Windows
                pygame.draw.rect(screen, (100, 200, 255), (screen_x+4, screen_y+5, TILE_SIZE//2, TILE_SIZE//2-2))
                pygame.draw.rect(screen, (100, 200, 255), (screen_x+TILE_SIZE, screen_y+5, TILE_SIZE//2, TILE_SIZE//2-2))
        
        # Draw side elements (trees, signs, etc.)
        for i in range(0, visible_length + TILE_SIZE, TILE_SIZE*4):
            # Adjust for position to create scrolling effect
            x_pos = i - (position % (TILE_SIZE*4))
            
            # Trees on sides
            screen.blit(pygame.transform.scale(TREE_IMG, (TILE_SIZE*2, TILE_SIZE*2)), 
                      (x_pos, SCREEN_HEIGHT // 6))
            screen.blit(pygame.transform.scale(TREE_IMG, (TILE_SIZE*2, TILE_SIZE*2)), 
                      (x_pos + TILE_SIZE*2, SCREEN_HEIGHT * 2 // 3))
            
            # Occasional road sign
            if random.random() < 0.3:
                pygame.draw.rect(screen, (100, 100, 100), (x_pos + TILE_SIZE, SCREEN_HEIGHT // 4, 5, TILE_SIZE))
                pygame.draw.rect(screen, (255, 255, 255), (x_pos + TILE_SIZE - 10, SCREEN_HEIGHT // 4 - 20, 25, 20))
                
        # Draw distance marker
        remaining = max(0, (self.length - position) // TILE_SIZE)
        distance_text = pygame.font.SysFont(None, 30).render(f"Distance: {remaining}", True, (255, 255, 255))
        screen.blit(distance_text, (SCREEN_WIDTH - 150, 20))
    
    def check_collision(self, x, y, width, height, position):
        # Check if the vehicle (at position) collides with any obstacle
        for obs_pos, obs_lane in self.obstacles:
            # Calculate relative position
            rel_pos = obs_pos - position
            
            # If obstacle is on screen and overlaps with vehicle
            if (0 <= rel_pos < SCREEN_WIDTH and
                x < rel_pos + TILE_SIZE*2 and
                x + width > rel_pos and
                y < SCREEN_HEIGHT // 3 + obs_lane + TILE_SIZE and
                y + height > SCREEN_HEIGHT // 3 + obs_lane):
                return True
                
        return False

# Boss Monster class (for chase sequence)
class BossMonster:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = TILE_SIZE*2
        self.height = TILE_SIZE*2
        self.speed = MONSTER_SPEED * 1.2  # Slightly faster than regular monsters
        self.image = BOSS_MONSTER_IMG
        self.rect = pygame.Rect(x, y, self.width, self.height)
        
    def update(self, target_x, target_y, neighborhood):
        # Calculate direction to target
        dx = target_x - self.x
        dy = target_y - self.y
        
        # Calculate distance
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance > 0:
            # Normalize direction
            dx /= distance
            dy /= distance
            
            # Move towards target
            new_x = self.x + dx * self.speed
            new_y = self.y + dy * self.speed
            
            # Try to stay on roads when possible
            if neighborhood.is_road(new_x + self.width//2, new_y + self.height//2):
                self.x = new_x
                self.y = new_y
            else:
                # Try each direction separately
                if neighborhood.is_road(new_x + self.width//2, self.y + self.height//2):
                    self.x = new_x
                elif neighborhood.is_road(self.x + self.width//2, new_y + self.height//2):
                    self.y = new_y
                else:
                    # If no road available, just move slower
                    self.x += dx * self.speed * 0.5
                    self.y += dy * self.speed * 0.5
        
        # Update rectangle
        self.rect.x = self.x
        self.rect.y = self.y
        
    def draw(self, screen, camera_x, camera_y):
        screen.blit(self.image, (self.x - camera_x, self.y - camera_y))
        
    def collides_with(self, other):
        return self.rect.colliderect(other.rect)
import pygame
import random
import sys
import os
import math
from enum import Enum

# Initialize pygame
pygame.init()
pygame.mixer.init()

# Game constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TILE_SIZE = 50
PLAYER_SPEED = 3
MONSTER_SPEED = 1.5
FRIEND_SPEED = 2.5
FONT_SIZE = 24
SCOOBY_SNACK_BOOST_DURATION = 5000  # 5 seconds in milliseconds
MONSTER_STUN_DURATION = 6000  # 6 seconds

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 128, 0)
DARK_GREEN = (0, 100, 0)
BROWN = (139, 69, 19)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)

# Initialize the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Scooby Doo: Forest Rescue")

# Load images
def load_image(filename, width, height):
    try:
        image = pygame.image.load(os.path.join("assets", filename))
        return pygame.transform.scale(image, (width, height))
    except:
        # If image can't be loaded, create a colored rectangle as a placeholder
        surface = pygame.Surface((width, height))
        surface.fill(YELLOW)  # Default color for Scooby
        pygame.draw.rect(surface, BLACK, (0, 0, width, height), 2)
        return surface

# Character images - these would be replaced with actual assets
SCOOBY_IMG = load_image("scooby.png", TILE_SIZE, TILE_SIZE)
SHAGGY_IMG = load_image("shaggy.png", TILE_SIZE, TILE_SIZE)
VELMA_IMG = load_image("velma.png", TILE_SIZE, TILE_SIZE)
DAPHNE_IMG = load_image("daphne.png", TILE_SIZE, TILE_SIZE)
FRED_IMG = load_image("fred.png", TILE_SIZE, TILE_SIZE)
MONSTER_IMG = load_image("monster.png", TILE_SIZE, TILE_SIZE)
MYSTERY_MACHINE_IMG = load_image("mystery_machine.png", TILE_SIZE*2, TILE_SIZE)
SCOOBY_SNACK_IMG = load_image("scooby_snack.png", TILE_SIZE//2, TILE_SIZE//2)
TRAP_IMG = load_image("trap.png", TILE_SIZE//2, TILE_SIZE//2)

# Create 90s style pixel art images
def create_pixel_art_images():
    global SCOOBY_IMG, SHAGGY_IMG, VELMA_IMG, DAPHNE_IMG, FRED_IMG
    global MONSTER_IMG, MYSTERY_MACHINE_IMG, SCOOBY_SNACK_IMG, TRAP_IMG
    global TREE_IMG, GROUND_IMG, SKY_IMG, ROAD_IMG, HOUSE_IMGS, BOSS_MONSTER_IMG
    global HIGHWAY_IMG, STREET_LIGHT_IMG, MYSTERY_MACHINE_DRIVING_IMG
    
    # 90s style color palette
    SCOOBY_BROWN = (139, 101, 8)
    SCOOBY_COLLAR = (0, 162, 232)
    SHAGGY_GREEN = (113, 143, 65)
    SHAGGY_HAIR = (184, 134, 11)
    VELMA_ORANGE = (255, 127, 39)
    VELMA_RED = (204, 51, 51)
    DAPHNE_PURPLE = (204, 0, 204)
    DAPHNE_HAIR_RED = (230, 115, 0)
    FRED_BLUE = (51, 102, 255)
    FRED_HAIR_BLONDE = (255, 215, 0)
    
    # Create sky and ground textures
    SKY_IMG = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    SKY_GRADIENT = [
    (70, 130, 180),   # Deep blue at top
    (120, 150, 200),  # Transition blue
    (255, 150, 100),  # Orange sunset color
    (255, 120, 80),   # Warm orange/pink
    (200, 100, 100)   # Pink/purple horizon
]
    for y in range(SCREEN_HEIGHT):
        # Create a gradient effect
        color_idx = min(int(y / SCREEN_HEIGHT * len(SKY_GRADIENT)), len(SKY_GRADIENT) - 1)
        pygame.draw.line(SKY_IMG, SKY_GRADIENT[color_idx], (0, y), (SCREEN_WIDTH, y))
    
    # Create a pixel art ground texture (16x16 pixels repeating)
    GROUND_IMG = pygame.Surface((16, 16))
    GROUND_IMG.fill((100, 120, 40))  # Warmer green base with evening sun
    # Add some pixel variation

    for _ in range(10):
        px, py = random.randint(0, 15), random.randint(0, 15)
        GROUND_IMG.set_at((px, py), (85, 105, 35))  # Slightly darker warm green

    # Add some "evening sunlight" highlights to the ground
    for _ in range(5):
        px, py = random.randint(0, 15), random.randint(0, 15)
        GROUND_IMG.set_at((px, py), (160, 140, 60))  # Golden/amber highlights
    
    # Create Scooby pixel art
    SCOOBY_IMG = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
    # Body
    pygame.draw.rect(SCOOBY_IMG, SCOOBY_BROWN, (5, 10, TILE_SIZE-10, TILE_SIZE-15))
    # Head
    pygame.draw.rect(SCOOBY_IMG, SCOOBY_BROWN, (TILE_SIZE-20, 5, 15, 15))
    # Ears
    pygame.draw.rect(SCOOBY_IMG, SCOOBY_BROWN, (TILE_SIZE-18, 0, 5, 8))
    pygame.draw.rect(SCOOBY_IMG, SCOOBY_BROWN, (TILE_SIZE-10, 0, 5, 8))
    # Eyes
    pygame.draw.rect(SCOOBY_IMG, WHITE, (TILE_SIZE-18, 7, 4, 4))
    pygame.draw.rect(SCOOBY_IMG, WHITE, (TILE_SIZE-10, 7, 4, 4))
    pygame.draw.rect(SCOOBY_IMG, BLACK, (TILE_SIZE-17, 8, 2, 2))
    pygame.draw.rect(SCOOBY_IMG, BLACK, (TILE_SIZE-9, 8, 2, 2))
    # Nose
    pygame.draw.rect(SCOOBY_IMG, BLACK, (TILE_SIZE-15, 12, 4, 4))
    # Spots
    for _ in range(6):
        spot_x = random.randint(7, TILE_SIZE-12)
        spot_y = random.randint(15, TILE_SIZE-8)
        spot_size = random.randint(3, 5)
        pygame.draw.rect(SCOOBY_IMG, (84, 60, 4), (spot_x, spot_y, spot_size, spot_size))
    # Collar
    pygame.draw.rect(SCOOBY_IMG, SCOOBY_COLLAR, (5, TILE_SIZE-20, TILE_SIZE-15, 5))
    pygame.draw.rect(SCOOBY_IMG, YELLOW, (TILE_SIZE//2-3, TILE_SIZE-18, 6, 6))
    
    # Create Shaggy pixel art
    SHAGGY_IMG = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
    # Body
    pygame.draw.rect(SHAGGY_IMG, SHAGGY_GREEN, (10, 20, TILE_SIZE-20, TILE_SIZE-25))
    # Head
    pygame.draw.rect(SHAGGY_IMG, (255, 213, 170), (10, 5, TILE_SIZE-20, 15))
    # Hair
    for y in range(3, 13):
        hair_width = 5 + int(abs(y - 8) * 1.5)
        pygame.draw.rect(SHAGGY_IMG, SHAGGY_HAIR, (10-hair_width, y, hair_width, 1))
        pygame.draw.rect(SHAGGY_IMG, SHAGGY_HAIR, (TILE_SIZE-10, y, hair_width, 1))
    pygame.draw.rect(SHAGGY_IMG, SHAGGY_HAIR, (5, 0, TILE_SIZE-10, 6))
    # Face
    pygame.draw.rect(SHAGGY_IMG, BLACK, (15, 10, 2, 2))  # Eyes
    pygame.draw.rect(SHAGGY_IMG, BLACK, (TILE_SIZE-17, 10, 2, 2))
    pygame.draw.rect(SHAGGY_IMG, (255, 150, 150), (18, 15, 4, 2))  # Mouth
    
    # Create Velma pixel art
    VELMA_IMG = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
    # Body
    pygame.draw.rect(VELMA_IMG, VELMA_ORANGE, (10, 20, TILE_SIZE-20, TILE_SIZE-25))
    # Head
    pygame.draw.rect(VELMA_IMG, (255, 213, 170), (10, 5, TILE_SIZE-20, 15))
    # Hair
    pygame.draw.rect(VELMA_IMG, (139, 69, 19), (8, 3, TILE_SIZE-16, 7))
    # Glasses
    pygame.draw.rect(VELMA_IMG, BLACK, (12, 10, 8, 5), 1)
    pygame.draw.rect(VELMA_IMG, BLACK, (TILE_SIZE-20, 10, 8, 5), 1)
    pygame.draw.line(VELMA_IMG, BLACK, (20, 12), (TILE_SIZE-20, 12), 1)
    # Face
    pygame.draw.rect(VELMA_IMG, VELMA_RED, (18, 18, 4, 2))  # Mouth
    
    # Create Daphne pixel art
    DAPHNE_IMG = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
    # Body
    pygame.draw.rect(DAPHNE_IMG, DAPHNE_PURPLE, (10, 20, TILE_SIZE-20, TILE_SIZE-25))
    # Head
    pygame.draw.rect(DAPHNE_IMG, (255, 213, 170), (10, 5, TILE_SIZE-20, 15))
    # Hair
    for y in range(2, 18):
        hair_width = 8 - abs(y - 10) // 2
        pygame.draw.rect(DAPHNE_IMG, DAPHNE_HAIR_RED, (10-hair_width, y, hair_width, 1))
        pygame.draw.rect(DAPHNE_IMG, DAPHNE_HAIR_RED, (TILE_SIZE-10, y, hair_width, 1))
    pygame.draw.rect(DAPHNE_IMG, DAPHNE_HAIR_RED, (7, 0, TILE_SIZE-14, 5))
    # Face
    pygame.draw.rect(DAPHNE_IMG, (0, 0, 0), (15, 10, 2, 2))  # Eyes
    pygame.draw.rect(DAPHNE_IMG, (0, 0, 0), (TILE_SIZE-17, 10, 2, 2))
    pygame.draw.rect(DAPHNE_IMG, (255, 100, 100), (18, 15, 4, 2))  # Lips
    
    # Create Fred pixel art
    FRED_IMG = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
    # Body
    pygame.draw.rect(FRED_IMG, FRED_BLUE, (10, 20, TILE_SIZE-20, TILE_SIZE-25))
    # White collar
    pygame.draw.rect(FRED_IMG, WHITE, (13, 18, TILE_SIZE-26, 5))
    # Head
    pygame.draw.rect(FRED_IMG, (255, 213, 170), (10, 5, TILE_SIZE-20, 15))
    # Hair
    pygame.draw.rect(FRED_IMG, FRED_HAIR_BLONDE, (8, 2, TILE_SIZE-16, 6))
    pygame.draw.rect(FRED_IMG, FRED_HAIR_BLONDE, (5, 5, 10, 3))  # Side swept look
    # Face
    pygame.draw.rect(FRED_IMG, BLACK, (15, 10, 2, 2))  # Eyes
    pygame.draw.rect(FRED_IMG, BLACK, (TILE_SIZE-17, 10, 2, 2))
    pygame.draw.rect(FRED_IMG, (255, 150, 150), (18, 15, 4, 2))  # Mouth
    
    # Create Monster pixel art (ghost-like)
    MONSTER_IMG = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
    # Ghost body
    monster_color = (150, 0, 0)  # Dark red
    points = [
        (TILE_SIZE//2, 5),                 # Top
        (5, TILE_SIZE//2),                 # Left middle
        (TILE_SIZE//4, TILE_SIZE-10),      # Bottom left
        (TILE_SIZE//2, TILE_SIZE-5),       # Bottom middle
        (TILE_SIZE*3//4, TILE_SIZE-10),    # Bottom right
        (TILE_SIZE-5, TILE_SIZE//2)        # Right middle
    ]
    pygame.draw.polygon(MONSTER_IMG, monster_color, points)
    # Eyes
    pygame.draw.rect(MONSTER_IMG, WHITE, (TILE_SIZE//3, TILE_SIZE//3, 5, 5))
    pygame.draw.rect(MONSTER_IMG, WHITE, (TILE_SIZE*2//3-5, TILE_SIZE//3, 5, 5))
    pygame.draw.rect(MONSTER_IMG, BLACK, (TILE_SIZE//3+1, TILE_SIZE//3+1, 3, 3))
    pygame.draw.rect(MONSTER_IMG, BLACK, (TILE_SIZE*2//3-4, TILE_SIZE//3+1, 3, 3))
    # Mouth
    for i in range(5):
        pygame.draw.rect(MONSTER_IMG, BLACK, (TILE_SIZE//3+i*3, TILE_SIZE//2+5, 2, 2))
    
    # Create Mystery Machine pixel art
    MYSTERY_MACHINE_IMG = pygame.Surface((TILE_SIZE*2, TILE_SIZE), pygame.SRCALPHA)
    # Van body
    pygame.draw.rect(MYSTERY_MACHINE_IMG, (0, 180, 0), (5, 10, TILE_SIZE*2-10, TILE_SIZE-15))
    # Windows
    pygame.draw.rect(MYSTERY_MACHINE_IMG, (200, 230, 255), (10, 15, 20, 15))
    pygame.draw.rect(MYSTERY_MACHINE_IMG, (200, 230, 255), (40, 15, TILE_SIZE-20, 15))
    # Wheels
    pygame.draw.circle(MYSTERY_MACHINE_IMG, BLACK, (20, TILE_SIZE-10), 8)
    pygame.draw.circle(MYSTERY_MACHINE_IMG, BLACK, (TILE_SIZE+20, TILE_SIZE-10), 8)
    pygame.draw.circle(MYSTERY_MACHINE_IMG, (100, 100, 100), (20, TILE_SIZE-10), 5)
    pygame.draw.circle(MYSTERY_MACHINE_IMG, (100, 100, 100), (TILE_SIZE+20, TILE_SIZE-10), 5)
    # Flower power designs
    for _ in range(5):
        x = random.randint(30, TILE_SIZE*2-20)
        y = random.randint(25, TILE_SIZE-20)
        color = random.choice([(200, 50, 50), (50, 50, 200), (200, 200, 50)])
        pygame.draw.circle(MYSTERY_MACHINE_IMG, color, (x, y), 3)
        for i in range(5):
            angle = i * 2 * math.pi / 5
            dx = int(5 * math.cos(angle))
            dy = int(5 * math.sin(angle))
            pygame.draw.line(MYSTERY_MACHINE_IMG, color, (x, y), (x + dx, y + dy), 1)
    # "Mystery Machine" text (simplified)
    for i in range(8):
        pygame.draw.rect(MYSTERY_MACHINE_IMG, BLUE, (TILE_SIZE-15+i*3, 5, 2, 2))
    
    # Create Mystery Machine driving view (top-down)
    MYSTERY_MACHINE_DRIVING_IMG = pygame.Surface((TILE_SIZE*2, TILE_SIZE*2), pygame.SRCALPHA)
    # Van body (from top)
    pygame.draw.rect(MYSTERY_MACHINE_DRIVING_IMG, (0, 180, 0), (10, 5, TILE_SIZE*2-20, TILE_SIZE*2-10), 0, 10)
    # Windows (windshield)
    pygame.draw.rect(MYSTERY_MACHINE_DRIVING_IMG, (200, 230, 255), (15, 10, TILE_SIZE*2-30, 15), 0, 5)
    # Side windows
    pygame.draw.rect(MYSTERY_MACHINE_DRIVING_IMG, (200, 230, 255), (10, TILE_SIZE-10, 5, TILE_SIZE-15), 0, 2)
    pygame.draw.rect(MYSTERY_MACHINE_DRIVING_IMG, (200, 230, 255), (TILE_SIZE*2-15, TILE_SIZE-10, 5, TILE_SIZE-15), 0, 2)
    # Decorative lines
    pygame.draw.line(MYSTERY_MACHINE_DRIVING_IMG, (0, 100, 0), (15, TILE_SIZE+5), (TILE_SIZE*2-15, TILE_SIZE+5), 2)
    pygame.draw.line(MYSTERY_MACHINE_DRIVING_IMG, (0, 100, 0), (TILE_SIZE, 10), (TILE_SIZE, TILE_SIZE*2-10), 2)
    # Flower power designs
    for _ in range(8):
        x = random.randint(20, TILE_SIZE*2-20)
        y = random.randint(TILE_SIZE-5, TILE_SIZE*2-15)
        color = random.choice([(200, 50, 50), (50, 50, 200), (200, 200, 50)])
        pygame.draw.circle(MYSTERY_MACHINE_DRIVING_IMG, color, (x, y), 4)
        for i in range(5):
            angle = i * 2 * math.pi / 5
            dx = int(6 * math.cos(angle))
            dy = int(6 * math.sin(angle))
            pygame.draw.line(MYSTERY_MACHINE_DRIVING_IMG, color, (x, y), (x + dx, y + dy), 1)
    
    # Create Scooby Snack pixel art (cookie-like)
    SCOOBY_SNACK_IMG = pygame.Surface((TILE_SIZE//2, TILE_SIZE//2), pygame.SRCALPHA)
    pygame.draw.circle(SCOOBY_SNACK_IMG, (205, 133, 63), (TILE_SIZE//4, TILE_SIZE//4), TILE_SIZE//5)
    for i in range(4):
        angle = i * math.pi / 2
        x = TILE_SIZE//4 + int((TILE_SIZE//8) * math.cos(angle))
        y = TILE_SIZE//4 + int((TILE_SIZE//8) * math.sin(angle))
        pygame.draw.circle(SCOOBY_SNACK_IMG, (139, 69, 19), (x, y), 2)
    
    # Create Trap pixel art (net-like)
    TRAP_IMG = pygame.Surface((TILE_SIZE//2, TILE_SIZE//2), pygame.SRCALPHA)
    pygame.draw.circle(TRAP_IMG, (150, 75, 0), (TILE_SIZE//4, TILE_SIZE//4), TILE_SIZE//6)
    # Net pattern
    for i in range(4):
        start_angle = i * math.pi / 2
        for j in range(3):
            radius = (j+1) * TILE_SIZE // 16
            points = []
            for k in range(4):
                angle = start_angle + k * math.pi / 2
                x = TILE_SIZE//4 + int(radius * math.cos(angle))
                y = TILE_SIZE//4 + int(radius * math.sin(angle))
                points.append((x, y))
            if len(points) >= 2:
                pygame.draw.lines(TRAP_IMG, (80, 40, 0), True, points, 1)
    
    # Create Tree pixel art
    TREE_IMG = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
    # Trunk
    pygame.draw.rect(TREE_IMG, (101, 67, 33), (TILE_SIZE//2-5, TILE_SIZE//2, 10, TILE_SIZE//2))
    # Leaves (pine tree style)
    for i in range(5):
        width = TILE_SIZE - i * 8
        height = 10
        x = (TILE_SIZE - width) // 2
        y = TILE_SIZE//2 - height * (i+1)
        pygame.draw.polygon(TREE_IMG, (0, 100+i*15, 0), [(x, y+height), (x+width, y+height), (x+width//2, y)])
    
    # Create Road pixel art
    ROAD_IMG = pygame.Surface((TILE_SIZE, TILE_SIZE))
    ROAD_IMG.fill((60, 60, 60))  # Asphalt color
    # Road markings
    if random.random() < 0.5:  # Horizontal road
        pygame.draw.rect(ROAD_IMG, (255, 255, 255), (0, TILE_SIZE//2-2, TILE_SIZE, 4))  # Center line
    else:  # Vertical road
        pygame.draw.rect(ROAD_IMG, (255, 255, 255), (TILE_SIZE//2-2, 0, 4, TILE_SIZE))  # Center line
    
    # Create Highway pixel art
    HIGHWAY_IMG = pygame.Surface((TILE_SIZE, TILE_SIZE))
    HIGHWAY_IMG.fill((70, 70, 70))  # Darker asphalt for highway
    pygame.draw.rect(HIGHWAY_IMG, (255, 255, 255), (0, TILE_SIZE//2-8, TILE_SIZE, 2))  # Top line
    pygame.draw.rect(HIGHWAY_IMG, (255, 255, 255), (0, TILE_SIZE//2+6, TILE_SIZE, 2))  # Bottom line
    
    # Create street light
    STREET_LIGHT_IMG = pygame.Surface((TILE_SIZE//2, TILE_SIZE), pygame.SRCALPHA)
    # Pole
    pygame.draw.rect(STREET_LIGHT_IMG, (100, 100, 100), (TILE_SIZE//4-2, TILE_SIZE//3, 4, TILE_SIZE*2//3))
    # Light
    pygame.draw.circle(STREET_LIGHT_IMG, (255, 255, 150), (TILE_SIZE//4, TILE_SIZE//3), 5)
    pygame.draw.circle(STREET_LIGHT_IMG, (255, 255, 100), (TILE_SIZE//4, TILE_SIZE//3), 3)
    
    # Create house pixel art
    HOUSE_IMGS = []
    house_colors = [
        (200, 150, 150),  # Pink
        (150, 200, 150),  # Light green
        (150, 150, 200),  # Light blue
        (200, 200, 150),  # Light yellow
        (200, 150, 200),  # Light purple
    ]
    
    for color in house_colors:
        house = pygame.Surface((TILE_SIZE*2, TILE_SIZE*2), pygame.SRCALPHA)
        
        # House base
        pygame.draw.rect(house, color, (5, TILE_SIZE//2, TILE_SIZE*2-10, TILE_SIZE*3//2-5))
        
        # Roof
        roof_points = [
            (0, TILE_SIZE//2),
            (TILE_SIZE, 5),
            (TILE_SIZE*2, TILE_SIZE//2)
        ]
        pygame.draw.polygon(house, (100, 60, 60), roof_points)
        
        # Door
        door_color = (80, 50, 30)
        pygame.draw.rect(house, door_color, (TILE_SIZE-TILE_SIZE//4, TILE_SIZE*3//2-5, TILE_SIZE//2, TILE_SIZE//2))
        pygame.draw.rect(house, (220, 220, 150), (TILE_SIZE+5, TILE_SIZE-10, TILE_SIZE//3, TILE_SIZE//3))  # Window
        pygame.draw.rect(house, (220, 220, 150), (TILE_SIZE//2-10, TILE_SIZE-10, TILE_SIZE//3, TILE_SIZE//3))  # Window
        
        # Add some random details
        if random.random() < 0.5:
            # Chimney
            pygame.draw.rect(house, (100, 60, 60), (TILE_SIZE*3//2, 15, TILE_SIZE//6, TILE_SIZE//3))
            
        if random.random() < 0.7:
            # Flower box
            pygame.draw.rect(house, (80, 50, 30), (TILE_SIZE//2-15, TILE_SIZE+TILE_SIZE//4, TILE_SIZE//2+10, 5))
            for i in range(3):
                flower_color = random.choice([(255, 50, 50), (255, 255, 50), (255, 150, 50)])
                pygame.draw.circle(house, flower_color, (TILE_SIZE//2-10+i*10, TILE_SIZE+TILE_SIZE//4-3), 3)
        
        HOUSE_IMGS.append(house)
    
    # Create boss monster (more menacing)
    BOSS_MONSTER_IMG = pygame.Surface((TILE_SIZE*2, TILE_SIZE*2), pygame.SRCALPHA)
    # Monster body
    boss_color = (120, 0, 40)  # Darker red
    
    # Body shape (more angular and menacing)
    body_points = [
        (TILE_SIZE, 10),                  # Top
        (TILE_SIZE//2, TILE_SIZE//2),     # Upper left
        (10, TILE_SIZE),                  # Left
        (TILE_SIZE//2, TILE_SIZE*3//2),   # Lower left
        (TILE_SIZE, TILE_SIZE*2-10),      # Bottom
        (TILE_SIZE*3//2, TILE_SIZE*3//2), # Lower right
        (TILE_SIZE*2-10, TILE_SIZE),      # Right
        (TILE_SIZE*3//2, TILE_SIZE//2),   # Upper right
    ]
    pygame.draw.polygon(BOSS_MONSTER_IMG, boss_color, body_points)
    
    # Jagged edges for more menacing look
    for i in range(8):
        angle = i * math.pi / 4
        x1 = TILE_SIZE + int(TILE_SIZE*0.8 * math.cos(angle))
        y1 = TILE_SIZE + int(TILE_SIZE*0.8 * math.sin(angle))
        x2 = TILE_SIZE + int(TILE_SIZE*0.9 * math.cos(angle + math.pi/8))
        y2 = TILE_SIZE + int(TILE_SIZE*0.9 * math.sin(angle + math.pi/8))
        pygame.draw.line(BOSS_MONSTER_IMG, (80, 0, 20), (x1, y1), (x2, y2), 2)
    
    # Eyes (glowing)
    eye_size = 8
    pygame.draw.rect(BOSS_MONSTER_IMG, (255, 255, 0), (TILE_SIZE//2+5, TILE_SIZE//2+5, eye_size, eye_size))
    pygame.draw.rect(BOSS_MONSTER_IMG, (255, 255, 0), (TILE_SIZE*3//2-eye_size-5, TILE_SIZE//2+5, eye_size, eye_size))
    
    # Pupils
    pygame.draw.rect(BOSS_MONSTER_IMG, (255, 0, 0), (TILE_SIZE//2+7, TILE_SIZE//2+7, 4, 4))
    pygame.draw.rect(BOSS_MONSTER_IMG, (255, 0, 0), (TILE_SIZE*3//2-9, TILE_SIZE//2+7, 4, 4))
    
    # Mouth with sharp teeth
    teeth_color = (255, 255, 255)
    mouth_y = TILE_SIZE + 15
    mouth_width = TILE_SIZE - 20
    
    pygame.draw.rect(BOSS_MONSTER_IMG, (0, 0, 0), (TILE_SIZE//2+10, mouth_y, mouth_width, 12))
    
    # Teeth
    for i in range(6):
        tooth_x = TILE_SIZE//2 + 10 + i * (mouth_width // 6)
        pygame.draw.polygon(BOSS_MONSTER_IMG, teeth_color, [
            (tooth_x, mouth_y),
            (tooth_x + 4, mouth_y),
            (tooth_x + 2, mouth_y + 8)
        ])
        
        # Bottom teeth
        pygame.draw.polygon(BOSS_MONSTER_IMG, teeth_color, [
            (tooth_x, mouth_y + 12),
            (tooth_x + 4, mouth_y + 12),
            (tooth_x + 2, mouth_y + 4)
        ])

# Create 90s style pixel art assets
create_pixel_art_images()

# Load sounds or create placeholders
try:
    COLLECT_SOUND = pygame.mixer.Sound(os.path.join("assets", "collect.wav"))
    MONSTER_SOUND = pygame.mixer.Sound(os.path.join("assets", "monster.wav"))
    WIN_SOUND = pygame.mixer.Sound(os.path.join("assets", "win.wav"))
    LOSE_SOUND = pygame.mixer.Sound(os.path.join("assets", "lose.wav"))
    SNACK_SOUND = pygame.mixer.Sound(os.path.join("assets", "snack.wav"))
    TRAP_SOUND = pygame.mixer.Sound(os.path.join("assets", "trap.wav"))
except:
    # Create dummy sounds
    COLLECT_SOUND = pygame.mixer.Sound(pygame.sndarray.array([0]))
    MONSTER_SOUND = pygame.mixer.Sound(pygame.sndarray.array([0]))
    WIN_SOUND = pygame.mixer.Sound(pygame.sndarray.array([0]))
    LOSE_SOUND = pygame.mixer.Sound(pygame.sndarray.array([0]))
    SNACK_SOUND = pygame.mixer.Sound(pygame.sndarray.array([0]))
    TRAP_SOUND = pygame.mixer.Sound(pygame.sndarray.array([0]))

# Game states
class GameState(Enum):
    MENU = 0
    PLAYING = 1
    DRIVING = 2  # New state for driving the Mystery Machine
    GAME_OVER = 3
    WIN = 4
    PAUSED = 5

# Character class
class Character:
    def __init__(self, x, y, image, speed):
        self.x = x
        self.y = y
        self.image = image
        self.speed = speed
        self.width = image.get_width()
        self.height = image.get_height()
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.direction = random.choice(["up", "down", "left", "right"])
        self.steps = 0
        
    def update(self):
        self.rect.x = self.x
        self.rect.y = self.y
        
    def draw(self, screen, camera_x, camera_y):
        screen.blit(self.image, (self.x - camera_x, self.y - camera_y))
        
    def collides_with(self, other):
        return self.rect.colliderect(other.rect)

# Player class (Scooby Doo)
class Player(Character):
    def __init__(self, x, y):
        super().__init__(x, y, SCOOBY_IMG, PLAYER_SPEED)
        self.found_friends = []
        self.has_speed_boost = False
        self.boost_end_time = 0
        self.courage = 100  # Courage meter (decreases when near monsters)
        
    def move(self, dx, dy, forest):
        # Check if speed boost is active
        if self.has_speed_boost and pygame.time.get_ticks() > self.boost_end_time:
            self.has_speed_boost = False
            self.speed = PLAYER_SPEED
        
        # Apply movement
        speed = self.speed * 2 if self.has_speed_boost else self.speed
        new_x = self.x + dx * speed
        new_y = self.y + dy * speed
        
        # Check for collisions with forest boundaries and trees
        if self.can_move_to(new_x, self.y, forest):
            self.x = new_x
        if self.can_move_to(self.x, new_y, forest):
            self.y = new_y
            
        # Update rectangle position
        self.update()
        
    def can_move_to(self, x, y, forest):
        # Check forest boundaries
        if x < 0 or y < 0 or x > forest.width - self.width or y > forest.height - self.height:
            return False
        
        # Check collision with trees
        test_rect = pygame.Rect(x, y, self.width, self.height)
        for tree in forest.trees:
            if test_rect.colliderect(tree):
                return False
                
        return True
        
    def activate_speed_boost(self):
        self.has_speed_boost = True
        self.boost_end_time = pygame.time.get_ticks() + SCOOBY_SNACK_BOOST_DURATION
        
    def update_courage(self, monsters):
        # Decrease courage when near monsters
        closest_distance = float('inf')
        for monster in monsters:
            if not monster.is_stunned:  # Only count active monsters
                dx = monster.x - self.x
                dy = monster.y - self.y
                distance = math.sqrt(dx**2 + dy**2)
                if distance < closest_distance:
                    closest_distance = distance
        
        # Update courage based on distance to nearest monster
        if closest_distance < 100:
            self.courage = max(0, self.courage - 1)
        elif closest_distance < 200:
            self.courage = max(0, self.courage - 0.5)
        else:
            self.courage = min(100, self.courage + 0.2)
        
        # Game over if courage reaches zero
        return self.courage <= 0

# Friend class (Shaggy, Velma, Daphne, Fred)
class Friend(Character):
    def __init__(self, x, y, image, name):
        super().__init__(x, y, image, FRIEND_SPEED)
        self.name = name
        self.is_found = False
        self.follow_distance = TILE_SIZE * 1.5
        
    def follow(self, target_x, target_y, forest):
        if not self.is_found:
            return
            
        # Calculate direction to target
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx**2 + dy**2)
        
        # Only move if we're too far from the target
        if distance > self.follow_distance:
            # Normalize direction vector
            if distance > 0:
                dx /= distance
                dy /= distance
                
            # Calculate new position
            new_x = self.x + dx * self.speed
            new_y = self.y + dy * self.speed
            
            # Check for collisions with forest and trees
            if self.can_move_to(new_x, self.y, forest):
                self.x = new_x
            if self.can_move_to(self.x, new_y, forest):
                self.y = new_y
                
            self.update()
    
    def can_move_to(self, x, y, forest):
        # Check forest boundaries
        if x < 0 or y < 0 or x > forest.width - self.width or y > forest.height - self.height:
            return False
        
        # Check collision with trees
        test_rect = pygame.Rect(x, y, self.width, self.height)
        for tree in forest.trees:
            if test_rect.colliderect(tree):
                return False
                
        return True

# Monster class
class Monster(Character):
    def __init__(self, x, y, patrol_type="random"):
        super().__init__(x, y, MONSTER_IMG, MONSTER_SPEED)
        self.patrol_type = patrol_type
        self.direction_change_timer = 0
        self.is_stunned = False
        self.stun_end_time = 0
        
    def update_monster(self, forest, player_x=None, player_y=None):
        # Skip movement if stunned
        if self.is_stunned:
            if pygame.time.get_ticks() > self.stun_end_time:
                self.is_stunned = False
            else:
                # Just update the rectangle position without calling any update method
                self.rect.x = self.x
                self.rect.y = self.y
                return
        
        # Change direction periodically for random patrol
        if self.patrol_type == "random":
            current_time = pygame.time.get_ticks()
            if current_time > self.direction_change_timer:
                self.direction = random.choice(["up", "down", "left", "right"])
                self.direction_change_timer = current_time + random.randint(1000, 3000)
                
        # Move based on patrol type
        if self.patrol_type == "chase" and player_x is not None and player_y is not None:
            # Chase the player if they're within range
            dx = player_x - self.x
            dy = player_y - self.y
            distance = math.sqrt(dx**2 + dy**2)
            
            if distance < 200:  # Chase range
                # Normalize direction vector
                if distance > 0:
                    dx /= distance
                    dy /= distance
                    
                # Apply movement
                new_x = self.x + dx * self.speed
                new_y = self.y + dy * self.speed
                
                # Check for collisions with forest and trees
                if self.can_move_to(new_x, self.y, forest):
                    self.x = new_x
                if self.can_move_to(self.x, new_y, forest):
                    self.y = new_y
            else:
                self.move_in_direction(forest)
        else:
            self.move_in_direction(forest)
            
        # Update rectangle position
        self.rect.x = self.x
        self.rect.y = self.y
        
    def move_in_direction(self, forest):
        dx, dy = 0, 0
        if self.direction == "up":
            dy = -self.speed
        elif self.direction == "down":
            dy = self.speed
        elif self.direction == "left":
            dx = -self.speed
        elif self.direction == "right":
            dx = self.speed
            
        # Apply movement
        new_x = self.x + dx
        new_y = self.y + dy
        
        # Check for collisions with forest boundaries and trees
        can_move_x = self.can_move_to(new_x, self.y, forest)
        can_move_y = self.can_move_to(self.x, new_y, forest)
        
        if can_move_x:
            self.x = new_x
        else:
            # Change direction if we hit an obstacle
            if self.direction == "left":
                self.direction = "right"
            elif self.direction == "right":
                self.direction = "left"
                
        if can_move_y:
            self.y = new_y
        else:
            # Change direction if we hit an obstacle
            if self.direction == "up":
                self.direction = "down"
            elif self.direction == "down":
                self.direction = "up"
    
    def can_move_to(self, x, y, forest):
        # Check forest boundaries
        if x < 0 or y < 0 or x > forest.width - self.width or y > forest.height - self.height:
            return False
        
        # Check collision with trees
        test_rect = pygame.Rect(x, y, self.width, self.height)
        for tree in forest.trees:
            if test_rect.colliderect(tree):
                return False
                
        return True
        
    def stun(self):
        self.is_stunned = True
        self.stun_end_time = pygame.time.get_ticks() + MONSTER_STUN_DURATION
        
    def draw(self, screen, camera_x, camera_y):
        if self.is_stunned:
            # Draw a stunned version (add visual indicator)
            stunned_img = self.image.copy()
            pygame.draw.line(stunned_img, YELLOW, (0, 0), (self.width, self.height), 3)
            pygame.draw.line(stunned_img, YELLOW, (0, self.height), (self.width, 0), 3)
            screen.blit(stunned_img, (self.x - camera_x, self.y - camera_y))
        else:
            super().draw(screen, camera_x, camera_y)

# Collectible class
class Collectible:
    def __init__(self, x, y, image, type_name):
        self.x = x
        self.y = y
        self.image = image
        self.type = type_name
        self.width = image.get_width()
        self.height = image.get_height()
        self.rect = pygame.Rect(x, y, self.width, self.height)
        
    def draw(self, screen, camera_x, camera_y):
        screen.blit(self.image, (self.x - camera_x, self.y - camera_y))

# Forest class
class Forest:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.trees = []
        self.collectibles = []
        
        # Generate trees (obstacles)
        self.generate_trees()
        
        # Generate collectibles
        self.generate_collectibles()
        
    def generate_trees(self):
        # Create a border of trees
        for x in range(0, self.width, TILE_SIZE):
            self.trees.append(pygame.Rect(x, 0, TILE_SIZE, TILE_SIZE))
            self.trees.append(pygame.Rect(x, self.height - TILE_SIZE, TILE_SIZE, TILE_SIZE))
            
        for y in range(0, self.height, TILE_SIZE):
            self.trees.append(pygame.Rect(0, y, TILE_SIZE, TILE_SIZE))
            self.trees.append(pygame.Rect(self.width - TILE_SIZE, y, TILE_SIZE, TILE_SIZE))
            
        # Create a grid-based forest with clearer pathways
        grid_size = TILE_SIZE * 3  # Larger grid cells to ensure wider paths
        
        # Setup a grid to track where we've placed trees
        grid_width = self.width // grid_size
        grid_height = self.height // grid_size
        forest_grid = [[False for _ in range(grid_height)] for _ in range(grid_width)]
        
        # Create paths through the forest
        # Horizontal paths
        for y in range(2, grid_height-2, 3):
            for x in range(grid_width):
                forest_grid[x][y] = True  # Mark as path (no trees)
                
        # Vertical paths
        for x in range(2, grid_width-2, 3):
            for y in range(grid_height):
                forest_grid[x][y] = True  # Mark as path (no trees)
        
        # Add some random clearings
        num_clearings = grid_width * grid_height // 15
        for _ in range(num_clearings):
            cx = random.randint(1, grid_width-2)
            cy = random.randint(1, grid_height-2)
            # Create a small clearing
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    if 0 <= cx+dx < grid_width and 0 <= cy+dy < grid_height:
                        forest_grid[cx+dx][cy+dy] = True
        
        # Place trees in non-path areas
        for gx in range(grid_width):
            for gy in range(grid_height):
                if not forest_grid[gx][gy]:  # Not a path
                    # Only place trees if we're away from the starting area
                    real_x = gx * grid_size
                    real_y = gy * grid_size
                    
                    # Check distance from start position
                    if (real_x > TILE_SIZE * 6 or real_y > TILE_SIZE * 6) and \
                       real_x < self.width - TILE_SIZE * 3 and real_y < self.height - TILE_SIZE * 3:
                        
                        # Add some randomness to tree placement
                        if random.random() < 0.7:  # 70% chance to place a tree
                            # Place 1-2 trees in this grid cell with spacing
                            num_trees = random.randint(1, 2)
                            for _ in range(num_trees):
                                tree_x = real_x + random.randint(0, grid_size - TILE_SIZE)
                                tree_y = real_y + random.randint(0, grid_size - TILE_SIZE)
                                
                                # Check if this position would block a path
                                is_blocking = False
                                for existing_tree in self.trees:
                                    if abs(existing_tree.x - tree_x) < TILE_SIZE*1.5 and \
                                       abs(existing_tree.y - tree_y) < TILE_SIZE*1.5:
                                        is_blocking = True
                                        break
                                        
                                if not is_blocking:
                                    self.trees.append(pygame.Rect(tree_x, tree_y, TILE_SIZE, TILE_SIZE))
    
    def generate_collectibles(self):
        # Create Scooby Snacks
        num_snacks = 10
        for _ in range(num_snacks):
            while True:
                x = random.randint(TILE_SIZE * 2, self.width - TILE_SIZE * 3)
                y = random.randint(TILE_SIZE * 2, self.height - TILE_SIZE * 3)
                
                # Check if position is valid (not colliding with trees)
                valid_position = True
                snack_rect = pygame.Rect(x, y, TILE_SIZE//2, TILE_SIZE//2)
                for tree in self.trees:
                    if snack_rect.colliderect(tree):
                        valid_position = False
                        break
                        
                if valid_position:
                    self.collectibles.append(Collectible(x, y, SCOOBY_SNACK_IMG, "snack"))
                    break
        
        # Create trap items (to use against monsters)
        num_traps = 5
        for _ in range(num_traps):
            while True:
                x = random.randint(TILE_SIZE * 2, self.width - TILE_SIZE * 3)
                y = random.randint(TILE_SIZE * 2, self.height - TILE_SIZE * 3)
                
                # Check if position is valid (not colliding with trees)
                valid_position = True
                trap_rect = pygame.Rect(x, y, TILE_SIZE//2, TILE_SIZE//2)
                for tree in self.trees:
                    if trap_rect.colliderect(tree):
                        valid_position = False
                        break
                        
                if valid_position:
                    self.collectibles.append(Collectible(x, y, TRAP_IMG, "trap"))
                    break
                    
    def draw(self, screen, camera_x, camera_y):
        # Draw sky background
        screen.blit(SKY_IMG, (0, 0))
        
        # Draw ground texture (tiled)
        ground_width, ground_height = GROUND_IMG.get_width(), GROUND_IMG.get_height()
        for x in range(0, SCREEN_WIDTH, ground_width):
            for y in range(0, SCREEN_HEIGHT, ground_height):
                # Apply a slight offset based on camera to create parallax effect
                offset_x = (camera_x // 3) % ground_width
                offset_y = (camera_y // 3) % ground_height
                screen.blit(GROUND_IMG, (x - offset_x, y - offset_y))
        
        # Draw trees using pixel art
        for tree in self.trees:
            if (tree.x + TILE_SIZE > camera_x and tree.x < camera_x + SCREEN_WIDTH and
                tree.y + TILE_SIZE > camera_y and tree.y < camera_y + SCREEN_HEIGHT):
                screen.blit(TREE_IMG, (tree.x - camera_x, tree.y - camera_y))
                
        # Draw collectibles
        for collectible in self.collectibles:
            collectible.draw(screen, camera_x, camera_y)

                                  
# Game class
class Game:
    def __init__(self):
        self.state = GameState.MENU
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, FONT_SIZE)
        self.score = 0
        self.time_elapsed = 0
        self.traps_available = 0
        self.riddle_text = "Are drop sets on leg day really needed? (press 'Enter' key to submit.)"
        self.answer_input = ""  # Player's typed answer
        
        # Create environments
        self.forest_width = TILE_SIZE * 40  # 2000 pixels
        self.forest_height = TILE_SIZE * 30  # 1500 pixels
        self.forest = Forest(self.forest_width, self.forest_height)
        
        # Neighborhood (will be initialized when needed)
        self.neighborhood = None
        self.neighborhood_width = TILE_SIZE * 60  # 3000 pixels
        self.neighborhood_height = TILE_SIZE * 40  # 2000 pixels
        
        # Highway (will be initialized when needed)
        self.highway = None
        self.highway_position = 0  # Current position on the highway
        self.highway_lane = 2  # Current lane (middle lane)
        
        # Create player (Scooby)
        self.player = Player(TILE_SIZE * 2, TILE_SIZE * 2)
        
        # Create Mystery Machine (initially in forest)
        self.mystery_machine = Character(TILE_SIZE * 2, TILE_SIZE * 3, MYSTERY_MACHINE_IMG, 0)
        
        # Create friends
        self.friends = self.create_friends()
        
        # Create monsters
        self.monsters = self.create_monsters()
        
        # Create boss monster (will be initialized when needed)
        self.boss_monster = None
        
        # Camera position
        self.camera_x = 0
        self.camera_y = 0
        
        # Game status
        self.all_friends_found = False
        self.game_over_reason = ""
        self.transition_ready = False
        
        # Driving variables
        self.driving_speed = 5
        self.is_turning = False
        self.turn_progress = 0
        self.turn_duration = 30  # frames for a turn
        self.turn_direction = 0  # -1 for left, 1 for right
        
    def create_friends(self):
        friends = []
        
        # Place friends randomly in the forest (away from start position)
        friend_data = [
            ("Shaggy", SHAGGY_IMG),
            ("Velma", VELMA_IMG),
            ("Daphne", DAPHNE_IMG),
            ("Fred", FRED_IMG)
        ]
        
        for name, image in friend_data:
            while True:
                x = random.randint(TILE_SIZE * 8, self.forest_width - TILE_SIZE * 3)
                y = random.randint(TILE_SIZE * 8, self.forest_height - TILE_SIZE * 3)
                
                # Check if position is valid (not colliding with trees)
                valid_position = True
                friend_rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
                for tree in self.forest.trees:
                    if friend_rect.colliderect(tree):
                        valid_position = False
                        break
                        
                if valid_position:
                    friends.append(Friend(x, y, image, name))
                    break
                    
        return friends
        
    def create_monsters(self):
        monsters = []
        
        # Create different types of monsters
        num_monsters = 5
        for i in range(num_monsters):
            while True:
                x = random.randint(TILE_SIZE * 5, self.forest_width - TILE_SIZE * 3)
                y = random.randint(TILE_SIZE * 5, self.forest_height - TILE_SIZE * 3)
                
                # Check if position is valid (not colliding with trees)
                valid_position = True
                monster_rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
                for tree in self.forest.trees:
                    if monster_rect.colliderect(tree):
                        valid_position = False
                        break
                        
                # Also check distance from player start position
                dx = x - (TILE_SIZE * 2)
                dy = y - (TILE_SIZE * 2)
                distance = math.sqrt(dx**2 + dy**2)
                if distance < TILE_SIZE * 5:
                    valid_position = False
                
                if valid_position:
                    # Different patrol types
                    patrol_type = "random" if i < 3 else "chase"
                    monsters.append(Monster(x, y, patrol_type))
                    break
                    
        return monsters
    
    def initialize_neighborhood(self):
        # Create the suburban neighborhood
        self.neighborhood = Neighborhood(self.neighborhood_width, self.neighborhood_height)
        
        # Position the Mystery Machine in a suitable location
        # Find a road near the "forest entrance" (left side of neighborhood)
        for y in range(self.neighborhood_height // TILE_SIZE):
            if self.neighborhood.is_road(TILE_SIZE * 5, y * TILE_SIZE):
                # Place Mystery Machine on this road
                self.mystery_machine = Character(TILE_SIZE * 5, y * TILE_SIZE, MYSTERY_MACHINE_IMG, 0)
                # Position player and friends nearby
                self.player.x = TILE_SIZE * 3
                self.player.y = y * TILE_SIZE
                
                # Reset friend positions to follow behind player
                for i, friend in enumerate(self.player.found_friends):
                    friend.x = TILE_SIZE * (2 - i)
                    friend.y = y * TILE_SIZE
                
                break
    
    def initialize_driving_mode(self):
        # Start the chase sequence
        self.state = GameState.DRIVING
        
        # Create boss monster to chase
        monster_x = self.player.x - TILE_SIZE * 10  # Start some distance behind
        monster_y = self.player.y
        self.boss_monster = BossMonster(monster_x, monster_y)
        
        # Create highway for escape
        self.highway = Highway(TILE_SIZE * 200)  # Length of 200 tiles
        self.highway_position = 0
        self.highway_lane = 2  # Middle lane
        
        # Reset driving variables
        self.driving_speed = 5
        self.is_turning = False
        self.turn_progress = 0

        # Reset riddle input
        self.answer_input = ""
        
    def initialize_highway_escape(self):
        # Initialize highway escape sequence
        self.state = GameState.DRIVING
        self.highway_position = 0
        self.highway_lane = 2  # Middle lane
        
    def update_camera(self):
        if self.state == GameState.PLAYING:
            # Center camera on player
            if self.all_friends_found and self.transition_ready:
                # In neighborhood, we're heading to the Mystery Machine
                self.camera_x = self.mystery_machine.x - SCREEN_WIDTH // 2
                self.camera_y = self.mystery_machine.y - SCREEN_HEIGHT // 2
            else:
                # Normal gameplay
                self.camera_x = self.player.x - SCREEN_WIDTH // 2
                self.camera_y = self.player.y - SCREEN_HEIGHT // 2
            
            # Keep camera within bounds
            if self.all_friends_found and self.transition_ready:
                # In neighborhood
                self.camera_x = max(0, min(self.camera_x, self.neighborhood_width - SCREEN_WIDTH))
                self.camera_y = max(0, min(self.camera_y, self.neighborhood_height - SCREEN_HEIGHT))
            else:
                # In forest
                self.camera_x = max(0, min(self.camera_x, self.forest_width - SCREEN_WIDTH))
                self.camera_y = max(0, min(self.camera_y, self.forest_height - SCREEN_HEIGHT))
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == GameState.PLAYING or self.state == GameState.DRIVING:
                        self.state = GameState.PAUSED
                    elif self.state == GameState.PAUSED:
                        self.state = GameState.PLAYING if self.all_friends_found and self.transition_ready else GameState.PLAYING
                    else:
                        pygame.quit()
                        sys.exit()
                # Start game from menu
                if self.state == GameState.MENU and event.key == pygame.K_RETURN:
                    self.state = GameState.PLAYING
                # Restart after game over or win
                if (self.state == GameState.GAME_OVER or self.state == GameState.WIN) and event.key == pygame.K_r:
                    self.__init__()  # Reset game
                # Use trap if available
                if self.state == GameState.PLAYING and event.key == pygame.K_SPACE:
                    self.use_trap()
                # Handle riddle input during driving
                if self.state == GameState.DRIVING:
                    if event.key == pygame.K_BACKSPACE:
                        self.answer_input = self.answer_input[:-1]  # Remove last character
                    elif event.key == pygame.K_RETURN:
                        if self.answer_input.lower() == "no":  # Case-insensitive check
                            self.state = GameState.WIN
                            self.score += 1000  # Bonus for solving riddle
                            WIN_SOUND.play()
                        self.answer_input = ""  # Reset input after Enter
                    elif event.unicode.isalnum():  # Only alphanumeric characters
                        self.answer_input += event.unicode
                    
    def use_trap(self):
        if self.traps_available <= 0:
            return
            
        # Find the nearest monster
        nearest_monster = None
        nearest_distance = float('inf')
        
        for monster in self.monsters:
            if not monster.is_stunned:  # Only target active monsters
                dx = monster.x - self.player.x
                dy = monster.y - self.player.y
                distance = math.sqrt(dx**2 + dy**2)
                
                if distance < nearest_distance and distance < TILE_SIZE * 3:  # Trap range
                    nearest_monster = monster
                    nearest_distance = distance
                    
        if nearest_monster:
            nearest_monster.stun()
            self.traps_available -= 1
            TRAP_SOUND.play()
                    
    def update(self):
        if self.state == GameState.PLAYING:
            # Update game time
            self.time_elapsed += self.clock.get_time()
            
            if self.all_friends_found and self.transition_ready:
                # In neighborhood heading to Mystery Machine
                self.update_neighborhood()
            else:
                # Normal forest gameplay
                self.update_forest()
                
        elif self.state == GameState.DRIVING:
            # Update driving sequence
            self.update_driving()
            
    def update_forest(self):
        # Handle player movement
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy = -1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy = 1
            
        self.player.move(dx, dy, self.forest)
        
        # Update monsters
        for monster in self.monsters:
            monster.update_monster(self.forest, self.player.x, self.player.y)
            
            # Check collision with player
            if monster.collides_with(self.player) and not monster.is_stunned and not self.player.has_speed_boost:
                self.state = GameState.GAME_OVER
                self.game_over_reason = f"Scooby was caught by a monster!"
                MONSTER_SOUND.play()
                LOSE_SOUND.play()
                
        # Update courage level based on monsters
        if self.player.update_courage(self.monsters):
            self.state = GameState.GAME_OVER
            self.game_over_reason = "Scooby ran out of courage!"
            LOSE_SOUND.play()
                
        # Check collision with collectibles
        for collectible in self.forest.collectibles[:]:
            collectible_rect = pygame.Rect(collectible.x, collectible.y, 
                                          collectible.width, collectible.height)
            if self.player.rect.colliderect(collectible_rect):
                if collectible.type == "snack":
                    self.player.activate_speed_boost()
                    self.score += 50
                    SNACK_SOUND.play()
                elif collectible.type == "trap":
                    self.traps_available += 1
                    self.score += 30
                    COLLECT_SOUND.play()
                    
                self.forest.collectibles.remove(collectible)
        
        # Update friend positions (follow the player)
        previous_x, previous_y = self.player.x, self.player.y
        for friend in self.player.found_friends:
            current_x, current_y = friend.x, friend.y
            friend.follow(previous_x, previous_y, self.forest)
            previous_x, previous_y = current_x, current_y
            
        # Check collision with friends (to find them)
        for friend in self.friends:
            if not friend.is_found and self.player.collides_with(friend):
                friend.is_found = True
                self.player.found_friends.append(friend)
                self.score += 100
                COLLECT_SOUND.play()
                
        # Check if all friends are found
        if len(self.player.found_friends) == len(self.friends) and not self.all_friends_found:
            self.all_friends_found = True
            
        # Check if player has reached the Mystery Machine with all friends
        if self.all_friends_found and self.player.collides_with(self.mystery_machine):
            # Transition to neighborhood
            self.transition_ready = True
            self.initialize_neighborhood()
            
    def update_neighborhood(self):
        # Handle player movement (still controlling Scooby)
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy = -1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy = 1
            
        # Move towards Mystery Machine
        speed = self.player.speed
        new_x = self.player.x + dx * speed
        new_y = self.player.y + dy * speed
        
        # Keep player on roads when possible
        if self.neighborhood.is_road(new_x + self.player.width//2, new_y + self.player.height//2):
            self.player.x = new_x
            self.player.y = new_y
        else:
            # Try each direction separately
            if self.neighborhood.is_road(new_x + self.player.width//2, self.player.y + self.player.height//2):
                self.player.x = new_x
            if self.neighborhood.is_road(self.player.x + self.player.width//2, new_y + self.player.height//2):
                self.player.y = new_y
                
        # Update player rectangle
        self.player.rect.x = self.player.x
        self.player.rect.y = self.player.y
        
        # Update friend positions (follow the player)
        previous_x, previous_y = self.player.x, self.player.y
        for friend in self.player.found_friends:
            current_x, current_y = friend.x, friend.y
            # Simplified following in neighborhood
            dx = previous_x - friend.x
            dy = previous_y - friend.y
            dist = math.sqrt(dx*dx + dy*dy)
            
            if dist > friend.follow_distance:
                if dist > 0:
                    dx /= dist
                    dy /= dist
                    
                new_x = friend.x + dx * friend.speed
                new_y = friend.y + dy * friend.speed
                
                # Try to keep on roads
                if self.neighborhood.is_road(new_x + friend.width//2, new_y + friend.height//2):
                    friend.x = new_x
                    friend.y = new_y
                else:
                    # Try each direction separately
                    if self.neighborhood.is_road(new_x + friend.width//2, friend.y + friend.height//2):
                        friend.x = new_x
                    if self.neighborhood.is_road(friend.x + friend.width//2, new_y + friend.height//2):
                        friend.y = new_y
                        
            friend.rect.x = friend.x
            friend.rect.y = friend.y
            
            previous_x, previous_y = current_x, current_y
            
        # Check if player has reached the Mystery Machine
        if self.player.collides_with(self.mystery_machine):
            # Transition to driving mode
            self.initialize_driving_mode()
            
        # Check if player has reached the highway exit
        exit_x, exit_y = self.neighborhood.exit_position
        exit_rect = pygame.Rect(exit_x, exit_y, TILE_SIZE, TILE_SIZE)
        
        if self.player.rect.colliderect(exit_rect):
            # Transition to highway escape
            self.initialize_highway_escape()
            
    def update_driving(self):
        keys = pygame.key.get_pressed()
        
        if not self.is_turning:
            # Normal driving (forward movement)
            self.highway_position += self.driving_speed
            
            # Lane changes
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                if self.highway_lane > 0:
                    self.is_turning = True
                    self.turn_progress = 0
                    self.turn_direction = -1  # Left
            elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                if self.highway_lane < 4:
                    self.is_turning = True
                    self.turn_progress = 0
                    self.turn_direction = 1  # Right
            # Speed control
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                self.driving_speed = min(10, self.driving_speed + 0.1)  # Accelerate
            elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
                self.driving_speed = max(3, self.driving_speed - 0.1)  # Brake
        else:
            # In the middle of a lane change
            self.turn_progress += 1
            if self.turn_progress >= self.turn_duration:
                # Lane change complete
                self.highway_lane += self.turn_direction
                self.is_turning = False
                
        if self.highway:
            # Get current vehicle position
            vehicle_x = SCREEN_WIDTH // 3
            vehicle_y = SCREEN_HEIGHT // 3 + self.highway_lane * TILE_SIZE
            vehicle_width = TILE_SIZE*2
            vehicle_height = TILE_SIZE
            
            # Handle collisions (make obstacles swerve)
            self.highway.handle_collisions(vehicle_x, vehicle_y, vehicle_width, vehicle_height, self.highway_position)
            
            # Removed original collision check and game-over condition
            # Removed win condition based on self.highway_position >= self.highway.length
        
    def draw(self):
        if self.state == GameState.PLAYING:
            if self.all_friends_found and self.transition_ready:
                # Draw neighborhood
                self.neighborhood.draw(screen, self.camera_x, self.camera_y)
            else:
                # Draw forest
                self.forest.draw(screen, self.camera_x, self.camera_y)
                
            # Draw the Mystery Machine
            self.mystery_machine.draw(screen, self.camera_x, self.camera_y)
            
            if not self.transition_ready:
                # Draw collectibles (only in forest)
                for collectible in self.forest.collectibles:
                    collectible.draw(screen, self.camera_x, self.camera_y)
                
                # Draw friends that haven't been found yet
                for friend in self.friends:
                    if not friend.is_found:
                        friend.draw(screen, self.camera_x, self.camera_y)
                        
                # Draw monsters (only in forest)
                for monster in self.monsters:
                    monster.draw(screen, self.camera_x, self.camera_y)
            
            # Draw player (Scooby)
            self.player.draw(screen, self.camera_x, self.camera_y)
            
            # Draw found friends following Scooby
            for friend in self.player.found_friends:
                friend.draw(screen, self.camera_x, self.camera_y)
                
        elif self.state == GameState.DRIVING:
            if self.highway:
                # Draw highway escape sequence
                self.highway.draw(screen, self.highway_position)
                
                # Draw Mystery Machine on highway
                vehicle_x = SCREEN_WIDTH // 3
                vehicle_y = SCREEN_HEIGHT // 3 + self.highway_lane * TILE_SIZE
                
                # Apply lane change animation
                if self.is_turning:
                    # Calculate lane position during turn
                    progress_ratio = self.turn_progress / self.turn_duration
                    lane_offset = self.turn_direction * progress_ratio * TILE_SIZE
                    vehicle_y += lane_offset
                
                # Draw the Mystery Machine in driving view
                screen.blit(MYSTERY_MACHINE_DRIVING_IMG, (vehicle_x, vehicle_y))
                
                # Draw boss monster chasing (some distance behind)
                monster_x = SCREEN_WIDTH // 8
                monster_y = SCREEN_HEIGHT // 3 + self.highway_lane * TILE_SIZE
                screen.blit(BOSS_MONSTER_IMG, (monster_x, monster_y))
                
            else:
                # Draw neighborhood chase sequence
                self.neighborhood.draw(screen, self.camera_x, self.camera_y)
                
                # Draw Mystery Machine
                self.mystery_machine.draw(screen, self.camera_x, self.camera_y)
                
                # Draw player (Scooby) - now driving Mystery Machine
                self.player.draw(screen, self.camera_x, self.camera_y)
                
                # Draw boss monster chasing
                if self.boss_monster:
                    self.boss_monster.draw(screen, self.camera_x, self.camera_y)
            
        # Draw UI elements (score, time, etc.)
        self.draw_ui()
        
    def draw_game_over(self):
        # Draw darkened game screen
        self.draw()
        
        # 90s style overlay with pattern
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))  # Semi-transparent black
        
        # Add diagonal stripe pattern (90s style)
        for y in range(0, SCREEN_HEIGHT, 10):
            pygame.draw.line(overlay, (80, 0, 0, 200), (0, y), (SCREEN_WIDTH, y+SCREEN_HEIGHT), 2)
        
        screen.blit(overlay, (0, 0))
        
        # Create 90s style panel for game over
        panel_width, panel_height = 500, 300
        panel_x = SCREEN_WIDTH // 2 - panel_width // 2
        panel_y = SCREEN_HEIGHT // 2 - panel_height // 2
        
        game_over_panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        # Gradient background from dark red to black
        for y in range(panel_height):
            color_value = max(0, 80 - y // 3)
            pygame.draw.line(game_over_panel, (color_value, 0, 0, 230), 
                            (0, y), (panel_width, y))
        
        # Add 90s style border with zigzag pattern
        border_width = 10
        for x in range(0, panel_width, 20):
            pygame.draw.polygon(game_over_panel, (200, 0, 0), 
                               [(x, 0), (x+10, border_width), (x+20, 0)])
            pygame.draw.polygon(game_over_panel, (200, 0, 0), 
                               [(x, panel_height), (x+10, panel_height-border_width), (x+20, panel_height)])
        
        for y in range(0, panel_height, 20):
            pygame.draw.polygon(game_over_panel, (200, 0, 0), 
                               [(0, y), (border_width, y+10), (0, y+20)])
            pygame.draw.polygon(game_over_panel, (200, 0, 0), 
                               [(panel_width, y), (panel_width-border_width, y+10), (panel_width, y+20)])
        
        screen.blit(game_over_panel, (panel_x, panel_y))
        
        # Draw "GAME OVER" text with 90s style
        title_font = pygame.font.SysFont(None, FONT_SIZE * 3)
        # Shadow text for 3D effect
        for offset in range(5, 0, -1):
            shadow_text = title_font.render("GAME OVER", True, (150-offset*20, 0, 0))
            screen.blit(shadow_text, (SCREEN_WIDTH // 2 - shadow_text.get_width() // 2, 
                                     panel_y + 40 + offset*2))
        
        title_text = title_font.render("GAME OVER", True, RED)
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, panel_y + 40))
        
        # Draw reason with cool font and effect
        reason_font = pygame.font.SysFont(None, int(FONT_SIZE * 1.5))  # Convert to int
        reason_text = reason_font.render(self.game_over_reason, True, (255, 200, 200))
        # Add shadow
        shadow = reason_font.render(self.game_over_reason, True, (100, 0, 0))
        screen.blit(shadow, (SCREEN_WIDTH // 2 - reason_text.get_width() // 2 + 2, 
                           panel_y + 120 + 2))
        screen.blit(reason_text, (SCREEN_WIDTH // 2 - reason_text.get_width() // 2, 
                                 panel_y + 120))
        
        # Draw score with digital display style
        score_label = self.font.render("YOUR SCORE:", True, (200, 200, 0))
        screen.blit(score_label, (SCREEN_WIDTH // 2 - 100, panel_y + 180))
        
        # Create digital-looking score display
        score_display = pygame.Surface((150, 40))
        score_display.fill((0, 0, 0))  # Black background
        pygame.draw.rect(score_display, (100, 100, 100), (0, 0, 150, 40), 2)  # Gray border
        
        # Add LCD-style segments
        for i in range(5):
            pygame.draw.line(score_display, (50, 50, 50), 
                            (i*30+5, 5), (i*30+5, 35), 1)
        
        score_value = self.font.render(f"{self.score}", True, (0, 255, 0))  # Green digital text
        score_display.blit(score_value, (75 - score_value.get_width()//2, 10))
        screen.blit(score_display, (SCREEN_WIDTH // 2 - 75, panel_y + 210))
        
        # Draw restart button with 90s style
        restart_button = pygame.Surface((200, 40))
        # Gradient from blue to purple
        for x in range(200):
            color = (50, 50 + x//2, 150 - x//4)
            pygame.draw.line(restart_button, color, (x, 0), (x, 40))
        
        # Button border
        pygame.draw.rect(restart_button, (150, 150, 255), (0, 0, 200, 40), 3)
        # 3D effect
        pygame.draw.line(restart_button, (200, 200, 255), (3, 3), (197, 3), 2)
        pygame.draw.line(restart_button, (200, 200, 255), (3, 3), (3, 37), 2)
        pygame.draw.line(restart_button, (50, 50, 150), (3, 37), (197, 37), 2)
        pygame.draw.line(restart_button, (50, 50, 150), (197, 3), (197, 37), 2)
        
        restart_text = self.font.render("Press R to restart", True, WHITE)
        restart_button.blit(restart_text, (100 - restart_text.get_width()//2, 10))
        
        # Make button "glow" with timer
        if pygame.time.get_ticks() % 1000 < 500:
            pygame.draw.rect(restart_button, (200, 200, 255, 100), (0, 0, 200, 40), 5)
        
        screen.blit(restart_button, (SCREEN_WIDTH // 2 - 100, panel_y + 260))
                                  
    def draw_win(self):
        # Draw game screen
        self.draw()
        
        # 90s style celebration overlay with stars and confetti
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 100, 100))  # Semi-transparent blue
        
        # Add stars and confetti
        for _ in range(50):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            size = random.randint(2, 8)
            color = random.choice([
                (255, 255, 0),  # Yellow
                (255, 0, 255),  # Magenta
                (0, 255, 255),  # Cyan
                (255, 150, 0),  # Orange
                (0, 255, 0)     # Green
            ])
            
            # Draw either star or confetti
            if random.random() < 0.5:
                # Star
                points = []
                for i in range(5):
                    angle = i * 2 * math.pi / 5 - math.pi / 2
                    points.append((
                        x + size * math.cos(angle),
                        y + size * math.sin(angle)
                    ))
                    angle += math.pi / 5
                    points.append((
                        x + size/2 * math.cos(angle),
                        y + size/2 * math.sin(angle)
                    ))
                pygame.draw.polygon(overlay, color, points)
            else:
                # Confetti
                pygame.draw.rect(overlay, color, (x, y, size, size//2))
        
        screen.blit(overlay, (0, 0))
        
        # Create 90s style celebration panel
        panel_width, panel_height = 600, 400
        panel_x = SCREEN_WIDTH // 2 - panel_width // 2
        panel_y = SCREEN_HEIGHT // 2 - panel_height // 2
        
        win_panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        
        # Create a radial gradient background
        center_x, center_y = panel_width // 2, panel_height // 2
        max_dist = math.sqrt(center_x**2 + center_y**2)
        for y in range(panel_height):
            for x in range(panel_width):
                dist = math.sqrt((x - center_x)**2 + (y - center_y)**2)
                ratio = dist / max_dist
                color = (
                    int(50 + 100 * (1 - ratio)),  # Red
                    int(0 + 100 * (1 - ratio)),   # Green
                    int(100 + 155 * (1 - ratio)), # Blue
                    220                           # Alpha
                )
                win_panel.set_at((x, y), color)
        
        # Add 90s style geometric patterns to border
        border_size = 15
        for i in range(0, panel_width, 30):
            pygame.draw.rect(win_panel, (255, 255, 0), (i, 0, 15, border_size))
            pygame.draw.rect(win_panel, (0, 255, 255), (i+15, 0, 15, border_size))
            
            pygame.draw.rect(win_panel, (255, 255, 0), (i, panel_height-border_size, 15, border_size))
            pygame.draw.rect(win_panel, (0, 255, 255), (i+15, panel_height-border_size, 15, border_size))
        
        for i in range(0, panel_height, 30):
            pygame.draw.rect(win_panel, (255, 0, 255), (0, i, border_size, 15))
            pygame.draw.rect(win_panel, (255, 255, 0), (0, i+15, border_size, 15))
            
            pygame.draw.rect(win_panel, (255, 0, 255), (panel_width-border_size, i, border_size, 15))
            pygame.draw.rect(win_panel, (255, 255, 0), (panel_width-border_size, i+15, border_size, 15))
        
        screen.blit(win_panel, (panel_x, panel_y))
        
        # Draw "YOU WIN!" text with 90s style
        title_font = pygame.font.SysFont(None, FONT_SIZE * 4)
        
        # Multi-colored letters for "YOU WIN!"
        win_text = "YOU WIN!"
        letter_width = title_font.size(win_text)[0] // len(win_text)
        
        for i, letter in enumerate(win_text):
            color_angle = pygame.time.get_ticks() / 500 + i  # Rotate colors over time
            letter_color = (
                int(127 + 127 * math.sin(color_angle)),
                int(127 + 127 * math.sin(color_angle + 2)),
                int(127 + 127 * math.sin(color_angle + 4))
            )
            
            # Shadow for 3D effect
            shadow_letter = title_font.render(letter, True, (0, 0, 0))
            screen.blit(shadow_letter, (panel_x + 50 + i*letter_width + 4, panel_y + 50 + 4))
            
            # Colored letter
            colored_letter = title_font.render(letter, True, letter_color)
            screen.blit(colored_letter, (panel_x + 50 + i*letter_width, panel_y + 50))
        
        # Draw congratulation message with cool 90s font
        if self.highway:
            message = "You escaped with the Mystery Machine!"
            message2 = "Another case solved by Mystery Inc.!"
        else:
            message = "You saved all your friends and"
            message2 = "returned to the Mystery Machine!"
            
        message_font = pygame.font.SysFont(None, FONT_SIZE * 2)
        message_text = message_font.render(message, True, (255, 255, 200))
        message_text2 = message_font.render(message2, True, (255, 255, 200))
        
        # Add text shadow
        message_shadow = message_font.render(message, True, (100, 100, 150))
        message_shadow2 = message_font.render(message2, True, (100, 100, 150))
        screen.blit(message_shadow, (panel_x + panel_width//2 - message_text.get_width()//2 + 2, panel_y + 150 + 2))
        screen.blit(message_shadow2, (panel_x + panel_width//2 - message_text2.get_width()//2 + 2, panel_y + 180 + 2))
        
        screen.blit(message_text, (panel_x + panel_width//2 - message_text.get_width()//2, panel_y + 150))
        screen.blit(message_text2, (panel_x + panel_width//2 - message_text2.get_width()//2, panel_y + 180))
        
        # Draw score and time with digital display style
        minutes = int(self.time_elapsed / 60000)
        seconds = int((self.time_elapsed % 60000) / 1000)
        
        # Create digital display panel
        score_panel = pygame.Surface((400, 60))
        score_panel.fill((0, 0, 50))  # Dark blue background
        pygame.draw.rect(score_panel, (0, 255, 255), (0, 0, 400, 60), 2)  # Cyan border
        
        # Add LCD-style background
        pygame.draw.rect(score_panel, (0, 0, 30), (10, 10, 380, 40))
        pygame.draw.rect(score_panel, (0, 100, 100), (10, 10, 380, 40), 1)
        
        # Score and time text with digital font look
        score_text = self.font.render(f"SCORE: {self.score}", True, (0, 255, 0))  # Green digital text
        time_text = self.font.render(f"TIME: {minutes:02d}:{seconds:02d}", True, (0, 255, 0))
        
        score_panel.blit(score_text, (20, 20))
        score_panel.blit(time_text, (380 - time_text.get_width(), 20))
        
        screen.blit(score_panel, (panel_x + 100, panel_y + 240))
        
        # Show character lineup at bottom
        character_size = TILE_SIZE * 1.2
        character_y = panel_y + 320
        spacing = int(character_size * 1.2)  # Convert to int
        start_x = panel_x + (panel_width - spacing * 5) // 2
        
        # Draw the celebratory lineup of characters
        images = [SCOOBY_IMG, SHAGGY_IMG, VELMA_IMG, DAPHNE_IMG, FRED_IMG]
        for i, img in enumerate(images):
            scaled_img = pygame.transform.scale(img, (int(character_size), int(character_size)))
            
            # Add bounce animation
            bounce_offset = abs(math.sin((pygame.time.get_ticks() / 200) + i)) * 10
            screen.blit(scaled_img, (start_x + i*spacing, character_y - int(bounce_offset)))  # Convert to int
        
        # Draw restart button with 90s style
        restart_button = pygame.Surface((220, 50))
        # Gradient from purple to blue
        for x in range(220):
            color = (100 + x//3, 0, 150 - x//3)
            pygame.draw.line(restart_button, color, (x, 0), (x, 50))
        
        # Button border with geometric pattern
        pygame.draw.rect(restart_button, (200, 100, 255), (0, 0, 220, 50), 3)
        for i in range(0, 220, 20):
            pygame.draw.rect(restart_button, (255, 255, 0), (i, 0, 10, 3))
            pygame.draw.rect(restart_button, (255, 255, 0), (i, 47, 10, 3))
        
        restart_text = pygame.font.SysFont(None, FONT_SIZE * 2).render("'R' -> Menu", True, WHITE)
        restart_button.blit(restart_text, (110 - restart_text.get_width()//2, 12))
        
        # Make button "pulse" with timer
        glow = abs(math.sin(pygame.time.get_ticks() / 300)) * 3
        pygame.draw.rect(restart_button, (200, 100, 255), (0, 0, 220, 50), int(glow))  # Convert to int
        
        screen.blit(restart_button, (SCREEN_WIDTH // 2 - 110, panel_y + panel_height + 20))
                                  
    def draw_pause(self):
        # Draw darkened game screen
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))  # Semi-transparent black
        screen.blit(overlay, (0, 0))
        
        # Draw pause message
        title_font = pygame.font.SysFont(None, FONT_SIZE * 2)
        title_text = title_font.render("PAUSED", True, WHITE)
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, SCREEN_HEIGHT // 3))
        
        # Draw instructions based on current game state
        if self.state == GameState.DRIVING:
            if self.highway:
                # Highway driving instructions
                instructions = [
                    "Arrow keys or WASD to control the Mystery Machine",
                    "LEFT/RIGHT: Change lanes",
                    "UP/DOWN: Control your speed",
                    "Avoid all obstacles on the highway",
                    "Escape the monster chasing you",
                    "",
                    "Press ESC to resume"
                ]
            else:
                # Neighborhood driving instructions
                instructions = [
                    "Arrow keys or WASD to move",
                    "Find the highway exit to escape",
                    "The monster is chasing you! Hurry!",
                    "Stay on the roads for faster movement",
                    "",
                    "Press ESC to resume"
                ]
        else:
            # Forest/regular gameplay instructions
            instructions = [
                "Arrow keys or WASD to move",
                "Space to use trap (stuns nearby monsters)",
                "Collect Scooby Snacks for speed boosts",
                "Find all friends and take them to the Mystery Machine",
                "Stay away from monsters or Scooby will lose courage",
                "",
                "Press ESC to resume"
            ]
        
        for i, line in enumerate(instructions):
            text = self.font.render(line, True, WHITE)
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 
                               SCREEN_HEIGHT // 3 + title_text.get_height() + 20 + i * 30))
    

    def draw_menu(self):
        # Draw sky background
        screen.blit(SKY_IMG, (0, 0))
        
        # Draw title with a 90s flair
        title_font = pygame.font.SysFont(None, FONT_SIZE * 3)
        title_text = title_font.render("Scooby Doo: Forest Rescue", True, WHITE)
        title_x = SCREEN_WIDTH // 2 - title_text.get_width() // 2
        title_y = 100
        shadow_text = title_font.render("Scooby Doo: Forest Rescue", True, (100, 100, 100))
        screen.blit(shadow_text, (title_x + 2, title_y + 2))
        screen.blit(title_text, (title_x, title_y))
        
        # Draw instructions
        instruction_font = pygame.font.SysFont(None, FONT_SIZE * 2)
        start_text = instruction_font.render("Press 'ENTER' to start", True, WHITE)
        quit_text = instruction_font.render("Press 'ESC' to quit", True, WHITE)
        screen.blit(start_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2, 300))
        screen.blit(quit_text, (SCREEN_WIDTH // 2 - quit_text.get_width() // 2, 350))
        
        # Mechanics, Objective
        fact1 = self.font.render("Your friends got lost... you can get them back to the Mystery Machine...", True, BLACK)
        fact2 = self.font.render("Cookies: speed boost. Brown Square: collect trap; throw trap with 'Space Bar.'", True, BLACK)
        fact3 = self.font.render("Hope you have a great day.", True, GREEN)
        screen.blit(fact1, (100, 475))
        screen.blit(fact2, (100, 525))
        screen.blit(fact3, (100, 560))



        # Draw controls
        control1 = self.font.render("Arrow keys/WASD to move as Scooby.", True, BLACK)
        control2 = self.font.render("Mystery Machine: 'Left'/'Right' arrow keys to steer, 'Up'/'Down' arrow keys to adjust vehicle speed.", True, BLACK)
        screen.blit(control1, (100, 260))
        screen.blit(control2, (SCREEN_WIDTH - 45 - control2.get_width(), 279))
        
        # Add decorative elements
        screen.blit(SCOOBY_IMG, (100, 200))
        screen.blit(MYSTERY_MACHINE_IMG, (SCREEN_WIDTH - 200 - MYSTERY_MACHINE_IMG.get_width(), 200))


    def draw_ui(self):
        # Define colors
        WHITE = (255, 255, 255)
        GRAY = (100, 100, 100)
        
        # Score (top-left)
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        
        # Time (top-right)
        minutes = self.time_elapsed // 60000  # Convert milliseconds to minutes
        seconds = (self.time_elapsed % 60000) // 1000  # Remaining seconds
        time_text = self.font.render(f"Time: {minutes:02d}:{seconds:02d}", True, WHITE)
        screen.blit(time_text, (SCREEN_WIDTH - 100, 10))
        
        # Traps available (bottom-left)
        traps_text = self.font.render(f"Traps: {self.traps_available}", True, WHITE)
        screen.blit(traps_text, (10, SCREEN_HEIGHT - 30))
        
        # Courage meter (bottom-right)
        courage_label = self.font.render("Courage", True, WHITE)
        screen.blit(courage_label, (SCREEN_WIDTH - 150, SCREEN_HEIGHT - 70))
        pygame.draw.rect(screen, GRAY, (SCREEN_WIDTH - 150, SCREEN_HEIGHT - 50, 140, 20))
        filled_width = int(140 * (self.player.courage / 100))
        if self.player.courage > 50:
            courage_color = (0, 255, 0)  # Green for high courage
        elif self.player.courage > 25:
            courage_color = (255, 255, 0)  # Yellow for medium courage
        else:
            courage_color = (255, 0, 0)  # Red for low courage
        pygame.draw.rect(screen, courage_color, (SCREEN_WIDTH - 150, SCREEN_HEIGHT - 50, filled_width, 20))
        
        # Friends Found counter (only in forest phase)
        if self.state == GameState.PLAYING and not (self.all_friends_found and self.transition_ready):
            friends_found_text = self.font.render(f"Friends Found: {len(self.player.found_friends)}/4", True, WHITE)
            screen.blit(friends_found_text, (10, 40))
        
        # Riddle and input during driving
        if self.state == GameState.DRIVING:
            riddle_text = self.font.render("Riddle: " + self.riddle_text, True, WHITE)
            screen.blit(riddle_text, (10, 50))
            input_text = self.font.render("Your answer: " + self.answer_input, True, WHITE)
            screen.blit(input_text, (10, 80))

    
    def run(self):
        # Main game loop
        while True:
            self.handle_events()
            
            if self.state == GameState.PLAYING or self.state == GameState.DRIVING:
                self.update()
                self.update_camera()
                self.draw()
            elif self.state == GameState.MENU:
                self.draw_menu()
            elif self.state == GameState.GAME_OVER:
                self.draw_game_over()
            elif self.state == GameState.WIN:
                self.draw_win()
            elif self.state == GameState.PAUSED:
                self.draw()
                self.draw_pause()
                
            pygame.display.flip()
            self.clock.tick(60)  # 60 FPS



# Start the game
if __name__ == "__main__":
    game = Game()
    game.run()