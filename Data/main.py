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
        button_sound = None
        building_sound = None
    except FileNotFoundError as e:
        button_sound = None
        building_sound = None
    except Exception as e:
        button_sound = None
        building_sound = None

except pygame.error as e:
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

#region Inicializace herních objektů (přesunuto to sem, aby byly definovány před použitím)
# --- Skupiny spritů ---
enemies = pygame.sprite.Group()
towers = pygame.sprite.Group()
projectiles = pygame.sprite.Group()
decorations = pygame.sprite.Group()
#endregion Inicializace herních objektů

#region Funkce pro načítání a umístění dekorací

# Pomocná funkce pro kontrolu sousedství s platformou
def is_adjacent_to_platform(r, c, game_map_grid):
    rows = len(game_map_grid)
    cols = len(game_map_grid[0]) if rows > 0 else 0
    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            if dr == 0 and dc == 0:
                continue # Skip self
            nr, nc = r + dr, c + dc
            # Zkontrovat hranice mapy
            if 0 <= nr < rows and 0 <= nc < cols:
                # Zkontrovat, zda sousední dlaždice je platforma (typ 2 nebo 3)
                if game_map_grid[nr][nc] in [2, 3]:
                    return True
    return False

def load_and_place_decorations():
    """Načte obrázky dekorací z aktuální složky mapy a náhodně je umístí, vyhýbá se sousedství platforem."""
    global decorations # Potřebujeme upravit globální skupinu spritů

    # Vyčistit stávající dekorace před načtením nových
    decorations.empty()

    # --- Načtení obrázků dekorací ---
    decoration_images = {}
    # Použijte aktuální cestu ke složce dekorací z configu (aktualizováno pomocí switch_map)
    decoration_folder = config.DECORATION_FOLDER
    if not decoration_folder: # Přidána kontrola pro případ, že cesta ještě není nastavena
        return
    try:
        abs_decoration_folder_path = config.get_resource_path(decoration_folder)
        if os.path.isdir(abs_decoration_folder_path):
            for filename in os.listdir(abs_decoration_folder_path):
                if filename.endswith('.png'):
                    name = os.path.splitext(filename)[0]
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

    # --- Umístění dekorací ---
    if decoration_images:
        decoration_names = list(decoration_images.keys())
        placed_decorations = 0
        max_decorations = 50 # Můžete upravit podle potřeby
        attempts = 0
        max_attempts = 300 # Zvýšit pokusy, protože přidáváme omezení

        while placed_decorations < max_decorations and attempts < max_attempts:
            attempts += 1
            # Zajistit, že ROWS a COLS jsou aktuální (i když by se neměly měnit)
            try:
                current_rows = len(map.game_map)
                current_cols = len(map.game_map[0]) if current_rows > 0 else 0
                if current_rows == 0 or current_cols == 0: continue # Přeskočit, pokud mapa není platná
            except IndexError:
                continue # Přeskočit, pokud je mapa nekonzistentní

            rand_row = random.randint(0, current_rows - 1)
            rand_col = random.randint(0, current_cols - 1)

            # Umístit pouze na dlaždice trávy (typ 0)
            if map.game_map[rand_row][rand_col] == 0:

                # NOVÁ KONTROLA: Zkontrovat sousedství s platformami
                if is_adjacent_to_platform(rand_row, rand_col, map.game_map):
                    continue # Přeskočit tuto pozici, je příliš blízko platformy

                # Pokračovat pouze pokud není blízko platformy
                tile_center_x = rand_col * TILE_SIZE + TILE_SIZE // 2
                tile_center_y = rand_row * TILE_SIZE + TILE_SIZE // 2
                potential_rect = pygame.Rect(rand_col * TILE_SIZE, rand_row * TILE_SIZE, TILE_SIZE, TILE_SIZE)

                # Zkontrovat kolize s již umístěnými dekoracemi
                occupied = False
                for deco in decorations:
                    if deco.rect.colliderect(potential_rect):
                        occupied = True
                        break

                if not occupied:
                    deco_name = random.choice(decoration_names)
                    deco_image = decoration_images[deco_name]
                    # Zajistit, že obrázek není příliš velký pro dlaždici (volitelné)
                    # if deco_image.get_width() > TILE_SIZE or deco_image.get_height() > TILE_SIZE:
                    #     deco_image = pygame.transform.scale(deco_image, (TILE_SIZE, TILE_SIZE))
                    new_deco = Decoration(deco_image, (tile_center_x, tile_center_y))
                    decorations.add(new_deco)
                    placed_decorations += 1
