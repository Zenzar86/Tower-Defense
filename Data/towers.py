import pygame
import math
import os # Import os for path joining
from pygame.math import Vector2
# Import necessary items from config
from config import TILE_SIZE, TOWER_DATA, TOWER_SELL_PERCENTAGE, load_image, RED # Added RED
from projectiles import Projectile # Start with the base projectile
from languages import get_text # Import for localized text

# --- Base Tower Class ---
class Tower(pygame.sprite.Sprite):
    def __init__(self, tower_type_name, pos, projectile_group, enemy_group, building_sound=None): # Added building_sound
        super().__init__()
        self.tower_type_name = tower_type_name # Store the type name (e.g., "Archer")
        self.level = 1 # Towers start at level 1
        self.projectile_group = projectile_group
        self.enemy_group = enemy_group
        self.pos = Vector2(pos)
        self.building_sound = building_sound # Store the sound object

        # Get initial data for level 1
        self.config_data = TOWER_DATA[self.tower_type_name]
        level_data = self.get_current_level_data()
        if not level_data:
             raise ValueError(f"Could not find level 1 data for tower type {self.tower_type_name}")

        self.total_cost_invested = level_data.get('cost', 0) # Initial investment

        # --- Load Base Image ---
        # Image path might be per-level later, but start with the base path
        base_image_path = self.config_data.get('image_path')
        level_image_path = level_data.get('image_path', base_image_path) # Use level-specific image if available

        loaded_image = load_image(level_image_path) if level_image_path else None
        if loaded_image:
            self.image = pygame.transform.scale(loaded_image, (TILE_SIZE, TILE_SIZE))
        else:
            self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
            self.image.fill(RED) # Use color from config
            print(f"ERROR: Failed to load image for tower {self.tower_type_name} level {self.level}. Using fallback.")

        # --- Load Projectile Image ---
        # Projectile image usually stays the same across levels, but could be overridden
        base_projectile_path = self.config_data.get('projectile_path')
        level_projectile_path = level_data.get('projectile_path', base_projectile_path)

        self.projectile_image = load_image(level_projectile_path) if level_projectile_path else None
        if not self.projectile_image:
            self.projectile_image = pygame.Surface((10, 10))
            self.projectile_image.fill((0, 0, 255)) # Blue fallback
            print(f"ERROR: Failed to load projectile image for {self.tower_type_name}. Using fallback.")


        self.rect = self.image.get_rect(center=self.pos)
        self.target = None
        self.last_shot_time = pygame.time.get_ticks() # Initialize last shot time

        # --- Set Initial Stats from Level 1 Data ---
        self.update_stats_from_level_data(level_data)

        # --- Load Firing Sound ---
        self.fire_sound = None
        sound_path = self.config_data.get('sound_path')
        if sound_path:
            try:
                # Use get_resource_path for consistency
                # Need to import config directly to call the function
                import config as cfg
                abs_sound_path = cfg.get_resource_path(sound_path)
                self.fire_sound = pygame.mixer.Sound(abs_sound_path)
                # print(f"Loaded sound for {self.tower_type_name}: {abs_sound_path}") # Keep debug for now
            except pygame.error as e:
                print(f"ERROR: Could not load sound file for {self.tower_type_name}: {sound_path} (abs: {abs_sound_path}) - {e}")
            except FileNotFoundError:
                 print(f"ERROR: Sound file not found for {self.tower_type_name}: {sound_path} (abs: {abs_sound_path})")
            except Exception as e:
                 print(f"ERROR: An unexpected error occurred loading sound for {self.tower_type_name} ({sound_path}): {e}")

        # Allow shooting immediately after placement if possible
        self.last_shot_time -= self.cooldown


    def get_current_level_data(self):
        """Returns the configuration dictionary for the tower's current level."""
        try:
            # Levels are 1-based, list index is 0-based
            return self.config_data['levels'][self.level - 1]
        except (IndexError, KeyError):
            print(f"Error: Could not find level data for {self.tower_type_name} level {self.level}")
            return None

    def update_stats_from_level_data(self, level_data):
        """Updates tower attributes based on the provided level data dictionary."""
        if not level_data:
            print(f"Warning: Attempted to update stats with invalid level data for {self.tower_type_name}")
            return

        self.range = level_data.get('range', 100)
        self.fire_rate = level_data.get('fire_rate', 1.0)
        self.cooldown = 1000 / self.fire_rate if self.fire_rate > 0 else float('inf')
        self.damage = level_data.get('damage', 0)

        # Update special effect parameters if they exist for this tower type
        if 'slow_factor' in level_data:
            self.slow_factor = level_data['slow_factor']
        if 'slow_duration' in level_data:
            self.slow_duration = level_data['slow_duration']
        if 'chain_targets' in level_data:
            self.chain_targets = level_data['chain_targets']
        if 'chain_range' in level_data:
            self.chain_range = level_data['chain_range']
        if 'damage_over_time' in level_data:
            self.dot_damage = level_data['damage_over_time']
        if 'poison_duration' in level_data:
            self.poison_duration = level_data['poison_duration']
        if 'poison_interval' in level_data:
            self.poison_interval = level_data['poison_interval']

        # Update image if level-specific image exists
        level_image_path = level_data.get('image_path', self.config_data.get('image_path'))
        if level_image_path:
            loaded_image = load_image(level_image_path)
            if loaded_image:
                 # Keep existing center when changing image
                old_center = self.rect.center
                self.image = pygame.transform.scale(loaded_image, (TILE_SIZE, TILE_SIZE))
                self.rect = self.image.get_rect(center=old_center)
            # else: Keep old image if new one fails to load

    def get_upgrade_cost(self):
        """Returns the cost to upgrade to the next level, or 0 if max level."""
        current_level_data = self.get_current_level_data()
        if current_level_data:
            return current_level_data.get('upgrade_cost', 0)
        return 0 # Cannot upgrade if current level data is missing

    def get_sell_price(self):
        """Calculates the sell price based on total invested cost."""
        return int(self.total_cost_invested * TOWER_SELL_PERCENTAGE)

    def upgrade(self, player_stats):
        """Attempts to upgrade the tower to the next level."""
        upgrade_cost = self.get_upgrade_cost()

        # Check if already max level
        if upgrade_cost <= 0:
            print(get_text("tower_max_level", tower_type=self.tower_type_name, level=self.level))
            return False

        # Check currency
        if player_stats['currency'] < upgrade_cost:
            print(get_text("cannot_upgrade_no_gold", tower_type=self.tower_type_name, cost=upgrade_cost, have=player_stats['currency']))
            return False

        # Check if next level data exists
        next_level_index = self.level # Current level is 1, next index is 1 (level 2)
        if next_level_index >= len(self.config_data['levels']):
             print(f"Error: No data found for next level ({self.level + 1}) for {self.tower_type_name}.")
             return False # Should be caught by upgrade_cost check, but good safeguard

        # --- Proceed with upgrade ---
        player_stats['currency'] -= upgrade_cost
        self.total_cost_invested += upgrade_cost
        self.level += 1
        print(get_text("tower_upgraded", tower_type=self.tower_type_name, level=self.level, cost=upgrade_cost))

        # Update stats to new level
        new_level_data = self.get_current_level_data()
        self.update_stats_from_level_data(new_level_data)

        # Play sound on successful upgrade
        if self.building_sound:
            self.building_sound.play()

        return True

    def find_target(self):
        """Finds the closest enemy within range."""
        closest_enemy = None
        min_dist_sq = self.range ** 2 # Use squared distance for efficiency

        for enemy in self.enemy_group:
            if hasattr(enemy, 'pos') and enemy.alive(): # Check if enemy is alive
                distance_sq = self.pos.distance_squared_to(enemy.pos)
                if distance_sq < min_dist_sq:
                    min_dist_sq = distance_sq
                    closest_enemy = enemy
            # else: # Reduce console spam
            #     print(f"Warning: Enemy {enemy} missing 'pos' attribute or not alive.")

        self.target = closest_enemy # Can be None if no enemy in range

    def shoot(self, current_time):
        """Shoots at the target if cooldown is over."""
        if self.target and (current_time - self.last_shot_time >= self.cooldown):
            self.create_projectile() # Call projectile creation method
            self.last_shot_time = current_time
            # Play sound if available and not muted
            # Need to import config directly here to check mute state and volume
            import config as cfg
            if self.fire_sound and not cfg.sfx_muted:
                self.fire_sound.set_volume(cfg.sfx_volume) # Apply current SFX volume
                self.fire_sound.play()
            return True
        return False

    def create_projectile(self):
        """Creates the projectile for this tower type. To be implemented by subclasses."""
        # Default projectile creation (standard damage)
        projectile = Projectile(
            self.projectile_image,
            self.pos,
            self.target,
            self.damage
        )
        self.projectile_group.add(projectile)

    def update(self, current_time): # Simplified arguments
        self.find_target()
        self.shoot(current_time)

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        # Optional: Draw range indicator (useful for debugging)
        # pygame.draw.circle(surface, (100, 100, 100, 100), self.rect.center, self.range, 1) # Semi-transparent gray


