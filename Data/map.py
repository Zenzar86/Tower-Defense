import pygame
import os
from config import TILE_SIZE, PATH_DIR, load_image, CONFIG_DIR, BROWN

# --- Asset Loading ---
# --- Load Path Segment Images ---
path_images = {} # Use a dictionary

def load_path_segments():
    global path_images # Modify global dict
    # Load base path segments: horizontal, vertical, and one base corner
    required_paths = {
        "horizontal": "path0.png",
        "vertical":   "path3.png", # Assuming path3 is vertical (as originally)
        "corner_base": "path1.png" # Load path1.png as the base corner to be rotated
    }
    loaded_images = {}
    try:
        for key, filename in required_paths.items():
            img_path = os.path.join(PATH_DIR, filename)
            loaded_img = load_image(img_path, alpha=True)
            if loaded_img:
                scaled_img = pygame.transform.scale(loaded_img, (TILE_SIZE, TILE_SIZE))
                loaded_images[key] = scaled_img
                print(f"Loaded and scaled path segment: {filename} as '{key}' (from map.py)")
            else:
                print(f"ERROR: Failed to load required path segment: {filename} (from map.py). Creating fallback.")
                fallback_surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
                fallback_surf.fill(BROWN)
                loaded_images[key] = fallback_surf

        # Generate rotated corners if base corner loaded successfully
        # No pre-rotation needed here anymore. Rotation will happen dynamically.


    except Exception as e:
        print(f"ERROR loading path segments in map.py: {e}")
        # Create fallback dict if loading failed significantly
        if not loaded_images:
            print("Creating fallback path tiles for all types in map.py.")
            fallback_surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
            fallback_surf.fill(BROWN)
            loaded_images = {
                "horizontal": fallback_surf, "vertical": fallback_surf,
                "corner_ul": fallback_surf, "corner_ur": fallback_surf,
                "corner_dl": fallback_surf, "corner_dr": fallback_surf
            }

    path_images = loaded_images # Assign to global
    # The function doesn't need to return anything now as it modifies the global

# Initialize global variable for path pixels
path_pixels = []

# --- Map Definition ---
# Store the initial layout
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

# The active game map, initialized as empty
game_map = []

# --- Function to Reset the Map ---
def reset_game_map():
    """Resets the active game map to its initial state."""
    global game_map
    # Create a deep copy to avoid modifying the original
    game_map = [row[:] for row in _initial_game_map]
    print("Game map reset to initial state (from map.py).")

# --- Path Tile Image Logic ---
def get_path_tile_image(row, col): # Removed game_map parameter, uses global
    """Determines the correct path tile image based on neighbors, dynamically rotating a base corner image."""
    global game_map # Explicitly state usage of global
    is_path = lambda r, c: 0 <= r < ROWS and 0 <= c < COLS and game_map[r][c] == 1
    ROWS = len(game_map)
    COLS = len(game_map[0]) if ROWS > 0 else 0

    up = is_path(row - 1, col)
    down = is_path(row + 1, col)
    left = is_path(row, col - 1)
    right = is_path(row, col + 1)

    # Path images are now stored in the global `path_images` dictionary
    # Keys: "horizontal", "vertical", "corner_base"

    num_connections = sum([up, down, left, right])
    image_to_return = None # Store the final image here

    if num_connections == 2:
        # Determine segment type based on neighbors
        if left and right:
            image_to_return = path_images.get("horizontal")
        elif up and down:
            image_to_return = path_images.get("vertical")
        else: # It's a corner, determine rotation
            base_corner_img = path_images.get("corner_base")
            if base_corner_img:
                rotation = 0 # Default rotation
                # Determine rotation based on the two connected neighbors
                # Reverted Assumption: base corner image (path1.png) connects bottom and right when rotation is 0
                # Assuming base connects down and right (0), rotating CCW
                if down and right: rotation = 0    # Base: connects down and right
                elif down and left: rotation = -90 # Rotate -90 deg: connects down and left (User feedback)
                elif up and left: rotation = 180  # Rotate +180 CCW: connects up and left (Keep as 180)
                elif up and right: rotation = 90   # Rotate +90 CCW: connects up and right (User feedback)
                else:
                     # This case should ideally not happen if num_connections is 2 and it's not straight
                     print(f"Warning: Path tile at ({row},{col}) has unexpected 2 connections. Using unrotated corner.")
                image_to_return = pygame.transform.rotate(base_corner_img, rotation)
            else:
                print(f"Error: Base corner image 'corner_base' not found for tile at ({row},{col}). Using fallback.")
                image_to_return = path_images.get("horizontal") # Fallback to horizontal if base corner missing

    elif num_connections == 1: # End Caps
        if up or down: image_to_return = path_images.get("vertical")
        else: image_to_return = path_images.get("horizontal")
        # print(f"Warning: Path tile at (map.py) ({row},{col}) is an end cap.") # Less verbose
    elif num_connections == 3: # T-Junctions
        # Use dominant straight piece for T-junctions (can be refined later if needed)
        if left and right: image_to_return = path_images.get("horizontal") # T pointing up or down
        elif up and down: image_to_return = path_images.get("vertical")   # T pointing left or right
        else:
             print(f"Warning: Path tile at (map.py) ({row},{col}) has unexpected 3 connections. Using default 'horizontal'.")
             image_to_return = path_images.get("horizontal") # Fallback T
        # print(f"Warning: Path tile at (map.py) ({row},{col}) is a T-junction.") # Less verbose
    elif num_connections == 4: # Crossings
        image_to_return = path_images.get("vertical") # Default crossing to vertical (or could use horizontal)
        # print(f"Warning: Path tile at (map.py) ({row},{col}) is a crossing.") # Less verbose
    elif num_connections == 0: # Isolated
        image_to_return = path_images.get("horizontal") # Default for isolated
        print(f"ERROR: Isolated path tile at (map.py) ({row},{col}). Using default 'horizontal'.")

    # Return the determined image, or a final fallback if something went wrong
    if image_to_return:
        return image_to_return
    else:
        print(f"Error: Could not determine path image for ({row},{col}). Returning final fallback.")
        # Final fallback: try horizontal, then create a brown square
        fallback = path_images.get("horizontal")
        if fallback:
            return fallback
        else:
            fallback_surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
            fallback_surf.fill(BROWN)
            return fallback_surf

    # The logic above now directly returns the image or a fallback


