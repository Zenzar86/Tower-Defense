import pygame
import sys
import os
import math
import random
import config # Moved import to the top

pygame.init()
pygame.display.init()

#region Pygame Mixer Initialization and Sound Loading
try:
    pygame.mixer.init()
    # print("Pygame mixer initialized.") # Removed debug print
    # Load Sound Effects using get_resource_path from config
    try:
        # Note: get_resource_path expects path relative to Data folder now
        button_sound_path = config.get_resource_path("Audio/Button.mp3")
        building_sound_path = config.get_resource_path("Audio/Building.wav")
        music_path_1 = config.get_resource_path("Audio/Main_1.mp3")
        music_path_2 = config.get_resource_path("Audio/Main_2.mp3")

        button_sound = pygame.mixer.Sound(button_sound_path)
        building_sound = pygame.mixer.Sound(building_sound_path)
        # print("Sound effects loaded.")

        # Load and Start Background Music (Use volumes and mute state from config)
        pygame.mixer.music.load(music_path_1) # Path is already absolute via get_resource_path
        initial_music_vol = 0 if config.music_muted else config.music_volume
        pygame.mixer.music.set_volume(initial_music_vol)
        initial_sfx_vol = 0 if config.sfx_muted else config.sfx_volume
        if button_sound: button_sound.set_volume(initial_sfx_vol)
        if building_sound: building_sound.set_volume(initial_sfx_vol)
        pygame.mixer.music.play(-1) # Loop indefinitely
        # print(f"Loaded and playing music: {music_path_1}") # Removed debug print

    except pygame.error as e:
        print(f"ERROR: Could not load sound file: {e}")
        button_sound = None
        building_sound = None
    except FileNotFoundError as e:
        print(f"ERROR: Sound file not found: {e}")
        button_sound = None
        building_sound = None
    except Exception as e:
        print(f"ERROR: An unexpected error occurred loading sounds: {e}")
        button_sound = None
        building_sound = None

except pygame.error as e:
    print(f"ERROR: Failed to initialize pygame mixer: {e}. No sound will be played.")
    button_sound = None
    building_sound = None
#endregion


#region Imports
# import config # Removed redundant import here
from config import *
from enemies import create_enemy
import map
from towers import create_tower
from projectiles import Projectile
from decorations import Decoration
import languages
from languages import get_text, set_language
import screens # Import the new screens module
import tower_ui # Import the new tower_ui module
import game_ui # Import the game UI module
#endregion


#region Pygame Initialization
#endregion Pygame Initialization # Already removed commented init

#region Pygame Display Setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tower Defense")

# --- Load Assets AFTER Display Init ---
config.load_config_images() # Load images from config (platform, tower menu icons)
map.load_map_assets()    # Load images from map (path segments) and generate path pixels


#endregion Pygame Display Setup

#region Pygame Font Setup
# Create a dictionary to hold different fonts
fonts = {}
try:
    fonts['default'] = pygame.font.SysFont(None, 30) # Default UI font
    fonts['large'] = pygame.font.SysFont(None, 72)   # For titles
    fonts['medium'] = pygame.font.SysFont(None, 48)  # For buttons/medium text
    fonts['small'] = pygame.font.SysFont(None, 24)   # For smaller text (tower menu, tutorial body)
    fonts['tiny'] = pygame.font.SysFont(None, 20)    # For upgrade/sell panel text
    fonts['tower_stats'] = pygame.font.SysFont(None, 18) # For tutorial tower stats
    ui_font = fonts['default'] # Keep ui_font reference for compatibility if needed elsewhere
except Exception as e:
    print(f"Could not load system font: {e}. Using default pygame font.")
    # Fallback if SysFont fails
    fonts['default'] = pygame.font.Font(None, 30)
    fonts['large'] = pygame.font.Font(None, 72)
    fonts['medium'] = pygame.font.Font(None, 48)
    fonts['small'] = pygame.font.Font(None, 24)
    fonts['tiny'] = pygame.font.Font(None, 20)
    fonts['tower_stats'] = pygame.font.Font(None, 18)
    ui_font = fonts['default']
#endregion Pygame Font Setup

