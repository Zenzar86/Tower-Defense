import pygame
import config
from languages import get_text

def draw_tower_upgrade_ui(surface, selected_tower, fonts, button_rects):
    if not selected_tower:
        button_rects['upgrade'] = None 
        button_rects['sell'] = None
        return

    # Konfigurace UI panelu
    panel_width = 150
    panel_height = 100
    panel_padding = 10
    button_height = 25
    button_width = panel_width - 2 * panel_padding
    font_small = fonts['small'] 
    font_medium = fonts['medium']

    # Umístění panelu 
    panel_x = selected_tower.rect.centerx - panel_width // 2
    panel_y = selected_tower.rect.top - panel_height - 5

    # Omezit pozici
    panel_x = max(0, min(panel_x, config.SCREEN_WIDTH - panel_width))
    try:
        menu_h = config.MENU_HEIGHT
    except AttributeError:
        menu_h = 80 
    panel_y = max(0, min(panel_y, config.SCREEN_HEIGHT - panel_height - menu_h))

    # Kreslení pozadí
    panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
    try: 
        bg_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        bg_surface.fill(config.UI_BG_COLOR)
        surface.blit(bg_surface, panel_rect.topleft)
    except (NameError, AttributeError): 
         pygame.draw.rect(surface, (60, 60, 80), panel_rect) 
    pygame.draw.rect(surface, config.UI_BORDER_COLOR, panel_rect, 1) 

    # Zobrazení informací o věži
    y_offset = panel_padding

    # Název věže a úroveň
    level_label = get_text("tower_level_label")
    # Přeložit název věže
    tower_name_key = f"tower_name_{selected_tower.tower_type_name.lower().replace(' ', '_')}"
    translated_tower_name = get_text(tower_name_key)
    if f"<{tower_name_key}_missing>" in translated_tower_name: 
        translated_tower_name = selected_tower.tower_type_name
    tower_info_text = f"{translated_tower_name} ({level_label} {selected_tower.level})"
    info_render = font_small.render(tower_info_text, True, config.WHITE) 
    info_rect = info_render.get_rect(centerx=panel_rect.centerx, top=panel_rect.top + y_offset)
    surface.blit(info_render, info_rect)
    y_offset += info_rect.height + 5

    # Tlačítko pro vylepšení a text
    upgrade_cost = selected_tower.get_upgrade_cost()
    upgrade_possible = upgrade_cost > 0

    upgrade_text = get_text("max_level_button") 
    upgrade_color = (100, 100, 100) 
    if upgrade_possible:
        upgrade_text = f"{get_text('upgrade_button')} ({upgrade_cost} G)"
        upgrade_color = config.UI_UPGRADE_COLOR

    button_rects['upgrade'] = pygame.Rect(panel_x + panel_padding, panel_rect.top + y_offset, button_width, button_height)
    pygame.draw.rect(surface, upgrade_color, button_rects['upgrade'], border_radius=3)
    upgrade_render = font_small.render(upgrade_text, True, config.WHITE)
    upgrade_text_rect = upgrade_render.get_rect(center=button_rects['upgrade'].center)
    surface.blit(upgrade_render, upgrade_text_rect)
    y_offset += button_height + 5

    # Tlačítko pro prodej a text
    sell_price = selected_tower.get_sell_price()
    sell_text = f"{get_text('sell_button')} ({sell_price} G)"
    sell_color = config.UI_SELL_COLOR

    button_rects['sell'] = pygame.Rect(panel_x + panel_padding, panel_rect.top + y_offset, button_width, button_height)
    pygame.draw.rect(surface, sell_color, button_rects['sell'], border_radius=3)
    sell_render = font_small.render(sell_text, True, config.WHITE)
    sell_text_rect = sell_render.get_rect(center=button_rects['sell'].center)
    surface.blit(sell_render, sell_text_rect)