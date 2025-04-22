# --- Konstanty ---
SCREEN_WIDTH = 800  
SCREEN_HEIGHT = 600 
TILE_SIZE = 40 
ROWS = SCREEN_HEIGHT // TILE_SIZE
COLS = SCREEN_WIDTH // TILE_SIZE
FPS = 60

# --- Konfigurace vln ---
MAX_WAVES = 20
ENEMY_HEALTH_SCALE_FACTOR = 1.2 
ENEMY_SPEED_SCALE_FACTOR = 1.05   

# --- Nastavení zvuku ---
music_volume = 0.4 
sfx_volume = 0.4   
music_muted = False 
sfx_muted = False   

# --- Barvy ---
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

# --- Cesty k assetům ---
GRASS_PATH = None # Set dynamically by map.switch_map
PATH_DIR = None # Not used directly anymore, path segments loaded within map.py
TOWER_PATH = 'Towers/Combat Towers/spr_tower_archer.png' # Base path for tower menu icons, OK
PROJECTILE_PATH = 'Towers/Combat Towers Projectiles/spr_tower_archer_projectile.png' # Base path, OK
DECORATION_FOLDER = None # Set dynamically by map.switch_map
PLATFORM_PATH = None # Set dynamically by map.switch_map
# --- Nastavení věží ---
TOWER_SELL_PERCENTAGE = 0.6 

import pygame
import os
import sys 

# --- Pomocná funkce pro cesty k resource ---
def get_resource_path(relative_path): # Pro pyinstaller ...
    try:
        base_path = sys._MEIPASS
        return os.path.join(base_path, "Data", relative_path)
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_path, relative_path)

CONFIG_DIR = os.path.dirname(os.path.abspath(__file__))


# --- Načítání assetů ---
def load_image(filename, alpha=True):
    absolute_path = get_resource_path(filename) 
    try:
        image = pygame.image.load(absolute_path)
        if alpha:
            image = image.convert_alpha() 
        else:
            image = image.convert() 
    except pygame.error as e:
        return None
    return image

# --- Proměnné pro načtené assety (inicializováno na None/prázdné) ---
PLATFORM_IMAGE = None
TOWER_MENU_IMAGES = {}

# --- Funkce pro načítání assetů vyžadujících inicializaci Pygame ---
def load_config_images():
    global PLATFORM_IMAGE, TOWER_MENU_IMAGES 
    # --- Načíst obrázek platformy ---
    platform_image_loaded = load_image(PLATFORM_PATH)
    if platform_image_loaded:
        try:
            PLATFORM_IMAGE = pygame.transform.scale(platform_image_loaded, (TILE_SIZE, TILE_SIZE))
        except Exception as e:
             PLATFORM_IMAGE = None 
    else:
        PLATFORM_IMAGE = None 

    # --- Načíst obrázky věží změněné pro zobrazení v menu ---
    menu_image_size = TILE_SIZE - 10 
    temp_tower_menu_images = {} 

    for name, data in TOWER_DATA.items():
        img = load_image(data['image_path'])
        if img:
            try:
                scaled_img = pygame.transform.scale(img, (menu_image_size, menu_image_size))
                temp_tower_menu_images[name] = scaled_img
            except Exception as e:
                fallback_surf = pygame.Surface((menu_image_size, menu_image_size))
                fallback_surf.fill(RED) 
                temp_tower_menu_images[name] = fallback_surf
        else:
            fallback_surf = pygame.Surface((menu_image_size, menu_image_size))
            fallback_surf.fill(RED) 
            temp_tower_menu_images[name] = fallback_surf

    TOWER_MENU_IMAGES = temp_tower_menu_images 

