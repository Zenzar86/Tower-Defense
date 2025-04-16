# --- Constants ---
SCREEN_WIDTH = 800  
SCREEN_HEIGHT = 600 
TILE_SIZE = 40 
ROWS = SCREEN_HEIGHT // TILE_SIZE
COLS = SCREEN_WIDTH // TILE_SIZE
FPS = 60

# --- Wave Configuration ---
MAX_WAVES = 10
ENEMY_HEALTH_SCALE_FACTOR = 1.2 
ENEMY_SPEED_SCALE_FACTOR = 1.05   

# --- Audio Settings ---
music_volume = 0.4 
sfx_volume = 1.0   
music_muted = False 
sfx_muted = False   

# --- Colors ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0) 
BROWN = (139, 69, 19) 
RED = (255, 0, 0)
BLUE = (0, 0, 255) 
GOLD = (255, 215, 0)
UI_BG_COLOR = (60, 60, 80, 200) 
UI_BORDER_COLOR = (180, 180, 200)
UI_BUTTON_COLOR = (80, 80, 100)
UI_BUTTON_HOVER_COLOR = (100, 100, 120)
UI_SELL_COLOR = (200, 80, 80)
UI_UPGRADE_COLOR = (80, 200, 80)

# --- Asset Paths ---
GRASS_PATH = 'Environment/Grass/grass.png'
# PATH_PATH = 'Environment/Path/path.png' # Removed old single path
PATH_DIR = 'Environment/Path' # Directory containing path segments (path0.png, path1.png, etc.)
TOWER_PATH = 'Towers/Combat Towers/spr_tower_archer.png'
PROJECTILE_PATH = 'Towers/Combat Towers Projectiles/spr_tower_archer_projectile.png'
DECORATION_FOLDER = 'Environment/Decoration'
PLATFORM_PATH = 'Environment/Building_platform/platform.png'
# --- Tower Settings ---
TOWER_SELL_PERCENTAGE = 0.6 # Sell towers for 60% of their total invested cost

import pygame
import os
import sys 

# --- Resource Path Helper  ---
def get_resource_path(relative_path): # Pro pyinstallera ...
    try:
        base_path = sys._MEIPASS
        return os.path.join(base_path, "Data", relative_path)
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_path, relative_path)

# Get the directory where config.py resides (still useful for some relative loads)
CONFIG_DIR = os.path.dirname(os.path.abspath(__file__))


# --- Asset Loading ---
def load_image(filename, alpha=True):
    """Helper function to load images using get_resource_path."""
    absolute_path = get_resource_path(filename) # Use the helper function
    # print(f"Attempting to load image from: {absolute_path}") # Keep debug print for now
    try:
        image = pygame.image.load(absolute_path)
        if alpha:
            image = image.convert_alpha() # Use transparency
        else:
            image = image.convert() # No transparency needed (faster)
    except pygame.error as e:
        print(f"Cannot load image: {absolute_path}")
        print(f"Pygame error: {e}") # Print the specific pygame error
        # Return None on failure instead of exiting
        return None
    return image

# --- Variables for Loaded Assets (initialized to None/empty) ---
PLATFORM_IMAGE = None
TOWER_MENU_IMAGES = {}

# --- Function to Load Assets Requiring Pygame Initialization ---
def load_config_images():
    """Loads and processes images that require pygame display mode to be set."""
    global PLATFORM_IMAGE, TOWER_MENU_IMAGES # Declare intent to modify globals

    print("--- Loading Config Images ---")

    # --- Load Platform Image ---
    platform_image_loaded = load_image(PLATFORM_PATH)
    if platform_image_loaded:
        try:
            # Scale platform to match tower base size (TILE_SIZE)
            PLATFORM_IMAGE = pygame.transform.scale(platform_image_loaded, (TILE_SIZE, TILE_SIZE))
            print("Platform image loaded and scaled.")
        except Exception as e:
             print(f"ERROR: Could not scale platform image: {e}")
             PLATFORM_IMAGE = None # Ensure it's None if scaling fails
    else:
        print("ERROR: Failed to load platform image.")
        PLATFORM_IMAGE = None # Ensure it's None if loading fails

    # --- Load Tower Images Scaled for Menu Display ---
    menu_image_size = TILE_SIZE - 10 # Make menu icons slightly smaller than tiles
    temp_tower_menu_images = {} # Use a temporary dict

    for name, data in TOWER_DATA.items():
        img = load_image(data['image_path'])
        if img:
            try:
                scaled_img = pygame.transform.scale(img, (menu_image_size, menu_image_size))
                temp_tower_menu_images[name] = scaled_img
                print(f"Loaded and scaled menu image for tower: {name}")
            except Exception as e:
                print(f"ERROR: Could not scale menu image for {name}: {e}")
                # Create a fallback surface if scaling fails
                fallback_surf = pygame.Surface((menu_image_size, menu_image_size))
                fallback_surf.fill(RED) # Indicate error
                temp_tower_menu_images[name] = fallback_surf
        else:
            # Fallback if image fails to load (error already printed by load_image)
            fallback_surf = pygame.Surface((menu_image_size, menu_image_size))
            fallback_surf.fill(RED) # Indicate error
            temp_tower_menu_images[name] = fallback_surf
            print(f"Using fallback menu image for tower: {name}")

    TOWER_MENU_IMAGES = temp_tower_menu_images 
    print("--- Finished Loading Config Images ---")