#endregion Funkce pro načítání a umístění dekorací

#region Nastavení zobrazení Pygame
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tower Defense")

# --- Načtení assetů PO inicializaci zobrazení ---
# config.load_config_images() # Odstraněno - nyní se volá uvnitř map.load_map_assets() po nastavení cest
# map.load_map_assets()    # Načtení obrázků z map a generování pixelů cesty (načte Map_1) - Moved to mission select
# load_and_place_decorations() # Načtení a umístění dekorací pro Map_1 - Moved to mission select


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
    pass
    # řešení, pokud SysFont selže
    fonts['default'] = pygame.font.Font(None, 30)
    fonts['large'] = pygame.font.Font(None, 72)
    fonts['medium'] = pygame.font.Font(None, 48)
    fonts['small'] = pygame.font.Font(None, 24)
    fonts['tiny'] = pygame.font.Font(None, 20)
    fonts['tower_stats'] = pygame.font.Font(None, 18)
    ui_font = fonts['default']
#endregion Nastavení písem Pygame

# --- Nastavení hodin ---
clock = pygame.time.Clock()

#region Funkce pro kreslení mapy
def draw_map(surface):
    # Načtení dlaždic trávy a platformy zde, aby se zajistilo, že používají aktuální cesty z configu
    grass_img_loaded = config.load_image(config.GRASS_PATH, alpha=False) if config.GRASS_PATH else None
    if grass_img_loaded:
        grass_tile = pygame.transform.scale(grass_img_loaded, (TILE_SIZE, TILE_SIZE))
    else:
        grass_tile = pygame.Surface((TILE_SIZE, TILE_SIZE))
        grass_tile.fill(GREEN)
    
    # Ensure platform_tile is loaded based on the current map
    platform_img_loaded = config.load_image(config.PLATFORM_PATH, alpha=True) if config.PLATFORM_PATH else None
    if platform_img_loaded:
        platform_tile = pygame.transform.scale(platform_img_loaded, (TILE_SIZE, TILE_SIZE))
    else:
        # Není potřeba chyba, pokud platforma chybí, jen ji nekreslete
        platform_tile = None


    for row_index, row in enumerate(map.game_map):
        for col_index, tile_type in enumerate(row):
            x = col_index * TILE_SIZE
            y = row_index * TILE_SIZE
            # Vždy kreslete trávu jako pozadí
            surface.blit(grass_tile, (x, y))

            if tile_type == 2: # Platforma pro stavbu
                if platform_tile:
                    surface.blit(platform_tile, (x, y))
            # Odstraněno kreslení platformy pro tile_type == 3
            elif tile_type == 1: # Cesta
                path_image_to_draw = map.get_path_tile_image(row_index, col_index)
                if path_image_to_draw:
                    surface.blit(path_image_to_draw, (x, y))
                else:
                    pygame.draw.rect(surface, BROWN, (x, y, TILE_SIZE, TILE_SIZE))
#endregion Funkce pro kreslení mapy


#region Proměnné stavu hry
player_stats = {
    "health": 20,
    "currency": 200
}
current_wave = 0
wave_ongoing = False # Zda se aktuálně spawnují nepřátelé pro tuto vlnu
wave_complete = True # Zda je aktuální vlna kompletně poražena (začíná jako True pro spuštění vlny 1)
last_spawn_time = 0
spawn_interval = 1000
enemies_in_wave = 0
enemies_spawned_this_wave = 0
wave_delay = 5000 # Prodleva mezi vlnami v ms
last_wave_end_time = -wave_delay # Čas, kdy skončila poslední vlna (pro časovač)

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
    10: {"demon": 1, "skeleton": 10}, # Finální vlna Mapy 1
    # Vlny pro Mapu 2 (placeholders)
    11: {"goblin": 10, "zombie": 30},
    12: {"skeleton": 15, "bat": 15, "big_slime": 5},
    13: {"ghost": 20, "demon": 8},
    14: {"zombie": 20, "skeleton": 10, "king_slime": 1},
    15: {"bat": 25, "demon": 10, "goblin": 15},
    16: {"big_slime": 15, "ghost": 15, "skeleton": 15},
    17: {"king_slime": 2, "normal_slime": 20, "demon": 5},
    18: {"zombie": 25, "bat": 20, "skeleton": 10},
    19: {"demon": 15, "ghost": 25, "big_slime": 10},
    20: {"demon": 3, "king_slime": 2, "skeleton": 20} # Finální vlna Mapy 2
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
    'mute_music': None, 'mute_sfx': None,
    'map1_continue': None, # Přidáno pro tlačítko po dokončení Mapy 1
    'mission1_select': None, # New
    'mission2_select': None, # New
    'mission_select_back': None # New
}

