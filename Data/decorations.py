import pygame
from config import TILE_SIZE 

# --- Dekorace ---
class Decoration(pygame.sprite.Sprite):
    def __init__(self, image, pos):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(midbottom=(pos[0], pos[1] + TILE_SIZE // 2))

    def draw(self, surface):
        surface.blit(self.image, self.rect)