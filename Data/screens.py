# Data/screens.py
import pygame
import config
import languages
from languages import get_text

# --- Menu/Screen Drawing Helper Functions ---
def draw_menu_background(surface):
    """Draws a dark semi-transparent overlay for menus."""
    overlay = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    surface.blit(overlay, (0, 0))

def draw_main_menu(surface, fonts, button_rects):
    """Draws the main menu with Title, Start, Exit, and Language buttons."""
    draw_menu_background(surface)
    menu_font_large = fonts['large']
    menu_font_medium = fonts['medium']

    # Title
    title_text = menu_font_large.render(get_text("main_menu_title"), True, config.WHITE)
    title_rect = title_text.get_rect(center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 3))
    surface.blit(title_text, title_rect)

    # Start/Exit Buttons
    button_width = 200
    button_height = 50
    button_y_start = config.SCREEN_HEIGHT // 2
    button_spacing = 20

    # Start Button
    button_rects['start'] = pygame.Rect(
        (config.SCREEN_WIDTH - button_width) // 2, button_y_start, button_width, button_height
    )
    pygame.draw.rect(surface, config.UI_BUTTON_COLOR, button_rects['start'], border_radius=5)
    start_text = menu_font_medium.render(get_text("start_button"), True, config.WHITE)
    start_text_rect = start_text.get_rect(center=button_rects['start'].center)
    surface.blit(start_text, start_text_rect)

    # Settings Button (Now second)
    settings_button_y = button_rects['start'].bottom + button_spacing
    button_rects['settings'] = pygame.Rect(
        (config.SCREEN_WIDTH - button_width) // 2, settings_button_y, button_width, button_height
    )
    pygame.draw.rect(surface, config.UI_BUTTON_COLOR, button_rects['settings'], border_radius=5)
    settings_text = menu_font_medium.render(get_text("settings_button"), True, config.WHITE)
    settings_text_rect = settings_text.get_rect(center=button_rects['settings'].center)
    surface.blit(settings_text, settings_text_rect)

    # Exit Button (Now third)
    exit_button_y = button_rects['settings'].bottom + button_spacing
    button_rects['exit'] = pygame.Rect(
        (config.SCREEN_WIDTH - button_width) // 2, exit_button_y, button_width, button_height
    )
    pygame.draw.rect(surface, config.UI_BUTTON_COLOR, button_rects['exit'], border_radius=5)
    exit_text = menu_font_medium.render(get_text("exit_button"), True, config.WHITE)
    exit_text_rect = exit_text.get_rect(center=button_rects['exit'].center)
    surface.blit(exit_text, exit_text_rect)


    # Language Buttons
    lang_button_width = 50
    lang_button_height = 30
    lang_button_padding = 10
    lang_button_y = config.SCREEN_HEIGHT - lang_button_height - lang_button_padding

    # EN Button
    button_rects['lang_en'] = pygame.Rect(
        lang_button_padding, lang_button_y, lang_button_width, lang_button_height
    )
    en_color = config.UI_BUTTON_HOVER_COLOR if languages.current_language == 'EN' else config.UI_BUTTON_COLOR
    pygame.draw.rect(surface, en_color, button_rects['lang_en'], border_radius=3)
    en_text = menu_font_medium.render("EN", True, config.WHITE)
    en_text_rect = en_text.get_rect(center=button_rects['lang_en'].center)
    surface.blit(en_text, en_text_rect)

    # CZ Button
    button_rects['lang_cz'] = pygame.Rect(
        lang_button_padding * 2 + lang_button_width, lang_button_y, lang_button_width, lang_button_height
    )
    cz_color = config.UI_BUTTON_HOVER_COLOR if languages.current_language == 'CZ' else config.UI_BUTTON_COLOR
    pygame.draw.rect(surface, cz_color, button_rects['lang_cz'], border_radius=3)
    cz_text = menu_font_medium.render("CZ", True, config.WHITE)
    cz_text_rect = cz_text.get_rect(center=button_rects['lang_cz'].center)
    surface.blit(cz_text, cz_text_rect)

