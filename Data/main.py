import pygame
import sys
import os
import math
import random
import config 

pygame.init()
pygame.display.init()

#region Inicializace Pygame Mixer a načítání zvuků
try:
    pygame.mixer.init()
    # Načtení zvukových efektů z config
    try:
        button_sound_path = config.get_resource_path("Audio/Button.mp3")
        building_sound_path = config.get_resource_path("Audio/Building.wav")
        music_path_1 = config.get_resource_path("Audio/Main_1.mp3")
        music_path_2 = config.get_resource_path("Audio/Main_2.mp3")

        button_sound = pygame.mixer.Sound(button_sound_path)
        building_sound = pygame.mixer.Sound(building_sound_path)

        pygame.mixer.music.load(music_path_1) # Cesta je již absolutní díky
        initial_music_vol = 0 if config.music_muted else config.music_volume
        pygame.mixer.music.set_volume(initial_music_vol)
        initial_sfx_vol = 0 if config.sfx_muted else config.sfx_volume
        if button_sound: button_sound.set_volume(initial_sfx_vol)
        if building_sound: building_sound.set_volume(initial_sfx_vol)
        pygame.mixer.music.play(-1) 

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


#region Importy
from config import *
from enemies import create_enemy
import map
from towers import create_tower
from projectiles import Projectile
from decorations import Decoration
import languages
from languages import get_text, set_language
import screens 
import tower_ui 
import game_ui
#endregion

#region Nastavení zobrazení Pygame
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tower Defense")

# --- Načtení assetů PO inicializaci zobrazení ---
config.load_config_images() # Načtení obrázků z config (platforma, ikony menu věží)
map.load_map_assets()    # Načtení obrázků z map a generování pixelů cesty


#endregion Nastavení zobrazení Pygame

#region Nastavení písem Pygame
# Vytvoření slovníku pro různá písma
fonts = {}
try:
    fonts['default'] = pygame.font.SysFont(None, 30) # Výchozí písmo UI
    fonts['large'] = pygame.font.SysFont(None, 72)   # Pro nadpisy
    fonts['medium'] = pygame.font.SysFont(None, 48)  # Pro tlačítka/střední text
    fonts['small'] = pygame.font.SysFont(None, 24)   # Pro menší text (menu věže, text tutoriálu)
    fonts['tiny'] = pygame.font.SysFont(None, 20)    # Pro text panelu vylepšení/prodeje
    fonts['tower_stats'] = pygame.font.SysFont(None, 18) # Pro statistiky věží v tutoriálu
    ui_font = fonts['default']
except Exception as e:
    print(f"Could not load system font: {e}. Using default pygame font.")
    # řešení, pokud SysFont selže
    fonts['default'] = pygame.font.Font(None, 30)
    fonts['large'] = pygame.font.Font(None, 72)
    fonts['medium'] = pygame.font.Font(None, 48)
    fonts['small'] = pygame.font.Font(None, 24)
    fonts['tiny'] = pygame.font.Font(None, 20)
    fonts['tower_stats'] = pygame.font.Font(None, 18)
    ui_font = fonts['default']
#endregion Nastavení písem Pygame

#region Správa obdélníků tlačítek
# Centrální slovník pro uložení všech obdélníků tlačítek, spravovaný kreslícími funkcemi
button_rects = {
    'start': None, 'exit': None, 'tutorial_ok': None, 'lang_en': None, 'lang_cz': None,
    'game_over_restart': None, 'game_over_exit': None, 'victory_restart': None,
    'victory_exit': None, 'help': None, 'upgrade': None, 'sell': None,
    # Přidání klíčů pro tlačítka obrazovky nastavení (funkce draw_settings_screen)
    'settings_back': None, 'volume_bar_music': None, 'volume_bar_sfx': None,
    'mute_music': None, 'mute_sfx': None
}
#endregion Správa obdélníků tlačítek

#region Načítání assetů

# --- Dlaždice ---
grass_img_loaded = config.load_image(GRASS_PATH, alpha=False)

if grass_img_loaded:
    grass_tile = pygame.transform.scale(grass_img_loaded, (TILE_SIZE, TILE_SIZE))