# --- Path Pixel Generation ---
def generate_pixel_path(): # Removed game_map parameter, uses global
    """Generates a list of pixel coordinates defining the enemy path, adding curve points."""
    global game_map, path_pixels # Use global game_map, modify global path_pixels
    waypoints_map = {} # Store waypoints per tile (col, row) -> list of pixel coords
    start_node = None
    path_nodes = [] # Keep track of the sequence of (col, row) tiles
    ROWS = len(game_map)
    COLS = len(game_map[0]) if ROWS > 0 else 0


    # 1. Find the start node
    for r in range(ROWS):
        if game_map[r][0] == 1:
            start_node = (0, r)
            break
        # Allow start from right edge too if needed
        # if game_map[r][COLS - 1] == 1:
        #     start_node = (COLS - 1, r)
        #     break
    if not start_node:
        for c in range(COLS):
            if game_map[0][c] == 1:
                start_node = (c, 0)
                break
            # Allow start from bottom edge too if needed
            # if game_map[ROWS - 1][c] == 1:
            #     start_node = (c, ROWS - 1)
            #     break

    if not start_node:
        print("Error: Could not find path start node on left or top edge in map.py.")
        path_pixels = [] # Ensure path_pixels is empty if start not found
        return # Don't proceed further

    # 2. Trace the path
    # ... (logic remains the same, uses global game_map) ...
    current_node = start_node
    visited = {current_node}
    path_nodes.append(current_node)
    last_direction = None # Track entry direction for curve logic

    while True:
        col, row = current_node
        neighbors = []

        # Check potential neighbors (Prefer Right/Down first, then Left/Up to guide tracing)
        # Order matters for deterministic tracing on simple paths
        if col < COLS - 1 and game_map[row][col + 1] == 1: neighbors.append(((col + 1, row), 'R')) # Right
        if row < ROWS - 1 and game_map[row + 1][col] == 1: neighbors.append(((col, row + 1), 'D')) # Down
        if col > 0 and game_map[row][col - 1] == 1: neighbors.append(((col - 1, row), 'L')) # Left
        if row > 0 and game_map[row - 1][col] == 1: neighbors.append(((col, row - 1), 'U')) # Up

        # Find the next unvisited neighbor based on preferred order
        next_node = None
        move_direction = None
        for neighbor, direction in neighbors:
            if neighbor not in visited:
                next_node = neighbor
                move_direction = direction
                break

        # Determine segment type and add waypoints for the *current* node
        tile_center_x = col * TILE_SIZE + TILE_SIZE // 2
        tile_center_y = row * TILE_SIZE + TILE_SIZE // 2
        quarter_tile = TILE_SIZE // 4 # For curve points (adjust for smoother/sharper curves)
        # eighth_tile = TILE_SIZE // 8 # Finer control if needed

        current_waypoints = []

        # Determine entry direction (opposite of last move)
        entry_direction = None
        if last_direction == 'U': entry_direction = 'D'
        elif last_direction == 'D': entry_direction = 'U'
        elif last_direction == 'L': entry_direction = 'R'
        elif last_direction == 'R': entry_direction = 'L'

        exit_direction = move_direction # Direction we are *leaving* the current node

        # Simplified: Always add the center of the current tile as a waypoint.
        # The previous logic with entry/exit directions and curve points was removed.
        current_waypoints.append((tile_center_x, tile_center_y))

        waypoints_map[current_node] = current_waypoints

        if not next_node: # Reached the end of the path
            break

        # Move to the next node
        visited.add(next_node)
        path_nodes.append(next_node)
        current_node = next_node
        last_direction = move_direction # Store the direction we moved to get here

    # Add waypoints for the final node (just its center)
    final_col, final_row = current_node
    waypoints_map[current_node] = [(final_col * TILE_SIZE + TILE_SIZE // 2, final_row * TILE_SIZE + TILE_SIZE // 2)]

    # 3. Combine waypoints in order
    final_path_pixels = []
    for node in path_nodes:
        if node in waypoints_map:
            final_path_pixels.extend(waypoints_map[node])

    # Remove duplicates
    unique_path = []
    if final_path_pixels:
        unique_path.append(final_path_pixels[0])
        for i in range(1, len(final_path_pixels)):
            if final_path_pixels[i] != final_path_pixels[i-1]:
                unique_path.append(final_path_pixels[i])

    print(f"Generated path with {len(unique_path)} waypoints (from map.py).")
    path_pixels = unique_path # Assign to global


# --- Function to Load Map Assets ---
def load_map_assets():
    """Loads path images, resets the map, and generates the pixel path."""
    global path_pixels # Ensure we intend to modify the global

    print("--- Loading Map Assets ---")
    load_path_segments()
    reset_game_map() # Reset the map to its initial state
    generate_pixel_path() # Generate path based on the reset map
    print("--- Finished Loading Map Assets ---")

# (Call load_map_assets() from main.py after display init)
