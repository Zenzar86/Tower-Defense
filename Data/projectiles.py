import pygame
import math # Needed for distance calculation in chain effect
from pygame.math import Vector2

# --- Projectile Class ---
class Projectile(pygame.sprite.Sprite):
    def __init__(self, image, start_pos, target_enemy, damage, speed=5, effect_type=None, effect_params=None):
        super().__init__()
        self.image = image
        if not self.image: # Fallback if image loading failed in Tower
            self.image = pygame.Surface((10, 10))
            self.image.fill((255, 255, 0)) # Yellow fallback
        self.rect = self.image.get_rect(center=start_pos)
        self.pos = Vector2(start_pos)
        self.speed = speed
        self.target = target_enemy # Store the target enemy object
        self.damage = damage # Damage dealt on impact
        self.effect_type = effect_type
        self.effect_params = effect_params if effect_params else {} # Ensure it's a dict

        # Store enemy group if provided (needed for chain effect)
        self.enemy_group = self.effect_params.get('enemy_group', None)


    def apply_hit(self):
        """Applies damage and effects to the target upon impact."""
        if not self.target or not self.target.alive():
            return # Target already gone

        # 1. Apply direct damage
        if hasattr(self.target, 'take_damage'):
            self.target.take_damage(self.damage)
        else:
            print(f"Warning: Target {self.target} missing 'take_damage' method.")

        # 2. Apply effects based on type
        if self.effect_type == "slow":
            if hasattr(self.target, 'apply_slow'):
                factor = self.effect_params.get('factor', 0.5)
                duration = self.effect_params.get('duration', 2.0)
                self.target.apply_slow(factor, duration * 1000) # Convert duration to ms
            else:
                print(f"Warning: Target {self.target} missing 'apply_slow' method.")

        elif self.effect_type == "poison":
            if hasattr(self.target, 'apply_poison'):
                dot = self.effect_params.get('dot', 1)
                duration = self.effect_params.get('duration', 5.0)
                interval = self.effect_params.get('interval', 0.5)
                self.target.apply_poison(dot, duration * 1000, interval * 1000) # Convert to ms
            else:
                print(f"Warning: Target {self.target} missing 'apply_poison' method.")

        elif self.effect_type == "chain":
            self.apply_chain_lightning()

        # Kill the projectile after applying hit and effects
        self.kill()

    def apply_chain_lightning(self):
        """Handles the chain lightning effect."""
        if not self.enemy_group:
            print("Warning: Chain lightning effect requires 'enemy_group' in effect_params.")
            return

        max_targets = self.effect_params.get('max_targets', 3)
        chain_range_sq = self.effect_params.get('chain_range', 75) ** 2 # Use squared range
        chain_damage = self.damage # Or maybe reduced damage: self.damage * 0.75

        hit_enemies = {self.target} # Start with the initial target
        current_target = self.target
        targets_hit = 1 # Initial target counts as 1

        while targets_hit < max_targets:
            closest_unchained_enemy = None
            min_dist_sq = chain_range_sq + 1 # Start above range

            # Find the nearest *unchained* enemy to the *current* target
            for enemy in self.enemy_group:
                if enemy.alive() and enemy not in hit_enemies:
                    # Ensure both current_target and enemy have 'pos'
                    if hasattr(current_target, 'pos') and hasattr(enemy, 'pos'):
                        dist_sq = current_target.pos.distance_squared_to(enemy.pos)
                        if dist_sq < min_dist_sq:
                            min_dist_sq = dist_sq
                            closest_unchained_enemy = enemy
                    else:
                        print(f"Warning: Missing 'pos' attribute for chain lightning calculation.")


            if closest_unchained_enemy and min_dist_sq <= chain_range_sq:
                # Found a valid chain target
                if hasattr(closest_unchained_enemy, 'take_damage'):
                    closest_unchained_enemy.take_damage(chain_damage)
                    # TODO: Add visual effect for chain lightning jump
                else:
                     print(f"Warning: Chain target {closest_unchained_enemy} missing 'take_damage'.")

                hit_enemies.add(closest_unchained_enemy)
                current_target = closest_unchained_enemy # Next chain originates from this new target
                targets_hit += 1
            else:
                break # No more valid chain targets found

    def update(self):
        if not self.target or not self.target.alive(): # Check if target still exists and is alive
            self.kill() # Remove projectile if target is gone
            return

        # Move towards the target's current position
        if hasattr(self.target, 'pos'): # Use vector position for movement
            target_pos = self.target.pos
            move_vector = target_pos - self.pos
            distance = move_vector.length()

            if distance < self.speed:
                # Close enough to hit - apply damage and effects
                self.apply_hit() # Use the new method
            else:
                # Move projectile
                if distance > 0: # Avoid division by zero
                    try:
                        move_vector.scale_to_length(self.speed)
                    except ValueError: # Handle zero vector case if it occurs
                         move_vector = Vector2(0,0) # Or handle appropriately
                self.pos += move_vector
                self.rect.center = self.pos
        else:
            print(f"Warning: Target {self.target} missing 'pos' attribute.")
            self.kill() # Remove projectile if target is invalid

    def draw(self, surface):
         surface.blit(self.image, self.rect)