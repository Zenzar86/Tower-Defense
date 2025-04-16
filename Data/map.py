import pygame
import os
from config import TILE_SIZE, PATH_DIR, load_image, CONFIG_DIR, BROWN

# --- Načíst obrázky segmentů cesty ---
path_images = {} 

def load_path_segments():
    global path_images 
    required_paths = {
        "horizontal": "path0.png",
        "vertical":   "path3.png", 
        "corner_base": "path1.png" 
    }
    loaded_images = {}
    try:
        for key, filename in required_paths.items():
            img_path = os.path.join(PATH_DIR, filename)
            loaded_img = load_image(img_path, alpha=True)
            if loaded_img:
                scaled_img = pygame.transform.scale(loaded_img, (TILE_SIZE, TILE_SIZE))
                loaded_images[key] = scaled_img
            else:
                fallback_surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
                fallback_surf.fill(BROWN)
                loaded_images[key] = fallback_surf

    except Exception as e:
        if not loaded_images:
            fallback_surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
            fallback_surf.fill(BROWN)
            loaded_images = {
                "horizontal": fallback_surf, "vertical": fallback_surf,
                "corner_ul": fallback_surf, "corner_ur": fallback_surf,
                "corner_dl": fallback_surf, "corner_dr": fallback_surf
            }

    path_images = loaded_images

path_pixels = []

# --- Definice mapy ---
_initial_game_map = [
    # 0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], # 0
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], # 1
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], # 2
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], # 3
    [0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0], # 4
    [0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0], # 5
    [0, 2, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 2, 0, 0, 0, 0, 0], # 6
    [1, 1, 1, 0, 1, 0, 2, 1, 0, 2, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0], # 7
    [0, 2, 1, 2, 1, 0, 0, 1, 0, 0, 1, 0, 2, 1, 0, 0, 2, 0, 0, 0], # 8
    [0, 0, 1, 0, 1, 2, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 1, 1, 1], # 9
    [0, 0, 1, 0, 1, 0, 0, 1, 2, 0, 1, 0, 0, 1, 2, 0, 1, 2, 0, 0], # 10
    [0, 2, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 0], # 11
    [0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], # 12
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], # 13
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]  # 14
]

# Aktivní herní mapa, inicializována jako prázdná
game_map = []

# --- Funkce pro resetování mapy ---
def reset_game_map():
    global game_map
    # Vytvořte hlubokou kopii, abyste se vyhnuli úpravě originálu
    game_map = [row[:] for row in _initial_game_map]

# --- Logika obrázků dlaždic cesty ---
def get_path_tile_image(row, col): 
    global game_map 
    is_path = lambda r, c: 0 <= r < ROWS and 0 <= c < COLS and game_map[r][c] == 1
    ROWS = len(game_map)
    COLS = len(game_map[0]) if ROWS > 0 else 0

    up = is_path(row - 1, col)
    down = is_path(row + 1, col)
    left = is_path(row, col - 1)
    right = is_path(row, col + 1)

    num_connections = sum([up, down, left, right])
    image_to_return = None # Uložení konečného obrázku zde

    if num_connections == 2:
        # Určete typ segmentu na základě sousedů
        if left and right:
            image_to_return = path_images.get("horizontal")
        elif up and down:
            image_to_return = path_images.get("vertical")
        else: # Je to roh, určete rotaci
            base_corner_img = path_images.get("corner_base")
            if base_corner_img:
                rotation = 0 # Výchozí rotace

                if down and right: rotation = 0  
                elif down and left: rotation = -90 
                elif up and left: rotation = 180  
                elif up and right: rotation = 90   
                else: pass
                image_to_return = pygame.transform.rotate(base_corner_img, rotation)
            else:
                image_to_return = path_images.get("horizontal")

    elif num_connections == 1: 
        if up or down: image_to_return = path_images.get("vertical")
        else: image_to_return = path_images.get("horizontal")
    elif num_connections == 3: 
        if left and right: image_to_return = path_images.get("horizontal")
        elif up and down: image_to_return = path_images.get("vertical")
        else:
             image_to_return = path_images.get("horizontal") 
    elif num_connections == 4: 
        image_to_return = path_images.get("vertical") 
    elif num_connections == 0: 
        image_to_return = path_images.get("horizontal") 

    # Vraťte určený obrázek, nebo konečnou zálohu, pokud něco selhalo
    if image_to_return:
        return image_to_return
    else:
        fallback = path_images.get("horizontal")
        if fallback:
            return fallback
        else:
            fallback_surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
            fallback_surf.fill(BROWN)
            return fallback_surf

