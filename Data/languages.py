# -*- coding: utf-8 -*-

# Language data for the game
# Using simple keys for easy access

LANGUAGES = {
    'EN': {
        # Menu Titles
        "main_menu_title": "Tower Defense",
        "paused_title": "Paused",
        "tutorial_title": "How to Play",
        "game_over_title": "Game Over - You Lost!",
        "victory_title": "Victory! - You Won!",
        "settings_title": "Settings",

        # Button Labels
        "start_button": "Start",
        "exit_button": "Exit",
        "restart_button": "Restart",
        "tutorial_ok_button": "Ok, Lets Start",
        "upgrade_button": "Upgrade",
        "max_level_button": "Max Level",
        "sell_button": "Sell",
        "help_button": "?", # Keep simple for button size
        "settings_button": "Settings",
        "back_button": "Back",
        "mute_button": "Mute",     # New key
        "unmute_button": "Unmute", # New key

        # UI Labels
        "health_label": "Health",
        "gold_label": "Gold",
        "wave_label": "Wave",
        "next_wave_label": "Next",
        "next_wave_starting": "Starting...",
        "tower_level_label": "Lvl",
        "volume_label_music": "Music Volume:", # New key
        "volume_label_sfx": "SFX Volume:",     # New key

        # Tutorial Instructions
        "tut_line_1": "Enemies follow the path. Build towers on platforms to stop them.",
        "tut_line_2": "Click tower icons below to select, then click a platform to build.",
        "tut_line_3": "Click placed towers to Upgrade/Sell. Earn gold by defeating enemies.",
        "tut_line_4": "Survive all waves to win! Press '?' during game for this help.",

        # Tower Info Labels (in tutorial)
        "cost_label": "Cost",
        "damage_label": "Dmg",
        "range_label": "Range",
        "rate_label": "Rate",
        "effect_label": "Effect",
        "effect_slow": "Slow",
        "effect_poison": "Poison",
        "effect_chain": "Chain damage",
        "stats_error": "Error: Stats missing",
        "rate_suffix": "/s", # Suffix for fire rate

        # Tower Names (for Tutorial/Help)
        "tower_name_archer": "Archer",
        "tower_name_cannon": "Cannon",
        "tower_name_crossbow": "Crossbow",
        "tower_name_ice_wizard": "Ice Wizard",
        "tower_name_lightning_wizard": "Lightning Wizard", # Assuming name consistency
        "tower_name_poison_wizard": "Poison Wizard",

        # Other Messages
        "paused_message": "Game Paused",
        "resumed_message": "Game Resumed",
        "starting_message": "Starting New Game...",
        "restarting_message": "Restarting Game...",
        "showing_tutorial": "Showing Tutorial...",
        "tutorial_finished": "Tutorial finished. Starting New Game...",
        "wave_starting": "Wave {current_wave} starting! Enemies: {enemies_def}",
        "wave_completed": "Wave {current_wave} completed!",
        "wave_no_definition": "Wave {current_wave} has no definition.",
        "tower_placed": "Placed {tower_type} tower (Level 1) at ({grid_x}, {grid_y}) for {cost} gold. Marked tile as occupied.",
        "tower_selected": "Selected existing tower: {tower_type} at {pos}",
        "tower_upgraded": "Upgraded {tower_type} to Level {level} for {cost} gold.",
        "tower_max_level": "{tower_type} is already at max level.",
        "tower_sell": "Selling {tower_type} for {price} gold.",
        "platform_restored": "Restored platform at ({grid_x}, {grid_y})",
        "cannot_build_occupied": "Cannot build: Tower already exists at ({grid_x}, {grid_y}).",
        "cannot_build_invalid_tile": "Cannot build: Location ({grid_x}, {grid_y}) is not a buildable platform or out of bounds.",
        "cannot_build_no_gold": "Cannot build {tower_type}: Not enough gold (Need {cost}, Have {have})",
        "cannot_upgrade_no_gold": "Not enough gold to upgrade {tower_type}. Need {cost}, Have {have}.",
        "error_create_tower": "ERROR: Failed to create tower of type {tower_type}",
        "error_cost_missing": "ERROR: Could not find level 1 cost for tower type {tower_type}. Cannot build.",
        "warning_tile_not_occupied": "Warning: Tile at ({grid_x}, {grid_y}) was not type 3 when selling.",
        "warning_invalid_coords_sell": "Warning: Invalid grid coords ({grid_x}, {grid_y}) when selling tower.",
        "boss_scaling_applied": "Applying special scaling for Wave 10 Demon Boss!",

        # Game End Messages
        "game_over_message": "You survived {waves_survived} waves, but the enemies broke through!",
        "victory_message": "Congratulations! You defended the castle against all {max_waves} waves!",
    },
    'CZ': {
        # Menu Titles
        "main_menu_title": "Tower Defense",
        "paused_title": "Pozastaveno",
        "tutorial_title": "Jak Hrát",
        "game_over_title": "Konec Hry - Prohrál Jsi!",
        "victory_title": "Vítězství!",
        "settings_title": "Nastavení",

        # Button Labels
        "start_button": "Začít",
        "exit_button": "Konec",
        "restart_button": "Restart",
        "tutorial_ok_button": "Ok, Začít",
        "upgrade_button": "Vylepšit",
        "max_level_button": "Max Úroveň",
        "sell_button": "Prodat",
        "help_button": "?",
        "settings_button": "Nastavení",
        "back_button": "Zpět",
        "mute_button": "Ztlumit",  # New key
        "unmute_button": "Zapnout", # New key

        # UI Labels
        "health_label": "Životy",
        "gold_label": "Zlato",
        "wave_label": "Vlna",
        "next_wave_label": "Další",
        "next_wave_starting": "Začíná...",
        "tower_level_label": "Úr", # Zkratka pro úroveň
        "volume_label_music": "Hlasitost Hudby:", # New key
        "volume_label_sfx": "Hlasitost Zvuků:",   # New key

        # Tutorial Instructions
        "tut_line_1": "Nepřátelé jdou po cestě. Stavěj věže na platformách, abys je zastavil.",
        "tut_line_2": "Klikni na ikonu věže dole pro výběr, pak klikni na platformu pro stavbu.",
        "tut_line_3": "Klikni na postavenou věž pro Vylepšení/Prodej. Získávej zlato ničením nepřátel.",
        "tut_line_4": "Přežij všechny vlny a vyhraj! Stiskni '?' během hry pro tuto nápovědu.",

        # Tower Info Labels (in tutorial)
        "cost_label": "Cena",
        "damage_label": "Pošk", # Zkratka pro poškození
        "range_label": "Dosah",
        "rate_label": "Rychl", # Zkratka pro rychlost
        "effect_label": "Efekt",
        "effect_slow": "Zpomalení",
        "effect_poison": "Jed",
        "effect_chain": "Řetězové poškození",
        "stats_error": "Chyba: Statistiky chybí",
        "rate_suffix": "/s",

        # Tower Names (for Tutorial/Help)
        "tower_name_archer": "Lukostřelec",
        "tower_name_cannon": "Kanón",
        "tower_name_crossbow": "Kuše",
        "tower_name_ice_wizard": "Ledový Mág",
        "tower_name_lightning_wizard": "Bleskový Mág",
        "tower_name_poison_wizard": "Jedový Mág",

        # Other Messages
        "paused_message": "Hra Pozastavena",
        "resumed_message": "Hra Pokračuje",
        "starting_message": "Začíná Nová Hra...",
        "restarting_message": "Restartuji Hru...",
        "showing_tutorial": "Zobrazuji Nápovědu...",
        "tutorial_finished": "Nápověda dokončena. Začíná Nová Hra...",
        "wave_starting": "Vlna {current_wave} začíná! Nepřátelé: {enemies_def}",
        "wave_completed": "Vlna {current_wave} dokončena!",
        "wave_no_definition": "Vlna {current_wave} nemá definici.",
        "tower_placed": "Postavena věž {tower_type} (Úroveň 1) na ({grid_x}, {grid_y}) za {cost} zlata. Pole označeno jako obsazené.",
        "tower_selected": "Vybrána existující věž: {tower_type} na {pos}",
        "tower_upgraded": "Vylepšena věž {tower_type} na Úroveň {level} za {cost} zlata.",
        "tower_max_level": "Věž {tower_type} je již na maximální úrovni.",
        "tower_sell": "Prodávám věž {tower_type} za {price} zlata.",
        "platform_restored": "Obnovena platforma na ({grid_x}, {grid_y})",
        "cannot_build_occupied": "Nelze stavět: Věž již existuje na ({grid_x}, {grid_y}).",
        "cannot_build_invalid_tile": "Nelze stavět: Místo ({grid_x}, {grid_y}) není platná platforma nebo je mimo mapu.",
        "cannot_build_no_gold": "Nelze stavět {tower_type}: Nedostatek zlata (Potřeba {cost}, Máš {have})",
        "cannot_upgrade_no_gold": "Nedostatek zlata pro vylepšení {tower_type}. Potřeba {cost}, Máš {have}.",
        "error_create_tower": "CHYBA: Nepodařilo se vytvořit věž typu {tower_type}",
        "error_cost_missing": "CHYBA: Nelze najít cenu úrovně 1 pro typ věže {tower_type}. Nelze stavět.",
        "warning_tile_not_occupied": "Varování: Pole na ({grid_x}, {grid_y}) nebylo typu 3 při prodeji.",
        "warning_invalid_coords_sell": "Varování: Neplatné souřadnice ({grid_x}, {grid_y}) při prodeji věže.",
        "boss_scaling_applied": "Aplikuji speciální škálování pro Bossa Démona ve Vlně 10!",

        # Game End Messages
        "game_over_message": "Přežil jsi {waves_survived} vln, ale nepřátelé prorazili!",
        "victory_message": "Gratuluji! Ubránil jsi hrad proti všem {max_waves} vlnám!",
    }
}

