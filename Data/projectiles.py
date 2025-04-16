import pygame
import math 
from pygame.math import Vector2

# --- Třída Projektil ---
class Projectile(pygame.sprite.Sprite):
    def __init__(self, image, start_pos, target_enemy, damage, speed=5, effect_type=None, effect_params=None):
        super().__init__()
        self.image = image
        if not self.image: 
            self.image = pygame.Surface((10, 10))
            self.image.fill((255, 255, 0)) 
        self.rect = self.image.get_rect(center=start_pos)
        self.pos = Vector2(start_pos)
        self.speed = speed
        self.target = target_enemy 
        self.damage = damage 
        self.effect_type = effect_type
        self.effect_params = effect_params if effect_params else {} 

        # Uložení skupiny nepřátel, pokud je poskytnuta (potřebné pro řetězový efekt)
        self.enemy_group = self.effect_params.get('enemy_group', None)

    def apply_hit(self):
        if not self.target or not self.target.alive():
            return 

        # 1. Aplikovat přímé poškození
        if hasattr(self.target, 'take_damage'):
            self.target.take_damage(self.damage)
        else:
            print(f"Varování: Cíl {self.target} postrádá metodu 'take_damage'.")

        # 2. Aplikovat efekty na základě typu
        if self.effect_type == "slow":
            if hasattr(self.target, 'apply_slow'):
                factor = self.effect_params.get('factor', 0.5)
                duration = self.effect_params.get('duration', 2.0)
                self.target.apply_slow(factor, duration * 1000) 
            else:
                pass

        elif self.effect_type == "poison":
            if hasattr(self.target, 'apply_poison'):
                dot = self.effect_params.get('dot', 1)
                duration = self.effect_params.get('duration', 5.0)
                interval = self.effect_params.get('interval', 0.5)
                self.target.apply_poison(dot, duration * 1000, interval * 1000) 
            else:
                pass

        elif self.effect_type == "chain":
            self.apply_chain_lightning()

        # Zničit projektil po aplikaci zásahu a efektů
        self.kill()

    def apply_chain_lightning(self):
        if not self.enemy_group:
            return

        max_targets = self.effect_params.get('max_targets', 3)
        chain_range_sq = self.effect_params.get('chain_range', 75) ** 2 
        chain_damage = self.damage 

        hit_enemies = {self.target} 
        current_target = self.target
        targets_hit = 1 

        while targets_hit < max_targets:
            closest_unchained_enemy = None
            min_dist_sq = chain_range_sq + 1 

            for enemy in self.enemy_group:
                if enemy.alive() and enemy not in hit_enemies:
                    if hasattr(current_target, 'pos') and hasattr(enemy, 'pos'):
                        dist_sq = current_target.pos.distance_squared_to(enemy.pos)
                        if dist_sq < min_dist_sq:
                            min_dist_sq = dist_sq
                            closest_unchained_enemy = enemy
                    else:
                        pass

            if closest_unchained_enemy and min_dist_sq <= chain_range_sq:
                # Nalezen platný cíl pro řetěz
                if hasattr(closest_unchained_enemy, 'take_damage'):
                    closest_unchained_enemy.take_damage(chain_damage)
                    # TODO: 
                else: 
                    pass

                hit_enemies.add(closest_unchained_enemy)
                current_target = closest_unchained_enemy 
                targets_hit += 1
            else:
                break 

    def update(self):
        if not self.target or not self.target.alive(): # Zkontrolujte, zda cíl stále existuje a je naživu
            self.kill() 
            return

        # Pohyb směrem k aktuální pozici cíle
        if hasattr(self.target, 'pos'): 
            target_pos = self.target.pos
            move_vector = target_pos - self.pos
            distance = move_vector.length()

            if distance < self.speed:
                # Dostatečně blízko k zásahu - aplikovat poškození a efekty
                self.apply_hit() 
            else:
                # Pohyb projektilu
                if distance > 0: # Vyhněte se dělení nulou
                    try:
                        move_vector.scale_to_length(self.speed)
                    except ValueError: # Zpracování případu nulového vektoru, pokud k němu dojde
                        move_vector = Vector2(0, 0) # Nebo zpracovat vhodně
                self.pos += move_vector
                self.rect.center = self.pos
        else:
            self.kill()

    def draw(self, surface):
         surface.blit(self.image, self.rect)