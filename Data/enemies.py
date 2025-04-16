#region Imports
from config import *
import pygame
import math
import os


from config import TILE_SIZE, RED, GREEN, load_image, ENEMY_HEALTH_SCALE_FACTOR, ENEMY_SPEED_SCALE_FACTOR

ENEMY_SPRITE_SCALE_FACTOR = 1.35
#endregion



#region Base Enemy Class
class Enemy(pygame.sprite.Sprite):
    def __init__(self, path, enemy_type_data):
        super().__init__()
        if not path:
            raise ValueError("Enemy created with an empty path.")

        self.path = path
        self.path_index = 0
        self.speed = enemy_type_data.get("speed", 2)
        self.original_speed = self.speed # Store original speed
        self.max_health = enemy_type_data.get("health", 100)
        self.health = self.max_health
        self.currency_reward = enemy_type_data.get("reward", 10)
        self.sprite_base_path = enemy_type_data.get("sprite_base_path") # e.g., "enemies/normal_slime/"
        self.num_walk_frames = enemy_type_data.get("num_frames", 4) # Total frames including idle (0)
        self.animation_speed = enemy_type_data.get("anim_speed", 150) # milliseconds per frame

        self.walk_frames = self.load_frames() # Now loads all frames 0 to num_frames-1
        self.current_walk_frame = 0


        if not self.walk_frames:
             # This part might be redundant now if load_frames guarantees a fallback
             print(f"Error: No frames loaded for {self.sprite_base_path} even after fallback attempt. Using final fallback.")
             fallback_size = int(TILE_SIZE // 2 * ENEMY_SPRITE_SCALE_FACTOR) # Apply scaling here too
             fallback_surface = pygame.Surface((fallback_size, fallback_size))
             fallback_surface.fill(RED)
             self.walk_frames = [fallback_surface] # List with one frame
             self.image = fallback_surface
        else:
             # Start with the first frame (index 0)
             self.image = self.walk_frames[self.current_walk_frame]

        self.rect = self.image.get_rect() # Rect will now be based on the scaled image
        self.pos = pygame.Vector2(self.path[0])
        self.target_pos = pygame.Vector2(self.path[self.path_index]) # Start targeting the first point
        self.rect.center = self.pos
        
        # Effect tracking attributes
        self.is_slowed = False
        self.slow_end_time = 0
        self.slow_factor = 1.0 # 1.0 means no slow

        self.is_poisoned = False
        self.poison_end_time = 0
        self.poison_damage = 0
        self.poison_interval = float('inf') # Time between ticks
        self.last_poison_tick_time = 0

        self.last_anim_update = pygame.time.get_ticks()


    def load_frames(self):
        """Loads animation frames (0 to num_frames-1) from individual files and scales them.""" # Modified docstring
        frames = []
        if not self.sprite_base_path:
            print(f"Warning: No sprite base path provided for enemy type.")
            # Create a scaled fallback surface if loading failed entirely
            fallback_size = int(TILE_SIZE // 2 * ENEMY_SPRITE_SCALE_FACTOR) # Apply scaling here too
            fallback_surface = pygame.Surface((fallback_size, fallback_size))
            fallback_surface.fill(RED)
            return [fallback_surface] # Return list with one scaled fallback frame

        try:
            # Load frames from 0 up to num_frames - 1
            for i in range(self.num_walk_frames):
                frame_path = f"{self.sprite_base_path}{i}.png"
                # Use load_image from config
                frame = load_image(frame_path, alpha=True)
                if frame: # Check if frame loaded successfully before scaling
                    original_size = frame.get_size()
                    new_size = (int(original_size[0] * ENEMY_SPRITE_SCALE_FACTOR), int(original_size[1] * ENEMY_SPRITE_SCALE_FACTOR))
                    scaled_frame = pygame.transform.smoothscale(frame, new_size) # Use smoothscale for better quality
                    frames.append(scaled_frame)
                    # print(f"Loaded and scaled frame: {frame_path}") # Debug print removed
                else:
                    # If a specific frame fails to load, append None or handle differently?
                    # For now, let's skip appending if load_image returned None
                    print(f"Warning: Failed to load frame {i} from {frame_path}. Skipping.")

        except Exception as e:
            print(f"Error loading frames from base path {self.sprite_base_path}: {e}")
            # If error during loading/scaling, return what we have, fallback handled in __init__

        # If after trying, frames list is still empty, create the fallback
        if not frames:
             print(f"Error: No frames loaded successfully for {self.sprite_base_path}. Using fallback.")
             fallback_size = int(TILE_SIZE // 2 * ENEMY_SPRITE_SCALE_FACTOR)
             fallback_surface = pygame.Surface((fallback_size, fallback_size))
             fallback_surface.fill(RED)
             frames = [fallback_surface]

        return frames


    def update_animation(self):
        """Cycles through the animation frames."""
        if not self.walk_frames or len(self.walk_frames) <= 1: # Don't animate if no frames or only one
             return

        now = pygame.time.get_ticks()
        if now - self.last_anim_update > self.animation_speed:
            self.last_anim_update = now
            self.current_walk_frame = (self.current_walk_frame + 1) % len(self.walk_frames)
            next_frame = self.walk_frames[self.current_walk_frame]
            if next_frame: # Check if the frame loaded successfully
                self.image = next_frame
                # Keep the center position consistent
                old_center = self.rect.center
                self.rect = self.image.get_rect(center=old_center)
            else:
                # Optional: Log an error or handle the missing frame case
                # print(f"Warning: Missing animation frame {self.current_walk_frame} for {self.sprite_base_path}")
                pass # Keep the previous frame if the current one is missing


    def apply_slow(self, factor, duration_ms):
        """Applies a slow effect to the enemy."""
        if not self.is_slowed: # Store original speed only when first slowed
            self.original_speed = self.speed
        self.is_slowed = True
        self.slow_factor = factor # Store the factor causing the slow
        self.speed = self.original_speed * factor # Apply slow
        self.slow_end_time = pygame.time.get_ticks() + duration_ms
        # print(f"Enemy slowed! Speed: {self.speed}, Ends at: {self.slow_end_time}") # Debug

    def apply_poison(self, dot, duration_ms, interval_ms):
        """Applies a poison effect to the enemy."""
        self.is_poisoned = True
        self.poison_damage = dot
        self.poison_interval = interval_ms
        self.poison_end_time = pygame.time.get_ticks() + duration_ms
        # Reset tick timer so the first tick happens after 'interval_ms' from application
        self.last_poison_tick_time = pygame.time.get_ticks()
        # print(f"Enemy poisoned! DoT: {dot}, Duration: {duration_ms}, Interval: {interval_ms}") # Debug


    def update(self, player_stats):
        """Updates enemy position, animation, effects, and checks for path end/death."""
        current_time = pygame.time.get_ticks()

        # --- Handle Effects ---
        # Slow Effect
        if self.is_slowed and current_time >= self.slow_end_time:
            self.is_slowed = False
            self.speed = self.original_speed # Restore speed
            self.slow_factor = 1.0
            # print("Slow expired.") # Debug

        # Poison Effect
        if self.is_poisoned:
            if current_time >= self.poison_end_time:
                self.is_poisoned = False
                # print("Poison expired.") # Debug
            elif current_time - self.last_poison_tick_time >= self.poison_interval:
                # print(f"Poison!{self.poison_damage} damage.") # Debug
                self.take_damage(self.poison_damage)
                self.last_poison_tick_time = current_time # Reset timer

        # --- Check Death (after poison) ---
        if self.health <= 0:
            player_stats["currency"] += self.currency_reward
            self.kill() 
            return True 

        # --- Movement ---
        if self.path_index >= len(self.path):
            print(f"Warning: Enemy already finished path at index {self.path_index}. Killing.")
            self.kill()
            return False 

        current_target_pos = pygame.Vector2(self.path[self.path_index])

        move_vector = current_target_pos - self.pos
        distance_to_target = move_vector.length()

        if distance_to_target > 0:
            dist_to_move_this_frame = min(self.speed, distance_to_target)
            try:
                
                move_vector.scale_to_length(dist_to_move_this_frame)
            except ValueError: 
                move_vector = pygame.Vector2(0,0)
            
            self.pos += move_vector
        
        
        arrival_threshold = 1.5 
        
        new_distance_to_target = (current_target_pos - self.pos).length()

        if new_distance_to_target < arrival_threshold:
            
            self.pos = current_target_pos
            self.path_index += 1
            
            if self.path_index >= len(self.path):
                player_stats["health"] -= 1
                self.kill()
                return False 

        
        self.rect.center = self.pos

        # --- Animation ---
        self.update_animation()
        return False 


    def take_damage(self, amount):
        """Reduces enemy health by the given amount."""
        self.health -= amount
        if self.health < 0:
            self.health = 0

    def draw(self, surface):
        """Draws the enemy and its health bar."""
        # Draw enemy sprite first
        surface.blit(self.image, self.rect)

        # Draw health bar , if damaged
        if self.health < self.max_health and self.max_health > 0:
            bar_width_ratio = self.health / self.max_health
            max_bar_width = self.rect.width 
            current_bar_width = max(1, int(max_bar_width * bar_width_ratio)) 
            bar_height = 5

            #  health bar 
            bar_x = self.rect.left
            bar_y = self.rect.top - bar_height - 2 

            health_bar_bg_rect = pygame.Rect(bar_x, bar_y, max_bar_width, bar_height)
            health_fill_rect = pygame.Rect(bar_x, bar_y, current_bar_width, bar_height)

            pygame.draw.rect(surface, RED, health_bar_bg_rect) 
            pygame.draw.rect(surface, GREEN, health_fill_rect) 

#endregion

#region Specific Enemy Type Data
ENEMY_DATA = {
    "normal_slime": {
        "sprite_base_path": "enemies/normal_slime/",
        "num_frames": 4, 
        "anim_speed": 200,
        "speed": 1.5,
        "health": 80,
        "reward": 5,
    },
    "big_slime": {
        "sprite_base_path": "enemies/big_slime/",
        "num_frames": 4,
        "anim_speed": 250,
        "speed": 1,
        "health": 200,
        "reward": 15,
    },
     "king_slime": { # Boss
        "sprite_base_path": "enemies/king_slime/",
        "num_frames": 4,
        "anim_speed": 300,
        "speed": 0.8,
        "health": 1000,
        "reward": 100,
    },
    "bat": {
        "sprite_base_path": "enemies/Bat/", 
        "num_frames": 4,
        "anim_speed": 100, 
        "speed": 2.5,
        "health": 50,
        "reward": 8,
    },
     "ghost": {
        "sprite_base_path": "enemies/ghost/",
        "num_frames": 8, 
        "anim_speed": 180,
        "speed": 1.8,
        "health": 70,
        "reward": 7,
    },
    "demon": {
        "sprite_base_path": "enemies/demon/",
        "num_frames": 4,
        "anim_speed": 150,
        "speed": 2.0,
        "health": 150,
        "reward": 20,
    },
    "goblin": {
        "sprite_base_path": "enemies/goblin/",
        "num_frames": 4,
        "anim_speed": 180,
        "speed": 1.7,
        "health": 90,
        "reward": 10,
    },
    "skeleton": {
        "sprite_base_path": "enemies/skeleton/",
        "num_frames": 4,
        "anim_speed": 220,
        "speed": 1.2,
        "health": 120,
        "reward": 12,
    },
    "zombie": {
        "sprite_base_path": "enemies/zombie/",
        "num_frames": 4,
        "anim_speed": 280,
        "speed": 0.9,
        "health": 180,
        "reward": 18,
    },
    
}

#endregion

#region Factory Function
def create_enemy(enemy_type_name, path, wave_level):
    """Creates an enemy instance based on its type name."""
    enemy_type_name_lower = enemy_type_name.lower() 
    if enemy_type_name_lower in ENEMY_DATA:
        enemy_data = ENEMY_DATA[enemy_type_name_lower]

        
        scaled_health = enemy_data["health"] * (ENEMY_HEALTH_SCALE_FACTOR ** (wave_level - 1))
        scaled_speed = enemy_data["speed"] * (ENEMY_SPEED_SCALE_FACTOR ** (wave_level - 1))

        
        scaled_enemy_data = {**enemy_data, "health": scaled_health, "speed": scaled_speed}
        return Enemy(path, scaled_enemy_data)
    else:
        print(f"Warning: Unknown enemy type '{enemy_type_name}'. Spawning normal slime instead.")
        if "normal_slime" in ENEMY_DATA:
             return Enemy(path, ENEMY_DATA["normal_slime"])
        else:
            
             raise ValueError("Default enemy type 'normal_slime' not found in ENEMY_DATA.")
#endregion