# Default language
DEFAULT_LANG = 'EN'
current_language = DEFAULT_LANG # Start with default

def set_language(lang_code):
    """Sets the current language."""
    global current_language
    if lang_code in LANGUAGES:
        current_language = lang_code
        print(f"Language set to: {lang_code}")
    else:
        print(f"Warning: Language code '{lang_code}' not found. Keeping '{current_language}'.")
        # Optionally fall back to default if current is somehow invalid
        if current_language not in LANGUAGES:
             current_language = DEFAULT_LANG

def get_text(key, **kwargs):
    """Gets the text for a given key in the current language, with optional formatting."""
    # Ensure current_language is valid, fallback to DEFAULT_LANG if not
    if current_language not in LANGUAGES:
        print(f"Warning: Current language '{current_language}' is invalid. Falling back to '{DEFAULT_LANG}'.")
        set_language(DEFAULT_LANG) # Reset to default

    lang_dict = LANGUAGES.get(current_language) # No need for default here due to check above
    text_template = lang_dict.get(key, f"<{key}_missing>") # Return key name if missing

    # Attempt formatting only if kwargs are provided
    if kwargs:
        try:
            return text_template.format(**kwargs)
        except KeyError as e:
            print(f"Warning: Missing format key '{e}' for text key '{key}' in language '{current_language}'")
            return text_template # Return unformatted template on error
        except Exception as e:
            print(f"Error formatting text key '{key}' in language '{current_language}': {e}")
            return text_template # Return unformatted template on other errors
    else:
        # If no kwargs, return the template directly (avoids .format() errors if template has {})
        return text_template

# Example usage:
# set_language('CZ')
# print(get_text("start_button"))
# print(get_text("wave_starting", current_wave=5, enemies_def="Slimes"))
# print(get_text("tower_name_archer"))