else:
    print("ERROR: Failed to load grass tile. Using fallback color.")
    grass_tile = pygame.Surface((TILE_SIZE, TILE_SIZE))
    grass_tile.fill(GREEN)

# Načtení dlaždice platformy
platform_img_loaded = config.load_image("Environment/Building_platform/platform.png", alpha=True)
if platform_img_loaded:
    platform_tile = pygame.transform.scale(platform_img_loaded, (TILE_SIZE, TILE_SIZE))
else:
    print("ERROR: Failed to load platform tile. Building might not be visually indicated.")
    platform_tile = None
#endregion Načítání assetů

#region Funkce pro kreslení mapy
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
                path_image_to_draw = map.get_path_tile_image(row_index, col_index)
                if path_image_to_draw:
                    surface.blit(path_image_to_draw, (x, y))
                else:
                    pygame.draw.rect(surface, BROWN, (x, y, TILE_SIZE, TILE_SIZE))
#endregion Funkce pro kreslení mapy

#region Načítání a umístění dekorací
# --- Načtení obrázků dekorací ---
decoration_images = {}
decoration_folder = DECORATION_FOLDER # Toto je 'Environment/Decoration'
try:
    # K nalezení absolutní cesty ke složce dekorací, ať už běží normálně nebo jako zmrazená aplikace.
    abs_decoration_folder_path = config.get_resource_path(decoration_folder)
    if os.path.isdir(abs_decoration_folder_path):
        for filename in os.listdir(abs_decoration_folder_path):
            if filename.endswith('.png'):
                name = os.path.splitext(filename)[0]
                # Relativní cesta pro load_image je stále správná, protože load_image
                # zpracovává prefix 'Data' při zmrazení.
                relative_path = os.path.join(decoration_folder, filename)
                loaded_deco_img = config.load_image(relative_path, alpha=True)
                if loaded_deco_img:
                    decoration_images[name] = loaded_deco_img
                else:
                    pass
    else:
        pass
except Exception as e:
   pass
# --- Nastavení hodin ---
clock = pygame.time.Clock()
#endregion Načítání a umístění dekorací

#region Inicializace herních objektů
# --- Skupiny spritů ---
enemies = pygame.sprite.Group()
towers = pygame.sprite.Group()
projectiles = pygame.sprite.Group()
decorations = pygame.sprite.Group()

# --- Umístění počátečních dekorací ---
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
#endregion Inicializace herních objektů

#region Proměnné stavu hry
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

game_state = "main_menu"
previous_game_state = "main_menu"

wave_definitions = { # Definice nepřátel a jejich počtů pro každou vlnu
    1: {"normal_slime": 10},
    2: {"normal_slime": 12, "bat": 4},
    3: {"normal_slime": 7, "big_slime": 6, "bat": 6},
    4: {"big_slime": 10, "ghost": 7, "bat": 7},
    5: {"king_slime": 1, "normal_slime": 10}, # Vlna 5 s bossem
    6: {"goblin": 25, "skeleton": 5},
    7: {"zombie": 12, "ghost": 6, "bat": 10},
    8: {"skeleton": 10, "big_slime": 4, "demon": 6},
    9: {"demon": 5, "king_slime": 1, "ghost": 18},
    10: {"demon": 1, "skeleton": 10} # Finální vlna
    # 11:{}
}
current_wave_enemies_to_spawn = []
#endregion Proměnné stavu hry

#region Správa obdélníků tlačítek
# Centrální slovník pro uložení všech obdélníků tlačítek (přesunuté klíče nastavení sem)
button_rects = {
    'start': None, 'exit': None, 'tutorial_ok': None, 'lang_en': None, 'lang_cz': None,
    'game_over_restart': None, 'game_over_exit': None, 'victory_restart': None,
    'victory_exit': None, 'help': None, 'upgrade': None, 'sell': None,
    'settings_back': None, 'volume_bar_music': None, 'volume_bar_sfx': None,
    'mute_music': None, 'mute_sfx': None
}

# Příznak pro zobrazení nápovědy zůstává zatím globální
show_help_overlay = False
#endregion Správa obdélníků tlačítek