# --- Specific Tower Subclasses ---

# --- Specific Tower Subclasses ---
# Most subclasses might not need changes if they correctly use base class attributes
# that are updated by update_stats_from_level_data.
# We only need to ensure __init__ calls the base class correctly.

class ArcherTower(Tower):
    def __init__(self, pos, projectile_group, enemy_group, building_sound=None):
        super().__init__("Archer", pos, projectile_group, enemy_group, building_sound)
    # Uses the default shoot method

class CannonTower(Tower):
    def __init__(self, pos, projectile_group, enemy_group, building_sound=None):
        super().__init__("Cannon", pos, projectile_group, enemy_group, building_sound)
    # Uses the default shoot method (Projectile might need splash later)

class CrossbowTower(Tower):
    def __init__(self, pos, projectile_group, enemy_group, building_sound=None):
        super().__init__("Crossbow", pos, projectile_group, enemy_group, building_sound)
    # Uses the default shoot method

class IceWizardTower(Tower):
    def __init__(self, pos, projectile_group, enemy_group, building_sound=None):
        super().__init__("Ice Wizard", pos, projectile_group, enemy_group, building_sound)
        # slow_factor and slow_duration are now set in update_stats_from_level_data

    def create_projectile(self):
        """Creates an ice projectile that slows enemies."""
        projectile = Projectile(
            self.projectile_image,
            self.pos,
            self.target,
            self.damage,
            effect_type="slow",
            effect_params={'factor': self.slow_factor, 'duration': self.slow_duration}
        )
        self.projectile_group.add(projectile)