# Příznak pro zobrazení nápovědy zůstává zatím globální
show_help_overlay = False
#endregion Správa obdélníků tlačítek

#region Funkce pro resetování stavu hry
def reset_game_state():
    """Resetuje herní proměnné do počátečního stavu pro spuštění/restartování."""
    global player_stats, current_wave, wave_ongoing, wave_complete, enemies_spawned_this_wave
    global last_wave_end_time, game_state, selected_tower_type, selected_tower_for_ui
    global enemies, towers, projectiles, previous_game_state, selected_map_id # Added selected_map_id

    # Statistiky hráče
    # Statistiky hráče
    initial_currency = 200 # Default currency for Map 1
    if selected_map_id == "Map_2":
        initial_currency = 800 # Starting currency for Map 2
 
    player_stats = {
        "health": 20,
        "currency": initial_currency
    }

    # Proměnné vlny
    current_wave = 0 # Start from wave 0 for both missions
    wave_ongoing = False
    wave_complete = False # Začíná jako False, aby se čekalo na počáteční prodlevu
    enemies_spawned_this_wave = 0
    # Nastavte last_wave_end_time na aktuální čas minus wave_delay, aby se vytvořila počáteční prodleva před první vlnou
    # Nastavte last_wave_end_time tak, aby první vlna začala po 10 sekundách (10000 ms)
    # Odecitame wave_delay (5000 ms) od aktualniho casu, aby casovac zacal na 5 sekundach
    # a celkova prodleva do prvni vlny byla 10 sekund (5s pocatecni casovac + 5s wave_delay)
    last_wave_end_time = current_game_time - 5000

    # Výběry
    selected_tower_type = None
    selected_tower_for_ui = None

    # Skupiny spritů (vyprázdnění všech dynamických objektů)
    enemies.empty()
    towers.empty()
    projectiles.empty()

    # Znovu načtení assetů mapy (což zahrnuje resetování mřížky mapy)
    # Load map assets based on selected_map_id, default to Map_1 if none selected
    map_to_load = selected_map_id if selected_map_id else "Map_1"
    map.switch_map(map_to_load) # Use switch_map to load the correct map assets
    load_and_place_decorations() # Load decorations for the selected map
 
    # Load and play music based on the selected map
    if pygame.mixer.get_init(): # Check if mixer is initialized
        try:
            if selected_map_id == "Map_2":
                music_path = config.get_resource_path("Audio/Main_2.mp3")
            else: # Default to Map_1 music
                music_path = config.get_resource_path("Audio/Main_1.mp3")
 
            pygame.mixer.music.load(music_path)
            initial_music_vol = 0 if config.music_muted else config.music_volume
            pygame.mixer.music.set_volume(initial_music_vol)
            pygame.mixer.music.play(-1)
        except pygame.error as e:
            pass
        except FileNotFoundError as e:
            pass
        except Exception as e:
            pass
 
    # Stav hry je nastaven volajícím po resetu
#endregion Funkce pro resetování stavu hry

#region Hlava hry
running = True
current_game_time = 0
# last_wave_end_time se inicializuje v reset_game_state

dragging_music_bar = False
dragging_sfx_bar = False