#region Funkce pro resetování stavu hry
def reset_game_state():
    """Resetuje herní proměnné do počátečního stavu pro spuštění/restartování."""
    global player_stats, current_wave, wave_ongoing, enemies_spawned_this_wave
    global last_wave_end_time, game_state, selected_tower_type, selected_tower_for_ui
    global enemies, towers, projectiles, previous_game_state # Přidáno previous_game_state

    # Statistiky hráče
    player_stats = {
        "health": 20,
        "currency": 200
    }

    # Proměnné vlny
    current_wave = 0
    wave_ongoing = False
    enemies_spawned_this_wave = 0
    last_wave_end_time = -wave_delay # Umožní první vlně začít okamžitě po tutoriálu/resetu

    # Výběry
    selected_tower_type = None
    selected_tower_for_ui = None

    # Skupiny spritů (vyprázdnění všech dynamických objektů)
    enemies.empty()
    towers.empty()
    projectiles.empty()

    # Znovu načtení assetů mapy (což zahrnuje resetování mřížky mapy)
    map.load_map_assets()

    # Stav hry je nastaven volajícím po resetu
#endregion Funkce pro resetování stavu hry

#region Hlava hry
running = True
current_game_time = 0
last_wave_end_time = -wave_delay

dragging_music_bar = False
dragging_sfx_bar = False

