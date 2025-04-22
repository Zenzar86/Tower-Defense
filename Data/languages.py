# -*- coding: utf-8 -*-
LANGUAGES = {
    'EN': {
        # Názvy Menu
        "main_menu_title": "Tower Defense",
        "paused_title": "Paused",
        "tutorial_title": "How to Play",
        "game_over_title": "Game Over - You Lost!",
        "victory_title": "Victory! - You Won!",
        "settings_title": "Settings",
        "mission_select_title": "Select Mission", # New

        # Popisky Tlačítek
        "start_button": "Start",
        "exit_button": "Exit",
        "restart_button": "Restart",
        "tutorial_ok_button": "Ok, Lets Start",
        "upgrade_button": "Upgrade",
        "max_level_button": "Max Level",
        "sell_button": "Sell",
        "help_button": "?", 
        "settings_button": "Settings",
        "back_button": "Back",
        "mute_button": "Mute",     
        "unmute_button": "Unmute", 
        "continue_button": "Continue",
        "mission1_button": "Mission 1", # New
        "mission2_button": "Mission 2", # New
        "main_menu_button": "Main Menu", # New
 
        # UI Popisky
        "health_label": "Health",
        "gold_label": "Gold",
        "wave_label": "Wave",
        "next_wave_label": "Next",
        "next_wave_starting": "Starting...",
        "tower_level_label": "Lvl",
        "volume_label_music": "Music Volume:", 
        "volume_label_sfx": "SFX Volume:",     

        # Instrukce v Tutoriálu
        "tut_line_1": "Enemies follow the path. Build towers on platforms to stop them.",
        "tut_line_2": "Click tower icons below to select, then click a platform to build.",
        "tut_line_3": "Click placed towers to Upgrade/Sell. Earn gold by defeating enemies.",
        "tut_line_4": "Survive all waves to win! Press '?' during game for this help.",

        # Popisky Informací o Věžích (v tutoriálu)
        "cost_label": "Cost",
        "damage_label": "Dmg",
        "range_label": "Range",
        "rate_label": "Rate",
        "effect_label": "Effect",
        "effect_slow": "Slow",
        "effect_poison": "Poison",
        "effect_chain": "Chain damage",
        "stats_error": "Error: Stats missing",
        "rate_suffix": "/s",

        # Názvy Věží (pro Tutoriál/Nápovědu)
        "tower_name_archer": "Archer",
        "tower_name_cannon": "Cannon",
        "tower_name_crossbow": "Crossbow",
        "tower_name_ice_wizard": "Ice Wizard",
        "tower_name_lightning_wizard": "Lightning Wizard", 
        "tower_name_poison_wizard": "Poison Wizard",

        # Ostatní Zprávy
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

        # Zprávy na Konci Hry
        "game_over_message": "You survived {waves_survived} waves, but the enemies broke through!",
        "victory_message": "Congratulations! You defended the castle against all {max_waves} waves!",

        # Map Transition Messages
        "map1_complete_title": "Map 1 Complete!",
        "map1_complete_message": "Prepare for the next challenge!",
        "continue_button": "Continue",
    },
    'CZ': {
        # Tituly menu
        "main_menu_title": "Obrana Věží",
        "paused_title": "Pozastaveno",
        "tutorial_title": "Jak Hrát",
        "game_over_title": "Konec Hry - Prohrál Jsi!",
        "victory_title": "Vítězství!",
        "settings_title": "Nastavení",
        "mission_select_title": "Výběr Mise", # New

        # Popisky tlačítek
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
        "mute_button": "Ztlumit",  
        "unmute_button": "Zapnout",
        "continue_button": "Pokračovat",
        "mission1_button": "Mise 1", # New
        "mission2_button": "Mise 2", # New
        "main_menu_button": "Hlavní Menu", # New
 
        # Popisky UI
        "health_label": "Životy",
        "gold_label": "Zlato",
        "wave_label": "Vlna",
        "next_wave_label": "Další",
        "next_wave_starting": "Začíná...",
        "tower_level_label": "Úroveň", 
        "volume_label_music": "Hlasitost Hudby:", 
        "volume_label_sfx": "Hlasitost Zvuků:",   

        # Pokyny pro tutoriál
        "tut_line_1": "Nepřátelé jdou po cestě. Stavěj věže na platformách, abys je zastavil.",
        "tut_line_2": "Klikni na ikonu věže dole pro výběr, pak klikni na platformu pro stavbu.",
        "tut_line_3": "Klikni na postavenou věž pro Vylepšení/Prodej. Získávej zlato ničením nepřátel.",
        "tut_line_4": "Přežij všechny vlny a vyhraj! Stiskni '?' během hry pro tuto nápovědu.",

        # Popisky informací o věžích (v tutoriálu)
        "cost_label": "Cena",
        "damage_label": "Poškození", 
        "range_label": "Dosah",
        "rate_label": "Rychlost", 
        "effect_label": "Efekt",
        "effect_slow": "Zpomalení",
        "effect_poison": "Jed",
        "effect_chain": "Řetězové poškození",
        "stats_error": "Chyba: Statistiky chybí",
        "rate_suffix": "/s",

        # Názvy věží (pro tutoriál/nápovědu)
        "tower_name_archer": "Lukostřelec",
        "tower_name_cannon": "Kanón",
        "tower_name_crossbow": "Kuše",
        "tower_name_ice_wizard": "Ledový Mág",
        "tower_name_lightning_wizard": "Bleskový Mág",
        "tower_name_poison_wizard": "Jedový Mág",

        # Další zprávy
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

        # Map Transition Messages (Překlady)
        "map1_complete_title": "Mapa 1 Dokončena!",
        "map1_complete_message": "Připrav se na další výzvu!",
        "continue_button": "Pokračovat",
    }
}

# Výchozí jazyk
DEFAULT_LANG = 'EN'
current_language = DEFAULT_LANG # výchozí

def set_language(lang_code):
    """Nastaví aktuální jazyk."""
    global current_language
    if lang_code in LANGUAGES:
        current_language = lang_code
    else:
        # Volitelně se vrátit k výchozímu, pokud je aktuální nějakým způsobem neplatný
        if current_language not in LANGUAGES:
             current_language = DEFAULT_LANG

def get_text(key, **kwargs):
    """Získá text pro daný klíč v aktuálním jazyce, s volitelným formátováním."""
    # Zajistěte, aby byl current_language platný, v případě neplatnosti se vrátí k DEFAULT_LANG
    if current_language not in LANGUAGES:
        set_language(DEFAULT_LANG) 

    lang_dict = LANGUAGES.get(current_language) 
    text_template = lang_dict.get(key, f"<{key}_missing>") 

    # Pokus o formátování pouze pokud jsou poskytnuty kwargs
    if kwargs:
        try:
            return text_template.format(**kwargs)
        except KeyError as e:
            return text_template 
        except Exception as e:
            return text_template 
    else:
        # Pokud nejsou žádné kwargs, vraťte šablonu přímo (vyhnete se chybám .format(), pokud má šablona {})
        return text_template