# --- Generování pixelové cesty ---
def generate_pixel_path(): 
    global game_map, path_pixels 
    waypoints_map = {}
    start_node = None
    path_nodes = [] 
    ROWS = len(game_map)
    COLS = len(game_map[0]) if ROWS > 0 else 0


     # 1. Najděte počáteční uzel
    for r in range(ROWS):
        if game_map[r][0] == 1:
            start_node = (0, r)
            break
    if not start_node:
        for c in range(COLS):
            if game_map[0][c] == 1:
                start_node = (c, 0)
                break

    if not start_node:
        path_pixels = [] 
        return 

    # 2. Sledujte cestu
    current_node = start_node
    visited = {current_node}
    path_nodes.append(current_node)
    last_direction = None 

    while True:
        col, row = current_node
        neighbors = []
        if col < COLS - 1 and game_map[row][col + 1] == 1: neighbors.append(((col + 1, row), 'R')) # Vpravo
        if row < ROWS - 1 and game_map[row + 1][col] == 1: neighbors.append(((col, row + 1), 'D')) # Dole
        if col > 0 and game_map[row][col - 1] == 1: neighbors.append(((col - 1, row), 'L')) # Vlevo
        if row > 0 and game_map[row - 1][col] == 1: neighbors.append(((col, row - 1), 'U')) # Nahoru

        # Najděte další nenavštíveného souseda podle preferovaného pořadí
        next_node = None
        move_direction = None
        for neighbor, direction in neighbors:
            if neighbor not in visited:
                next_node = neighbor
                move_direction = direction
                break

        # Určete typ segmentu a přidejte waypoints pro *aktuální* uzel
        tile_center_x = col * TILE_SIZE + TILE_SIZE // 2
        tile_center_y = row * TILE_SIZE + TILE_SIZE // 2
        quarter_tile = TILE_SIZE // 4 

        current_waypoints = []

        # Určete vstupní směr (opačný od posledního pohybu)
        entry_direction = None
        if last_direction == 'U': entry_direction = 'D'
        elif last_direction == 'D': entry_direction = 'U'
        elif last_direction == 'L': entry_direction = 'R'
        elif last_direction == 'R': entry_direction = 'L'

        exit_direction = move_direction # Směr, kterým opouštíme aktuální uzel

        current_waypoints.append((tile_center_x, tile_center_y))

        waypoints_map[current_node] = current_waypoints

        if not next_node: # Dosáhli jsme konce cesty
            break

        # Přesuňte se na další uzel
        visited.add(next_node)
        path_nodes.append(next_node)
        current_node = next_node
        last_direction = move_direction

    # Přidejte waypoints pro poslední uzel (jen jeho střed)
    final_col, final_row = current_node
    waypoints_map[current_node] = [(final_col * TILE_SIZE + TILE_SIZE // 2, final_row * TILE_SIZE + TILE_SIZE // 2)]

    # 3. Kombinujte waypoints v pořadí
    final_path_pixels = []
    for node in path_nodes:
        if node in waypoints_map:
            final_path_pixels.extend(waypoints_map[node])

    # Odstraňte duplicity
    unique_path = []
    if final_path_pixels:
        unique_path.append(final_path_pixels[0])
        for i in range(1, len(final_path_pixels)):
            if final_path_pixels[i] != final_path_pixels[i-1]:
                unique_path.append(final_path_pixels[i])

    path_pixels = unique_path 

# --- Funkce pro načtení mapových assetů ---
def load_map_assets():
    global path_pixels 
    load_path_segments()
    reset_game_map() 
    generate_pixel_path() 