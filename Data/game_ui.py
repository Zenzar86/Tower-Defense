import pygame
import math
import config
import map # Import map module to access current_map_id
from languages import get_text

def draw_ui(surface, fonts, player_stats, game_state, current_wave, wave_ongoing, last_wave_end_time, wave_delay, button_rects):
    """Kreslí hlavní herní HUD (Zdraví, Zlato, Vlna, Časovač, Tlačítko nápovědy)."""
    ui_font = fonts['default']
    # Zdraví a Zlato
    health_label = get_text("health_label"); gold_label = get_text("gold_label")
    health_text = ui_font.render(f"{health_label}: {player_stats['health']}", True, config.RED)
    currency_text = ui_font.render(f"{gold_label}: {player_stats['currency']}", True, config.GOLD)
    surface.blit(health_text, (10, 10)); surface.blit(currency_text, (10, 40))
    # Zobrazení Vlny
    wave_label = get_text("wave_label")
    # Zobrazení Vlny - Upraveno pro zobrazení správného čísla vlny pro obě mapy
    wave_label = get_text("wave_label")
    # Pokud je mapa 2, odečtěte 10 od aktuální vlny pro zobrazení 1-10
    display_wave = current_wave - 10 if map.current_map_id == "Map_2" and current_wave > 10 else current_wave
    # Zobrazte celkový počet vln pro aktuální mapu (10 pro každou mapu)
    wave_number_text = ui_font.render(f"{wave_label}: {display_wave}/10", True, config.WHITE)
    wave_number_rect = wave_number_text.get_rect(topright=(config.SCREEN_WIDTH - 10, 10))
    surface.blit(wave_number_text, wave_number_rect)
    # Časovač pro další vlnu
    if game_state == "playing" and not wave_ongoing and current_wave < 10: # Fixed MAX_WAVES to 10 for check
        time_now = pygame.time.get_ticks()
        time_remaining = wave_delay - (time_now - last_wave_end_time)
        seconds_remaining = max(0, math.ceil(time_remaining / 1000))
        next_label = get_text("next_wave_label")
        timer_text_content = f"{next_label}: {seconds_remaining}s" if seconds_remaining > 0 else f"{next_label}: {get_text('next_wave_starting')}"
        timer_text = ui_font.render(timer_text_content, True, config.WHITE)
        timer_rect = timer_text.get_rect(topright=(config.SCREEN_WIDTH - 10, wave_number_rect.bottom + 5))
        surface.blit(timer_text, timer_rect)
    # Tlačítko nápovědy "?"
    help_font = fonts['small']
    help_text = help_font.render(get_text("help_button"), True, config.WHITE)
    help_text_rect = help_text.get_rect()
    help_button_padding = 5; help_button_size = help_text_rect.height + 2 * help_button_padding
    help_button_x = wave_number_rect.left - help_button_size - 5
    help_button_y = wave_number_rect.top + (wave_number_rect.height - help_button_size) // 2
    temp_help_button_rect = pygame.Rect(help_button_x, help_button_y, help_button_size, help_button_size)
    help_bg_surface = pygame.Surface((help_button_size, help_button_size), pygame.SRCALPHA)
    help_bg_surface.fill((80, 80, 100, 180))
    surface.blit(help_bg_surface, temp_help_button_rect.topleft)
    pygame.draw.rect(surface, config.UI_BORDER_COLOR, temp_help_button_rect, 1, border_radius=3)
    help_text_rect.center = temp_help_button_rect.center
    surface.blit(help_text, help_text_rect)
    button_rects['help'] = temp_help_button_rect # Uložení obdélníku

def draw_tower_menu(surface, fonts, selected_tower_type):
    """Kreslí menu pro výběr věží na spodní části obrazovky."""
    menu_font = fonts['small']
    # Použijte config pro výšku menu, pokud je k dispozici, jinak výchozí
    try: menu_height = config.MENU_HEIGHT
    except AttributeError: menu_height = 80

    menu_rect = pygame.Rect(0, config.SCREEN_HEIGHT - menu_height, config.SCREEN_WIDTH, menu_height)
    pygame.draw.rect(surface, (40, 40, 60), menu_rect)
    num_towers = len(config.TOWER_DATA)
    if num_towers == 0: return
    # Vypočítejte rozložení
    item_w=60; item_h=menu_height-10; space=15
    total_w = (item_w * num_towers) + (space * (num_towers - 1))
    start_x = (config.SCREEN_WIDTH - total_w) // 2; current_x = start_x
    for tower_name, data in config.TOWER_DATA.items():
        try: cost = data['levels'][0]['cost']
        except (KeyError, IndexError, TypeError): cost = 0;
        image = config.TOWER_MENU_IMAGES.get(tower_name)
        item_rect = pygame.Rect(current_x, config.SCREEN_HEIGHT - menu_height + 5, item_w, item_h)
       # Pozadí a Okraj
        bg_color = (70, 70, 90); border_color = (150, 150, 180)
        if selected_tower_type == tower_name: border_color = config.GOLD
        pygame.draw.rect(surface, bg_color, item_rect, border_radius=5)
        pygame.draw.rect(surface, border_color, item_rect, 2, border_radius=5)
        # Obrázek
        if image:
            img_rect = image.get_rect(centerx=item_rect.centerx, top=item_rect.top + 5)
            surface.blit(image, img_rect)
        else: 
            pygame.draw.rect(surface, config.RED, (item_rect.left + 5, item_rect.top + 5, item_w - 10, item_h // 2 - 10))
        # Text ceny
        cost_text = menu_font.render(f"{cost}", True, config.GOLD)
        cost_rect = cost_text.get_rect(centerx=item_rect.centerx, bottom=item_rect.bottom - 5)
        surface.blit(cost_text, cost_rect)
        current_x += item_w + space
