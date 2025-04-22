import pygame
import math
import os 
from pygame.math import Vector2
from config import TILE_SIZE, TOWER_DATA, TOWER_SELL_PERCENTAGE, load_image, RED 
from projectiles import Projectile 
from languages import get_text 

# --- Základní třída věže ---
class Tower(pygame.sprite.Sprite):
    def __init__(self, tower_type_name, pos, projectile_group, enemy_group, building_sound=None): 
        super().__init__()
        self.tower_type_name = tower_type_name 
        self.level = 1 
        self.projectile_group = projectile_group
        self.enemy_group = enemy_group
        self.pos = Vector2(pos)
        self.building_sound = building_sound

        # Získání počátečních dat pro úroveň 1
        self.config_data = TOWER_DATA[self.tower_type_name]
        level_data = self.get_current_level_data()
        if not level_data:
             raise ValueError(f"Nepodařilo se najít data pro úroveň 1 pro typ věže {self.tower_type_name}")

        self.total_cost_invested = level_data.get('cost', 0) 

        # --- Načtení základního obrázku ---
        base_image_path = self.config_data.get('image_path')
        level_image_path = level_data.get('image_path', base_image_path) 

        loaded_image = load_image(level_image_path) if level_image_path else None
        if loaded_image:
            # Scale the image by 2x
            original_width, original_height = loaded_image.get_size()
            new_size = (original_width * 2, original_height * 2)
            self.image = pygame.transform.scale(loaded_image, new_size)
        else:
            # Fallback if image loading fails
            # Create a fallback surface, scaled by 2x for consistency
            fallback_size = (TILE_SIZE * 2, TILE_SIZE * 2)
            self.image = pygame.Surface(fallback_size)
            self.image.fill(RED)

        # --- Načtení obrázku projektilu ---
        base_projectile_path = self.config_data.get('projectile_path')
        level_projectile_path = level_data.get('projectile_path', base_projectile_path)

        self.projectile_image = load_image(level_projectile_path) if level_projectile_path else None
        if not self.projectile_image:
            self.projectile_image = pygame.Surface((10, 10))
            self.projectile_image.fill((0, 0, 255))

        # Vytvoření rect na základě velikosti obrázku, ale s centrem na pozici dlaždice
        self.rect = self.image.get_rect(center=self.pos)
        self.target = None
        self.last_shot_time = pygame.time.get_ticks() 

        # --- Nastavení počátečních statistik z dat úrovně 1 ---
        self.update_stats_from_level_data(level_data)

        # --- Načtení zvuku střelby ---
        self.fire_sound = None
        sound_path = self.config_data.get('sound_path')
        if sound_path:
                import config as cfg
                abs_sound_path = cfg.get_resource_path(sound_path)
                self.fire_sound = pygame.mixer.Sound(abs_sound_path)

        self.last_shot_time -= self.cooldown

    def get_current_level_data(self):
        try:
            return self.config_data['levels'][self.level - 1]
        except (IndexError, KeyError):
            return None

    def update_stats_from_level_data(self, level_data):
        if not level_data:
            return

        self.range = level_data.get('range', 100)
        self.fire_rate = level_data.get('fire_rate', 1.0)
        self.cooldown = 1000 / self.fire_rate if self.fire_rate > 0 else float('inf')
        self.damage = level_data.get('damage', 0)

        # Aktualizace parametrů speciálních efektů, pokud existují pro tento typ věže
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

        # Aktualizace obrázku, pokud existuje obrázek specifický pro úroveň
        level_image_path = level_data.get('image_path', self.config_data.get('image_path'))
        if level_image_path:
            loaded_image = load_image(level_image_path)
            if loaded_image:
                old_center = self.rect.center
                # Scale the new level image by 2x
                original_width, original_height = loaded_image.get_size()
                new_size = (original_width * 2, original_height * 2)
                self.image = pygame.transform.scale(loaded_image, new_size)
                # Adjust the vertical position by -2 pixels after upgrade
                self.rect = self.image.get_rect(center=(old_center[0], old_center[1] - 2)) # Update rect

    def get_upgrade_cost(self):
        current_level_data = self.get_current_level_data()
        if current_level_data:
            return current_level_data.get('upgrade_cost', 0)
        return 0 

    def get_sell_price(self):
        return int(self.total_cost_invested * TOWER_SELL_PERCENTAGE)

    def upgrade(self, player_stats):
        upgrade_cost = self.get_upgrade_cost()

              # Zkontrolovat, zda je již na max úrovni
        if upgrade_cost <= 0:
            return False

        # Zkontrolovat měnu
        if player_stats['currency'] < upgrade_cost:
            return False

        # Zkontrolovat, zda existují data pro další úroveň
        next_level_index = self.level 
        if next_level_index >= len(self.config_data['levels']):
             return False 

        # --- Pokračovat s vylepšením ---
        player_stats['currency'] -= upgrade_cost
        self.total_cost_invested += upgrade_cost
        self.level += 1

        # Aktualizovat statistiky na novou úroveň
        new_level_data = self.get_current_level_data()
        self.update_stats_from_level_data(new_level_data)

        # Přehrát zvuk při úspěšném vylepšení
        if self.building_sound:
            self.building_sound.play()

        return True

    def find_target(self):
        closest_enemy = None
        min_dist_sq = self.range ** 2 

        for enemy in self.enemy_group:
            if hasattr(enemy, 'pos') and enemy.alive(): 
                distance_sq = self.pos.distance_squared_to(enemy.pos)
                if distance_sq < min_dist_sq:
                    min_dist_sq = distance_sq
                    closest_enemy = enemy

        self.target = closest_enemy 

    def shoot(self, current_time):
        """Střílí na cíl, pokud je vypršena doba čekání."""
        if self.target and (current_time - self.last_shot_time >= self.cooldown):
            self.create_projectile() 
            self.last_shot_time = current_time

            import config as cfg
            if self.fire_sound and not cfg.sfx_muted:
                self.fire_sound.set_volume(cfg.sfx_volume) 
                self.fire_sound.play()
            return True
        return False

    def create_projectile(self):
        # Výchozí vytvoření projektilu (standardní poškození)
        projectile = Projectile(
            self.projectile_image,
            self.pos,
            self.target,
            self.damage
        )
        self.projectile_group.add(projectile)

    def update(self, current_time): 
        self.find_target()
        self.shoot(current_time)

    def draw(self, surface):
        surface.blit(self.image, self.rect)