#region Button Rect Management
# Central dictionary to store all button rectangles, managed by drawing functions
button_rects = {
    'start': None, 'exit': None, 'tutorial_ok': None, 'lang_en': None, 'lang_cz': None,
    'game_over_restart': None, 'game_over_exit': None, 'victory_restart': None,
    'victory_exit': None, 'help': None, 'upgrade': None, 'sell': None,
    # Add keys for settings screen buttons (will be populated by draw_settings_screen)
    'settings_back': None, 'volume_bar_music': None, 'volume_bar_sfx': None,
    'mute_music': None, 'mute_sfx': None
}
#endregion Button Rect Management

#region Asset Loading

# --- Tiles ---
grass_img_loaded = config.load_image(GRASS_PATH, alpha=False)

if grass_img_loaded:
    grass_tile = pygame.transform.scale(grass_img_loaded, (TILE_SIZE, TILE_SIZE))
else:
    print("ERROR: Failed to load grass tile. Using fallback color.")
    grass_tile = pygame.Surface((TILE_SIZE, TILE_SIZE))
    grass_tile.fill(GREEN)

# Load platform tile
platform_img_loaded = config.load_image("Environment/Building_platform/platform.png", alpha=True)
if platform_img_loaded:
    platform_tile = pygame.transform.scale(platform_img_loaded, (TILE_SIZE, TILE_SIZE))
else:
    print("ERROR: Failed to load platform tile. Building might not be visually indicated.")
    platform_tile = None
#endregion Asset Loading

#region Map Drawing Function
def draw_map(surface):
    for row_index, row in enumerate(map.game_map):
        for col_index, tile_type in enumerate(row):
            x = col_index * TILE_SIZE
            y = row_index * TILE_SIZE
            if tile_type == 0:
                if grass_tile:
                     surface.blit(grass_tile, (x, y))
                else:
                     pygame.draw.rect(surface, GREEN, (x, y, TILE_SIZE, TILE_SIZE))
            elif tile_type == 2:
                if platform_tile:
                    surface.blit(platform_tile, (x, y))
                elif grass_tile:
                     surface.blit(grass_tile, (x, y))
                else:
                     pygame.draw.rect(surface, GREEN, (x, y, TILE_SIZE, TILE_SIZE))
            elif tile_type == 3:
                if grass_tile:
                     surface.blit(grass_tile, (x, y))
                else:
                     pygame.draw.rect(surface, GREEN, (x, y, TILE_SIZE, TILE_SIZE))
            elif tile_type == 1:
                # Call the updated function which now uses the global map internally
                path_image_to_draw = map.get_path_tile_image(row_index, col_index)
                if path_image_to_draw:
                    surface.blit(path_image_to_draw, (x, y))
                else:
                    pygame.draw.rect(surface, BROWN, (x, y, TILE_SIZE, TILE_SIZE))
#endregion Map Drawing Function

#region Decoration Loading and Placement
# --- Load decoration images ---
decoration_images = {}
decoration_folder = DECORATION_FOLDER # This is 'Environment/Decoration'
try:
    # Use get_resource_path to find the absolute path to the decoration folder,
    # whether running normally or frozen.
    abs_decoration_folder_path = config.get_resource_path(decoration_folder)
    # print(f"Attempting to list decorations in: {abs_decoration_folder_path}") # Optional debug print

    if os.path.isdir(abs_decoration_folder_path):
        for filename in os.listdir(abs_decoration_folder_path):
            if filename.endswith('.png'):
                name = os.path.splitext(filename)[0]
                # The relative path for load_image is still correct, as load_image
                # handles the 'Data' prefix when frozen.
                relative_path = os.path.join(decoration_folder, filename)
                loaded_deco_img = config.load_image(relative_path, alpha=True)
                if loaded_deco_img:
                    decoration_images[name] = loaded_deco_img
                else:
                    print(f"Skipping decoration due to loading error: {relative_path}") # Keep error
    else:
        # Update error message to show the path we tried
        print(f"ERROR: Decoration folder not found or not a directory at resolved path: {abs_decoration_folder_path}")
except Exception as e:
    # Add more context to the exception message if possible
    print(f"ERROR: Could not list or load decorations from '{decoration_folder}': {e}")


# --- Clock Setup ---
clock = pygame.time.Clock()

# --- Clock Setup ---
clock = pygame.time.Clock()
#endregion Decoration Loading and Placement

#region Game Object Initialization
# --- Sprite Groups ---
enemies = pygame.sprite.Group()
towers = pygame.sprite.Group()
projectiles = pygame.sprite.Group()
decorations = pygame.sprite.Group()

