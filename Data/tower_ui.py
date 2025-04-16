# Data/tower_ui.py
import pygame
import config
from languages import get_text

def draw_tower_upgrade_ui(surface, selected_tower, fonts, button_rects):
    """Draws the upgrade/sell UI panel for the selected tower."""
    if not selected_tower:
        button_rects['upgrade'] = None # Reset rects when no tower is selected
        button_rects['sell'] = None
        return

    # UI Panel Configuration
    panel_width = 150
    panel_height = 100
    panel_padding = 10
    button_height = 25
    button_width = panel_width - 2 * panel_padding
    font_small = fonts['small'] # Expecting fonts dict
    font_medium = fonts['medium']

    # Position Panel (tries above tower first, clamps to screen)
    panel_x = selected_tower.rect.centerx - panel_width // 2
    panel_y = selected_tower.rect.top - panel_height - 5

    # Clamp position
    panel_x = max(0, min(panel_x, config.SCREEN_WIDTH - panel_width))
    # Assuming menu_height is accessible via config or passed in if needed
    # If MENU_HEIGHT is not in config, this will need adjustment
    try:
        menu_h = config.MENU_HEIGHT
    except AttributeError:
        menu_h = 80 # Fallback if not defined in config
    panel_y = max(0, min(panel_y, config.SCREEN_HEIGHT - panel_height - menu_h))


    # Draw Background
    panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
    try: # Use semi-transparent if possible
        bg_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        bg_surface.fill(config.UI_BG_COLOR)
        surface.blit(bg_surface, panel_rect.topleft)
    except (NameError, AttributeError): # Fallback if UI_BG_COLOR not defined or SRCALPHA fails
         pygame.draw.rect(surface, (60, 60, 80), panel_rect) # Solid fallback
    pygame.draw.rect(surface, config.UI_BORDER_COLOR, panel_rect, 1) # Border

    # Display Tower Info
    y_offset = panel_padding

    # Tower Name & Level
    level_label = get_text("tower_level_label")
    # Translate tower name
    tower_name_key = f"tower_name_{selected_tower.tower_type_name.lower().replace(' ', '_')}"
    translated_tower_name = get_text(tower_name_key)
    if f"<{tower_name_key}_missing>" in translated_tower_name: # Fallback if translation missing
        translated_tower_name = selected_tower.tower_type_name
    tower_info_text = f"{translated_tower_name} ({level_label} {selected_tower.level})"
    info_render = font_small.render(tower_info_text, True, config.WHITE) # Changed to font_small
    info_rect = info_render.get_rect(centerx=panel_rect.centerx, top=panel_rect.top + y_offset)
    surface.blit(info_render, info_rect)
    y_offset += info_rect.height + 5

    # Upgrade Button & Text
    upgrade_cost = selected_tower.get_upgrade_cost()
    upgrade_possible = upgrade_cost > 0

    upgrade_text = get_text("max_level_button") # Default text if max level
    upgrade_color = (100, 100, 100) # Greyed out color
    if upgrade_possible:
        upgrade_text = f"{get_text('upgrade_button')} ({upgrade_cost} G)"
        upgrade_color = config.UI_UPGRADE_COLOR

    button_rects['upgrade'] = pygame.Rect(panel_x + panel_padding, panel_rect.top + y_offset, button_width, button_height)
    pygame.draw.rect(surface, upgrade_color, button_rects['upgrade'], border_radius=3)
    upgrade_render = font_small.render(upgrade_text, True, config.WHITE)
    upgrade_text_rect = upgrade_render.get_rect(center=button_rects['upgrade'].center)
    surface.blit(upgrade_render, upgrade_text_rect)
    y_offset += button_height + 5

    # Sell Button & Text
    sell_price = selected_tower.get_sell_price()
    sell_text = f"{get_text('sell_button')} ({sell_price} G)"
    sell_color = config.UI_SELL_COLOR

    button_rects['sell'] = pygame.Rect(panel_x + panel_padding, panel_rect.top + y_offset, button_width, button_height)
    pygame.draw.rect(surface, sell_color, button_rects['sell'], border_radius=3)
    sell_render = font_small.render(sell_text, True, config.WHITE)
    sell_text_rect = sell_render.get_rect(center=button_rects['sell'].center)
    surface.blit(sell_render, sell_text_rect)