# --- Konfigurace věží ---
TOWER_DATA = {
    "Archer": {
        "image_path": 'Towers/Combat Towers/spr_tower_archer.png',
        "projectile_path": 'Towers/Combat Towers Projectiles/spr_tower_archer_projectile.png',
        "sound_path": 'Audio/Towers/Archer.mp3', 
        "levels": [
            # Level 1 
            {
                "cost": 50, 
                "range": 150,
                "fire_rate": 1.0, 
                "damage": 25,
                "upgrade_cost": 75 
                
            },
            # Level 2 
            {
                "cost": 75, 
                "range": 170,
                "fire_rate": 1.2,
                "damage": 50,
                "upgrade_cost": 0,
                "image_path": 'Towers/Combat Towers/spr_tower_archer_level_2.png'
            }
        ]
    },
    "Cannon": {
        "image_path": 'Towers/Combat Towers/spr_tower_cannon.png',
        "projectile_path": 'Towers/Combat Towers Projectiles/spr_tower_cannon_projectile.png',
        "sound_path": 'Audio/Towers/Cannon.mp3',
        "levels": [
            { "cost": 75, "range": 100, "fire_rate": 0.5, "damage": 70, "upgrade_cost": 100 },
            { "cost": 100, "range": 115, "fire_rate": 0.6, "damage": 90, "upgrade_cost": 0, "image_path": 'Towers/Combat Towers/spr_tower_cannon_level_2.png' }
        ]
    },
    "Crossbow": {
        "image_path": 'Towers/Combat Towers/spr_tower_crossbow.png',
        "projectile_path": 'Towers/Combat Towers Projectiles/spr_tower_crossbow_projectile.png',
        "sound_path": 'Audio/Towers/Crossbow.mp3', 
        "levels": [
            { "cost": 60, "range": 180, "fire_rate": 1.2, "damage": 30, "upgrade_cost": 80 },
            { "cost": 80, "range": 200, "fire_rate": 1.4, "damage": 50, "upgrade_cost": 0, "image_path": 'Towers/Combat Towers/spr_tower_crossbow_level_2.png' }
        ]
    },
    "Ice Wizard": {
        "image_path": 'Towers/Combat Towers/spr_tower_ice_wizard.png',
        "projectile_path": 'Towers/Combat Towers Projectiles/spr_tower_ice_wizard_projectile.png',
        "sound_path": 'Audio/Towers/Ice_Wizard.mp3',
        "levels": [
            { "cost": 100, "range": 120, "fire_rate": 0.8, "damage": 10, "slow_factor": 0.5, "slow_duration": 2.0, "upgrade_cost": 120 },
            { "cost": 120, "range": 135, "fire_rate": 0.9, "damage": 20, "slow_factor": 0.4, "slow_duration": 2.5, "upgrade_cost": 0, "image_path": 'Towers/Combat Towers/spr_tower_ice_wizard_level_2.png' }
        ]
    },
    "Lightning Wizard": {
        "image_path": 'Towers/Combat Towers/spr_tower_lightning_tower.png',
        "projectile_path": 'Towers/Combat Towers Projectiles/spr_tower_lightning_tower_projectile.png',
        "sound_path": 'Audio/Towers/Lightning_Wizard.wav', 
        "levels": [
            { "cost": 120, "range": 140, "fire_rate": 0.7, "damage": 30, "chain_targets": 3, "chain_range": 180, "upgrade_cost": 150 },
            { "cost": 150, "range": 155, "fire_rate": 0.8, "damage": 50, "chain_targets": 4, "chain_range": 250, "upgrade_cost": 0, "image_path": 'Towers/Combat Towers/spr_tower_lightning_tower_level_2.png' }
        ]
    },
    "Poison Wizard": {
        "image_path": 'Towers/Combat Towers/spr_tower_poison_wizard.png',
        "projectile_path": 'Towers/Combat Towers Projectiles/spr_tower_poison_wizard_projectile.png',
        "sound_path": 'Audio/Towers/Poison_Wizard.mp3', 
        "levels": [
            { "cost": 90, "range": 130, "fire_rate": 0.9, "damage_over_time": 8, "poison_duration": 5.0, "poison_interval": 0.5, "upgrade_cost": 110 },
            { "cost": 110, "range": 145, "fire_rate": 1.0, "damage_over_time": 12, "poison_duration": 6.0, "poison_interval": 0.5, "upgrade_cost": 0, "image_path": 'Towers/Combat Towers/spr_tower_poison_wizard_level_2.png' }
        ]
    },
    
}