class LightningTower(Tower):
    def __init__(self, pos, projectile_group, enemy_group, building_sound=None):
        super().__init__("Lightning Wizard", pos, projectile_group, enemy_group, building_sound)
        # chain_targets and chain_range are now set in update_stats_from_level_data

    def create_projectile(self):
        """Creates a lightning projectile that chains to nearby enemies."""
        projectile = Projectile(
            self.projectile_image,
            self.pos,
            self.target,
            self.damage,
            effect_type="chain",
            effect_params={
                'max_targets': self.chain_targets,
                'chain_range': self.chain_range,
                'enemy_group': self.enemy_group
            }
        )
        self.projectile_group.add(projectile)

    # Optional: Override draw to show lightning effect?

class PoisonTower(Tower):
    def __init__(self, pos, projectile_group, enemy_group, building_sound=None):
        super().__init__("Poison Wizard", pos, projectile_group, enemy_group, building_sound)
        # dot_damage, poison_duration, poison_interval are now set in update_stats_from_level_data

    def create_projectile(self):
        """Creates a poison projectile that damages over time."""
        projectile = Projectile(
            self.projectile_image,
            self.pos,
            self.target,
            0,  # Poison tower might do 0 initial damage
            effect_type="poison",
            effect_params={
                'dot': self.dot_damage,
                'duration': self.poison_duration,
                'interval': self.poison_interval
            }
        )
        self.projectile_group.add(projectile)

# --- Helper Function to Create Towers ---
# This can be used in main.py to simplify tower creation
TOWER_CLASSES = {
    "Archer": ArcherTower,
    "Cannon": CannonTower,
    "Crossbow": CrossbowTower,
    "Ice Wizard": IceWizardTower,
    "Lightning Wizard": LightningTower, # Match config key
    "Poison Wizard": PoisonTower,   # Match config key
}

def create_tower(tower_type, pos, projectile_group, enemy_group, building_sound=None): # Added building_sound
    """Factory function to create a tower of the specified type."""
    if tower_type in TOWER_CLASSES:
        # Pass the building_sound to the constructor
        return TOWER_CLASSES[tower_type](pos, projectile_group, enemy_group, building_sound)
    else:
        print(f"Error: Unknown tower type '{tower_type}' requested.")
        return None # Or raise an error
