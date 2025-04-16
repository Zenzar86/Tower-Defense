import pygame
from config import TILE_SIZE # Import TILE_SIZE if needed

# --- Decoration Class ---
class Decoration(pygame.sprite.Sprite):
    def __init__(self, image, pos):
        super().__init__()
        self.image = image
        # Adjust rect placement based on image size and tile size if needed
        # Example: Place bottom-center of image at the center of the tile
        self.rect = self.image.get_rect(midbottom=(pos[0], pos[1] + TILE_SIZE // 2))

    def draw(self, surface):
        surface.blit(self.image, self.rect)