# TOWER_SAMPLE_IMAGE = load_image(TOWER_PATH)


# --- Tower Configuration ---
# Central dictionary holding data for each tower type
TOWER_DATA = {
    "Archer": {
        "image_path": 'Towers/Combat Towers/spr_tower_archer.png',
        "projectile_path": 'Towers/Combat Towers Projectiles/spr_tower_archer_projectile.png',
        "sound_path": 'Audio/Towers/Archer.mp3', 
        "levels": [
            # Level 1 (Index 0)
            {
                "cost": 50, # Initial cost
                "range": 150,
                "fire_rate": 1.0, # Shots per second
                "damage": 25,
                "upgrade_cost": 75 # Cost to upgrade TO level 2
                # "image_path": 'level1_image.png' # Optional: different image per level
            },
            # Level 2 (Index 1)
            {
                "cost": 75, # Cost of the upgrade itself
                "range": 170,
                "fire_rate": 1.2,
                "damage": 50,
                "upgrade_cost": 0 # Cost to upgrade TO level 3 (0 means max level)
                
            }
            # Add Level 3 etc. here
        ]
    },
    "Cannon": {
        "image_path": 'Towers/Combat Towers/spr_tower_cannon.png',
        "projectile_path": 'Towers/Combat Towers Projectiles/spr_tower_cannon_projectile.png',
        "sound_path": 'Audio/Towers/Cannon.mp3',
        "levels": [
            { "cost": 75, "range": 100, "fire_rate": 0.5, "damage": 70, "upgrade_cost": 100 },
            { "cost": 100, "range": 115, "fire_rate": 0.6, "damage": 90, "upgrade_cost": 0 }
        ]
    },
    "Crossbow": {
        "image_path": 'Towers/Combat Towers/spr_tower_crossbow.png',
        "projectile_path": 'Towers/Combat Towers Projectiles/spr_tower_crossbow_projectile.png',
        "sound_path": 'Audio/Towers/Crossbow.mp3', 
        "levels": [
            { "cost": 60, "range": 180, "fire_rate": 1.2, "damage": 30, "upgrade_cost": 80 },
            { "cost": 80, "range": 200, "fire_rate": 1.4, "damage": 50, "upgrade_cost": 0 }
        ]
    },
    "Ice Wizard": {
        "image_path": 'Towers/Combat Towers/spr_tower_ice_wizard.png',
        "projectile_path": 'Towers/Combat Towers Projectiles/spr_tower_ice_wizard_projectile.png',
        "sound_path": 'Audio/Towers/Ice_Wizard.mp3',
        "levels": [
            { "cost": 100, "range": 120, "fire_rate": 0.8, "damage": 10, "slow_factor": 0.5, "slow_duration": 2.0, "upgrade_cost": 120 },
            { "cost": 120, "range": 135, "fire_rate": 0.9, "damage": 20, "slow_factor": 0.4, "slow_duration": 2.5, "upgrade_cost": 0 }
        ]
    },
    "Lightning Wizard": {
        "image_path": 'Towers/Combat Towers/spr_tower_lightning_tower.png',
        "projectile_path": 'Towers/Combat Towers Projectiles/spr_tower_lightning_tower_projectile.png',
        "sound_path": 'Audio/Towers/Lightning_Wizard.wav', 
        "levels": [
            { "cost": 120, "range": 140, "fire_rate": 0.7, "damage": 30, "chain_targets": 3, "chain_range": 180, "upgrade_cost": 150 },
            { "cost": 150, "range": 155, "fire_rate": 0.8, "damage": 50, "chain_targets": 4, "chain_range": 250, "upgrade_cost": 0 }
        ]
    },
    "Poison Wizard": {
        "image_path": 'Towers/Combat Towers/spr_tower_poison_wizard.png',
        "projectile_path": 'Towers/Combat Towers Projectiles/spr_tower_poison_wizard_projectile.png',
        "sound_path": 'Audio/Towers/Poison_Wizard.mp3', 
        "levels": [
            { "cost": 90, "range": 130, "fire_rate": 0.9, "damage_over_time": 8, "poison_duration": 5.0, "poison_interval": 0.5, "upgrade_cost": 110 },
            { "cost": 110, "range": 145, "fire_rate": 1.0, "damage_over_time": 12, "poison_duration": 6.0, "poison_interval": 0.5, "upgrade_cost": 0 }
        ]
    },
    
}