# --- Specifické podtřídy věží ---

class ArcherTower(Tower):
    def __init__(self, pos, projectile_group, enemy_group, building_sound=None):
        super().__init__("Archer", pos, projectile_group, enemy_group, building_sound)

class CannonTower(Tower):
    def __init__(self, pos, projectile_group, enemy_group, building_sound=None):
        super().__init__("Cannon", pos, projectile_group, enemy_group, building_sound)

class CrossbowTower(Tower):
    def __init__(self, pos, projectile_group, enemy_group, building_sound=None):
        super().__init__("Crossbow", pos, projectile_group, enemy_group, building_sound)

class IceWizardTower(Tower):
    def __init__(self, pos, projectile_group, enemy_group, building_sound=None):
        super().__init__("Ice Wizard", pos, projectile_group, enemy_group, building_sound)

    def create_projectile(self):
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

    def create_projectile(self):
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


class PoisonTower(Tower):
    def __init__(self, pos, projectile_group, enemy_group, building_sound=None):
        super().__init__("Poison Wizard", pos, projectile_group, enemy_group, building_sound)

    def create_projectile(self):
        projectile = Projectile(
            self.projectile_image,
            self.pos,
            self.target,
            0, 
            effect_type="poison",
            effect_params={
                'dot': self.dot_damage,
                'duration': self.poison_duration,
                'interval': self.poison_interval
            }
        )
        self.projectile_group.add(projectile)

# --- Pomocná funkce ---
TOWER_CLASSES = {
    "Archer": ArcherTower,
    "Cannon": CannonTower,
    "Crossbow": CrossbowTower,
    "Ice Wizard": IceWizardTower,
    "Lightning Wizard": LightningTower, 
    "Poison Wizard": PoisonTower,  
}

def create_tower(tower_type, pos, projectile_group, enemy_group, building_sound=None): 
    """Factory function to create a tower of the specified type."""
    if tower_type in TOWER_CLASSES:
        return TOWER_CLASSES[tower_type](pos, projectile_group, enemy_group, building_sound)
    else:
        return None 