while running:
    current_game_time = pygame.time.get_ticks()

    #region Zpracování událostí
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # --- Klávesové vstupy ---
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE: 
                if game_state == "playing":
                    game_state = "paused"
                elif game_state == "paused":
                    game_state = "playing"
     # --- Myš ---
       # Zpracování MOUSEBUTTONDOWN
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_pos = event.pos

                # == Zpracování kliknutí ve stavu menu (Hlavní menu, Pozastavení, Tutoriál) ==
                if game_state in ["main_menu", "paused", "tutorial"]:
                    # --- Kliknutí na tlačítka jazyka (pouze v hlavním menu) ---
                    if game_state == "main_menu":
                        if button_rects.get('lang_en') and button_rects['lang_en'].collidepoint(mouse_pos):
                            set_language('EN')
                            if button_sound: button_sound.play()
                            continue 
                        elif button_rects.get('lang_cz') and button_rects['lang_cz'].collidepoint(mouse_pos):
                            set_language('CZ')
                            if button_sound: button_sound.play()
                            continue 

                    # Zkontrolovat tlačítko nastavení (Hlavní menu / Menu pozastavení)
                    if (game_state == "main_menu" or game_state == "paused") and button_rects.get('settings') and button_rects['settings'].collidepoint(mouse_pos):
                        if button_sound: button_sound.play()
                        previous_game_state = game_state 
                        game_state = "settings"
                        continue 

                    # kontrola tlačítka Start/Znovu (Hlavní menu / Menu pozastavení)
                    if (game_state == "main_menu" or game_state == "paused") and button_rects.get('start') and button_rects['start'].collidepoint(mouse_pos):
                        if button_sound: button_sound.play() 
                        if game_state == "main_menu":
                            game_state = "tutorial"
                            button_rects['start'] = None 
                            button_rects['exit'] = None
                        elif game_state == "paused":
                            reset_game_state()
                            game_state = "playing"
                            last_wave_end_time = pygame.time.get_ticks() - wave_delay
                            button_rects['start'] = None 
                            button_rects['exit'] = None
                        continue 

                    # kontrola tlačítka Konec (Hlavní menu / Menu pozastavení) 
                    elif (game_state == "main_menu" or game_state == "paused") and button_rects.get('exit') and button_rects['exit'].collidepoint(mouse_pos):
                        if button_sound: button_sound.play()
                        pygame.time.wait(100) 
                        running = False
                        continue 

                    # kontrola tlačítka OK tutoriálu
                    elif game_state == "tutorial" and button_rects.get('tutorial_ok') and button_rects['tutorial_ok'].collidepoint(mouse_pos):
                            if button_sound: button_sound.play()
                            reset_game_state()
                            game_state = "playing"
                            last_wave_end_time = pygame.time.get_ticks()
                            button_rects['tutorial_ok'] = None # 
                            continue 

              # == Zpracování kliknutí ve stavu hry ==
                elif game_state == "playing":
                    # --- Přepínání nápovědy ---
                    if show_help_overlay:
                        show_help_overlay = False
                        continue # Jakékoli kliknutí zavře nápovědu
                    if button_rects.get('help') and button_rects['help'].collidepoint(mouse_pos):
                        show_help_overlay = True
                        continue 

                    # --- Kliknutí během hry (Menu věží, dlaždice mapy) ---
                    try: m_height = config.MENU_HEIGHT
                    except AttributeError: m_height = 80
                    menu_rect = pygame.Rect(0, SCREEN_HEIGHT - m_height, SCREEN_WIDTH, m_height)

                    # Kliknutí na menu pro stavbu věží
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
                                    selected_tower_for_ui = None 
                                    break
                                current_x += item_base_width + spacing
                    # Kliknutí mimo menu
                    else:
                        clicked_on_ui_button = False
                        if selected_tower_for_ui:
                            if button_rects.get('upgrade') and button_rects['upgrade'].collidepoint(mouse_pos):
                                selected_tower_for_ui.upgrade(player_stats)
                                clicked_on_ui_button = True
                            elif button_rects.get('sell') and button_rects['sell'].collidepoint(mouse_pos):
                                sell_price = selected_tower_for_ui.get_sell_price()
                                
                                player_stats['currency'] += sell_price
                                if hasattr(selected_tower_for_ui, 'grid_x') and hasattr(selected_tower_for_ui, 'grid_y'):
                                    gx, gy = selected_tower_for_ui.grid_x, selected_tower_for_ui.grid_y
                                    if 0 <= gy < ROWS and 0 <= gx < COLS and map.game_map[gy][gx] == 3: map.game_map[gy][gx] = 2
                                selected_tower_for_ui.kill(); selected_tower_for_ui = None
                                button_rects['upgrade'] = None; button_rects['sell'] = None
                                clicked_on_ui_button = True
                                if button_sound: button_sound.play()
                        if not clicked_on_ui_button:
                            tile_col = mouse_pos[0] // TILE_SIZE
                            tile_row = mouse_pos[1] // TILE_SIZE
                            clicked_on_existing_tower = False
                            # Zkontrolujte existující věže
                            for tower in towers:
                                if tower.rect.collidepoint(mouse_pos):
                                    selected_tower_for_ui = tower
                                    selected_tower_type = None
                                    clicked_on_existing_tower = True
                                    break
                            # umístit novou věž nebo zrušit výběr UI
                            if not clicked_on_existing_tower:
                                if selected_tower_type:
                                    grid_x, grid_y = tile_col, tile_row
                                    if 0 <= grid_y < ROWS and 0 <= grid_x < COLS and map.game_map[grid_y][grid_x] == 2:
                                        can_build = True
                                        for t in towers:
                                            if hasattr(t, 'grid_x') and hasattr(t, 'grid_y') and t.grid_x == grid_x and t.grid_y == grid_y:
                                                can_build = False;
                                                break
                                        try: required_cost = config.TOWER_DATA[selected_tower_type]['levels'][0]['cost']
                                        except (KeyError, IndexError): print(get_text("error_cost_missing", tower_type=selected_tower_type)); required_cost = float('inf') 

                                        if can_build and player_stats["currency"] >= required_cost:
                                            player_stats["currency"] -= required_cost
                                            tower_pos = (grid_x * TILE_SIZE + TILE_SIZE // 2, grid_y * TILE_SIZE + TILE_SIZE // 2)
                                            new_tower = create_tower(selected_tower_type, tower_pos, projectiles, enemies, building_sound)
                                            if new_tower:
                                                towers.add(new_tower); new_tower.grid_x = grid_x; new_tower.grid_y = grid_y
                                                map.game_map[grid_y][grid_x] = 3
                                                
                                                if building_sound: building_sound.play()
                                            else: player_stats["currency"] += required_cost; print(get_text("error_create_tower", tower_type=selected_tower_type)) 
                                        elif not can_build: pass
                                        elif player_stats["currency"] < required_cost: print(get_text("cannot_build_no_gold", tower_type=selected_tower_type, cost=required_cost, have=player_stats['currency'])) # Keep message
                                    else: print(get_text("cannot_build_invalid_tile", grid_x=grid_x, grid_y=grid_y)) 
                                else: selected_tower_for_ui = None

                # == Zpracování kliknutí na obrazovce nastavení (přesunuto z screens.py) ==
                elif game_state == "settings":
                    # Tlačítko Zpět
                    if button_rects.get('settings_back') and button_rects['settings_back'].collidepoint(mouse_pos):
                        if button_sound: button_sound.play()
                        game_state = previous_game_state 
                        button_rects['settings_back'] = None
                        button_rects['volume_bar_music'] = None
                        button_rects['volume_bar_sfx'] = None
                        button_rects['mute_music'] = None
                        button_rects['mute_sfx'] = None
                    # Tlačítko pro ztlumení hudby
                    elif button_rects.get('mute_music') and button_rects['mute_music'].collidepoint(mouse_pos):
                        config.music_muted = not config.music_muted
                        if config.music_muted:
                            pygame.mixer.music.set_volume(0)
                        else:
                            pygame.mixer.music.set_volume(config.music_volume)
                        if button_sound: button_sound.play()
                    # Tlačítko pro ztlumení SFX
                    elif button_rects.get('mute_sfx') and button_rects['mute_sfx'].collidepoint(mouse_pos):
                        config.sfx_muted = not config.sfx_muted
                        current_sfx_vol = 0 if config.sfx_muted else config.sfx_volume
                        if button_sound: button_sound.set_volume(current_sfx_vol)
                        if building_sound: building_sound.set_volume(current_sfx_vol)
                        if button_sound: button_sound.play()
                    # Kliknutí na posuvník hlasitosti hudby (začátek tažení)
                    elif button_rects.get('volume_bar_music') and button_rects['volume_bar_music'].collidepoint(mouse_pos):
                        dragging_music_bar = True
                        # Okamžitě aktualizujte hlasitost při kliknutí
                        volume_bar_rect = button_rects['volume_bar_music']
                        click_x_relative = mouse_pos[0] - volume_bar_rect.left
                        new_music_volume = max(0.0, min(1.0, click_x_relative / volume_bar_rect.width))
                        if config.music_muted:
                            config.music_muted = False
                        config.music_volume = new_music_volume
                        pygame.mixer.music.set_volume(config.music_volume)
                    # Kliknutí na posuvník SFX (začátek tažení)
                    elif button_rects.get('volume_bar_sfx') and button_rects['volume_bar_sfx'].collidepoint(mouse_pos):
                        dragging_sfx_bar = True
                         # Okamžitě aktualizujte hlasitost při kliknutí
                        volume_bar_rect = button_rects['volume_bar_sfx']
                        click_x_relative = mouse_pos[0] - volume_bar_rect.left
                        new_sfx_volume = max(0.0, min(1.0, click_x_relative / volume_bar_rect.width))
                        if config.sfx_muted:
                            config.sfx_muted = False
                        config.sfx_volume = new_sfx_volume
                        current_sfx_vol = 0 if config.sfx_muted else config.sfx_volume # Kontrola
                        if button_sound: button_sound.set_volume(current_sfx_vol)
                        if building_sound: building_sound.set_volume(current_sfx_vol)

                # == Zpracování kliknutí ve stavu Game Over ==
                elif game_state == "lost":
                    if button_rects.get('game_over_restart') and button_rects['game_over_restart'].collidepoint(mouse_pos):
                        if button_sound: button_sound.play()
                        reset_game_state(); game_state = "playing"; last_wave_end_time = pygame.time.get_ticks()
                        button_rects['game_over_restart']=None; button_rects['game_over_exit']=None
                    elif button_rects.get('game_over_exit') and button_rects['game_over_exit'].collidepoint(mouse_pos):
                        if button_sound: button_sound.play(); pygame.time.wait(100); running = False

                # == Zpracování kliknutí ve stavu vítězství ==
                elif game_state == "won":
                    if button_rects.get('victory_restart') and button_rects['victory_restart'].collidepoint(mouse_pos):
                        if button_sound: button_sound.play()
                        reset_game_state(); game_state = "playing"; last_wave_end_time = pygame.time.get_ticks()
                        button_rects['victory_restart']=None; button_rects['victory_exit']=None
                    elif button_rects.get('victory_exit') and button_rects['victory_exit'].collidepoint(mouse_pos):
                        if button_sound: button_sound.play(); pygame.time.wait(100); running = False
        # Zpracování MOUSEMOTION (tažení posuvníku hlasitosti)
        elif event.type == pygame.MOUSEMOTION:
            if game_state == "settings":
                mouse_pos = event.pos
                # Tažení posuvníku hudby
                if dragging_music_bar:
                    volume_bar_rect = button_rects.get('volume_bar_music')
                    if volume_bar_rect: 
                        click_x_relative = mouse_pos[0] - volume_bar_rect.left
                        new_music_volume = max(0.0, min(1.0, click_x_relative / volume_bar_rect.width))
                        if not config.music_muted: 
                            config.music_volume = new_music_volume
                            pygame.mixer.music.set_volume(config.music_volume)
                # Tažení posuvníku SFX
                elif dragging_sfx_bar:
                    volume_bar_rect = button_rects.get('volume_bar_sfx')
                    if volume_bar_rect:
                        click_x_relative = mouse_pos[0] - volume_bar_rect.left
                        new_sfx_volume = max(0.0, min(1.0, click_x_relative / volume_bar_rect.width))
                        if not config.sfx_muted: 
                            config.sfx_volume = new_sfx_volume
                            current_sfx_vol = config.sfx_volume 
                            if button_sound: button_sound.set_volume(current_sfx_vol)
                            if building_sound: building_sound.set_volume(current_sfx_vol)
        # Zpracování MOUSEBUTTONUP (zastavení tažení)
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                dragging_music_bar = False
                dragging_sfx_bar = False

    #endregion Zpracování událostí

    #region Herní logika (spawning vln, aktualizace)
    # --- Logika spawning vln ---
    if game_state == "playing":
        # --- Začátek další vlny ---
        if not wave_ongoing:
            if current_game_time - last_wave_end_time >= wave_delay:
                current_wave += 1
                # Zkontrolujte podmínku vítězství
                if current_wave > MAX_WAVES:
                    game_state = "won"
                    continue 

                # Připravte nepřátele pro novou vlnu
                if current_wave in wave_definitions:
                    # Vytvořte a zamíchejte seznam nepřátel pro vlnu
                    current_wave_enemies_to_spawn = []
                    wave_def = wave_definitions[current_wave]
                    for e_type, count in wave_def.items(): current_wave_enemies_to_spawn.extend([e_type] * count)
                    random.shuffle(current_wave_enemies_to_spawn)

                    # Resetujte počítadla a stav vlny
                    enemies_in_wave = len(current_wave_enemies_to_spawn)
                    enemies_spawned_this_wave = 0
                    wave_ongoing = True
                    last_spawn_time = current_game_time
                else: # Chybí definice vlny
                    wave_ongoing = False; last_wave_end_time = current_game_time; continue

        # --- Spawnování nepřátel během vlny ---
        if wave_ongoing:
            if enemies_spawned_this_wave < enemies_in_wave and (current_game_time - last_spawn_time >= spawn_interval):
                enemy_type = current_wave_enemies_to_spawn[enemies_spawned_this_wave]
                enemy = create_enemy(enemy_type, map.path_pixels, current_wave) 
                if enemy:
                    # Speciální škálování pro finálního bosse
                    if current_wave == 10 and enemy_type.lower() == "demon":
                        scale=1.5; hp_mult=3.0; spd_mult=0.7; reward_mult=2.5
                        # Škálování vizuálů
                        new_size = (int(enemy.image.get_width()*scale), int(enemy.image.get_height()*scale))
                        enemy.image = pygame.transform.smoothscale(enemy.image, new_size)
                        enemy.rect = enemy.image.get_rect(center=enemy.rect.center)
                        # Škálování statistik
                        enemy.max_health*=hp_mult; enemy.health=enemy.max_health
                        enemy.speed*=spd_mult; enemy.original_speed*=spd_mult
                        enemy.currency_reward*=reward_mult
                    # Přidejte nepřítele a aktualizujte počítadla
                    enemies.add(enemy); enemies_spawned_this_wave += 1; last_spawn_time = current_game_time
                else: print(f"Chyba při vytváření nepřítele: {enemy_type}") # Zachovat chybovou zprávu

            # Zkontrolujte, zda je vlna dokončena (všichni spawnováni a poraženi)
            elif enemies_spawned_this_wave >= enemies_in_wave and not enemies:
                wave_ongoing = False; last_wave_end_time = current_game_time

    # --- Aktualizace herních objektů ---
    if game_state == "playing" and not show_help_overlay: 
        enemies.update(player_stats) 
        towers.update(current_game_time) 
        projectiles.update()

        # Zkontrolujte podmínku Game Over
        if player_stats["health"] <= 0:
            game_state = "lost"; 

    #endregion Herní logika (spawning vln, aktualizace objektů, kontrola výhry/prohry)

    #region Kreslení (zpracovává všechny herní stavy)
    screen.fill(BLACK) # Vyčistěte obrazovku každý snímek

    # --- Připravte písmo a slovníky obdélníků tlačítek k předání ---
    screen_fonts = {
        'large': fonts['large'], 'medium': fonts['medium'],
        'small': fonts['small'], 'tiny': fonts['tiny'],
        'tower_stats': fonts['tower_stats']
    }

    # --- Kreslete na základě herního stavu ---
    if game_state == "main_menu":
        screens.draw_main_menu(screen, screen_fonts, button_rects)
    elif game_state == "tutorial":
        screens.draw_tutorial_window(screen, screen_fonts, button_rects, game_state)
    elif game_state == "paused":
        # herní svět pod pozastavenou nabídkou
        draw_map(screen); decorations.draw(screen); towers.draw(screen)
        for enemy in enemies: enemy.draw(screen) # Kreslete pozastavené sprity
        projectiles.draw(screen); game_ui.draw_ui(screen, fonts, player_stats, game_state, current_wave, wave_ongoing, last_wave_end_time, wave_delay, button_rects) # Použijte importovanou funkci
        # pozastavená nabídka 
        screens.draw_pause_menu(screen, screen_fonts, button_rects)
    elif game_state == "settings": # Kreslete obrazovku nastavení
        screens.draw_settings_screen(screen, screen_fonts, button_rects, config, button_sound, building_sound, config.music_volume, config.sfx_volume)
    elif game_state == "playing":
        # prvky světa
        draw_map(screen); decorations.draw(screen); towers.draw(screen)
        for enemy in enemies: enemy.draw(screen) # Zahrnuje zdraví
        projectiles.draw(screen)
        # Kreslete UI prvky 
        game_ui.draw_ui(screen, fonts, player_stats, game_state, current_wave, wave_ongoing, last_wave_end_time, wave_delay, button_rects)
        game_ui.draw_tower_menu(screen, fonts, selected_tower_type)
        # Kreslete UI pro vylepšení/prodej věží pomocí importované funkce
        tower_ui.draw_tower_upgrade_ui(screen, selected_tower_for_ui, screen_fonts, button_rects)
        # Kreslete překryvnou nápovědu, pokud je aktivní (používá funkci okna s tutoriálem)
        if show_help_overlay:
            screens.draw_tutorial_window(screen, screen_fonts, button_rects, game_state)
    elif game_state == "lost":
        screens.draw_game_over_screen(screen, screen_fonts, button_rects, current_wave)
    elif game_state == "won":
        screens.draw_victory_screen(screen, screen_fonts, button_rects)

    pygame.display.flip() 
    #endregion Kreslení

    #region FPS
    clock.tick(FPS)
    #endregion FPS

#endregion Hlavní herní smyčka

# --- Ukončení Pygame ---
pygame.quit()