# --- Place Initial Decorations ---
if decoration_images:
    decoration_names = list(decoration_images.keys())
    placed_decorations = 0
    max_decorations = 50
    attempts = 0
    max_attempts = 100

    while placed_decorations < max_decorations and attempts < max_attempts:
        attempts += 1
        rand_row = random.randint(0, ROWS - 1)
        rand_col = random.randint(0, COLS - 1)

        is_grass = map.game_map[rand_row][rand_col] == 0
        is_path_adjacent = False


        tile_center_x = rand_col * TILE_SIZE + TILE_SIZE // 2
        tile_center_y = rand_row * TILE_SIZE + TILE_SIZE // 2
        potential_rect = pygame.Rect(rand_col * TILE_SIZE, rand_row * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        occupied = False
        for deco in decorations:
            if deco.rect.colliderect(potential_rect):
                occupied = True
                break

        if is_grass and not occupied:
            deco_name = random.choice(decoration_names)
            deco_image = decoration_images[deco_name]
            new_deco = Decoration(deco_image, (tile_center_x, tile_center_y))
            decorations.add(new_deco)
            placed_decorations += 1
#endregion Game Object Initialization

#region Game State Variables
player_stats = {
    "health": 20,
    "currency": 200
}
current_wave = 0
wave_ongoing = False
last_spawn_time = 0
spawn_interval = 1000
enemies_in_wave = 0
enemies_spawned_this_wave = 0
wave_delay = 5000

# music_volume and sfx_volume are now managed in config.py
# music_muted and sfx_muted are now managed in config.py

game_state = "main_menu"
previous_game_state = "main_menu"

wave_definitions = { # Defines enemies and counts for each wave
    1: {"normal_slime": 10},
    2: {"normal_slime": 12, "bat": 4},
    3: {"normal_slime": 7, "big_slime": 6, "bat": 6},
    4: {"big_slime": 10, "ghost": 7, "bat": 7},
    5: {"king_slime": 1, "normal_slime": 10}, # Boss wave 5
    6: {"goblin": 25, "skeleton": 5},
    7: {"zombie": 12, "ghost": 6, "bat": 10},
    8: {"skeleton": 10, "big_slime": 4, "demon": 6},
    9: {"demon": 5, "king_slime": 1, "ghost": 18},
    10: {"demon": 1, "skeleton": 10} # Final wave
    # 11:{}
}
current_wave_enemies_to_spawn = []
#endregion Game State Variables

#region Button Rect Management
# Central dictionary to store all button rectangles (moved settings keys here)
button_rects = {
    'start': None, 'exit': None, 'tutorial_ok': None, 'lang_en': None, 'lang_cz': None,
    'game_over_restart': None, 'game_over_exit': None, 'victory_restart': None,
    'victory_exit': None, 'help': None, 'upgrade': None, 'sell': None,
    'settings_back': None, 'volume_bar_music': None, 'volume_bar_sfx': None,
    'mute_music': None, 'mute_sfx': None
}

# Flag for showing help overlay remains global for now
show_help_overlay = False
#endregion Button Rect Management

#region Game State Reset Function
def reset_game_state():
    """Resets game variables to initial state for starting/restarting."""
    global player_stats, current_wave, wave_ongoing, enemies_spawned_this_wave
    global last_wave_end_time, game_state, selected_tower_type, selected_tower_for_ui
    global enemies, towers, projectiles, previous_game_state # Added previous_game_state

    print("Resetting game state...")

    # Player stats
    player_stats = {
        "health": 20,
        "currency": 200
    }

    # Wave variables
    current_wave = 0
    wave_ongoing = False
    enemies_spawned_this_wave = 0
    last_wave_end_time = -wave_delay # Allows first wave to start immediately after tutorial/reset

    # Selections
    selected_tower_type = None
    selected_tower_for_ui = None

    # Sprite groups (clear all dynamic objects)
    enemies.empty()
    towers.empty()
    projectiles.empty()

    # Reload map assets (which includes resetting the map grid)
    map.load_map_assets()

    # Game state is set by the caller after reset

    print("Game state reset.") # Keep for console feedback
#endregion Game State Reset Function

#region Main Game Loop
running = True
current_game_time = 0
last_wave_end_time = -wave_delay # Allow first wave to start immediately

# Flags for dragging volume bars (add these before the loop)
dragging_music_bar = False
dragging_sfx_bar = False

while running:
    current_game_time = pygame.time.get_ticks()

    #region Event Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # --- Keyboard Input ---
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE: # Pause/Resume
                if game_state == "playing":
                    game_state = "paused"
                    print(get_text("paused_message")) # Keep console message for pause/resume
                elif game_state == "paused":
                    game_state = "playing"
                    print(get_text("resumed_message"))

        # --- Mouse Input ---
        # MOUSEBUTTONDOWN Handling
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: # Left mouse button
                mouse_pos = event.pos

                # == Menu State Click Handling (Main Menu, Pause, Tutorial) ==
                if game_state in ["main_menu", "paused", "tutorial"]:
                    # --- Language Button Clicks (Only in Main Menu) ---
                    if game_state == "main_menu":
                        if button_rects.get('lang_en') and button_rects['lang_en'].collidepoint(mouse_pos):
                            set_language('EN')
                            if button_sound: button_sound.play()
                            continue # Skip other checks
                        elif button_rects.get('lang_cz') and button_rects['lang_cz'].collidepoint(mouse_pos):
                            set_language('CZ')
                            if button_sound: button_sound.play()
                            continue # Skip other checks

                    # Check Settings Button (Main Menu / Pause Menu)
                    if (game_state == "main_menu" or game_state == "paused") and button_rects.get('settings') and button_rects['settings'].collidepoint(mouse_pos):
                        if button_sound: button_sound.play()
                        previous_game_state = game_state # Store current state to return to
                        game_state = "settings"
                        print(f"Going to settings from {previous_game_state}...")
                        continue # Skip further menu checks

                    # Check Start/Restart Button (Main Menu / Pause Menu) - Uses 'start' key
                    if (game_state == "main_menu" or game_state == "paused") and button_rects.get('start') and button_rects['start'].collidepoint(mouse_pos):
                        if button_sound: button_sound.play() # Play sound first
                        if game_state == "main_menu":
                            game_state = "tutorial"
                            print(get_text("showing_tutorial"))
                            button_rects['start'] = None # Clear main menu button rects
                            button_rects['exit'] = None
                        elif game_state == "paused":
                            reset_game_state()
                            game_state = "playing"
                            last_wave_end_time = pygame.time.get_ticks() - wave_delay
                            print(get_text("restarting_message"))
                            button_rects['start'] = None # Clear pause menu button rects
                            button_rects['exit'] = None
                        continue # Skip other checks

                    # Check Exit Button (Main Menu / Pause Menu) - Uses 'exit' key
                    elif (game_state == "main_menu" or game_state == "paused") and button_rects.get('exit') and button_rects['exit'].collidepoint(mouse_pos):
                        if button_sound: button_sound.play()
                        pygame.time.wait(100) # Allow sound to play
                        running = False
                        continue # Exit loop

                    # Check Tutorial OK Button - Uses 'tutorial_ok' key
                    elif game_state == "tutorial" and button_rects.get('tutorial_ok') and button_rects['tutorial_ok'].collidepoint(mouse_pos):
                            if button_sound: button_sound.play()
                            reset_game_state()
                            game_state = "playing"
                            last_wave_end_time = pygame.time.get_ticks()
                            print(get_text("tutorial_finished"))
                            button_rects['tutorial_ok'] = None # Clear tutorial button rect
                            continue # Skip other checks

                # == Playing State Click Handling ==
                elif game_state == "playing":
                    # --- Help Overlay Toggle ---
                    if show_help_overlay:
                        show_help_overlay = False
                        continue # Any click closes help overlay
                    if button_rects.get('help') and button_rects['help'].collidepoint(mouse_pos):
                        show_help_overlay = True
                        continue # Click help button opens it

                    # --- Gameplay Clicks (Tower Menu, Map Tiles) ---
                    # Use config.MENU_HEIGHT if defined, otherwise default to 80
                    try: m_height = config.MENU_HEIGHT
                    except AttributeError: m_height = 80
                    menu_rect = pygame.Rect(0, SCREEN_HEIGHT - m_height, SCREEN_WIDTH, m_height)

                    # Tower Build Menu Click
                    if menu_rect.collidepoint(mouse_pos):
                        num_towers = len(config.TOWER_DATA)
                        if num_towers > 0:
                            item_base_width = 60; item_height = m_height - 10; spacing = 15
                            total_content_width = (item_base_width * num_towers) + (spacing * (num_towers - 1))
                            start_x = (SCREEN_WIDTH - total_content_width) // 2
                            current_x = start_x
                            tower_names = list(config.TOWER_DATA.keys())
                            for i in range(num_towers):
                                item_click_rect = pygame.Rect(current_x, SCREEN_HEIGHT - m_height + 5, item_base_width, item_height)
                                if item_click_rect.collidepoint(mouse_pos):
                                    selected_tower_type = tower_names[i]
                                    selected_tower_for_ui = None # Deselect any existing tower UI
                                    print(f"Selected tower type: {selected_tower_type}")
                                    break
                                current_x += item_base_width + spacing
                    # Click outside build menu
                    else:
                        clicked_on_ui_button = False
                        # Check Upgrade/Sell UI first
                        if selected_tower_for_ui:
                            if button_rects.get('upgrade') and button_rects['upgrade'].collidepoint(mouse_pos):
                                selected_tower_for_ui.upgrade(player_stats)
                                clicked_on_ui_button = True
                            elif button_rects.get('sell') and button_rects['sell'].collidepoint(mouse_pos):
                                sell_price = selected_tower_for_ui.get_sell_price()
                                print(get_text("tower_sell", tower_type=selected_tower_for_ui.tower_type_name, price=sell_price))
                                player_stats['currency'] += sell_price
                                if hasattr(selected_tower_for_ui, 'grid_x') and hasattr(selected_tower_for_ui, 'grid_y'):
                                    gx, gy = selected_tower_for_ui.grid_x, selected_tower_for_ui.grid_y
                                    if 0 <= gy < ROWS and 0 <= gx < COLS and map.game_map[gy][gx] == 3: map.game_map[gy][gx] = 2
                                selected_tower_for_ui.kill(); selected_tower_for_ui = None
                                button_rects['upgrade'] = None; button_rects['sell'] = None
                                clicked_on_ui_button = True
                                if button_sound: button_sound.play()

                        # If not UI button, handle map clicks
                        if not clicked_on_ui_button:
                            tile_col = mouse_pos[0] // TILE_SIZE
                            tile_row = mouse_pos[1] // TILE_SIZE
                            clicked_on_existing_tower = False
                            # Check existing towers
                            for tower in towers:
                                if tower.rect.collidepoint(mouse_pos):
                                    selected_tower_for_ui = tower
                                    selected_tower_type = None
                                    print(get_text("tower_selected", tower_type=selected_tower_for_ui.tower_type_name, pos=selected_tower_for_ui.rect.center))
                                    clicked_on_existing_tower = True
                                    break
                            # Try placing new tower OR deselect UI
                            if not clicked_on_existing_tower:
                                if selected_tower_type:
                                    grid_x, grid_y = tile_col, tile_row
                                    if 0 <= grid_y < ROWS and 0 <= grid_x < COLS and map.game_map[grid_y][grid_x] == 2:
                                        can_build = True
                                        for t in towers:
                                            if hasattr(t, 'grid_x') and hasattr(t, 'grid_y') and t.grid_x == grid_x and t.grid_y == grid_y:
                                                can_build = False; print(get_text("cannot_build_occupied", grid_x=grid_x, grid_y=grid_y)); break
                                        try: required_cost = config.TOWER_DATA[selected_tower_type]['levels'][0]['cost']
                                        except (KeyError, IndexError): print(get_text("error_cost_missing", tower_type=selected_tower_type)); required_cost = float('inf')

                                        if can_build and player_stats["currency"] >= required_cost:
                                            player_stats["currency"] -= required_cost
                                            tower_pos = (grid_x * TILE_SIZE + TILE_SIZE // 2, grid_y * TILE_SIZE + TILE_SIZE // 2)
                                            new_tower = create_tower(selected_tower_type, tower_pos, projectiles, enemies, building_sound)
                                            if new_tower:
                                                towers.add(new_tower); new_tower.grid_x = grid_x; new_tower.grid_y = grid_y
                                                map.game_map[grid_y][grid_x] = 3
                                                print(get_text("tower_placed", tower_type=selected_tower_type, grid_x=grid_x, grid_y=grid_y, cost=required_cost))
                                                if building_sound: building_sound.play()
                                            else: player_stats["currency"] += required_cost; print(get_text("error_create_tower", tower_type=selected_tower_type))
                                        elif not can_build: pass
                                        elif player_stats["currency"] < required_cost: print(get_text("cannot_build_no_gold", tower_type=selected_tower_type, cost=required_cost, have=player_stats['currency']))
                                    else: print(get_text("cannot_build_invalid_tile", grid_x=grid_x, grid_y=grid_y))
                                else: selected_tower_for_ui = None # Clicked map, deselect UI

                # == Settings Screen Click Handling (Moved from screens.py) ==
                elif game_state == "settings":
                    # Back Button
                    if button_rects.get('settings_back') and button_rects['settings_back'].collidepoint(mouse_pos):
                        if button_sound: button_sound.play()
                        game_state = previous_game_state # Return to main_menu or paused
                        print(f"Returning to {game_state}...")
                        # Clear settings-specific button rects when leaving
                        button_rects['settings_back'] = None
                        button_rects['volume_bar_music'] = None
                        button_rects['volume_bar_sfx'] = None
                        button_rects['mute_music'] = None
                        button_rects['mute_sfx'] = None
                    # Mute Music Button
                    elif button_rects.get('mute_music') and button_rects['mute_music'].collidepoint(mouse_pos):
                        config.music_muted = not config.music_muted
                        if config.music_muted:
                            pygame.mixer.music.set_volume(0)
                            print("Music Muted")
                        else:
                            pygame.mixer.music.set_volume(config.music_volume)
                            print("Music Unmuted")
                        if button_sound: button_sound.play()
                    # Mute SFX Button
                    elif button_rects.get('mute_sfx') and button_rects['mute_sfx'].collidepoint(mouse_pos):
                        config.sfx_muted = not config.sfx_muted
                        current_sfx_vol = 0 if config.sfx_muted else config.sfx_volume
                        if button_sound: button_sound.set_volume(current_sfx_vol)
                        if building_sound: building_sound.set_volume(current_sfx_vol)
                        print(f"SFX Muted: {config.sfx_muted}")
                        if button_sound: button_sound.play()
                    # Music Volume Bar Click (Start Drag)
                    elif button_rects.get('volume_bar_music') and button_rects['volume_bar_music'].collidepoint(mouse_pos):
                        dragging_music_bar = True
                        # Update volume immediately on click
                        volume_bar_rect = button_rects['volume_bar_music']
                        click_x_relative = mouse_pos[0] - volume_bar_rect.left
                        new_music_volume = max(0.0, min(1.0, click_x_relative / volume_bar_rect.width))
                        if config.music_muted: # Unmute if clicking bar while muted
                            config.music_muted = False
                            print("Music Unmuted (by clicking bar)")
                        config.music_volume = new_music_volume
                        pygame.mixer.music.set_volume(config.music_volume)
                        print(f"Music Volume set to {config.music_volume:.2f}")
                    # SFX Volume Bar Click (Start Drag)
                    elif button_rects.get('volume_bar_sfx') and button_rects['volume_bar_sfx'].collidepoint(mouse_pos):
                        dragging_sfx_bar = True
                         # Update volume immediately on click
                        volume_bar_rect = button_rects['volume_bar_sfx']
                        click_x_relative = mouse_pos[0] - volume_bar_rect.left
                        new_sfx_volume = max(0.0, min(1.0, click_x_relative / volume_bar_rect.width))
                        if config.sfx_muted: # Unmute if clicking bar while muted
                            config.sfx_muted = False
                            print("SFX Unmuted (by clicking bar)")
                        config.sfx_volume = new_sfx_volume
                        current_sfx_vol = 0 if config.sfx_muted else config.sfx_volume # Re-check mute state just in case
                        if button_sound: button_sound.set_volume(current_sfx_vol)
                        if building_sound: building_sound.set_volume(current_sfx_vol)
                        print(f"SFX Volume set to {config.sfx_volume:.2f}")

                # == Game Over State Click Handling ==
                elif game_state == "lost":
                    if button_rects.get('game_over_restart') and button_rects['game_over_restart'].collidepoint(mouse_pos):
                        if button_sound: button_sound.play()
                        reset_game_state(); game_state = "playing"; last_wave_end_time = pygame.time.get_ticks()
                        print(get_text("restarting_message")); button_rects['game_over_restart']=None; button_rects['game_over_exit']=None
                    elif button_rects.get('game_over_exit') and button_rects['game_over_exit'].collidepoint(mouse_pos):
                        if button_sound: button_sound.play(); pygame.time.wait(100); running = False

                # == Victory State Click Handling ==
                elif game_state == "won":
                    if button_rects.get('victory_restart') and button_rects['victory_restart'].collidepoint(mouse_pos):
                        if button_sound: button_sound.play()
                        reset_game_state(); game_state = "playing"; last_wave_end_time = pygame.time.get_ticks()
                        print(get_text("restarting_message")); button_rects['victory_restart']=None; button_rects['victory_exit']=None
                    elif button_rects.get('victory_exit') and button_rects['victory_exit'].collidepoint(mouse_pos):
                        if button_sound: button_sound.play(); pygame.time.wait(100); running = False

        # MOUSEMOTION Handling (Volume Bar Dragging)
        elif event.type == pygame.MOUSEMOTION:
            if game_state == "settings":
                mouse_pos = event.pos
                # Music Bar Dragging
                if dragging_music_bar:
                    volume_bar_rect = button_rects.get('volume_bar_music')
                    if volume_bar_rect: # Check if rect exists
                        click_x_relative = mouse_pos[0] - volume_bar_rect.left
                        new_music_volume = max(0.0, min(1.0, click_x_relative / volume_bar_rect.width))
                        if not config.music_muted: # Only update if not muted
                            config.music_volume = new_music_volume
                            pygame.mixer.music.set_volume(config.music_volume)
                            # print(f"Music Volume set to {config.music_volume:.2f} (dragging)") # Optional: reduce console spam
                # SFX Bar Dragging
                elif dragging_sfx_bar:
                    volume_bar_rect = button_rects.get('volume_bar_sfx')
                    if volume_bar_rect: # Check if rect exists
                        click_x_relative = mouse_pos[0] - volume_bar_rect.left
                        new_sfx_volume = max(0.0, min(1.0, click_x_relative / volume_bar_rect.width))
                        if not config.sfx_muted: # Only update if not muted
                            config.sfx_volume = new_sfx_volume
                            current_sfx_vol = config.sfx_volume # Use the new volume
                            if button_sound: button_sound.set_volume(current_sfx_vol)
                            if building_sound: building_sound.set_volume(current_sfx_vol)
                            # print(f"SFX Volume set to {config.sfx_volume:.2f} (dragging)") # Optional: reduce console spam

        # MOUSEBUTTONUP Handling (Stop Dragging)
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                dragging_music_bar = False
                dragging_sfx_bar = False

    #endregion Event Handling

    #region Game Logic (Wave Spawning, Updates)
    # --- Wave Spawning Logic ---
    if game_state == "playing":
        # --- Start Next Wave ---
        if not wave_ongoing:
            if current_game_time - last_wave_end_time >= wave_delay:
                current_wave += 1
                # Check for Victory Condition
                if current_wave > MAX_WAVES:
                    game_state = "won"
                    continue 

                # Prepare enemies for the new wave
                if current_wave in wave_definitions:
                    # Build and shuffle enemy list for the wave
                    current_wave_enemies_to_spawn = []
                    wave_def = wave_definitions[current_wave]
                    for e_type, count in wave_def.items(): current_wave_enemies_to_spawn.extend([e_type] * count)
                    random.shuffle(current_wave_enemies_to_spawn)

                    # Reset wave counters and state
                    enemies_in_wave = len(current_wave_enemies_to_spawn)
                    enemies_spawned_this_wave = 0
                    wave_ongoing = True
                    last_spawn_time = current_game_time
                    print(get_text("wave_starting", current_wave=current_wave, enemies_def=wave_def)) # Console message
                else: # Wave definition missing
                    print(get_text("wave_no_definition", current_wave=current_wave))
                    wave_ongoing = False; last_wave_end_time = current_game_time; continue # Skip wave

        # --- Spawn Enemies During Wave ---
        if wave_ongoing:
            # Spawn next enemy if interval passed and enemies remain in list
            if enemies_spawned_this_wave < enemies_in_wave and (current_game_time - last_spawn_time >= spawn_interval):
                enemy_type = current_wave_enemies_to_spawn[enemies_spawned_this_wave]
                enemy = create_enemy(enemy_type, map.path_pixels, current_wave) # Pass wave for scaling
                if enemy:
                    # Special scaling for final boss
                    if current_wave == 10 and enemy_type.lower() == "demon":
                        print("Applying special scaling for Wave 10 Demon Boss!") # Keep console message
                        scale=1.5; hp_mult=3.0; spd_mult=0.7; reward_mult=2.5
                        # Scale visuals
                        new_size = (int(enemy.image.get_width()*scale), int(enemy.image.get_height()*scale))
                        enemy.image = pygame.transform.smoothscale(enemy.image, new_size)
                        enemy.rect = enemy.image.get_rect(center=enemy.rect.center)
                        # Scale stats
                        enemy.max_health*=hp_mult; enemy.health=enemy.max_health
                        enemy.speed*=spd_mult; enemy.original_speed*=spd_mult
                        enemy.currency_reward*=reward_mult
                    # Add enemy and update counters
                    enemies.add(enemy); enemies_spawned_this_wave += 1; last_spawn_time = current_game_time
                else: print(f"Error creating enemy: {enemy_type}") # Keep error message

            # Check if wave complete (all spawned and all defeated)
            elif enemies_spawned_this_wave >= enemies_in_wave and not enemies:
                wave_ongoing = False; last_wave_end_time = current_game_time
                print(get_text("wave_completed", current_wave=current_wave)) # Console message

    # --- Game Object Updates ---
    if game_state == "playing" and not show_help_overlay: # Only update when playing and help is hidden
        enemies.update(player_stats) # Pass player_stats for health reduction
        towers.update(current_game_time) # Pass time for cooldowns
        projectiles.update() # Move projectiles, check collisions

        # Check Game Over Condition
        if player_stats["health"] <= 0:
            game_state = "lost"; print("--- GAME OVER ---") # Keep console message
    #endregion Game Logic (Wave Spawning, Object Updates, Win/Loss Check)

    #region Drawing (Handles all game states)
    screen.fill(BLACK) # Clear screen each frame

    # --- Prepare font and button rect dictionaries to pass ---
    # (Fonts are already prepared globally)
    # (Button rects are managed globally in button_rects dict)
    screen_fonts = {
        'large': fonts['large'], 'medium': fonts['medium'],
        'small': fonts['small'], 'tiny': fonts['tiny'],
        'tower_stats': fonts['tower_stats']
    }

    # --- Draw based on Game State ---
    if game_state == "main_menu":
        screens.draw_main_menu(screen, screen_fonts, button_rects)
    elif game_state == "tutorial":
        screens.draw_tutorial_window(screen, screen_fonts, button_rects, game_state)
    elif game_state == "paused":
        # Draw game world underneath pause menu
        draw_map(screen); decorations.draw(screen); towers.draw(screen)
        for enemy in enemies: enemy.draw(screen) # Draw paused sprites
        projectiles.draw(screen); game_ui.draw_ui(screen, fonts, player_stats, game_state, current_wave, wave_ongoing, last_wave_end_time, wave_delay, button_rects) # Use imported function
        # Draw pause menu overlay using the imported function
        screens.draw_pause_menu(screen, screen_fonts, button_rects)
    elif game_state == "settings": # Draw settings screen
        # Pass necessary objects AND current volume values from config for drawing (Removed event)
        screens.draw_settings_screen(screen, screen_fonts, button_rects, config, button_sound, building_sound, config.music_volume, config.sfx_volume)
    elif game_state == "playing":
        # Draw game world elements
        draw_map(screen); decorations.draw(screen); towers.draw(screen)
        for enemy in enemies: enemy.draw(screen) # Includes health bars
        projectiles.draw(screen)
        # Draw UI elements on top using imported functions
        game_ui.draw_ui(screen, fonts, player_stats, game_state, current_wave, wave_ongoing, last_wave_end_time, wave_delay, button_rects)
        game_ui.draw_tower_menu(screen, fonts, selected_tower_type)
        # Draw tower upgrade/sell UI using imported function
        tower_ui.draw_tower_upgrade_ui(screen, selected_tower_for_ui, screen_fonts, button_rects)
        # Draw help overlay if active (uses the tutorial window function)
        if show_help_overlay:
            screens.draw_tutorial_window(screen, screen_fonts, button_rects, game_state)
    elif game_state == "lost":
        screens.draw_game_over_screen(screen, screen_fonts, button_rects, current_wave)
    elif game_state == "won":
        screens.draw_victory_screen(screen, screen_fonts, button_rects)

    pygame.display.flip() # Update the full display surface
    #endregion Drawing

    #region Frame Rate Control
    clock.tick(FPS) # Limit FPS
    #endregion Frame Rate Control

#endregion Main Game Loop

# --- Quit Pygame ---
pygame.quit() # Cleanly exit Pygame when loop ends