# --- Tutorial/Help Window ---
def draw_tutorial_window(surface, fonts, button_rects, game_state):
    """Draws the tutorial/help overlay with instructions and tower stats."""
    draw_menu_background(surface)

    # Fonts (Reduced sizes by 4 points)
    try:
        tut_font_large = pygame.font.SysFont(None, 50) 
        tut_font_medium = pygame.font.SysFont(None, 40) 
        tut_font_small = pygame.font.SysFont(None, 20) 
        tower_font = pygame.font.SysFont(None, 14)   
    except Exception as e:
        print(f"Could not load system font for tutorial: {e}. Using default pygame font.")
        # Fallback with reduced sizes
        tut_font_large = pygame.font.Font(None, 68)
        tut_font_medium = pygame.font.Font(None, 44)
        tut_font_small = pygame.font.Font(None, 20)
        tower_font = pygame.font.Font(None, 14)


    # Title
    title_text = tut_font_large.render(get_text("tutorial_title"), True, config.WHITE)
    title_rect = title_text.get_rect(centerx=(config.SCREEN_WIDTH // 2), top=2)
    surface.blit(title_text, title_rect)

    # Instructions
    instructions = [
        get_text("tut_line_1"), get_text("tut_line_2"),
        get_text("tut_line_3"), get_text("tut_line_4"),
    ]
    line_height = 22 # Adjusted line height for smaller font
    instr_start_y = title_rect.bottom + 15
    for i, line in enumerate(instructions):
        line_text = tut_font_small.render(line, True, config.WHITE) # Use smaller font
        line_rect = line_text.get_rect(centerx=config.SCREEN_WIDTH // 2, top=instr_start_y + i * line_height)
        surface.blit(line_text, line_rect)

    # Tower Information (Displayed in Columns)
    tower_info_start_y = instr_start_y + len(instructions) * line_height + 20
    tower_line_height = 14 # Adjusted line height for smaller font
    column_width = config.SCREEN_WIDTH // 2
    column_padding = 25
    current_column = 0
    max_towers_per_column = 3
    tower_count_in_column = 0
    item_width = column_width - 2 * column_padding
    image_size = 25
    current_x = column_padding + (column_width * current_column)
    current_y = tower_info_start_y
    max_y = tower_info_start_y # Track the lowest point reached by tower info

    for tower_name, data in config.TOWER_DATA.items():
        # Reset Y for new column if needed
        if tower_count_in_column >= max_towers_per_column:
            current_column += 1
            current_x = column_padding + (column_width * current_column)
            current_y = tower_info_start_y
            tower_count_in_column = 0

        # Image
        tower_image = config.TOWER_MENU_IMAGES.get(tower_name)
        text_start_x = current_x + image_size + 10 # Default start for text
        if tower_image:
             try:
                 scaled_img = pygame.transform.smoothscale(tower_image, (image_size, image_size))
                 img_rect = scaled_img.get_rect(left=current_x, top=current_y)
                 surface.blit(scaled_img, img_rect)
                 text_start_x = img_rect.right + 10
             except Exception as e:
                 print(f"Error scaling tutorial image for {tower_name}: {e}")
                 pygame.draw.rect(surface, config.RED, (current_x, current_y, image_size, image_size))
        else:
             pygame.draw.rect(surface, config.RED, (current_x, current_y, image_size, image_size))

        # Name (Translated)
        translation_key = f"tower_name_{tower_name.lower().replace(' ', '_')}"
        translated_name = get_text(translation_key)
        if f"<{translation_key}_missing>" in translated_name: translated_name = tower_name # Fallback
        name_text = tut_font_medium.render(translated_name, True, config.GOLD) # Use medium font for name
        name_rect = name_text.get_rect(left=text_start_x, top=current_y + (image_size - name_text.get_height()) // 2)
        surface.blit(name_text, name_rect)

        # Stats (Level 1)
        stats_y = current_y + image_size + 5
        try:
            level1 = data['levels'][0]
            cost = level1.get('cost', 'N/A')
            dmg = level1.get('damage', level1.get('damage_over_time', 'N/A'))
            rng = level1.get('range', 'N/A')
            rate = level1.get('fire_rate', 'N/A')
            effect_text = ""
            if 'slow_factor' in level1: effect_text = get_text("effect_slow")
            elif 'chain_targets' in level1: effect_text = get_text("effect_chain")
            elif 'damage_over_time' in level1: effect_text = get_text("effect_poison")

            stats_text = [
                f"{get_text('cost_label')}: {cost}", f"{get_text('damage_label')}: {dmg}",
                f"{get_text('range_label')}: {rng}", f"{get_text('rate_label')}: {rate}{get_text('rate_suffix')}",
            ]
            if effect_text: stats_text.append(f"{get_text('effect_label')}: {effect_text}")

        except (KeyError, IndexError, TypeError):
            print(f"Error getting level 1 stats for {tower_name} in tutorial.")
            stats_text = [get_text("stats_error")]

        # Draw Stats Lines
        for i, stat_line in enumerate(stats_text):
            stat_render = tower_font.render(stat_line, True, config.WHITE)
            stat_rect = stat_render.get_rect(left=text_start_x, top=stats_y + i * tower_line_height)
            surface.blit(stat_render, stat_rect)
            max_y = max(max_y, stat_rect.bottom) # Update max_y

        # Update y position for the next tower entry in the *same* column
        # We base this on the calculated height of the stats block for this tower
        current_y = stats_y + len(stats_text) * tower_line_height + 8 # Add padding
        max_y = max(max_y, current_y) # Ensure max_y considers padding too

        tower_count_in_column += 1

    # OK Button (Only shown in initial tutorial state, not help overlay)
    if game_state == "tutorial":
        button_width = 200; button_height = 50
        button_x = (config.SCREEN_WIDTH - button_width) // 2
        # Position button below the tower info content, with padding
        button_y = max_y + 20
        # Ensure button doesn't go off-screen if content is very tall
        button_y = min(button_y, config.SCREEN_HEIGHT - button_height - 10)

        button_rects['tutorial_ok'] = pygame.Rect(button_x, button_y, button_width, button_height)
        pygame.draw.rect(surface, config.UI_BUTTON_COLOR, button_rects['tutorial_ok'], border_radius=5)
        ok_text = tut_font_medium.render(get_text("tutorial_ok_button"), True, config.WHITE) # Use medium font for button
        ok_text_rect = ok_text.get_rect(center=button_rects['tutorial_ok'].center)
        surface.blit(ok_text, ok_text_rect)

# --- Pause Menu ---
def draw_pause_menu(surface, fonts, button_rects):
    """Draws the pause menu with Title, Restart, and Exit buttons."""
    draw_menu_background(surface)
    menu_font_large = fonts['large']
    menu_font_medium = fonts['medium']

    # Title
    title_text = menu_font_large.render(get_text("paused_title"), True, config.WHITE)
    title_rect = title_text.get_rect(center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 3))
    surface.blit(title_text, title_rect)

    # Buttons
    button_width = 200; button_height = 50
    button_y_start = config.SCREEN_HEIGHT // 2
    button_spacing = 20

    # Restart Button (uses 'start' key in button_rects for collision)
    button_rects['start'] = pygame.Rect(
        (config.SCREEN_WIDTH - button_width) // 2, button_y_start, button_width, button_height
    )
    pygame.draw.rect(surface, config.UI_BUTTON_COLOR, button_rects['start'], border_radius=5)
    restart_text = menu_font_medium.render(get_text("restart_button"), True, config.WHITE)
    restart_text_rect = restart_text.get_rect(center=button_rects['start'].center)
    surface.blit(restart_text, restart_text_rect)

    # Settings Button (Now second)
    settings_button_y = button_rects['start'].bottom + button_spacing
    button_rects['settings'] = pygame.Rect(
        (config.SCREEN_WIDTH - button_width) // 2, settings_button_y, button_width, button_height
    )
    pygame.draw.rect(surface, config.UI_BUTTON_COLOR, button_rects['settings'], border_radius=5)
    settings_text = menu_font_medium.render(get_text("settings_button"), True, config.WHITE)
    settings_text_rect = settings_text.get_rect(center=button_rects['settings'].center)
    surface.blit(settings_text, settings_text_rect)

    # Exit Button (Now third)
    exit_button_y = button_rects['settings'].bottom + button_spacing
    button_rects['exit'] = pygame.Rect(
        (config.SCREEN_WIDTH - button_width) // 2, exit_button_y, button_width, button_height
    )
    pygame.draw.rect(surface, config.UI_BUTTON_COLOR, button_rects['exit'], border_radius=5)
    exit_text = menu_font_medium.render(get_text("exit_button"), True, config.WHITE)
    exit_text_rect = exit_text.get_rect(center=button_rects['exit'].center)
    surface.blit(exit_text, exit_text_rect)

# --- Game Over Screen ---
def draw_game_over_screen(surface, fonts, button_rects, current_wave):
    """Draws the game over screen with message and Restart/Exit buttons."""
    draw_menu_background(surface)
    menu_font_large = fonts['large']
    menu_font_medium = fonts['medium']
    menu_font_small = fonts['small']

    # Title
    title_text = menu_font_large.render(get_text("game_over_title"), True, config.RED)
    title_rect = title_text.get_rect(center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 4))
    surface.blit(title_text, title_rect)

    # Message (Shows waves survived)
    waves_survived = max(0, current_wave -1)
    message_text = menu_font_small.render(get_text("game_over_message", waves_survived=waves_survived), True, config.WHITE)
    message_rect = message_text.get_rect(center=(config.SCREEN_WIDTH // 2, title_rect.bottom + 30))
    surface.blit(message_text, message_rect)

    # Buttons
    button_width = 200; button_height = 50
    button_y_start = config.SCREEN_HEIGHT // 2 + 30
    button_spacing = 20

    # Restart Button
    button_rects['game_over_restart'] = pygame.Rect(
        (config.SCREEN_WIDTH - button_width) // 2, button_y_start, button_width, button_height
    )
    pygame.draw.rect(surface, config.UI_BUTTON_COLOR, button_rects['game_over_restart'], border_radius=5)
    restart_text = menu_font_medium.render(get_text("restart_button"), True, config.WHITE)
    restart_text_rect = restart_text.get_rect(center=button_rects['game_over_restart'].center)
    surface.blit(restart_text, restart_text_rect)

    # Exit Button
    button_rects['game_over_exit'] = pygame.Rect(
        (config.SCREEN_WIDTH - button_width) // 2, button_y_start + button_height + button_spacing, button_width, button_height
    )
    pygame.draw.rect(surface, config.UI_BUTTON_COLOR, button_rects['game_over_exit'], border_radius=5)
    exit_text = menu_font_medium.render(get_text("exit_button"), True, config.WHITE)
    exit_text_rect = exit_text.get_rect(center=button_rects['game_over_exit'].center)
    surface.blit(exit_text, exit_text_rect)


# --- Settings Screen ---
# REMOVED event parameter. Drawing only, no event handling here.
def draw_settings_screen(surface, fonts, button_rects, config, button_sound, building_sound, music_volume, sfx_volume):
    """Draws the settings screen with separate volume controls and back button."""
    draw_menu_background(surface)
    menu_font_large = fonts['large']
    menu_font_medium = fonts['medium']
    menu_font_small = fonts['small']

    # --- Event handling logic removed from here ---
    # --- It's now handled in main.py's event loop ---

    # Title
    title_text = menu_font_large.render(get_text("settings_title"), True, config.WHITE)
    title_rect = title_text.get_rect(center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 4))
    surface.blit(title_text, title_rect)

    # --- Volume Controls ---
    volume_bar_width = 300
    volume_bar_height = 25 # Slightly thinner bars
    bar_spacing = 60 # Space between music and sfx bars
    volume_bar_x = (config.SCREEN_WIDTH - volume_bar_width) // 2
    handle_radius = 12 # Slightly larger handle

    # --- Music Volume ---
    music_label_text = menu_font_medium.render(get_text("volume_label_music"), True, config.WHITE)
    music_label_rect = music_label_text.get_rect(center=(config.SCREEN_WIDTH // 2, title_rect.bottom + 60))
    surface.blit(music_label_text, music_label_rect)

    music_bar_y = music_label_rect.bottom + 15
    music_bar_rect = pygame.Rect(volume_bar_x, music_bar_y, volume_bar_width, volume_bar_height)
    pygame.draw.rect(surface, (150, 150, 150), music_bar_rect, border_radius=5) # Background bar
    pygame.draw.rect(surface, config.WHITE, music_bar_rect, 2, border_radius=5) # Border

    # Music Volume Fill & Handle
    # Use passed music_volume parameter for drawing
    current_music_volume_width = int(volume_bar_width * music_volume)
    current_music_volume_rect = pygame.Rect(volume_bar_x, music_bar_y, current_music_volume_width, volume_bar_height)
    pygame.draw.rect(surface, config.GOLD, current_music_volume_rect, border_radius=5) # Fill
    # pygame.draw.rect(surface, config.WHITE, current_music_volume_rect, 2, border_radius=5) # Optional: Border for fill

    music_handle_x = volume_bar_x + current_music_volume_width
    music_handle_y = music_bar_y + volume_bar_height // 2
    pygame.draw.circle(surface, config.WHITE, (music_handle_x, music_handle_y), handle_radius) # Handle
    pygame.draw.circle(surface, config.GOLD, (music_handle_x, music_handle_y), handle_radius - 3) # Inner part

    button_rects['volume_bar_music'] = music_bar_rect # Store rect for interaction

    # Music Mute Button
    mute_button_width = 80
    mute_button_height = volume_bar_height
    mute_button_x = music_bar_rect.right + 15
    mute_button_y = music_bar_y
    button_rects['mute_music'] = pygame.Rect(mute_button_x, mute_button_y, mute_button_width, mute_button_height)
    mute_music_text_key = "unmute_button" if config.music_muted else "mute_button"
    mute_music_text = menu_font_small.render(get_text(mute_music_text_key), True, config.WHITE)
    mute_music_color = config.RED if config.music_muted else config.UI_BUTTON_COLOR
    pygame.draw.rect(surface, mute_music_color, button_rects['mute_music'], border_radius=5)
    mute_music_text_rect = mute_music_text.get_rect(center=button_rects['mute_music'].center)
    surface.blit(mute_music_text, mute_music_text_rect)


    # --- SFX Volume ---
    sfx_label_text = menu_font_medium.render(get_text("volume_label_sfx"), True, config.WHITE)
    sfx_label_rect = sfx_label_text.get_rect(center=(config.SCREEN_WIDTH // 2, music_bar_rect.bottom + 40))
    surface.blit(sfx_label_text, sfx_label_rect)

    sfx_bar_y = sfx_label_rect.bottom + 15
    sfx_bar_rect = pygame.Rect(volume_bar_x, sfx_bar_y, volume_bar_width, volume_bar_height)
    pygame.draw.rect(surface, (150, 150, 150), sfx_bar_rect, border_radius=5) # Background bar
    pygame.draw.rect(surface, config.WHITE, sfx_bar_rect, 2, border_radius=5) # Border

    # SFX Volume Fill & Handle
    # Use passed sfx_volume parameter for drawing
    current_sfx_volume_width = int(volume_bar_width * sfx_volume)
    current_sfx_volume_rect = pygame.Rect(volume_bar_x, sfx_bar_y, current_sfx_volume_width, volume_bar_height)
    pygame.draw.rect(surface, config.BLUE, current_sfx_volume_rect, border_radius=5) # Fill (use different color)
    # pygame.draw.rect(surface, config.WHITE, current_sfx_volume_rect, 2, border_radius=5) # Optional: Border for fill

    sfx_handle_x = volume_bar_x + current_sfx_volume_width
    sfx_handle_y = sfx_bar_y + volume_bar_height // 2
    pygame.draw.circle(surface, config.WHITE, (sfx_handle_x, sfx_handle_y), handle_radius) # Handle
    pygame.draw.circle(surface, config.BLUE, (sfx_handle_x, sfx_handle_y), handle_radius - 3) # Inner part

    button_rects['volume_bar_sfx'] = sfx_bar_rect # Store rect for interaction

    # SFX Mute Button
    # Position relative to the SFX bar, same X offset as music mute
    button_rects['mute_sfx'] = pygame.Rect(mute_button_x, sfx_bar_y, mute_button_width, mute_button_height)
    mute_sfx_text_key = "unmute_button" if config.sfx_muted else "mute_button"
    mute_sfx_text = menu_font_small.render(get_text(mute_sfx_text_key), True, config.WHITE)
    mute_sfx_color = config.RED if config.sfx_muted else config.UI_BUTTON_COLOR
    pygame.draw.rect(surface, mute_sfx_color, button_rects['mute_sfx'], border_radius=5)
    mute_sfx_text_rect = mute_sfx_text.get_rect(center=button_rects['mute_sfx'].center)
    surface.blit(mute_sfx_text, mute_sfx_text_rect)


    # Back Button
    button_width = 150; button_height = 50
    button_x = (config.SCREEN_WIDTH - button_width) // 2
    button_y = config.SCREEN_HEIGHT - button_height - 40 # Position near bottom
    button_rects['settings_back'] = pygame.Rect(button_x, button_y, button_width, button_height)
    pygame.draw.rect(surface, config.UI_BUTTON_COLOR, button_rects['settings_back'], border_radius=5)
    back_text = menu_font_medium.render(get_text("back_button"), True, config.WHITE)
    back_text_rect = back_text.get_rect(center=button_rects['settings_back'].center)
    surface.blit(back_text, back_text_rect)

# --- Victory Screen ---
def draw_victory_screen(surface, fonts, button_rects):
    """Draws the victory screen with message and Restart/Exit buttons."""
    draw_menu_background(surface)
    menu_font_large = fonts['large']
    menu_font_medium = fonts['medium']
    menu_font_small = fonts['small']

    # Title
    title_text = menu_font_large.render(get_text("victory_title"), True, config.GREEN)
    title_rect = title_text.get_rect(center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 4))
    surface.blit(title_text, title_rect)

    # Message
    message_text = menu_font_small.render(get_text("victory_message", max_waves=config.MAX_WAVES), True, config.WHITE)
    message_rect = message_text.get_rect(center=(config.SCREEN_WIDTH // 2, title_rect.bottom + 30))
    surface.blit(message_text, message_rect)

    # Buttons
    button_width = 200; button_height = 50
    button_y_start = config.SCREEN_HEIGHT // 2 + 30
    button_spacing = 20

    # Restart Button
    button_rects['victory_restart'] = pygame.Rect(
        (config.SCREEN_WIDTH - button_width) // 2, button_y_start, button_width, button_height
    )
    pygame.draw.rect(surface, config.UI_BUTTON_COLOR, button_rects['victory_restart'], border_radius=5)
    restart_text = menu_font_medium.render(get_text("restart_button"), True, config.WHITE)
    restart_text_rect = restart_text.get_rect(center=button_rects['victory_restart'].center)
    surface.blit(restart_text, restart_text_rect)

    # Exit Button
    button_rects['victory_exit'] = pygame.Rect(
        (config.SCREEN_WIDTH - button_width) // 2, button_y_start + button_height + button_spacing, button_width, button_height
    )
    pygame.draw.rect(surface, config.UI_BUTTON_COLOR, button_rects['victory_exit'], border_radius=5)
    exit_text = menu_font_medium.render(get_text("exit_button"), True, config.WHITE)
    exit_text_rect = exit_text.get_rect(center=button_rects['victory_exit'].center)
    surface.blit(exit_text, exit_text_rect)