# Globální proměnné pro výběr věží a mapy
selected_tower_type = None
selected_tower_for_ui = None
selected_map_id = None # New global variable to store selected map

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

                # --- Main Menu State ---
                if game_state == "main_menu":
                    if button_rects.get('lang_en') and button_rects['lang_en'].collidepoint(mouse_pos):
                        set_language('EN')
                        if button_sound: button_sound.play()
                        continue
                    elif button_rects.get('lang_cz') and button_rects['lang_cz'].collidepoint(mouse_pos):
                        set_language('CZ')
                        if button_sound: button_sound.play()
                        continue
                    elif button_rects.get('settings') and button_rects['settings'].collidepoint(mouse_pos):
                        if button_sound: button_sound.play()
                        previous_game_state = game_state
                        game_state = "settings"
                        continue
                    elif button_rects.get('start') and button_rects['start'].collidepoint(mouse_pos):
                        if button_sound: button_sound.play()
                        game_state = "mission_select"
                        button_rects['start'] = None
                        button_rects['exit'] = None
                        button_rects['settings'] = None
                        temp_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                        screens.draw_mission_select_screen(temp_surface, fonts, button_rects)
                        continue
                    elif button_rects.get('exit') and button_rects['exit'].collidepoint(mouse_pos):
                        if button_sound: button_sound.play()
                        pygame.time.wait(100)
                        running = False
                        continue

                # --- Paused State ---
                elif game_state == "paused":
                    if button_rects.get('settings') and button_rects['settings'].collidepoint(mouse_pos):
                        if button_sound: button_sound.play()
                        previous_game_state = game_state
                        game_state = "settings"
                        continue
                    elif button_rects.get('exit') and button_rects['exit'].collidepoint(mouse_pos):
                        if button_sound: button_sound.play()
                        reset_game_state() # Reset game state before returning to main menu
                        game_state = "main_menu"
                        continue
                    elif button_rects.get('continue') and button_rects['continue'].collidepoint(mouse_pos):
                        if button_sound: button_sound.play()
                        game_state = "playing"
                        continue
                    # --- Restart Button (uses 'start' key from draw_pause_menu) ---
                    elif button_rects.get('start') and button_rects['start'].collidepoint(mouse_pos):
                        if button_sound: button_sound.play()
                        reset_game_state() # Reset with current selected_map_id
                        game_state = "playing"
                        continue

                # --- Tutorial State ---
                elif game_state == "tutorial":
                    if button_rects.get('tutorial_ok') and button_rects['tutorial_ok'].collidepoint(mouse_pos):
                        if button_sound: button_sound.play()
                        game_state = "mission_select"
                        button_rects['tutorial_ok'] = None
                        continue

                # --- Settings State ---
                elif game_state == "settings":
                    if button_rects.get('settings_back') and button_rects['settings_back'].collidepoint(mouse_pos):
                        if button_sound: button_sound.play()
                        game_state = previous_game_state
                        continue
                    elif button_rects.get('mute_music') and button_rects['mute_music'].collidepoint(mouse_pos):
                        config.music_muted = not config.music_muted
                        if config.music_muted: pygame.mixer.music.set_volume(0)
                        else: pygame.mixer.music.set_volume(config.music_volume)
                        if button_sound: button_sound.play()
                        continue
                    elif button_rects.get('mute_sfx') and button_rects['mute_sfx'].collidepoint(mouse_pos):
                        config.sfx_muted = not config.sfx_muted
                        current_sfx_vol = 0 if config.sfx_muted else config.sfx_volume
                        if button_sound: button_sound.set_volume(current_sfx_vol)
                        if building_sound: building_sound.set_volume(current_sfx_vol)
                        if button_sound: button_sound.play()
                        continue
                    elif button_rects.get('volume_bar_music') and button_rects['volume_bar_music'].collidepoint(mouse_pos):
                        dragging_music_bar = True
                        bar = button_rects['volume_bar_music']
                        new_volume = max(0.0, min(1.0, (mouse_pos[0] - bar.left) / bar.width))
                        if not config.music_muted:
                            config.music_volume = new_volume
                            pygame.mixer.music.set_volume(config.music_volume)
                        continue
                    elif button_rects.get('volume_bar_sfx') and button_rects['volume_bar_sfx'].collidepoint(mouse_pos):
                        dragging_sfx_bar = True
                        bar = button_rects['volume_bar_sfx']
                        new_sfx_volume = max(0.0, min(1.0, (mouse_pos[0] - bar.left) / bar.width))
                        if not config.sfx_muted:
                            config.sfx_volume = new_sfx_volume
                            current_sfx_vol = config.sfx_volume
                            if button_sound: button_sound.set_volume(current_sfx_vol)
                            if building_sound: building_sound.set_volume(current_sfx_vol)
                        continue

                # --- Game Over/Lost State ---
                elif game_state == "game_over" or game_state == "lost":
                    if button_rects.get('game_over_restart') and button_rects['game_over_restart'].collidepoint(mouse_pos):
                        if button_sound: button_sound.play()
                        reset_game_state()
                        game_state = "playing"
                        continue
                    elif button_rects.get('game_over_exit') and button_rects['game_over_exit'].collidepoint(mouse_pos):
                        if button_sound: button_sound.play()
                        pygame.time.wait(100)
                        running = False
                        continue

                # --- Victory State ---
                elif game_state == "victory":
                    if button_rects.get('victory_restart') and button_rects['victory_restart'].collidepoint(mouse_pos):
                        if button_sound: button_sound.play()
                        reset_game_state()
                        game_state = "playing"
                        continue
                    elif button_rects.get('victory_exit') and button_rects['victory_exit'].collidepoint(mouse_pos):
                        if button_sound: button_sound.play()
                        pygame.time.wait(100)
                        running = False
                        continue

                # --- Map 1 Complete State ---
                elif game_state == "map1_complete":
                    if button_rects.get('map1_continue') and button_rects['map1_continue'].collidepoint(mouse_pos):
                        if button_sound: button_sound.play()
                        game_state = "main_menu"
                        continue

                # --- Mission Select State ---
                elif game_state == "mission_select":
                    if button_rects.get('mission1_select') and button_rects['mission1_select'].collidepoint(mouse_pos):
                        if button_sound: button_sound.play()
                        selected_map_id = "Map_1"
                        reset_game_state()
                        game_state = "playing"
                        button_rects['mission1_select'] = None
                        button_rects['mission2_select'] = None
                        button_rects['mission_select_back'] = None
                        continue
                    elif button_rects.get('mission2_select') and button_rects['mission2_select'].collidepoint(mouse_pos):
                        if button_sound: button_sound.play()
                        selected_map_id = "Map_2"
                        reset_game_state()
                        game_state = "playing"
                        button_rects['mission1_select'] = None
                        button_rects['mission2_select'] = None
                        button_rects['mission_select_back'] = None
                        continue
                    elif button_rects.get('mission_select_back') and button_rects['mission_select_back'].collidepoint(mouse_pos):
                        if button_sound: button_sound.play()
                        game_state = "main_menu"
                        button_rects['mission1_select'] = None
                        button_rects['mission2_select'] = None
                        button_rects['mission_select_back'] = None
                        continue

                # --- Playing State ---
                elif game_state == "playing":
                    if show_help_overlay:
                        show_help_overlay = False
                        continue
                    if button_rects.get('help') and button_rects['help'].collidepoint(mouse_pos):
                        show_help_overlay = True
                        continue

                    try: m_height = config.MENU_HEIGHT
                    except AttributeError: m_height = 80
                    menu_rect = pygame.Rect(0, SCREEN_HEIGHT - m_height, SCREEN_WIDTH, m_height)

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
                                    if button_sound: button_sound.play()
                                    break
                                current_x += item_base_width + spacing
                        continue
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
                            for tower in towers:
                                if tower.rect.collidepoint(mouse_pos):
                                    selected_tower_for_ui = tower
                                    selected_tower_type = None
                                    clicked_on_existing_tower = True
                                    if button_sound: button_sound.play()
                                    break
                            if not clicked_on_existing_tower:
                                if selected_tower_type:
                                    grid_x, grid_y = tile_col, tile_row
                                    if 0 <= grid_y < ROWS and 0 <= grid_x < COLS and map.game_map[grid_y][grid_x] == 2:
                                        can_build = True
                                        try: required_cost = config.TOWER_DATA[selected_tower_type]['levels'][0]['cost']
                                        except (KeyError, IndexError):
                                            required_cost = float('inf')

                                        if can_build and player_stats["currency"] >= required_cost:
                                            player_stats["currency"] -= required_cost
                                            tower_pos = (grid_x * TILE_SIZE + TILE_SIZE // 2, grid_y * TILE_SIZE + TILE_SIZE // 2)
                                            new_tower = create_tower(selected_tower_type, tower_pos, projectiles, enemies, building_sound)
                                            if new_tower:
                                                towers.add(new_tower)
                                                new_tower.grid_x = grid_x
                                                new_tower.grid_y = grid_y
                                                map.game_map[grid_y][grid_x] = 3
                                                if building_sound: building_sound.play()
                                            else:
                                                player_stats["currency"] += required_cost
                                        elif player_stats["currency"] < required_cost:
                                            selected_tower_type = None
                                    else:
                                        selected_tower_type = None
                                        selected_tower_for_ui = None
                                else:
                                    selected_tower_for_ui = None
                                    button_rects['upgrade'] = None
                                    button_rects['sell'] = None
                        continue


        # Zpracování MOUSEMOTION (pro posuvníky hlasitosti)
        elif event.type == pygame.MOUSEMOTION:
            mouse_pos = event.pos
            if dragging_music_bar and button_rects.get('volume_bar_music'):
                bar = button_rects['volume_bar_music']
                new_volume = max(0.0, min(1.0, (mouse_pos[0] - bar.left) / bar.width))
                if not config.music_muted:
                    config.music_volume = new_volume
                    pygame.mixer.music.set_volume(config.music_volume)
            elif dragging_sfx_bar and button_rects.get('volume_bar_sfx'):
                bar = button_rects['volume_bar_sfx']
                new_sfx_volume = max(0.0, min(1.0, (mouse_pos[0] - bar.left) / bar.width))
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

    #region Herní logika (spawning vln, aktualizace objektů, kontrola výhry/prohry)
    if game_state == "playing":

        # 1. Zkontrovat, zda je čas spustit další vlnu
        max_waves_for_map = 10 

        if current_wave == 0 and not wave_complete and current_game_time - last_wave_end_time >= 10000:
            wave_complete = True 
            last_wave_end_time = current_game_time 
 
        if wave_complete and current_wave < max_waves_for_map and current_game_time - last_wave_end_time >= wave_delay:
            current_wave += 1
            wave_ongoing = True 
            wave_complete = False 
            enemies_spawned_this_wave = 0
            current_wave_enemies_to_spawn = [] 
            last_spawn_time = current_game_time 

            wave_number_for_definition = current_wave
            if map.current_map_id == "Map_2":
                 wave_number_for_definition = current_wave + 10 

            if wave_number_for_definition in wave_definitions:
                wave_data = wave_definitions[wave_number_for_definition]
                enemies_in_wave = sum(wave_data.values()) # Celkový počet nepřátel v této vlně
                # Vytvoření seznamu nepřátel k naspawnování pro tuto vlnu
                for enemy_type, count in wave_data.items():
                    current_wave_enemies_to_spawn.extend([enemy_type] * count)
                random.shuffle(current_wave_enemies_to_spawn) 
            else:
                enemies_in_wave = 0
                wave_ongoing = False 
                wave_complete = True 
                last_wave_end_time = current_game_time 

        # 2. Spawnování nepřátel BĚHEM probíhající vlny
        if wave_ongoing and enemies_spawned_this_wave < enemies_in_wave and current_game_time - last_spawn_time >= spawn_interval:
            if current_wave_enemies_to_spawn:
                enemy_type_to_spawn = current_wave_enemies_to_spawn.pop(0)
                wave_number_for_scaling = current_wave
                if map.current_map_id == "Map_2":
                     wave_number_for_scaling = current_wave + 10 

                new_enemy = create_enemy(enemy_type_to_spawn, map.path_pixels, wave_number_for_scaling)
                if new_enemy:
                    # Speciální škálování pro finálního bosse (zůstává, pokud je potřeba)
                    boss_wave = 10 
                    if current_wave == boss_wave and enemy_type_to_spawn.lower() == "demon":
                        scale=1.5; hp_mult=3.0; spd_mult=0.7; reward_mult=2.5
                        # Škálování vizuálů
                        new_size = (int(new_enemy.image.get_width()*scale), int(new_enemy.image.get_height()*scale))
                        new_enemy.image = pygame.transform.smoothscale(new_enemy.image, new_size)
                        new_enemy.rect = new_enemy.image.get_rect(center=new_enemy.rect.center)
                        # Škálování statistik
                        new_enemy.max_health*=hp_mult; new_enemy.health=new_enemy.max_health
                        new_enemy.speed*=spd_mult; new_enemy.original_speed*=spd_mult
                        new_enemy.currency_reward*=reward_mult
                    enemies.add(new_enemy)
                    enemies_spawned_this_wave += 1
                    last_spawn_time = current_game_time
                else:
                    enemies_in_wave -= 1 

            # Zkontrovat, zda byli všichni nepřátelé pro tuto vlnu naspawnováni
            if enemies_spawned_this_wave >= enemies_in_wave:
                 wave_ongoing = False 

        # 3. Zkontrovat, zda je vlna KOMPLETNĚ dokončena
        if not wave_ongoing and not wave_complete and not enemies:
            wave_complete = True # Označit vlnu jako dokončenou
            last_wave_end_time = current_game_time # Nastavit časovač pro další vlnu

            # Zkontrovat přechod na Mapu 2 nebo vítězství
            if current_wave == 10 and map.current_map_id == "Map_1":
                game_state = "map1_complete"
                projectiles.empty() 
            elif current_wave == 10 and map.current_map_id == "Map_2": 
                 game_state = "victory"


        # 4. Aktualizace herních objektů (pokud hra běží a není zobrazena nápověda)
        if not show_help_overlay:
            enemies.update(player_stats)
            towers.update(current_game_time)
            projectiles.update()

        # 5. Zkontrujte podmínku Game Over
        if player_stats["health"] <= 0:
            game_state = "lost";

    #endregion Herní logika (spawning vln, aktualizace objektů, kontrola výhry/prohry)

    #region Kreslení (zpracovává všechny herní stavy)
    screen.fill(BLACK) 

    # --- Kreslete na základě herního stavu ---
    if game_state == "main_menu":
        screens.draw_main_menu(screen, fonts, button_rects)
    elif game_state == "mission_select": # New mission select state
        screens.draw_mission_select_screen(screen, fonts, button_rects)
    elif game_state == "tutorial":
        screens.draw_tutorial_window(screen, fonts, button_rects, game_state)
    elif game_state == "paused":
        # herní svět pod pozastavenou nabídkou
        draw_map(screen); decorations.draw(screen); towers.draw(screen)
        for enemy in enemies: enemy.draw(screen) # Kreslete pozastavené sprity
        game_ui.draw_ui(screen, fonts, player_stats, game_state, current_wave, wave_ongoing, last_wave_end_time, wave_delay, button_rects) # Použijte importovanou funkci
        # pozastavená nabídka
        screens.draw_pause_menu(screen, fonts, button_rects)
    elif game_state == "settings": # Kreslete obrazovku nastavení
        screens.draw_settings_screen(screen, fonts, button_rects, config, button_sound, building_sound, config.music_volume, config.sfx_volume)
    elif game_state == "map1_complete": # Přidáno kreslení pro nový stav
         screens.draw_map1_complete_screen(screen, fonts, button_rects)
    elif game_state == "playing":
        # prvky světa
        draw_map(screen); decorations.draw(screen); towers.draw(screen)

        # --- Kreslení dosahu věže, pokud je vybrána pro UI ---
        if selected_tower_for_ui:
            tower_center = selected_tower_for_ui.rect.center
            # Ensure the tower has a 'range' attribute before accessing it
            if hasattr(selected_tower_for_ui, 'range'):
                tower_range = selected_tower_for_ui.range

                # Vytvoření průhledného povrchu pro kruh
                range_surface = pygame.Surface((tower_range * 2, tower_range * 2), pygame.SRCALPHA)
                # Kreslení žlutého průhledného kruhu
                pygame.draw.circle(range_surface, (255, 255, 0, 50), (tower_range, tower_range), tower_range) # Žlutá s 50 alpha

                # Vykreslení průhledného povrchu na obrazovku
                # Vypočítat pozici pro blit tak, aby střed kruhu byl na středu věže
                blit_x = tower_center[0] - tower_range
                blit_y = tower_center[1] - tower_range
                screen.blit(range_surface, (blit_x, blit_y))

        for enemy in enemies: enemy.draw(screen) 
        projectiles.draw(screen)
        # Kreslete UI prvky
        game_ui.draw_ui(screen, fonts, player_stats, game_state, current_wave, not wave_complete, last_wave_end_time, wave_delay, button_rects)
        game_ui.draw_tower_menu(screen, fonts, selected_tower_type)
        # Kreslete UI pro vylepšení/prodej věží pomocí importované funkce
        tower_ui.draw_tower_upgrade_ui(screen, selected_tower_for_ui, fonts, button_rects) 
        # Kreslete překryvnou nápovědu, pokud je aktivní (používá funkci okna s tutoriálem)
        if show_help_overlay:
            screens.draw_tutorial_window(screen, fonts, button_rects, game_state)
    elif game_state == "lost":
        screens.draw_game_over_screen(screen, fonts, button_rects, current_wave)
    elif game_state == "victory": 
        screens.draw_victory_screen(screen, fonts, button_rects)

    pygame.display.flip()
    #endregion Kreslení

    #region FPS
    clock.tick(FPS)
    #endregion FPS

#endregion Hlavní herní smyčka

# --- Ukončení Pygame ---
pygame.quit()
